@echo off
cls
echo ============================================================
echo    TESTE BTC AI - DIAGNOSTICO BREAK-EVEN E TRAILING
echo ============================================================
echo.
echo Este teste vai mostrar logs DETALHADOS de:
echo   [BREAK-EVEN DEBUG] - Calculo do lucro e threshold
echo   [BREAK-EVEN] - Ativacao do break-even
echo   [TRAILING] - Ativacao do trailing stop
echo   [WORKER] - Status do monitor continuo
echo.
echo CONFIGURACAO:
echo   - SL: $8.00
echo   - Break-Even: $1.50 (move SL para entry)
echo   - Trailing: $4.00 (ativa), $2.00 (protege)
echo   - Logs de DEBUG ativados!
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

title BTC_AI_TEST - Break-Even Debug
uv run python src\agents\btc_ai_agent.py --symbol BTCUSDc --volume 0.05 --fixed-sl-dollars 8.0 --model-name llama3.2:1b

echo.
echo ============================================================
echo    TESTE CONCLUIDO
echo ============================================================
pause
