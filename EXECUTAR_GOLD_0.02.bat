@echo off
echo ========================================
echo GOLD LOSS ZERO - VOLUME 0.02 LOTE
echo ========================================
echo.
echo Configuracao:
echo - Volume: 0.02 lote (FIXO)
echo - SL: 90 pts = $0.18
echo - Trailing ativa: 24 pts = $0.05
echo - Trailing dist: 18 pts = $0.04
echo - Worker: 0.5s (RAPIDO!)
echo.
echo ========================================
echo.

python gold_loss_zero_0.02.py

pause
