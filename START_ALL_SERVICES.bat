@echo off
echo ============================================================
echo    INICIANDO TODOS OS SERVICOS DO TRADING CHATBOT
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist ".venv" (
    echo ERRO: Diretorio .venv nao encontrado!
    echo Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo [1/3] Iniciando MT5 MCP Server (porta 8000)...
start "MT5 MCP Server" cmd /k "uv run python start_mt5_http.py"
timeout /t 3 /nobreak >nul

echo [2/3] Iniciando Web Dashboard (porta 3000)...
start "Web Dashboard" cmd /k "uv run python run_simple_web.py"
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando Worker (background tasks)...
start "Worker Service" cmd /k "uv run python src\core\main.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    TODOS OS SERVICOS FORAM INICIADOS!
echo ============================================================
echo.
echo Servicos rodando:
echo   * MT5 MCP Server:  http://localhost:8000
echo   * Web Dashboard:   http://localhost:3000
echo   * Worker Service:  Background
echo   * Ollama Service:  http://localhost:11434 (ja estava rodando)
echo.
echo Pressione qualquer tecla para abrir o navegador...
pause >nul

start http://localhost:3000

echo.
echo Para parar todos os servicos, feche todas as janelas abertas
echo ou execute: taskkill /F /IM python.exe
echo.
pause
