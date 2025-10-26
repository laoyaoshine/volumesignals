@echo off
chcp 65001 >nul
echo ====================================
echo 正在上传代码到GitHub...
echo ====================================
echo.

cd /d "%~dp0交易量"

echo 步骤1: 检查Git状态...
git status

echo.
echo 步骤2: 添加远程仓库...
git remote add origin https://github.com/laoyaoshine/crypto-volume-trading-signals.git 2>nul || git remote set-url origin https://github.com/laoyaoshine/crypto-volume-trading-signals.git

echo.
echo 步骤3: 提交文件（如果还没有提交）...
git add -A
git commit -m "Initial commit: 加密货币交易机会分析器" 2>nul

echo.
echo 步骤4: 切换到main分支...
git branch -M main

echo.
echo 步骤5: 推送到GitHub...
git push -u origin main

echo.
echo ====================================
echo 上传完成！
echo.
echo 仓库地址: https://github.com/laoyaoshine/crypto-volume-trading-signals
echo.
echo 访问仓库查看您的代码！
echo ====================================
pause
