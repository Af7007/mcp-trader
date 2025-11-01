@echo off
REM ========================================================================
REM  Testar Visualizador BTC Loss Zero
REM  Gera dados simulados para testar o EA sem rodar o agente real
REM ========================================================================

echo.
echo ====================================================================
echo  TESTAR VISUALIZADOR BTC LOSS ZERO
echo ====================================================================
echo.
echo  Este script gera dados simulados para testar o visualizador
echo  sem precisar rodar o agente real.
echo.
echo ====================================================================
echo.

REM Executar script de teste
python testar_visualizador_loss_zero.py

echo.
echo ====================================================================
echo  Teste finalizado!
echo ====================================================================
echo.
pause
