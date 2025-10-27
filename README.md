# 🚀 加密货币交易机会分析器

基于交易量放大和移动平均线（MA）多头排列的加密货币交易信号识别工具。

## ✨ 主要功能

- **交易量分析**: 识别当前K线交易量是前30根K线平均交易量3倍以上的情况
- **MA排列判断**: 分析MA5、MA10、MA20的排列关系
- **交易信号生成**: 
  - 交易量放大 + MA多头排列（MA5 > MA10 > MA20）→ 做多信号
  - 交易量放大 + MA空头排列（MA5 < MA10 < MA20）→ 做空信号
- **双市场支持**: 同时支持现货(Spot)和合约(Future)市场交易分析
- **多交易所聚合**: 支持币安、OKX、Bybit等多个主流交易所
- **实时监控**: 自动扫描所有符合条件的交易对
- **可视化图表**: 显示价格、交易量和MA线的交互式图表
- **排行榜**: 按交易量比率排序的交易机会列表

## 🛠️ 技术架构

- **数据获取**: 使用CCXT库连接币安等主流交易所
- **技术分析**: 计算移动平均线、交易量比率等技术指标
- **Web界面**: 基于Dash框架的现代化Web应用
- **命令行工具**: 快速分析和批量扫描功能

## 📦 安装要求

### 系统要求
- Python 3.8+
- 稳定的网络连接（访问交易所API）

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- `ccxt`: 加密货币交易所API接口
- `pandas`: 数据处理和分析
- `plotly`: 交互式图表
- `dash`: Web应用框架
- `numpy`: 数值计算

## 🚀 快速开始

### 📋 环境要求
- Python 3.8+
- 稳定的网络连接（访问交易所API）

### 🔧 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/crypto-trading-analyzer.git
cd crypto-trading-analyzer
```

#### 2. 创建虚拟环境
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 启动应用
```bash
# 启动主Web应用
python app.py

# 或启动简化版系统
python simple_trading_system.py

# 或使用命令行工具
python cli.py scan
```

#### 5. 访问应用
- Web应用: http://localhost:8050
- React前端: http://localhost:5173 (需要先运行 `cd vol/project && npm install && npm run dev`)

### 🎯 一键启动脚本
```bash
# 使用启动脚本（推荐）
python start.py
```

### ⚡ 快速测试
```bash
# 测试命令行功能
python cli.py scan --top 10

# 测试特定交易对
python cli.py analyze BTC/USDT
```

## 📊 使用方法

### Web界面使用

1. **启动应用**: 运行 `python app.py`
2. **查看机会**: 主页面显示实时交易机会排行榜
3. **详细分析**: 选择交易对查看价格、交易量和MA线图表
4. **自动刷新**: 数据每5分钟自动更新

### 命令行使用

#### 扫描命令
```bash
# 扫描所有交易机会
python cli.py scan

# 扫描前10个机会
python cli.py scan --top 10

# 导出结果到JSON文件
python cli.py scan --export opportunities.json
```

#### 分析命令
```bash
# 分析BTC/USDT
python cli.py analyze BTC/USDT

# 使用4小时周期分析
python cli.py analyze BTC/USDT --timeframe 4h
```

## 📈 交易信号逻辑

### 做多信号条件
1. **交易量放大**: 当前K线交易量 ≥ 前30根K线平均交易量 × 3
2. **MA多头排列**: MA5 > MA10 > MA20

### 做空信号条件
1. **交易量放大**: 当前K线交易量 ≥ 前30根K线平均交易量 × 3
2. **MA空头排列**: MA5 < MA10 < MA20

### 指标说明
- **MA5**: 5周期移动平均线
- **MA10**: 10周期移动平均线
- **MA20**: 20周期移动平均线
- **交易量比率**: 当前交易量 / 前30根K线平均交易量

## ⚙️ 配置说明

编辑 `config.py` 文件可以调整以下参数：

```python
# 交易量放大阈值
'volume_ratio_threshold': 3.0

# 移动平均线周期
'ma_periods': [5, 10, 20]

# 最小交易量筛选
'min_volume_usd': 1000000

# 数据更新间隔
'update_interval': 300  # 5分钟
```

## 🔧 自定义配置

### 更换交易所
在 `crypto_analyzer.py` 中修改：
```python
analyzer = CryptoAnalyzer('okx')  # 使用OKX交易所
```

### 调整时间周期
支持的时间周期：
- `1m`: 1分钟
- `5m`: 5分钟
- `15m`: 15分钟
- `1h`: 1小时
- `4h`: 4小时
- `1d`: 1天

## 📝 输出示例

### 交易机会示例
```
1. BTC/USDT        🟢 做多
   价格: $43,250.000000 | 交易量比率: 4.25x
   MA5: $43,100.000000 | MA10: $42,800.000000 | MA20: $42,500.000000
   24h涨跌: +2.50% | 波动率: 0.0234
```

### 图表显示
- **价格图**: 显示收盘价和三条MA线
- **交易量图**: 显示每根K线的交易量
- **交易量比率图**: 显示交易量放大倍数，包含3倍阈值线

## ⚠️ 风险提示

1. **本工具仅用于技术分析，不构成投资建议**
2. **加密货币交易存在高风险，请谨慎投资**
3. **交易量放大可能意味着价格剧烈波动**
4. **请根据自身风险承受能力做出投资决策**
5. **建议在实盘交易前进行充分的回测和模拟交易**

## 🐛 故障排除

### 常见问题

1. **网络连接错误**
   - 检查网络连接
   - 确认防火墙设置
   - 尝试更换网络环境

2. **API限制错误**
   - 降低请求频率
   - 增加请求间隔时间
   - 使用代理服务器

3. **数据获取失败**
   - 检查交易对名称格式
   - 确认交易所支持该交易对
   - 查看日志文件获取详细错误信息

### 日志查看
程序运行时会生成 `crypto_analyzer.log` 日志文件，包含详细的运行信息和错误记录。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork项目到你的GitHub账户
2. Clone到本地开发环境
3. 创建功能分支
4. 提交更改并推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件到项目维护者

---

**免责声明**: 本工具仅供学习和研究使用，使用者需自行承担投资风险。开发者不对任何投资损失承担责任。 