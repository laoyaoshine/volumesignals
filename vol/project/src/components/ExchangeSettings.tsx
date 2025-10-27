import React from 'react';
import { Exchange } from '../types/trading';
import { Settings, ToggleLeft, ToggleRight } from 'lucide-react';

interface ExchangeSettingsProps {
  exchanges: Exchange[];
  onToggleExchange: (exchangeName: string, enabled: boolean) => void;
}

const ExchangeSettings: React.FC<ExchangeSettingsProps> = ({ exchanges, onToggleExchange }) => {
  return (
    <div className="bg-crypto-card border border-crypto-border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Settings className="w-5 h-5 text-crypto-blue" />
        <h2 className="text-lg font-semibold text-white">交易所设置</h2>
      </div>
      
      <div className="space-y-3">
        {exchanges.map(exchange => (
          <div key={exchange.name} className="flex items-center justify-between p-3 bg-crypto-dark/30 rounded-lg">
            <div>
              <h3 className="text-sm font-medium text-white">{exchange.name}</h3>
              <p className="text-xs text-gray-400">{exchange.pairs.length} 交易对</p>
            </div>
            <button
              onClick={() => onToggleExchange(exchange.name, !exchange.enabled)}
              className={`flex items-center gap-2 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                exchange.enabled 
                  ? 'bg-crypto-green/20 text-crypto-green hover:bg-crypto-green/30' 
                  : 'bg-gray-600/20 text-gray-400 hover:bg-gray-600/30'
              }`}
            >
              {exchange.enabled ? (
                <>
                  <ToggleRight className="w-4 h-4" />
                  启用
                </>
              ) : (
                <>
                  <ToggleLeft className="w-4 h-4" />
                  禁用
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExchangeSettings;