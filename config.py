# 加密货币交易机会分析器配置文件

import os
from typing import Dict, List, Any

def validate_config() -> bool:
    """验证配置文件的完整性"""
    required_configs = [
        'EXCHANGE_CONFIG', 'EXCHANGES', 'NETWORK_CONFIG',
        'SYMBOL_FILTER', 'INDICATOR_CONFIG', 'DATA_CONFIG'
    ]
    
    for config_name in required_configs:
        if config_name not in globals():
            print(f"❌ 缺少配置: {config_name}")
            return False
    
    # 验证交易所配置
    if not EXCHANGES:
        print("❌ EXCHANGES 配置为空")
        return False
    
    enabled_exchanges = [ex for ex in EXCHANGES if ex.get('enabled', True)]
    if not enabled_exchanges:
        print("⚠️ 没有启用的交易所")
    
    print("✅ 配置验证通过")
    return True

# 交易所配置
EXCHANGE_CONFIG = {
    'name': 'binance',  # 交易所名称
    'testnet': False,   # 是否使用测试网络
    'rate_limit': True, # 是否启用频率限制
    'timeout': 30000,   # 请求超时时间（毫秒）
}

# 新增：多交易所与网络配置（供后续多交易所聚合使用）
EXCHANGES = [
    {
        'name': 'binance',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 1_000_000,
        'priority': 1,  # 优先级，数字越小优先级越高
        'description': '币安 - 全球最大加密货币交易所',
        'options': {
            'defaultType': 'future',  # 默认市场类型：'spot'现货 或 'future'合约
        }
    },
    {
        'name': 'okx',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 800_000,
        'priority': 2,
        'description': 'OKX - 知名衍生品交易所',
        'options': {
            'defaultType': 'future',
        }
    },
    {
        'name': 'kucoin',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 500_000,
        'priority': 3,
        'description': 'KuCoin - 用户友好的交易所'
    },
    {
        'name': 'huobi',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 600_000,
        'priority': 4,
        'description': 'Huobi - 老牌交易所'
    },
    {
        'name': 'bybit',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 400_000,
        'priority': 5,
        'description': 'Bybit - 专业衍生品交易所',
        'options': {
            'defaultType': 'future',
        }
    },
    {
        'name': 'gateio',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 300_000,
        'priority': 6,
        'description': 'Gate.io - 创新币种丰富'
    },
    {
        'name': 'mexc',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 200_000,
        'priority': 7,
        'description': 'MEXC - 新兴交易所'
    },
    {
        'name': 'bitget',
        'enabled': True,
        'quote_currency': 'USDT',
        'min_volume_usd': 300_000,
        'priority': 8,
        'description': 'Bitget - 社交交易平台'
    },
    {
        'name': 'coinbase',
        'enabled': False,  # 默认关闭，需要特殊配置
        'quote_currency': 'USD',
        'min_volume_usd': 2_000_000,
        'priority': 9,
        'description': 'Coinbase - 美国合规交易所'
    },
    {
        'name': 'kraken',
        'enabled': False,  # 默认关闭，需要特殊配置
        'quote_currency': 'USD',
        'min_volume_usd': 1_500_000,
        'priority': 10,
        'description': 'Kraken - 欧洲老牌交易所'
    },
    {
        'name': 'bitfinex',
        'enabled': False,  # 默认关闭，需要特殊配置
        'quote_currency': 'USD',
        'min_volume_usd': 1_000_000,
        'priority': 11,
        'description': 'Bitfinex - 专业交易平台'
    },
    {
        'name': 'upbit',
        'enabled': False,  # 默认关闭，韩国交易所
        'quote_currency': 'KRW',
        'min_volume_usd': 500_000,
        'priority': 12,
        'description': 'Upbit - 韩国最大交易所'
    }
]

NETWORK_CONFIG = {
    'rate_limit': True,
    'timeout': 10000,  # 减少到10秒超时
    'retry_count': 2,  # 减少重试次数
    'retry_delay': 1,  # 减少重试延迟
    # 'proxies': {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'},
}

# 交易对筛选配置
SYMBOL_FILTER = {
    'quote_currency': 'USDT',     # 计价货币
    'min_volume_usd': 1000000,    # 最小24小时交易量（美元）
    'max_symbols': 200,           # 最大分析交易对数量
    'market_types': ['spot', 'future'],  # 市场类型：现货和合约都支持
}

# 技术指标配置
INDICATOR_CONFIG = {
    'volume_ratio_threshold': 3.0,  # 交易量放大倍数阈值
    'ma_periods': [5, 10, 20],     # 移动平均线周期
    'volume_ma_period': 30,         # 近30根作为均量，更稳定的交易量分析
    'price_volatility_period': 10,  # 价格波动率计算周期
}

# 数据获取配置
DATA_CONFIG = {
    'default_timeframe': '1h',      # 默认时间周期
    'default_limit': 100,           # 默认K线数量
    'update_interval': 180,         # 数据更新间隔（秒）- Bolt.host优化
    'chart_limit': 100,             # 图表显示K线数量
}

# 图表配置
CHART_CONFIG = {
    'height': 800,                  # 图表高度
    'colors': {
        'price': '#1f77b4',         # 价格线颜色
        'ma5': '#ff7f0e',           # MA5颜色
        'ma10': '#2ca02c',          # MA10颜色
        'ma20': '#d62728',          # MA20颜色
        'volume': '#17a2b8',        # 交易量颜色
        'volume_ratio': '#e83e8c',  # 交易量比率颜色
    }
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',                # 日志级别
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'crypto_analyzer.log',  # 日志文件
}

# 风险提示
RISK_DISCLAIMER = """
⚠️ 风险提示：
1. 本工具仅用于技术分析，不构成投资建议
2. 加密货币交易存在高风险，请谨慎投资
3. 交易量放大可能意味着价格剧烈波动
4. 请根据自身风险承受能力做出投资决策
""" 