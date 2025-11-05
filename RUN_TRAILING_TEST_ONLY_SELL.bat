@echo off
title TESTE TRAILING STOP ONLY SELL
echo.
echo ================================================================
echo        GOLD TRAILING STOP - TESTE ONLY SELL
echo ================================================================
echo.
echo OBJETIVO: Analisar comportamento especifico de SELL
echo COMPORTAMENTO: Forca apenas operacoes SELL
echo TESTE: Verificar ativacao do trailing em SELL
echo.
echo CONFIGURACOES ONLY SELL:
echo - SL: 10.0 x ATR = 1000 pontos (muito maior!)
echo - Volume: 0.01 lotes (menor risco)
echo - Trailing ativa: 1 ponto (ultra-baixo)
echo - ATR forcado: 100 pontos
echo - Operacoes: ONLY SELL (BUY desabilitado)
echo.
echo VANTAGENS:
echo - Foco em comportamento de SELL
echo - SL grande evita "Invalid stops"
echo - Sistema trailing rapido
echo - Analise especifica de vendas
echo.
echo ================================================================
echo.
python gold_trailing_test_only_sell.py
pause
