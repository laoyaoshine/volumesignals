export interface KlineData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma5?: number;
  ma10?: number;
  ma20?: number;
}

export interface TradingPair {
  symbol: string;
  exchange: string;
  marketType: 'spot' | 'future';  // 市场类型：现货或合约
  price: number;
  change24h: number;
  volume24h: number;
  volumeRatio: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  maAlignment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  klineData: KlineData[];
}

export type MarketType = 'spot' | 'future';

export interface Exchange {
  name: string;
  enabled: boolean;
  pairs: string[];
}

export interface Trade {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  price: number;
  amount: number;
  timestamp: number;
  pnl?: number;
}

export interface Portfolio {
  balance: number;
  totalPnl: number;
  totalReturn: number;
  winRate: number;
  trades: Trade[];
  balanceHistory: { timestamp: number; balance: number }[];
}