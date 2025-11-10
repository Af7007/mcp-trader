@echo off
echo ============================================================
echo BTC v3.2.0 - ACOES ANTI-LOSS - Executando...
echo ============================================================
echo.
echo VERSAO: v3.2.0 (v3.1.0 + Circuit Breaker + Break-Even + Cooldown)
echo.
echo NOVAS ACOES ANTI-LOSS v3.2.0:
echo   [1] Circuit Breaker: Para apos 3 losses consecutivas (aguarda 5min) - AGRESSIVO!
echo   [2] Break-Even Move: Move SL para entry apos $1.50 lucro
echo   [3] Cooldown: 30s entre trades (evita overtrading)
echo.
echo PARAMETROS BTC v3.2.0:
echo   - Volume: 0.05 lotes (ULTRA CONSERVADOR - minimo risco)
echo   - SL: $20.00 fixo (MAIOR ESPACO - melhor timing)
echo   - Trailing: Ativa $4, protege $2
echo   - Max ATR: SEM LIMITE
echo   - Max Spread: $50
echo   - Score M5: 4.5 (apenas sinais FORTES)
echo.
echo RESULTADO ESPERADO v3.2.0:
echo   - Win Rate: 65%% -^> 70%% (+5%%)
echo   - Max Losses Consecutivas: 3 (para agente) - MUITO AGRESSIVO!
echo   - Trades viram Loss apos $1.50: ELIMINADO (break-even)
echo   - Overtrading: ELIMINADO (cooldown 30s)
echo.
echo ============================================================
echo.

python src/agents/btc_loss_zero_v3.py

pause
