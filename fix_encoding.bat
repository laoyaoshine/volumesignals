@echo off
chcp 65001
cls

echo ======================================
echo Fixing GitHub commit message (UTF-8)
echo ======================================
echo.

cd /d "C:\Users\quzhi\Desktop\交易量\交易量"

echo [1/4] Checking repository status...
git status
echo.

echo [2/4] Staging all changes...
git add -A
echo.

echo [3/4] Amending commit with UTF-8 message...
git commit --amend -m "Initial commit: Cryptocurrency Trading Opportunity Analyzer"
echo.

echo [4/4] Force pushing to GitHub...
git push -f origin main
echo.

echo ======================================
echo Done! Fixed commit message.
echo Repository: https://github.com/laoyaoshine/crypto-volume-trading-signals
echo ======================================
pause
