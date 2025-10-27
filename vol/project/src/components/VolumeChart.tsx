import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, ComposedChart, Candlestick, ReferenceLine } from 'recharts';
import { KlineData } from '../types/trading';
import { formatVolume } from '../utils/tradingAnalysis';

interface VolumeChartProps {
  data: KlineData[];
}

const VolumeChart: React.FC<VolumeChartProps> = ({ data }) => {
  const chartData = data.slice(-20).map(item => ({
    timestamp: new Date(item.timestamp).toLocaleDateString(),
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    price: item.close,
    ma5: item.ma5,
    ma10: item.ma10,
    ma20: item.ma20,
    volume: item.volume,
  }));

  // 计算平均交易量
  const avgVolume = chartData.reduce((sum, item) => sum + item.volume, 0) / chartData.length;

  return (
    <div className="space-y-4">
      {/* K线图和MA线图 */}
      <div className="h-48">
        <h5 className="text-xs text-gray-400 mb-2">K线 & 移动平均线</h5>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="timestamp" 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              axisLine={{ stroke: '#374151' }}
            />
            <YAxis 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              axisLine={{ stroke: '#374151' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a2332', 
                border: '1px solid #374151',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Candlestick 
              dataKey="price" 
              fill="#00ff88" 
              stroke="#00ff88"
              strokeWidth={1}
            />
            <Line type="monotone" dataKey="ma5" stroke="#10b981" strokeWidth={1} dot={false} />
            <Line type="monotone" dataKey="ma10" stroke="#f59e0b" strokeWidth={1} dot={false} />
            <Line type="monotone" dataKey="ma20" stroke="#ef4444" strokeWidth={1} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* 交易量图 */}
      <div className="h-32">
        <h5 className="text-xs text-gray-400 mb-2">交易量</h5>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="timestamp" 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              axisLine={{ stroke: '#374151' }}
            />
            <YAxis 
              tick={{ fontSize: 10, fill: '#9CA3AF' }}
              axisLine={{ stroke: '#374151' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a2332', 
                border: '1px solid #374151',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Bar dataKey="volume" fill="#6366f1" />
            <ReferenceLine 
              y={avgVolume} 
              stroke="#f59e0b" 
              strokeDasharray="5 5"
              label={{ value: `平均: ${formatVolume(avgVolume)}`, position: "topRight" }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 图例 */}
      <div className="flex flex-wrap gap-3 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-2 bg-green-400 border border-green-400"></div>
          <span className="text-gray-400">K线</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-crypto-green"></div>
          <span className="text-gray-400">MA5</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-yellow-500"></div>
          <span className="text-gray-400">MA10</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-crypto-red"></div>
          <span className="text-gray-400">MA20</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-yellow-500 border-dashed border"></div>
          <span className="text-gray-400">平均交易量</span>
        </div>
      </div>
    </div>
  );
};

export default VolumeChart;