@echo off
chcp 65001

cd /d "C:\Users\quzhi\Desktop\交易量\交易量"

git add -A

git commit --amend -m "Initial commit: Cryptocurrency Trading Opportunity Analyzer"

git push -f origin main

echo Done!
pause
