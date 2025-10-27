import { useState, useEffect, useCallback } from 'react';
import { TradingPair, Exchange, Portfolio, Trade, MarketType } from '../types/trading';
import { generateMockTradingPairs, getExchanges, updateExchangeStatus } from '../utils/mockData';

export const useTradingData = () => {
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio>({
    balance: 1000,
    totalPnl: 0,
    totalReturn: 0,
    winRate: 0,
    trades: [],
    balanceHistory: [{ timestamp: Date.now(), balance: 1000 }],
  });
  const [autoTrading, setAutoTrading] = useState(false);
  const [signalFilter, setSignalFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL');
  const [marketType, setMarketType] = useState<MarketType>('future'); // 默认合约市场

  // 更新交易数据
  const updateTradingData = useCallback(() => {
    const newPairs = generateMockTradingPairs();
    // 根据marketType过滤数据
    const filteredPairs = newPairs.filter(pair => pair.marketType === marketType);
    setTradingPairs(filteredPairs);
  }, [marketType]);

  // 初始化数据
  useEffect(() => {
    setExchanges(getExchanges());
    updateTradingData();
    
    // 每30秒更新一次数据
    const interval = setInterval(updateTradingData, 30000);
    return () => clearInterval(interval);
  }, [updateTradingData]);

  // 市场类型变化时更新数据
  useEffect(() => {
    updateTradingData();
  }, [marketType]);

  // 自动交易逻辑
  useEffect(() => {
    if (!autoTrading) return;

    const autoTradeInterval = setInterval(() => {
      const signalPairs = tradingPairs.filter(pair => pair.signal !== 'HOLD' && pair.volumeRatio >= 3);
      
      if (signalPairs.length > 0) {
        const randomPair = signalPairs[Math.floor(Math.random() * signalPairs.length)];
        executeTrade(randomPair, randomPair.signal as 'BUY' | 'SELL');
      }
    }, 60000); // 每分钟检查一次

    return () => clearInterval(autoTradeInterval);
  }, [autoTrading, tradingPairs]);

  // 执行交易
  const executeTrade = useCallback((pair: TradingPair, action: 'BUY' | 'SELL') => {
    const tradeAmount = 100; // 固定交易金额
    
    if (portfolio.balance < tradeAmount && action === 'BUY') {
      return; // 余额不足
    }

    const newTrade: Trade = {
      id: Date.now().toString(),
      symbol: pair.symbol,
      type: action,
      price: pair.price,
      amount: tradeAmount,
      timestamp: Date.now(),
    };

    setPortfolio(prev => {
      const newBalance = action === 'BUY' ? prev.balance - tradeAmount : prev.balance + tradeAmount;
      
      // 计算盈亏（简化版本）
      const pnl = action === 'SELL' ? (Math.random() - 0.5) * 20 : 0; // 模拟盈亏
      newTrade.pnl = pnl;
      
      const newTrades = [...prev.trades, newTrade];
      const totalPnl = newTrades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
      const totalReturn = ((newBalance - 1000) / 1000) * 100;
      const winningTrades = newTrades.filter(trade => (trade.pnl || 0) > 0).length;
      const winRate = newTrades.length > 0 ? (winningTrades / newTrades.length) * 100 : 0;
      
      const newBalanceHistory = [...prev.balanceHistory, { timestamp: Date.now(), balance: newBalance }];
      
      return {
        balance: newBalance,
        totalPnl,
        totalReturn,
        winRate,
        trades: newTrades,
        balanceHistory: newBalanceHistory,
      };
    });
  }, [portfolio.balance]);

  // 切换交易所状态
  const toggleExchange = useCallback((exchangeName: string, enabled: boolean) => {
    updateExchangeStatus(exchangeName, enabled);
    setExchanges(getExchanges());
    updateTradingData();
  }, [updateTradingData]);

  // 过滤交易对
  const filteredPairs = tradingPairs.filter(pair => {
    if (signalFilter === 'ALL') return true;
    return pair.signal === signalFilter;
  });

  return {
    tradingPairs: filteredPairs,
    exchanges,
    portfolio,
    autoTrading,
    marketType,
    signalFilter,
    setAutoTrading,
    setSignalFilter,
    setMarketType,
    executeTrade,
    toggleExchange,
    updateTradingData,
  };
};
