@echo off
cls
echo ============================================================
echo    DASHBOARD DE TRADES
echo ============================================================
echo.
echo  Este dashboard exibe todos os seus trades no banco de dados
echo  com gráficos, estatísticas e filtros.
echo.
echo  Acesso: http://localhost:3001
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Iniciando dashboard...
echo.
echo Abra seu navegador em: http://localhost:3001
echo.
echo Para parar, pressione Ctrl+C
echo.

timeout /t 2 /nobreak >nul

uv run python src\web\dashboard.py

pause
