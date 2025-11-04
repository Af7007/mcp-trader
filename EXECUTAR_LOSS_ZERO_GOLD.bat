@echo off
echo ============================================================
echo GOLD LOSS ZERO - ESTRATEGIA TRAILING STOP
echo ============================================================
echo.
echo Simbolo: XAUUSDc (Gold - Conta Cents)
echo.
echo CONFIGURACAO GOLD:
echo - Volume: 0.01 lotes
echo - SL: ATR x 1.5 (60-90 pontos)
echo - Trailing ativa: ATR x 0.4 (~24 pontos)
echo - Trailing distancia: ATR x 0.3 (~18 pontos)
echo - ATR minimo: 60 pontos
echo - Momentum: 0.03%% (~$0.78 em Gold $2,600)
echo.
echo ESTRATEGIA LOSS ZERO:
echo 1. Abre posicao com SL (sem TP fixo)
echo 2. Quando lucrando >= ATR x 0.4, trailing ATIVA
echo 3. Trailing protege e maximiza lucros
echo 4. NUNCA fecha no prejuizo!
echo.
echo ============================================================
echo EXECUTANDO AGENTE GOLD...
echo ============================================================
echo.
echo Pressione Ctrl+C para parar o agente
echo.

python EXECUTAR_LOSS_ZERO.py --live --symbol XAUUSDc

pause
