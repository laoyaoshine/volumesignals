import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import threading
import time
import logging
from typing import List, Dict, Any

from crypto_analyzer import CryptoAnalyzer
from config import EXCHANGES

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化分析器
analyzer = CryptoAnalyzer()

# 创建Dash应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "加密货币交易机会分析器"

# 全局变量存储数据
opportunities_data: List[Dict[str, Any]] = []
last_update_time: datetime = None
update_thread: threading.Thread = None
stop_update: bool = False

# 数据缓存
data_cache: Dict[str, Any] = {}
cache_timeout: int = 300  # 5分钟缓存

def get_cached_data(key: str) -> Any:
    """获取缓存数据"""
    if key not in data_cache:
        return None
    
    cached_data = data_cache[key]
    if time.time() - cached_data['timestamp'] > cache_timeout:
        del data_cache[key]
        return None
    
    return cached_data['data']

def set_cached_data(key: str, data: Any) -> None:
    """设置缓存数据"""
    data_cache[key] = {
        'data': data,
        'timestamp': time.time()
    }

def format_volume(volume: float) -> str:
    """智能格式化交易量显示"""
    if volume >= 1000000:
        return f"{volume/1000000:.1f}M"
    elif volume >= 1000:
        return f"{volume/1000:.1f}K"
    else:
        return f"{volume:.0f}"

def update_data_background():
    """后台更新数据的线程函数"""
    global opportunities_data, last_update_time, stop_update
    
    while not stop_update:
        try:
            logger.info("开始扫描交易机会...")
            # 获取可交易交易对
            symbols = analyzer.get_tradable_symbols()
            if symbols:
                # 扫描交易机会
                opportunities = analyzer.get_top_opportunities(20, 'volume_ratio')  # 只获取前20个用于表格显示
                opportunities_data = opportunities
                last_update_time = datetime.now()
                logger.info(f"找到 {len(opportunities)} 个交易机会")
            else:
                logger.warning("未找到符合条件的交易对，请检查网络连接")
                opportunities_data = []
            
            # 等待3分钟再次更新
            time.sleep(180)
            
        except Exception as e:
            logger.error(f"更新数据时出错: {e}", exc_info=True)
            logger.info("将在60秒后重试...")
            time.sleep(60)

def start_update_thread():
    """启动更新线程"""
    global update_thread, stop_update
    if update_thread is None or not update_thread.is_alive():
        stop_update = False
        update_thread = threading.Thread(target=update_data_background, daemon=True)
        update_thread.start()

# 启动更新线程
start_update_thread()

# 应用布局
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🚀 加密货币交易机会分析器", className="text-center mb-4"),
            html.P("基于交易量放大和MA多头排列的交易信号识别", className="text-center text-muted")
        ])
    ]),
    
    # 排行图表区域
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📊 交易量排行图表", className="mb-0"),
                    html.Small(f"最后更新: {last_update_time.strftime('%Y-%m-%d %H:%M:%S') if last_update_time else '未更新'}", 
                              className="text-muted")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("排序方式:"),
                            dcc.Dropdown(
                                id="ranking-sort",
                                options=[
                                    {"label": "交易量比率", "value": "volume_ratio"},
                                    {"label": "综合评分", "value": "composite_score"},
                                    {"label": "24h交易量", "value": "current_volume"},
                                    {"label": "24h涨跌", "value": "price_change_24h"},
                                    {"label": "当前价格", "value": "current_price"}
                                ],
                                value="volume_ratio",
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("显示数量:"),
                            dcc.Dropdown(
                                id="ranking-limit",
                                options=[
                                    {"label": "前10名", "value": 10},
                                    {"label": "前20名", "value": 20},
                                    {"label": "前50名", "value": 50},
                                    {"label": "前100名", "value": 100}
                                ],
                                value=20,
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("交易所筛选:"),
                            dcc.Dropdown(
                                id="ranking-exchange-filter",
                                options=[
                                    {"label": ex["name"].upper(), "value": ex["name"]}
                                    for ex in EXCHANGES if ex.get("enabled", True)
                                ],
                                multi=True,
                                placeholder="全部交易所",
                                clearable=True,
                                value=[]
                            )
                        ], width=6)
                    ], className="mb-3"),
                    html.Div(id="ranking-chart")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # 详细表格区域
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📋 详细数据表格", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("交易所筛选:"),
                            dcc.Dropdown(
                                id="exchange-filter",
                                options=[
                                    {"label": ex["name"].upper(), "value": ex["name"]}
                                    for ex in EXCHANGES if ex.get("enabled", True)
                                ],
                                multi=True,
                                placeholder="选择交易所（留空=全部）",
                                clearable=True,
                                value=[]
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("排序字段:"),
                            dcc.Dropdown(
                                id="sort-by",
                                options=[
                                    {"label": "交易量比率", "value": "volume_ratio"},
                                    {"label": "当前价格", "value": "current_price"},
                                    {"label": "24h涨跌", "value": "price_change_24h"}
                                ],
                                value="volume_ratio",
                                clearable=False
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("排序方式:"),
                            dcc.RadioItems(
                                id="sort-order",
                                options=[
                                    {"label": "降序", "value": "desc"},
                                    {"label": "升序", "value": "asc"}
                                ],
                                value="desc",
                                inline=True
                            )
                        ], width=4)
                    ], className="mb-3"),
                    html.Div(id="opportunities-table")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📈 交易对详细分析", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("选择交易对:"),
                            dcc.Dropdown(
                                id="symbol-dropdown",
                                placeholder="选择要分析的交易对...",
                                clearable=True
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("时间周期:"),
                            dcc.Dropdown(
                                id="timeframe-dropdown",
                                options=[
                                    {'label': '1分钟', 'value': '1m'},
                                    {'label': '5分钟', 'value': '5m'},
                                    {'label': '15分钟', 'value': '15m'},
                                    {'label': '1小时', 'value': '1h'},
                                    {'label': '4小时', 'value': '4h'},
                                    {'label': '1天', 'value': '1d'}
                                ],
                                value='1h',
                                clearable=False
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    html.Div(id="charts-container")
                ])
            ])
        ], width=12)
    ]),
    
    # 隐藏的存储组件
    dcc.Store(id="data-store"),
    
    # 自动刷新间隔（Bolt.host优化）
    dcc.Interval(
        id='interval-component',
        interval=60000,  # 60秒刷新一次，减少服务器负载
        n_intervals=0
    )
    
], fluid=True, className="py-4")

