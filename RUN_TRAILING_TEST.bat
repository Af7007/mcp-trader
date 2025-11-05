@echo off
title TESTE TRAILING STOP COM SL GRANDE
echo.
echo ================================================================
echo        GOLD TRAILING STOP - TESTE COM SL GRANDE
echo ================================================================
echo.
echo OBJETIVO: Evitar erro "Invalid stops"
echo COMPORTAMENTO: Abre posicao IMEDIATAMENTE com SL muito maior
echo TESTE: Verificar ativacao do trailing em 30-60 segundos
echo.
echo CORRECAO APLICADA:
echo - SL: 10.0 x ATR = 1000 pontos (muito maior!)
echo - Volume: 0.01 lotes (menor risco)
echo - Trailing ativa: 1 ponto (ultra-baixo)
echo - ATR forcado: 100 pontos
echo.
echo VANTAGENS:
echo - SL grande evita "Invalid stops"
echo - Mantem teste rapido do trailing
echo - Volume menor reduz risco
echo.
echo ================================================================
echo.
python gold_trailing_test_sl_grande.py
pause
