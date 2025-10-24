@echo off
cls
echo ============================================================
echo    TESTE DE CONEXAO - CLAUDE HAIKU 4.5
echo ============================================================
echo.
echo  Este script testa se a API da Anthropic esta configurada
echo  corretamente e se consegue conectar ao Claude 3.5 Haiku.
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Testando Claude Haiku...
echo.

uv run python test_haiku.py

echo.
pause
