@echo off
cls
echo ============================================================
echo    TESTE DO SIMBOLO XAUUSD (OURO)
echo ============================================================
echo.
echo  Este script verifica se XAUUSDm esta disponivel
echo  e funcionando corretamente no MT5.
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Testando simbolo XAUUSDm...
echo.

uv run python test_gold_symbol.py

echo.
pause
