import { useTradingData } from './hooks/useTradingData';
import TradingPairCard from './components/TradingPairCard';
import Portfolio from './components/Portfolio';
import ExchangeSettings from './components/ExchangeSettings';
import { Bot, Filter, RefreshCw, BarChart3 } from 'lucide-react';

function App() {
  const {
    tradingPairs,
    exchanges,
    portfolio,
    autoTrading,
    signalFilter,
    setAutoTrading,
    setSignalFilter,
    executeTrade,
    toggleExchange,
    updateTradingData,
  } = useTradingData();

  return (
    <div className="min-h-screen bg-crypto-dark">
      <div className="container mx-auto px-4 py-6">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-crypto-blue" />
            <h1 className="text-2xl font-bold text-white">加密货币交易分析系统</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={updateTradingData}
              className="flex items-center gap-2 px-4 py-2 bg-crypto-card border border-crypto-border rounded-lg text-white hover:border-crypto-blue/50 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              刷新数据
            </button>
            
            <button
              onClick={() => setAutoTrading(!autoTrading)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                autoTrading
                  ? 'bg-crypto-green text-white hover:bg-crypto-green/80'
                  : 'bg-crypto-card border border-crypto-border text-white hover:border-crypto-blue/50'
              }`}
            >
              <Bot className="w-4 h-4" />
              {autoTrading ? '自动交易已开启' : '开启自动交易'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 左侧主要内容 */}
          <div className="lg:col-span-3 space-y-6">
            {/* 过滤器 */}
            <div className="bg-crypto-card border border-crypto-border rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-crypto-blue" />
                  <span className="text-sm text-white">信号过滤:</span>
                </div>
                <div className="flex gap-2">
                  {(['ALL', 'BUY', 'SELL', 'HOLD'] as const).map(filter => (
                    <button
                      key={filter}
                      onClick={() => setSignalFilter(filter)}
                      className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                        signalFilter === filter
                          ? 'bg-crypto-blue text-white'
                          : 'bg-crypto-dark text-gray-400 hover:text-white'
                      }`}
                    >
                      {filter === 'ALL' ? '全部' : filter === 'BUY' ? '买入' : filter === 'SELL' ? '卖出' : '观望'}
                    </button>
                  ))}
                </div>
                <div className="ml-auto text-sm text-gray-400">
                  显示前20个交易对 (共 {tradingPairs.length} 个)
                </div>
              </div>
            </div>

            {/* 交易对列表 - 只显示前20个 */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {tradingPairs.slice(0, 20).map((pair, index) => (
                <TradingPairCard
                  key={`${pair.exchange}-${pair.symbol}-${index}`}
                  pair={pair}
                  onTrade={executeTrade}
                />
              ))}
            </div>

            {tradingPairs.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-400">没有找到符合条件的交易对</p>
              </div>
            )}
          </div>

          {/* 右侧边栏 */}
          <div className="space-y-6">
            {/* 投资组合 */}
            <Portfolio portfolio={portfolio} />
            
            {/* 交易所设置 */}
            <ExchangeSettings exchanges={exchanges} onToggleExchange={toggleExchange} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;