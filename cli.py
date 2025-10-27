#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币交易机会分析器 - 命令行工具
"""

import argparse
import sys
import json
from datetime import datetime
from crypto_analyzer import CryptoAnalyzer
from config import SYMBOL_FILTER, INDICATOR_CONFIG

def format_volume(volume: float) -> str:
    """智能格式化交易量显示"""
    if volume >= 1000000:
        return f"{volume/1000000:.1f}M"
    elif volume >= 1000:
        return f"{volume/1000:.1f}K"
    else:
        return f"{volume:.0f}"

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🚀 加密货币交易机会分析器 - CLI工具")
    print("基于交易量放大和MA多头排列的交易信号识别")
    print("=" * 60)
    print()

def print_opportunity(opp, index):
    """打印单个交易机会"""
    signal_icon = "🟢" if opp['signal'] == 'long' else "🔴"
    signal_text = "做多" if opp['signal'] == 'long' else "做空"
    ex = opp.get('exchange', '')
    
    print(f"{index:2d}. {opp['symbol']:<15} [{ex}] {signal_icon} {signal_text}")
    print(f"    价格: ${opp['current_price']:<12.6f} | 交易量比率: {opp['volume_ratio']:.2f}x")
    print(f"    平均交易量: {format_volume(opp.get('avg_volume_30', 0))} | 当前交易量: {format_volume(opp['current_volume'])}")
    print(f"    MA5: ${opp['ma5']:<12.6f} | MA10: ${opp['ma10']:<12.6f} | MA20: ${opp['ma20']:<12.6f}")
    print(f"    24h涨跌: {opp['price_change_24h']*100:+.2f}% | 波动率: {opp['volatility']:.4f}")
    print()

def scan_opportunities(analyzer, top_n=20):
    """扫描交易机会"""
    print("🔍 正在扫描交易机会...")
    print(f"筛选条件: 交易量比率 >= {INDICATOR_CONFIG['volume_ratio_threshold']}x (基于前30根K线平均)")
    print(f"MA多头排列: MA5 > MA10 > MA20 (做多信号)")
    print(f"MA空头排列: MA5 < MA10 < MA20 (做空信号)")
    print()
    
    try:
        # 获取可交易交易对
        symbols = analyzer.get_tradable_symbols(
            quote_currency=SYMBOL_FILTER['quote_currency'],
            min_volume=SYMBOL_FILTER['min_volume_usd']
        )
        
        if not symbols:
            print("❌ 未找到符合条件的交易对")
            print("💡 建议:")
            print("   1. 检查网络连接")
            print("   2. 降低最小交易量要求")
            print("   3. 检查交易所API状态")
            return []
        
        print(f"✅ 找到 {len(symbols)} 个符合条件的交易对")
        print("正在分析技术指标...")
        print()
        
        # 扫描交易机会
        opportunities = analyzer.get_top_opportunities(top_n)
        
        if not opportunities:
            print("❌ 未找到符合条件的交易机会")
            return []
        
        print(f"🎯 找到 {len(opportunities)} 个交易机会:")
        print()
        
        # 按信号类型分组
        long_signals = [opp for opp in opportunities if opp['signal'] == 'long']
        short_signals = [opp for opp in opportunities if opp['signal'] == 'short']
        
        if long_signals:
            print("🟢 做多信号:")
            for i, opp in enumerate(long_signals, 1):
                print_opportunity(opp, i)
        
        if short_signals:
            print("🔴 做空信号:")
            for i, opp in enumerate(short_signals, 1):
                print_opportunity(opp, len(long_signals) + i)
        
        return opportunities
        
    except Exception as e:
        print(f"❌ 扫描失败: {e}")
        return []

def analyze_symbol(analyzer, symbol, timeframe='1h'):
    """分析单个交易对"""
    print(f"📊 分析 {symbol} ({timeframe})")
    print("-" * 40)
    
    try:
        # 获取分析结果
        result = analyzer.identify_trading_opportunities(symbol)
        
        if not result:
            print("❌ 无法获取分析结果")
            return
        
        # 打印基本信息
        print(f"交易对: {result['symbol']}")
        print(f"当前价格: ${result['current_price']:.6f}")
        print(f"交易量比率: {result['volume_ratio']:.2f}x")
        print(f"当前交易量: {format_volume(result['current_volume'])}")
        print(f"平均交易量: {format_volume(result['avg_volume_30'])}")
        print()
        
        # 打印MA信息
        print("移动平均线:")
        print(f"  MA5:  ${result['ma5']:.6f}")
        print(f"  MA10: ${result['ma10']:.6f}")
        print(f"  MA20: ${result['ma20']:.6f}")
        print()
        
        # 判断MA排列
        ma5, ma10, ma20 = result['ma5'], result['ma10'], result['ma20']
        if ma5 > ma10 > ma20:
            print("✅ MA多头排列 (MA5 > MA10 > MA20)")
        elif ma5 < ma10 < ma20:
            print("✅ MA空头排列 (MA5 < MA10 < MA20)")
        else:
            print("❌ MA排列混乱")
        print()
        
        # 打印交易信号
        if result['signal'] == 'long':
            print("🟢 交易信号: 做多")
            print("   理由: 交易量放大 + MA多头排列")
        elif result['signal'] == 'short':
            print("🔴 交易信号: 做空")
            print("   理由: 交易量放大 + MA空头排列")
        else:
            print("⚪ 无交易信号")
            if result['volume_ratio'] < INDICATOR_CONFIG['volume_ratio_threshold']:
                print(f"   原因: 交易量比率 {result['volume_ratio']:.2f}x < {INDICATOR_CONFIG['volume_ratio_threshold']}x")
            else:
                print("   原因: MA排列不符合要求")
        print()
        
        # 打印其他信息
        print(f"24小时涨跌: {result['price_change_24h']*100:+.2f}%")
        print(f"价格波动率: {result['volatility']:.4f}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

def export_results(opportunities, filename):
    """导出结果到JSON文件"""
    try:
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_opportunities': len(opportunities),
            'opportunities': opportunities
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已导出到: {filename}")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="加密货币交易机会分析器 - 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python cli.py scan                    # 扫描所有交易机会
  python cli.py scan --top 10          # 扫描前10个机会
  python cli.py analyze BTC/USDT       # 分析特定交易对
  python cli.py analyze BTC/USDT --timeframe 4h  # 使用4小时周期
  python cli.py scan --export results.json  # 导出结果
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 扫描命令
    scan_parser = subparsers.add_parser('scan', help='扫描交易机会')
    scan_parser.add_argument('--top', type=int, default=20, help='返回前N个机会 (默认: 20)')
    scan_parser.add_argument('--export', help='导出结果到JSON文件')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析特定交易对')
    analyze_parser.add_argument('symbol', help='交易对符号 (如: BTC/USDT)')
    analyze_parser.add_argument('--timeframe', default='1h', help='时间周期 (默认: 1h)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    # 初始化分析器
    try:
        analyzer = CryptoAnalyzer()
        print("✅ 分析器初始化成功")
        print()
    except Exception as e:
        print(f"❌ 分析器初始化失败: {e}")
        return
    
    if args.command == 'scan':
        opportunities = scan_opportunities(analyzer, args.top)
        
        if args.export and opportunities:
            export_results(opportunities, args.export)
    
    elif args.command == 'analyze':
        analyze_symbol(analyzer, args.symbol, args.timeframe)
    
    print("\n" + "=" * 60)
    print("分析完成！")

if __name__ == '__main__':
    main() 