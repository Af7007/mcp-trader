@echo off
cls
echo ============================================================
echo    TESTE DOS SIMBOLOS FOREX
echo ============================================================
echo.
echo  Este script verifica se os simbolos Forex estao disponiveis
echo  e funcionando corretamente no MT5.
echo.
echo  Simbolos testados:
echo    - GBPUSDc (Libra Esterlina)
echo    - EURUSDc (Euro)
echo    - USDJPYc (Yen Japones)
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Testando simbolos Forex...
echo.

uv run python test_forex_symbols.py

echo.
pause
