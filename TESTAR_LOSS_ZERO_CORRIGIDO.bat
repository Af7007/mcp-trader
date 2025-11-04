@echo off
echo ================================================================
echo    BTC LOSS ZERO - TESTE DA VERSAO CORRIGIDA
echo ================================================================
echo.
echo Testando agente com novas configuracoes:
echo   - SL: $80 (antes: $30)
echo   - TP: $160 (antes: $50) - R/R 2:1
echo   - Circuit Breaker: 5 perdas consecutivas
echo   - Blacklist: 18-20h e 22-23h UTC
echo   - Confirmacao dupla de sinais
echo.
echo Pressione qualquer tecla para iniciar teste...
pause > nul

python EXECUTAR_LOSS_ZERO.py --test --duration 120

echo.
echo ================================================================
echo   TESTE CONCLUIDO
echo ================================================================
echo.
echo Proximo passo: Revisar resultados acima
echo.
echo Para rodar em modo LIVE:
echo   python EXECUTAR_LOSS_ZERO.py --live
echo.
pause
