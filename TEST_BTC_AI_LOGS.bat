@echo off
cls
echo ============================================================
echo    TESTE BTC AI - LOGS DETALHADOS DA IA
echo ============================================================
echo.
echo Este teste vai:
echo   1. Iniciar BTC AI Agent
echo   2. Mostrar TODOS os logs da IA (input + output)
echo   3. Rodar por 5 minutos
echo.
echo LOGS QUE VOCE VERA:
echo   [IA ANALYSIS] - Consultando LLM
echo   [INPUT] - Dados enviados (preco, momentum, volume, etc)
echo   [CONTEXT] - Contexto adicional (horario, streak, etc)
echo   [OUTPUT] - Decisao da IA (BUY/SELL/HOLD + confianca + raciocinio)
echo   [IA VALIDATION] - Validacao com M5 trend
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

title BTC_AI_TEST - Logs Detalhados
uv run python src\agents\btc_ai_agent.py --symbol BTCUSDc --volume 0.05 --fixed-sl-dollars 8.0 --model-name llama3.2:1b

echo.
echo ============================================================
echo    TESTE CONCLUIDO
echo ============================================================
pause
