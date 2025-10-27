import React, { useState } from 'react';
import { TradingPair } from '../types/trading';
import { TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react';
import VolumeChart from './VolumeChart';
import { formatVolume } from '../utils/tradingAnalysis';

interface TradingPairCardProps {
  pair: TradingPair;
  onTrade?: (pair: TradingPair, action: 'BUY' | 'SELL') => void;
}

const TradingPairCard: React.FC<TradingPairCardProps> = ({ pair, onTrade }) => {
  const [showChart, setShowChart] = useState(false);

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return 'text-crypto-green bg-crypto-green/10 border-crypto-green/20';
      case 'SELL': return 'text-crypto-red bg-crypto-red/10 border-crypto-red/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY': return <TrendingUp className="w-4 h-4" />;
      case 'SELL': return <TrendingDown className="w-4 h-4" />;
      default: return <Minus className="w-4 h-4" />;
    }
  };

  const handleTrade = (action: 'BUY' | 'SELL') => {
    if (onTrade) {
      onTrade(pair, action);
    }
  };

  return (
    <div 
      className="bg-crypto-card border border-crypto-border rounded-lg p-4 hover:border-crypto-blue/50 transition-all duration-200 relative"
      onMouseEnter={() => setShowChart(true)}
      onMouseLeave={() => setShowChart(false)}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-white">{pair.symbol}</h3>
          <p className="text-sm text-gray-400">{pair.exchange}</p>
        </div>
        <div className={`px-2 py-1 rounded-md border text-xs font-medium flex items-center gap-1 ${getSignalColor(pair.signal)}`}>
          {getSignalIcon(pair.signal)}
          {pair.signal}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-400">价格</p>
          <p className="text-sm font-medium text-white">${pair.price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">24h涨跌</p>
          <p className={`text-sm font-medium ${pair.change24h >= 0 ? 'text-crypto-green' : 'text-crypto-red'}`}>
            {pair.change24h >= 0 ? '+' : ''}{pair.change24h.toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-400">交易量比率</p>
          <p className={`text-sm font-medium ${pair.volumeRatio >= 3 ? 'text-crypto-green' : 'text-gray-300'}`}>
            {pair.volumeRatio.toFixed(1)}x
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400">24h交易量</p>
          <p className="text-sm font-medium text-white">{formatVolume(pair.volume24h)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">MA排列</p>
          <p className={`text-xs font-medium ${
            pair.maAlignment === 'BULLISH' ? 'text-crypto-green' : 
            pair.maAlignment === 'BEARISH' ? 'text-crypto-red' : 'text-gray-400'
          }`}>
            {pair.maAlignment === 'BULLISH' ? '多头' : pair.maAlignment === 'BEARISH' ? '空头' : '中性'}
          </p>
        </div>
      </div>

      {pair.signal !== 'HOLD' && (
        <div className="flex gap-2">
          {pair.signal === 'BUY' && (
            <button
              onClick={() => handleTrade('BUY')}
              className="flex-1 bg-crypto-green hover:bg-crypto-green/80 text-white py-2 px-3 rounded-md text-sm font-medium transition-colors"
            >
              买入
            </button>
          )}
          {pair.signal === 'SELL' && (
            <button
              onClick={() => handleTrade('SELL')}
              className="flex-1 bg-crypto-red hover:bg-crypto-red/80 text-white py-2 px-3 rounded-md text-sm font-medium transition-colors"
            >
              卖出
            </button>
          )}
        </div>
      )}

      {showChart && (
        <div className="absolute top-0 left-full ml-2 z-50 bg-crypto-card border border-crypto-border rounded-lg p-4 shadow-xl w-96">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-4 h-4 text-crypto-blue" />
            <h4 className="text-sm font-medium text-white">{pair.symbol} 图表分析</h4>
          </div>
          <VolumeChart data={pair.klineData} />
        </div>
      )}
    </div>
  );
};

export default TradingPairCard;

