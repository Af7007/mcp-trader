@echo off
cls
echo ============================================================
echo    DIAGNOSTICO DO MT5
echo ============================================================
echo.
echo  Este script verifica a conexao e estado do MT5
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

uv run python diagnostico_mt5.py

echo.
pause
