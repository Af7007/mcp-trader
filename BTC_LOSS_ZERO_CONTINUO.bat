@echo off
cd /d "%~dp0"
echo ================================
echo BTC LOSS ZERO - EXECUCAO CONTINUA
echo ================================
echo.
echo Agente Loss Zero vai rodar continuamente...
echo Para parar, pressione Ctrl+C
echo.
python BTC_LOSS_ZERO_CONTINUO.py
echo.
echo ================================
echo Agente parado!
echo ================================
pause
