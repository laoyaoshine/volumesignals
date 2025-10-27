import { KlineData, TradingPair } from '../types/trading';

export function formatVolume(volume: number): string {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(1)}M`;
  } else if (volume >= 1000) {
    return `${(volume / 1000).toFixed(1)}K`;
  } else {
    return volume.toFixed(0);
  }
}

export function calculateMA(data: number[], period: number): number[] {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(0);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }
  }
  return result;
}

export function calculateVolumeRatio(klineData: KlineData[]): number {
  if (klineData.length < 31) return 1; // 需要至少31根K线
  
  const currentVolume = klineData[klineData.length - 1].volume;
  const previous30Volumes = klineData.slice(-31, -1).map(k => k.volume); // 前30根K线
  const avgVolume30 = previous30Volumes.reduce((sum, vol) => sum + vol, 0) / 30;
  
  return avgVolume30 > 0 ? currentVolume / avgVolume30 : 1;
}

export function analyzeMAAlignment(klineData: KlineData[]): 'BULLISH' | 'BEARISH' | 'NEUTRAL' {
  if (klineData.length === 0) return 'NEUTRAL';
  
  const latest = klineData[klineData.length - 1];
  if (!latest.ma5 || !latest.ma10 || !latest.ma20) return 'NEUTRAL';
  
  if (latest.ma5 > latest.ma10 && latest.ma10 > latest.ma20) {
    return 'BULLISH';
  } else if (latest.ma5 < latest.ma10 && latest.ma10 < latest.ma20) {
    return 'BEARISH';
  }
  
  return 'NEUTRAL';
}

export function generateTradingSignal(volumeRatio: number, maAlignment: string): 'BUY' | 'SELL' | 'HOLD' {
  if (volumeRatio >= 3) {
    if (maAlignment === 'BULLISH') return 'BUY';
    if (maAlignment === 'BEARISH') return 'SELL';
  }
  return 'HOLD';
}

export function processKlineData(rawData: Omit<KlineData, 'ma5' | 'ma10' | 'ma20'>[]): KlineData[] {
  const closes = rawData.map(d => d.close);
  const ma5 = calculateMA(closes, 5);
  const ma10 = calculateMA(closes, 10);
  const ma20 = calculateMA(closes, 20);
  
  return rawData.map((data, index) => ({
    ...data,
    ma5: ma5[index] || 0,
    ma10: ma10[index] || 0,
    ma20: ma20[index] || 0,
  }));
}