@echo off
cls
echo ============================================================
echo    VISUALIZAR TRADES NO BANCO DE DADOS
echo ============================================================
echo.
echo  Mostra todos os trades salvos pelo BTC Hedge Agent
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

uv run python ver_trades_banco.py

echo.
pause
