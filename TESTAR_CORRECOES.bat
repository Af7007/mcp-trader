@echo off
echo ============================================================
echo TESTE DO AGENTE BTC LOSS ZERO v1.1 CORRIGIDO
echo ============================================================
echo.
echo CORRECOES APLICADAS:
echo - SL minimo: 150 pontos (era 80)
echo - Volume: 0.01 lotes fixo (limite max 0.1)
echo - Momentum: 0.05%% (era 0.03%%)
echo - Confirmacoes: 3 (era 2)
echo - Trailing ajustado: ATR x 0.6 e 0.4
echo.
echo ============================================================
echo EXECUTANDO AGENTE...
echo ============================================================
echo.
echo Pressione Ctrl+C para parar o agente
echo.

python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc

pause