@app.callback(
    Output("ranking-chart", "children"),
    Input("interval-component", "n_intervals"),
    Input("ranking-sort", "value"),
    Input("ranking-limit", "value"),
    Input("ranking-exchange-filter", "value")
)
def update_ranking_chart(n, sort_by, limit, exchange_filter):
    """更新排行图表"""
    global opportunities_data
    
    opps = opportunities_data or []
    
    # 过滤：按交易所
    if exchange_filter:
        opps = [o for o in opps if o.get('exchange') in set(exchange_filter)]
    
    if not opps:
        return html.P("暂无数据，请等待更新...", className="text-muted text-center py-4")
    
    # 排序
    try:
        opps = sorted(opps, key=lambda o: o.get(sort_by, 0), reverse=True)
    except Exception:
        pass
    
    # 限制数量
    opps = opps[:limit]
    
    # 准备图表数据
    symbols = [o['symbol'] for o in opps]
    values = [o.get(sort_by, 0) for o in opps]
    
    # 根据排序字段设置标签和颜色
    if sort_by == 'volume_ratio':
        title = f"交易量比率排行 (前{limit}名)"
        y_label = "交易量比率"
        colors = ['#ff4757' if v > 10 else '#ff6b6b' if v > 5 else '#4ecdc4' if v > 3 else '#45b7d1' for v in values]
    elif sort_by == 'composite_score':
        title = f"综合评分排行 (前{limit}名)"
        y_label = "综合评分"
        colors = ['#ff4757' if v > 80 else '#ff6b6b' if v > 60 else '#4ecdc4' if v > 40 else '#45b7d1' for v in values]
    elif sort_by == 'current_volume':
        title = f"24小时交易量排行 (前{limit}名)"
        y_label = "交易量 (USDT)"
        colors = ['#ff4757' if v > 5000000 else '#ff6b6b' if v > 1000000 else '#4ecdc4' if v > 500000 else '#45b7d1' for v in values]
    elif sort_by == 'price_change_24h':
        title = f"24小时涨跌排行 (前{limit}名)"
        y_label = "涨跌幅 (%)"
        values = [v * 100 for v in values]  # 转换为百分比
        colors = ['#ff4757' if v > 20 else '#ff6b6b' if v > 10 else '#4ecdc4' if v > 0 else '#45b7d1' for v in values]
    else:
        title = f"当前价格排行 (前{limit}名)"
        y_label = "价格 (USDT)"
        colors = ['#ff4757' if v > 1000 else '#ff6b6b' if v > 100 else '#4ecdc4' if v > 10 else '#45b7d1' for v in values]
    
    # 创建条形图
    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}" if isinstance(v, float) else f"{v:,.0f}" for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' + 
                         f'{y_label}: %{{y}}<br>' +
                         '交易所: %{customdata[0]}<br>' +
                         '当前价格: $%{customdata[1]:.6f}<br>' +
                         '24h涨跌: %{customdata[2]:.2f}%<br>' +
                         '交易量比率: %{customdata[3]:.2f}x<br>' +
                         '综合评分: %{customdata[4]:.1f}<br>' +
                         '<extra></extra>',
            customdata=[[
                o.get('exchange', ''),
                o.get('current_price', 0),
                o.get('price_change_24h', 0) * 100,
                o.get('volume_ratio', 0),
                o.get('composite_score', 0)
            ] for o in opps]
        )
    ])
    
    # 更新布局
    fig.update_layout(
        title=title,
        xaxis_title="交易对",
        yaxis_title=y_label,
        height=500,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(tickangle=45),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # 添加网格线
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return dcc.Graph(figure=fig)

@app.callback(
    Output("opportunities-table", "children"),
    Output("symbol-dropdown", "options"),
    Input("interval-component", "n_intervals"),
    Input("exchange-filter", "value"),
    Input("sort-by", "value"),
    Input("sort-order", "value")
)
def update_opportunities_table(n, exchange_filter, sort_by, sort_order):
    """更新交易机会表格和交易对下拉选项（支持筛选与排序）"""
    global opportunities_data, last_update_time

    opps = opportunities_data or []

    # 过滤：按交易所
    if exchange_filter:
        opps = [o for o in opps if o.get('exchange') in set(exchange_filter)]

    # 排序
    key_fn = lambda o: o.get(sort_by, 0)
    reverse = (sort_order != 'asc')
    try:
        opps = sorted(opps, key=key_fn, reverse=reverse)
    except Exception:
        pass

    # 创建表格
    if not opps:
        return html.P("暂无交易机会数据", className="text-muted"), []

    table_rows = []
    for i, opp in enumerate(opps):
        signal_color = "success" if opp['signal'] == 'long' else "danger"
        signal_text = "做多" if opp['signal'] == 'long' else "做空"
        row = dbc.Row([
            dbc.Col(f"{i+1}", width=1, className="text-center"),
            dbc.Col(opp['symbol'], width=2, className="fw-bold"),
            dbc.Col(opp.get('exchange', ''), width=1, className="text-muted"),
            dbc.Col(f"${opp['current_price']:.6f}", width=2),
            dbc.Col(f"{opp['volume_ratio']:.2f}x", width=1, className="text-warning"),
            dbc.Col(f"{format_volume(opp.get('avg_volume_30', 0))}", width=1, className="text-info"),
            dbc.Col(f"{format_volume(opp['current_volume'])}", width=1, className="text-success"),
            dbc.Col([
                dbc.Badge(signal_text, color=signal_color, className="fs-6")
            ], width=1),
            dbc.Col(f"{opp['price_change_24h']*100:.2f}%", 
                    width=1, 
                    className="text-success" if opp['price_change_24h'] > 0 else "text-danger")
        ], className="mb-2 align-items-center")
        table_rows.append(row)

    header = dbc.Row([
        dbc.Col("排名", width=1, className="fw-bold text-center"),
        dbc.Col("交易对", width=2, className="fw-bold"),
        dbc.Col("交易所", width=1, className="fw-bold"),
        dbc.Col("当前价格", width=2, className="fw-bold"),
        dbc.Col("交易量比率", width=1, className="fw-bold"),
        dbc.Col("平均交易量", width=1, className="fw-bold"),
        dbc.Col("当前交易量", width=1, className="fw-bold"),
        dbc.Col("交易信号", width=1, className="fw-bold"),
        dbc.Col("24h涨跌", width=1, className="fw-bold")
    ], className="mb-3 fw-bold border-bottom pb-2")

    # 下拉选项基于过滤后的机会
    symbol_options = [{'label': o['symbol'], 'value': o['symbol']} for o in opps]

    return [header] + table_rows, symbol_options

@app.callback(
    Output("charts-container", "children"),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value")
)
def update_charts(selected_symbol, timeframe):
    """更新图表显示"""
    if not selected_symbol:
        return html.P("请选择一个交易对进行分析", className="text-muted")
    
    try:
        # 获取图表数据
        chart_data = analyzer.get_symbol_data_for_chart(selected_symbol, timeframe, 100)
        if not chart_data:
            return html.P(f"无法获取{selected_symbol}的数据", className="text-danger")
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('K线和MA线', '交易量', '交易量比率'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # K线图
        fig.add_trace(
            go.Candlestick(
                x=chart_data['timestamps'],
                open=chart_data['opens'],
                high=chart_data['highs'],
                low=chart_data['lows'],
                close=chart_data['prices'],
                name='K线',
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=chart_data['timestamps'],
                y=chart_data['ma5'],
                mode='lines',
                name='MA5',
                line=dict(color='#ff7f0e', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=chart_data['timestamps'],
                y=chart_data['ma10'],
                mode='lines',
                name='MA10',
                line=dict(color='#2ca02c', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=chart_data['timestamps'],
                y=chart_data['ma20'],
                mode='lines',
                name='MA20',
                line=dict(color='#d62728', width=1)
            ),
            row=1, col=1
        )
        
        # 交易量图
        fig.add_trace(
            go.Bar(
                x=chart_data['timestamps'],
                y=chart_data['volumes'],
                name='交易量',
                marker_color='#17a2b8',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 交易量比率图
        fig.add_trace(
            go.Scatter(
                x=chart_data['timestamps'],
                y=chart_data['volume_ratio'],
                mode='lines',
                name='交易量比率',
                line=dict(color='#e83e8c', width=2)
            ),
            row=3, col=1
        )
        
        # 添加水平参考线
        fig.add_hline(y=3.0, line_dash="dash", line_color="red", 
                     annotation_text="3倍交易量阈值", row=3, col=1)
        
        # 添加平均交易量横线
        if chart_data['volumes'] and len(chart_data['volumes']) > 0:
            avg_volume = sum(chart_data['volumes']) / len(chart_data['volumes'])
            fig.add_hline(y=avg_volume, line_dash="dash", line_color="orange", 
                         annotation_text=f"平均交易量: {format_volume(avg_volume)}", row=2, col=1)
        
        # 更新布局
        fig.update_layout(
            height=800,
            title=f"{selected_symbol} - {timeframe} 分析图表",
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # 更新x轴标签
        fig.update_xaxes(title_text="时间", row=3, col=1)
        fig.update_yaxes(title_text="价格", row=1, col=1)
        fig.update_yaxes(title_text="交易量", row=2, col=1)
        fig.update_yaxes(title_text="比率", row=3, col=1)
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        return html.P(f"生成图表时出错: {str(e)}", className="text-danger")

@app.callback(
    Output("exchange-status", "children"),
    Input("interval-component", "n_intervals")
)
def update_exchange_status(n):
    """更新交易所状态显示"""
    try:
        stats = analyzer.get_exchange_statistics()
        status_details = stats['status_details']
        
        # 创建状态卡片
        status_cards = []
        
        for exchange_name, status in status_details.items():
            if status.get('connected', False):
                # 连接成功
                status_color = "success"
                status_icon = "✅"
                status_text = "正常"
                
                # 显示详细信息
                info_items = [
                    f"交易对: {status.get('market_count', 0)}",
                    f"成功率: {status.get('ticker_success_rate', 0)*100:.1f}%",
                    f"最小交易量: ${status.get('min_volume_usd', 0):,.0f}"
                ]
            else:
                # 连接失败
                status_color = "danger"
                status_icon = "❌"
                status_text = "异常"
                info_items = [f"错误: {status.get('error', '未知错误')}"]
            
            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(f"{status_icon} {exchange_name.upper()}", className="mb-1"),
                            html.Small(status.get('description', ''), className="text-muted")
                        ], width=8),
                        dbc.Col([
                            dbc.Badge(status_text, color=status_color, className="mb-1")
                        ], width=4)
                    ]),
                    html.Div([
                        html.Small(item, className="d-block text-muted") 
                        for item in info_items
                    ])
                ])
            ], className="mb-2")
            
            status_cards.append(card)
        
        # 统计信息
        summary = dbc.Alert([
            html.H6("📊 交易所统计", className="mb-2"),
            html.P(f"总交易所: {stats['total_exchanges']} | "
                  f"已连接: {stats['connected_exchanges']} | "
                  f"连接率: {stats['connection_rate']*100:.1f}%", className="mb-0")
        ], color="info", className="mb-3")
        
        return [summary] + status_cards
        
    except Exception as e:
        logger.error(f"更新交易所状态失败: {e}")
        return html.P(f"获取交易所状态失败: {str(e)}", className="text-danger")

if __name__ == '__main__':
    print("🚀 启动加密货币交易机会分析器...")
    print("正在初始化数据，请稍候...")
    print("🌐 访问地址: http://localhost:8050")
    print("📊 系统将每5分钟自动更新数据")
    
    # Bolt.host 优化配置
    app.run_server(
        debug=False,  # 生产环境关闭调试
        host='0.0.0.0', 
        port=8050,
        threaded=True,  # 启用多线程
        dev_tools_hot_reload=False  # 关闭热重载
    ) 