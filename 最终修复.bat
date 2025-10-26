@echo off
chcp 65001
cls

echo ======================================
echo Fixing GitHub commit message 
echo ======================================
echo.

cd /d "C:\Users\quzhi\Desktop\交易量\交易量"

echo [1/5] Configuring Git...
git config --global core.quotepath false
git config --global i18n.commitencoding UTF-8
git config --global i18n.logoutputencoding UTF-8

echo.
echo [2/5] Adding files...
git add -A

echo.
echo [3/5] Creating new commit with English message...
git commit --amend -m "Initial commit: Cryptocurrency Trading Opportunity Analyzer" --allow-empty

echo.
echo [4/5] Updating commit message...
set "GIT_EDITOR=exit"
git commit --amend -m "Initial commit: Cryptocurrency Trading Opportunity Analyzer"

echo.
echo [5/5] Force pushing to GitHub...
git push -f origin main

echo.
echo ======================================
echo Completed!
echo ======================================
echo Check: https://github.com/laoyaoshine/crypto-volume-trading-signals
echo.
pause
