@echo off
echo ================================================================
echo    BTC LOSS ZERO - VERSAO CORRIGIDA 2.0
echo ================================================================
echo.
echo Novas configuracoes ativas:
echo   [+] Stop Loss: $80 (era $30)
echo   [+] Take Profit: $160 (era $50) - R/R 2:1
echo   [+] Circuit Breaker: Pausa apos 5 perdas consecutivas
echo   [+] Blacklist: 18-20h e 22-23h UTC bloqueados
echo   [+] Confirmacao dupla de sinais (filtros mais rigorosos)
echo   [+] Trailing: $10 ativa com $5 de lucro
echo.
echo ================================================================
echo   MODO LIVE - DINHEIRO REAL
echo ================================================================
echo.
echo IMPORTANTE: Certifique-se que MT5 esta aberto e logado!
echo.
echo Pressione Ctrl+C para parar o agente a qualquer momento.
echo.
pause

python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc

pause
