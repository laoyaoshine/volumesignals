import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Portfolio } from '../types/trading';
import { TrendingUp, TrendingDown, DollarSign, Target } from 'lucide-react';

interface PortfolioProps {
  portfolio: Portfolio;
}

const PortfolioComponent: React.FC<PortfolioProps> = ({ portfolio }) => {
  const chartData = portfolio.balanceHistory.map(item => ({
    timestamp: new Date(item.timestamp).toLocaleDateString(),
    balance: item.balance,
  }));

  const recentTrades = portfolio.trades.slice(-5).reverse();

  return (
    <div className="bg-crypto-card border border-crypto-border rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-6">投资组合</h2>
      
      {/* 关键指标 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-crypto-dark/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-crypto-blue" />
            <span className="text-xs text-gray-400">账户余额</span>
          </div>
          <p className="text-lg font-semibold text-white">${portfolio.balance.toFixed(2)}</p>
        </div>
        
        <div className="bg-crypto-dark/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {portfolio.totalPnl >= 0 ? (
              <TrendingUp className="w-4 h-4 text-crypto-green" />
            ) : (
              <TrendingDown className="w-4 h-4 text-crypto-red" />
            )}
            <span className="text-xs text-gray-400">总盈亏</span>
          </div>
          <p className={`text-lg font-semibold ${portfolio.totalPnl >= 0 ? 'text-crypto-green' : 'text-crypto-red'}`}>
            {portfolio.totalPnl >= 0 ? '+' : ''}${portfolio.totalPnl.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-crypto-dark/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-crypto-blue" />
            <span className="text-xs text-gray-400">收益率</span>
          </div>
          <p className={`text-lg font-semibold ${portfolio.totalReturn >= 0 ? 'text-crypto-green' : 'text-crypto-red'}`}>
            {portfolio.totalReturn >= 0 ? '+' : ''}{portfolio.totalReturn.toFixed(2)}%
          </p>
        </div>
        
        <div className="bg-crypto-dark/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-crypto-green" />
            <span className="text-xs text-gray-400">胜率</span>
          </div>
          <p className="text-lg font-semibold text-white">{portfolio.winRate.toFixed(1)}%</p>
        </div>
      </div>

      {/* 盈利图表 */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-white mb-3">账户余额变化</h3>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="timestamp" 
                tick={{ fontSize: 10, fill: '#9CA3AF' }}
                axisLine={{ stroke: '#374151' }}
              />
              <YAxis 
                tick={{ fontSize: 10, fill: '#9CA3AF' }}
                axisLine={{ stroke: '#374151' }}
                domain={['dataMin - 50', 'dataMax + 50']}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1a2332', 
                  border: '1px solid #374151',
                  borderRadius: '6px',
                  fontSize: '12px'
                }}
                formatter={(value: number) => [`$${value.toFixed(2)}`, '余额']}
              />
              <Line 
                type="monotone" 
                dataKey="balance" 
                stroke="#3b82f6" 
                strokeWidth={2} 
                dot={false}
                strokeDasharray={portfolio.totalPnl >= 0 ? "0" : "5 5"}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 最近交易 */}
      <div>
        <h3 className="text-sm font-medium text-white mb-3">最近交易</h3>
        <div className="space-y-2">
          {recentTrades.length === 0 ? (
            <p className="text-sm text-gray-400">暂无交易记录</p>
          ) : (
            recentTrades.map(trade => (
              <div key={trade.id} className="flex justify-between items-center bg-crypto-dark/30 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    trade.type === 'BUY' ? 'bg-crypto-green/20 text-crypto-green' : 'bg-crypto-red/20 text-crypto-red'
                  }`}>
                    {trade.type}
                  </div>
                  <span className="text-sm text-white">{trade.symbol}</span>
                  <span className="text-xs text-gray-400">${trade.price.toFixed(2)}</span>
                </div>
                <div className="text-right">
                  <p className="text-sm text-white">${trade.amount.toFixed(2)}</p>
                  {trade.pnl !== undefined && (
                    <p className={`text-xs ${trade.pnl >= 0 ? 'text-crypto-green' : 'text-crypto-red'}`}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioComponent;