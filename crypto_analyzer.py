import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Any
import logging
from config import EXCHANGE_CONFIG, EXCHANGES, NETWORK_CONFIG, INDICATOR_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoAnalyzer:
    def __init__(self, exchange_name: str = 'binance'):
        """
        初始化加密货币分析器
        
        Args:
            exchange_name: 兼容旧参数，不再仅依赖单一交易所
        """
        self.exchange_name = exchange_name
        self.exchanges = self._init_exchanges()
        self.symbols: List[str] = []
        self.exchange_by_symbol: Dict[str, str] = {}
        self.data_cache: Dict[Tuple[str, str], pd.DataFrame] = {}
    
    def _init_exchanges(self):
        """初始化交易所实例，按优先级排序"""
        instances = []
        enabled_exchanges = [ex for ex in EXCHANGES if ex.get('enabled', True)]
        
        # 按优先级排序
        enabled_exchanges.sort(key=lambda x: x.get('priority', 999))
        
        logger.info(f"初始化 {len(enabled_exchanges)} 个启用的交易所")
        
        for ex in enabled_exchanges:
            name = ex['name']
            params = {
                'enableRateLimit': NETWORK_CONFIG.get('rate_limit', True),
                'timeout': NETWORK_CONFIG.get('timeout', 30000)
            }
            
            # 添加交易所特定的options配置（如合约支持）
            options = ex.get('options', {})
            if options:
                params['options'] = options
            
            proxies = NETWORK_CONFIG.get('proxies')
            if proxies:
                params['proxies'] = proxies
            
            try:
                # 根据配置显示市场类型
                market_type = options.get('defaultType', 'spot')
                logger.info(f"正在初始化交易所: {name} ({ex.get('description', '')}) [{market_type} 市场]")
                inst = getattr(ccxt, name)(params)
                
                # 测试连接（带超时控制）
                try:
                    # 设置更短的超时时间
                    inst.timeout = 10000  # 10秒超时
                    markets = inst.load_markets()
                    logger.info(f"✅ {name} 初始化成功，支持 {len(markets)} 个交易对")
                    instances.append((name, ex, inst))
                except Exception as test_err:
                    error_msg = str(test_err)
                    if "TimeoutError" in error_msg or "timeout" in error_msg.lower():
                        logger.warning(f"⏰ {name} 连接超时，跳过该交易所")
                    elif "ConnectionError" in error_msg or "connection" in error_msg.lower():
                        logger.warning(f"🔌 {name} 连接错误，跳过该交易所")
                    else:
                        logger.warning(f"⚠️ {name} 连接测试失败: {test_err}")
                    # 连接失败的交易所直接跳过，不添加到实例列表
                    continue
                    
            except Exception as e:
                logger.error(f"❌ 初始化交易所 {name} 失败: {e}")
                continue
        
        # 向后兼容：若未配置或全部禁用，则创建单一 exchange_name
        if not instances:
            logger.warning("没有启用的交易所，使用默认配置")
            try:
                params = {
                    'enableRateLimit': EXCHANGE_CONFIG.get('rate_limit', True),
                    'timeout': EXCHANGE_CONFIG.get('timeout', 30000)
                }
                proxies = EXCHANGE_CONFIG.get('proxies')
                if proxies:
                    params['proxies'] = proxies
                inst = getattr(ccxt, self.exchange_name)(params)
                instances.append((self.exchange_name, {
                    'name': self.exchange_name,
                    'quote_currency': 'USDT',
                    'min_volume_usd': 1_000_000,
                    'priority': 999,
                    'description': f'默认交易所: {self.exchange_name}'
                }, inst))
                logger.info(f"✅ 默认交易所 {self.exchange_name} 初始化成功")
            except Exception as e:
                logger.error(f"❌ 初始化默认交易所失败: {e}")
        
        logger.info(f"成功初始化 {len(instances)} 个交易所")
        return instances

    def _estimate_quote_volume(self, ticker: Dict) -> float:
        price = (
            ticker.get('last')
            or ticker.get('close')
            or ticker.get('ask')
            or ticker.get('bid')
            or 0
        )
        base_volume = (
            ticker.get('baseVolume')
            or ticker.get('volume')
            or 0
        )
        quote_volume = ticker.get('quoteVolume')
        if quote_volume is None:
            quote_volume = base_volume * price if (base_volume and price) else 0
        return float(quote_volume or 0)

    def get_tradable_symbols(self, quote_currency: str = 'USDT', min_volume: float = 1000000) -> List[str]:
        """聚合多个交易所可交易对，按成交额过滤。支持现货和合约市场。"""
        aggregated: List[str] = []
        exchange_by_symbol: Dict[str, str] = {}
        
        logger.info(f"开始获取交易对，最小交易量: ${min_volume:,.0f}")
        
        for name, ex_conf, inst in self.exchanges:
            try:
                # 获取市场类型
                options = ex_conf.get('options', {})
                market_type = options.get('defaultType', 'spot')
                logger.info(f"正在处理交易所: {name} (市场类型: {market_type})")
                
                markets = inst.load_markets()
                
                # 优先使用各自配置的 quote 过滤
                q = ex_conf.get('quote_currency', quote_currency)
                mv = ex_conf.get('min_volume_usd', min_volume)
                
                # 根据市场类型过滤交易对
                if market_type == 'future':
                    # 过滤合约交易对
                    candidates = [s for s in markets.keys() if s.endswith(f'/{q}') and markets[s].get('type') == 'future']
                else:
                    # 过滤现货交易对
                    candidates = [s for s in markets.keys() if s.endswith(f'/{q}') and markets[s].get('type') == 'spot']
                
                logger.info(f"{name} [{market_type}] 找到 {len(candidates)} 个候选交易对")
                
                # 批量获取
                tickers = {}
                try:
                    if getattr(inst, 'has', {}).get('fetchTickers'):
                        tickers = inst.fetch_tickers(candidates)
                        logger.info(f"{name} 批量获取tickers成功")
                except Exception as bulk_err:
                    logger.warning(f"{name} 批量fetchTickers失败: {bulk_err}")
                    tickers = {}
                
                valid_count = 0
                for sym in candidates:
                    try:
                        t = tickers.get(sym) if tickers else inst.fetch_ticker(sym)
                        qv = self._estimate_quote_volume(t)
                        if qv and qv > mv:
                            aggregated.append(sym)
                            exchange_by_symbol[sym] = name
                            valid_count += 1
                    except Exception as e:
                        logger.debug(f"{name} 获取 {sym} ticker 失败: {e}")
                        continue
                
                logger.info(f"{name} 有效交易对数量: {valid_count}")
                
            except Exception as e:
                logger.error(f"获取 {name} 交易对列表失败: {e}")
                continue
        
        # 去重并保存映射
        unique_symbols = sorted(list(set(aggregated)))
        self.symbols = unique_symbols
        self.exchange_by_symbol = exchange_by_symbol
        logger.info(f"聚合得到 {len(unique_symbols)} 个可交易对")
        
        if not unique_symbols:
            logger.warning("未找到符合条件的交易对，请检查网络连接或调整筛选条件")
            return []
        
        return unique_symbols

    def get_exchange_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有交易所的状态信息"""
        status = {}
        
        for name, ex_conf, inst in self.exchanges:
            try:
                # 测试基本连接
                markets = inst.load_markets()
                market_count = len(markets)
                
                # 测试获取ticker
                test_symbols = list(markets.keys())[:5]  # 测试前5个交易对
                ticker_success = 0
                
                for symbol in test_symbols:
                    try:
                        ticker = inst.fetch_ticker(symbol)
                        if ticker:
                            ticker_success += 1
                    except:
                        pass
                
                status[name] = {
                    'enabled': True,
                    'connected': True,
                    'market_count': market_count,
                    'ticker_success_rate': ticker_success / len(test_symbols) if test_symbols else 0,
                    'description': ex_conf.get('description', ''),
                    'priority': ex_conf.get('priority', 999),
                    'quote_currency': ex_conf.get('quote_currency', 'USDT'),
                    'min_volume_usd': ex_conf.get('min_volume_usd', 0)
                }
                
            except Exception as e:
                status[name] = {
                    'enabled': True,
                    'connected': False,
                    'error': str(e),
                    'description': ex_conf.get('description', ''),
                    'priority': ex_conf.get('priority', 999),
                    'quote_currency': ex_conf.get('quote_currency', 'USDT'),
                    'min_volume_usd': ex_conf.get('min_volume_usd', 0)
                }
        
        return status

    def get_exchange_statistics(self) -> Dict[str, Any]:
        """获取交易所统计信息"""
        status = self.get_exchange_status()
        
        total_exchanges = len(status)
        connected_exchanges = sum(1 for s in status.values() if s.get('connected', False))
        total_markets = sum(s.get('market_count', 0) for s in status.values())
        
        # 按交易所统计交易对数量
        exchange_symbol_counts = {}
        for symbol, exchange in self.exchange_by_symbol.items():
            exchange_symbol_counts[exchange] = exchange_symbol_counts.get(exchange, 0) + 1
        
        return {
            'total_exchanges': total_exchanges,
            'connected_exchanges': connected_exchanges,
            'connection_rate': connected_exchanges / total_exchanges if total_exchanges > 0 else 0,
            'total_markets': total_markets,
            'exchange_symbol_counts': exchange_symbol_counts,
            'status_details': status
        }

    def _get_exchange_for_symbol(self, symbol: str):
        """根据交易对获取对应的交易所实例"""
        name = self.exchange_by_symbol.get(symbol)
        if not name:
            # 回退：第一个实例
            return self.exchanges[0][2] if self.exchanges else None
        for n, _, inst in self.exchanges:
            if n == name:
                return inst
        return None

    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """获取K线数据，仅使用真实API数据"""
        inst = self._get_exchange_for_symbol(symbol)
        if not inst:
            logger.error(f"无法找到 {symbol} 对应的交易所实例")
            return pd.DataFrame()
        
        try:
            ohlcv = inst.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                logger.warning(f"{symbol} 返回空数据")
                return pd.DataFrame()
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # 验证数据质量
            if df.empty or df['volume'].sum() == 0:
                logger.warning(f"{symbol} 数据质量不佳，跳过")
                return pd.DataFrame()
                
            logger.debug(f"成功获取 {symbol} 的 {len(df)} 条K线数据")
            return df
            
        except Exception as e:
            logger.error(f"获取 {symbol} 的OHLCV数据失败: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # MA
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        # 最近3根均量（对齐 vol）
        vol_n = max(1, int(INDICATOR_CONFIG.get('volume_ma_period', 3)))
        df['volume_maN'] = df['volume'].rolling(window=vol_n).mean()
        df['volume_ratio'] = df['volume'] / df['volume_maN']
        # 价格变化与波动率
        df['price_change'] = df['close'].pct_change()
        df['price_volatility'] = df['price_change'].rolling(window=INDICATOR_CONFIG.get('price_volatility_period', 10)).std()
        return df

    def identify_trading_opportunities(self, symbol: str) -> Dict:
        """识别交易机会，仅使用真实API数据"""
        try:
            df = self.get_ohlcv_data(symbol, '1h', 100)  # 增加数据量以确保有30根K线
            if df.empty or len(df) < 20:
                logger.debug(f"{symbol} 数据不足，跳过分析")
                return {}
            
            df = self.calculate_indicators(df)
            if df.empty or len(df) < 20:
                logger.debug(f"{symbol} 指标计算后数据不足，跳过分析")
                return {}
            
            latest = df.iloc[-1]
            
            # 验证数据有效性
            if (pd.isna(latest['volume']) or latest['volume'] <= 0 or
                pd.isna(latest['close']) or latest['close'] <= 0):
                logger.debug(f"{symbol} 最新数据无效，跳过分析")
                return {}
            
            # 计算交易量比率（当前K线交易量 / 前30根K线平均交易量）
            if len(df) < 31:
                logger.debug(f"{symbol} 数据不足31根K线，跳过分析")
                return {}
            
            # 当前K线交易量
            current_volume = latest['volume']
            
            # 前30根K线的平均交易量
            previous_30_volumes = df['volume'].iloc[-31:-1]  # 排除当前K线，取前30根
            avg_volume_30 = previous_30_volumes.mean()
            
            if pd.isna(avg_volume_30) or avg_volume_30 <= 0:
                logger.debug(f"{symbol} 前30根K线平均交易量无效，跳过分析")
                return {}
            
            # 计算交易量倍数
            volume_ratio = current_volume / avg_volume_30
            
            # 计算移动平均线
            ma5 = latest['MA5'] if not pd.isna(latest['MA5']) else 0
            ma10 = latest['MA10'] if not pd.isna(latest['MA10']) else 0
            ma20 = latest['MA20'] if not pd.isna(latest['MA20']) else 0
            
            # 判断MA排列
            ma_bullish = (ma5 > ma10 > ma20) and (ma5 > 0 and ma10 > 0 and ma20 > 0)
            ma_bearish = (ma5 < ma10 < ma20) and (ma5 > 0 and ma10 > 0 and ma20 > 0)
            
            # 生成交易信号和推荐状态
            signal = 'none'
            is_recommended = False
            
            # 5倍阈值推荐逻辑
            if volume_ratio >= 5.0:
                is_recommended = True
                if ma_bullish:
                    signal = 'long'
                elif ma_bearish:
                    signal = 'short'
                else:
                    signal = 'hold'  # 超过5倍但MA不明确
            elif volume_ratio >= INDICATOR_CONFIG.get('volume_ratio_threshold', 3.0):
                # 3-5倍之间，根据MA排列判断
                if ma_bullish:
                    signal = 'long'
                elif ma_bearish:
                    signal = 'short'
            
            # 计算24小时价格变化
            price_change_24h = 0.0
            if len(df) >= 24:
                price_24h_ago = df['close'].iloc[-24]
                if not pd.isna(price_24h_ago) and price_24h_ago > 0:
                    price_change_24h = (latest['close'] - price_24h_ago) / price_24h_ago
            
            exchange_name = self.exchange_by_symbol.get(symbol, 'unknown')
            
            result = {
                'symbol': symbol,
                'exchange': exchange_name,
                'current_price': float(latest['close']),
                'volume_ratio': float(volume_ratio),
                'current_volume': float(current_volume),
                'avg_volume_30': float(avg_volume_30),
                'ma5': float(ma5),
                'ma10': float(ma10),
                'ma20': float(ma20),
                'signal': signal,
                'is_recommended': is_recommended,
                'price_change_24h': float(price_change_24h),
                'volatility': float(latest['price_volatility']) if not pd.isna(latest['price_volatility']) else 0.0
            }
            
            logger.debug(f"{symbol} 分析完成: {signal} 信号, 交易量比率: {volume_ratio:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"识别交易机会失败 {symbol}: {e}")
            return {}

    def get_top_opportunities(self, top_n: int = 20, sort_by: str = 'volume_ratio') -> List[Dict]:
        """获取前N个交易机会，支持多种排序方式"""
        symbols = self.symbols or self.get_tradable_symbols()
        if not symbols:
            logger.warning("没有可用的交易对")
            return []
        
        logger.info(f"开始分析 {len(symbols)} 个交易对...")
        opportunities = []
        
        for i, symbol in enumerate(symbols, 1):
            try:
                opp = self.identify_trading_opportunities(symbol)
                if opp:  # 包含所有有数据的交易对
                    # 添加综合评分
                    opp['composite_score'] = self._calculate_composite_score(opp)
                    opportunities.append(opp)
                    logger.debug(f"分析完成: {symbol} - 比率: {opp['volume_ratio']:.2f}x, 推荐: {opp.get('is_recommended', False)}")
                
                # 显示进度
                if i % 50 == 0 or i == len(symbols):
                    logger.info(f"分析进度: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%)")
                    
            except Exception as e:
                logger.error(f"分析 {symbol} 失败: {e}")
                continue
        
        # 智能排序
        opportunities = self._smart_sort_opportunities(opportunities, sort_by)
        
        logger.info(f"找到 {len(opportunities)} 个交易机会，返回前 {min(top_n, len(opportunities))} 个")
        return opportunities[:top_n]
    
    def _calculate_composite_score(self, opp: Dict) -> float:
        """计算综合评分"""
        try:
            # 基础评分因子
            volume_ratio = opp.get('volume_ratio', 0)
            price_change = abs(opp.get('price_change_24h', 0)) * 100  # 转换为百分比
            current_volume = opp.get('current_volume', 0)
            
            # 评分权重
            volume_weight = 0.4  # 交易量比率权重
            momentum_weight = 0.3  # 价格动量权重
            liquidity_weight = 0.3  # 流动性权重
            
            # 标准化评分 (0-100)
            volume_score = min(volume_ratio * 10, 100)  # 交易量比率评分
            momentum_score = min(price_change * 2, 100)  # 价格动量评分
            liquidity_score = min(current_volume / 1000000 * 20, 100)  # 流动性评分
            
            # 综合评分
            composite_score = (
                volume_score * volume_weight +
                momentum_score * momentum_weight +
                liquidity_score * liquidity_weight
            )
            
            return round(composite_score, 2)
            
        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")
            return 0.0
    
    def _smart_sort_opportunities(self, opportunities: List[Dict], sort_by: str) -> List[Dict]:
        """智能排序交易机会"""
        try:
            if sort_by == 'volume_ratio':
                # 按交易量比率排序，但考虑其他因素
                return sorted(opportunities, key=lambda x: (
                    x.get('volume_ratio', 0),
                    x.get('composite_score', 0),
                    x.get('current_volume', 0)
                ), reverse=True)
            
            elif sort_by == 'current_volume':
                # 按交易量排序
                return sorted(opportunities, key=lambda x: x.get('current_volume', 0), reverse=True)
            
            elif sort_by == 'price_change_24h':
                # 按价格变化排序
                return sorted(opportunities, key=lambda x: abs(x.get('price_change_24h', 0)), reverse=True)
            
            elif sort_by == 'current_price':
                # 按价格排序
                return sorted(opportunities, key=lambda x: x.get('current_price', 0), reverse=True)
            
            elif sort_by == 'composite_score':
                # 按综合评分排序
                return sorted(opportunities, key=lambda x: x.get('composite_score', 0), reverse=True)
            
            else:
                # 默认按交易量比率排序
                return sorted(opportunities, key=lambda x: x.get('volume_ratio', 0), reverse=True)
                
        except Exception as e:
            logger.error(f"排序失败: {e}")
            # 回退到简单排序
            return sorted(opportunities, key=lambda x: x.get('volume_ratio', 0), reverse=True)


    def get_symbol_data_for_chart(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Dict:
        try:
            df = self.get_ohlcv_data(symbol, timeframe, limit)
            if df.empty:
                return {}
            df = self.calculate_indicators(df)
            return {
                'symbol': symbol,
                'timestamps': df.index.strftime('%Y-%m-%d %H:%M').tolist(),
                'prices': df['close'].tolist(),
                'opens': df['open'].tolist(),
                'highs': df['high'].tolist(),
                'lows': df['low'].tolist(),
                'volumes': df['volume'].tolist(),
                'ma5': df['MA5'].tolist(),
                'ma10': df['MA10'].tolist(),
                'ma20': df['MA20'].tolist(),
                'volume_ratio': df['volume_ratio'].tolist()
            }
        except Exception as e:
            logger.error(f"获取{symbol}图表数据失败: {e}")
            return {} 