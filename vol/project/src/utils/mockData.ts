import { TradingPair, Exchange, KlineData } from '../types/trading';
import { processKlineData, calculateVolumeRatio, analyzeMAAlignment, generateTradingSignal } from './tradingAnalysis';

const EXCHANGES: Exchange[] = [
  { name: 'Binance', enabled: true, pairs: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'] },
  { name: 'OKX', enabled: true, pairs: ['BTC/USDT', 'ETH/USDT', 'OKB/USDT', 'DOT/USDT', 'LINK/USDT'] },
  { name: 'Huobi', enabled: true, pairs: ['BTC/USDT', 'ETH/USDT', 'HT/USDT', 'LTC/USDT', 'XRP/USDT'] },
  { name: 'KuCoin', enabled: true, pairs: ['BTC/USDT', 'ETH/USDT', 'KCS/USDT', 'MATIC/USDT', 'AVAX/USDT'] },
];

function generateKlineData(symbol: string, days: number = 50): KlineData[] { // 增加天数确保有足够数据
  const data: Omit<KlineData, 'ma5' | 'ma10' | 'ma20'>[] = [];
  const basePrice = Math.random() * 50000 + 1000;
  let currentPrice = basePrice;
  
  const now = Date.now();
  
  for (let i = days; i >= 0; i--) {
    const timestamp = now - (i * 24 * 60 * 60 * 1000);
    
    // 生成价格波动
    const volatility = 0.02 + Math.random() * 0.03;
    const change = (Math.random() - 0.5) * volatility;
    currentPrice = currentPrice * (1 + change);
    
    const open = currentPrice;
    const high = open * (1 + Math.random() * 0.02);
    const low = open * (1 - Math.random() * 0.02);
    const close = low + Math.random() * (high - low);
    
    // 生成交易量，某些时候会有突然的大交易量
    let volume = Math.random() * 1000000 + 100000;
    if (Math.random() < 0.1) { // 10%的概率出现大交易量
      volume *= (3 + Math.random() * 5); // 3-8倍的交易量
    }
    
    data.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume,
    });
    
    currentPrice = close;
  }
  
  return processKlineData(data);
}

export function generateMockTradingPairs(): TradingPair[] {
  const pairs: TradingPair[] = [];
  
  EXCHANGES.forEach(exchange => {
    if (!exchange.enabled) return;
    
    exchange.pairs.forEach(symbol => {
      const klineData = generateKlineData(symbol);
      const volumeRatio = calculateVolumeRatio(klineData);
      const maAlignment = analyzeMAAlignment(klineData);
      const signal = generateTradingSignal(volumeRatio, maAlignment);
      
      const latest = klineData[klineData.length - 1];
      const previous = klineData[klineData.length - 2];
      const change24h = ((latest.close - previous.close) / previous.close) * 100;
      
      pairs.push({
        symbol,
        exchange: exchange.name,
        price: latest.close,
        change24h,
        volume24h: latest.volume,
        volumeRatio,
        signal,
        maAlignment,
        klineData,
      });
    });
  });
  
  return pairs.sort((a, b) => b.volumeRatio - a.volumeRatio);
}

export function getExchanges(): Exchange[] {
  return EXCHANGES;
}

export function updateExchangeStatus(exchangeName: string, enabled: boolean): void {
  const exchange = EXCHANGES.find(e => e.name === exchangeName);
  if (exchange) {
    exchange.enabled = enabled;
  }
}