@echo off
echo ========================================
echo BTC AGENT v2.0.0 - SCALPING M5/M1
echo ========================================
echo.
echo Symbol: BTCUSDc
echo Volume: 0.30 lotes
echo SL: $5.00 (mesma expectativa que Gold)
echo TS: Ativa com $2.00
echo Estrategia: M5 principal + M1 timing
echo.
echo Pressione CTRL+C para parar
echo ========================================
echo.

python src\agents\btc_loss_zero_v2.py

pause
