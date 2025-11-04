@echo off
echo ================================================================
echo    BTC LOSS ZERO V4.1 - ESTRATEGIA TRAILING STOP
echo ================================================================
echo.
echo CORRECOES V4.1:
echo   [OK] Bug critico corrigido (close_opposite_positions)
echo   [OK] ATR padrao otimizado (150 -^> 120 pontos)
echo   [OK] Exception handling melhorado
echo.
echo CONFIGURACAO:
echo   [OK] Volume FIXO em 0.03 lotes
echo   [OK] SL baseado em ATR x 1.5 (dinamico)
echo   [OK] SEM TP FIXO (lucro ilimitado!)
echo   [OK] Trailing ativa com ATR x 0.5 de lucro
echo   [OK] Trailing distancia ATR x 0.3
echo   [OK] Thresholds realistas (0.03%% = $33)
echo   [OK] Filtro M15 (confirma tendencia maior)
echo   [OK] 4 horarios bloqueados
echo   [OK] Circuit breaker (5 perdas)
echo.
echo ================================================================
echo   ESTRATEGIA LOSS ZERO - TRAILING STOP
echo ================================================================
echo.
echo   Com ATR = 120 pontos (padrao V4.1):
echo     SL: 120 x 1.5 = 180 pts = $5.40 risco inicial
echo     Trailing ativa: 120 x 0.5 = 60 pts = $1.80 lucro
echo     Trailing distancia: 120 x 0.3 = 36 pts = $1.08
echo     Lucro minimo protegido: $0.72 (sempre positivo!)
echo.
echo   COMO FUNCIONA:
echo     1. Abre posicao com SL (sem TP)
echo     2. Quando lucro >= $1.80, trailing ATIVA
echo     3. Trailing protege lucro de $0.72
echo     4. Trailing SOBE/DESCE com o preco
echo     5. NUNCA fecha no prejuizo!
echo.
echo ================================================================
echo.
echo Pressione qualquer tecla para iniciar...
pause > nul

python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc

pause
