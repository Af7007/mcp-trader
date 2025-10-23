@echo off
cls
echo ============================================================
echo    TRADING CHATBOT - INICIANDO SERVICOS
echo ============================================================
echo.
echo IMPORTANTE: Certifique-se que o MetaTrader 5 esta aberto!
echo.
echo Iniciando servicos...
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo [1/3] MT5 MCP Server (porta 8000)...
start "MT5 MCP Server" cmd /k "uv run python start_mt5_http.py"
timeout /t 3 /nobreak >nul

echo [2/3] Web Dashboard (porta 3000)...
start "Web Dashboard" cmd /k "uv run python run_simple_web.py"
timeout /t 3 /nobreak >nul

echo [3/3] Worker Service (background)...
start "Worker Service" cmd /k "uv run python src\core\main.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    SERVICOS INICIADOS!
echo ============================================================
echo.
echo Acesse: http://localhost:3000
echo.
echo Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Pressione qualquer tecla para sair...
pause >nul
