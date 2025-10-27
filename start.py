#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动交易系统
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    print("🚀 启动加密货币交易分析系统")
    print("🌐 Dash应用访问地址: http://localhost:8050")
    print("💡 React前端访问地址: http://localhost:5173")
    
    try:
        from app import app
        app.run_server(debug=False, host='0.0.0.0', port=8050)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
