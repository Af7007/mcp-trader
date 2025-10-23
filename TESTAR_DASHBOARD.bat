@echo off
cls
echo ============================================================
echo    TESTE DO DASHBOARD MT5 - DADOS SIMULADOS
echo ============================================================
echo.
echo  Este script gera dados de teste para o dashboard visual
echo  do MT5, permitindo testar a visualizacao antes de
echo  executar o agente real.
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Gerando dados de teste...
echo.

uv run python test_dashboard_data.py

echo.
echo ============================================================
echo.
pause
