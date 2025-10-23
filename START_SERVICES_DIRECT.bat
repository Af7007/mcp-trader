@echo off
cls
echo ============================================================
echo    TRADING CHATBOT - CONEXAO DIRETA COM MT5
echo ============================================================
echo.
echo IMPORTANTE: Certifique-se que o MetaTrader 5 esta aberto!
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Parando processos Python antigos...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Iniciando servicos...
echo.

echo [1/2] Web Dashboard (porta 3000)...
start "Web Dashboard" cmd /k "uv run python run_simple_web.py"
timeout /t 3 /nobreak >nul

echo [2/2] Worker Service (background)...
start "Worker Service" cmd /k "uv run python src\core\main.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    SERVICOS INICIADOS!
echo ============================================================
echo.
echo Servicos rodando:
echo   * Web Dashboard:   http://localhost:3000
echo   * Worker Service:  Background
echo   * MT5 Connection:  Direct (sem HTTP)
echo.
echo Abrindo navegador em 3 segundos...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ============================================================
echo   SISTEMA PRONTO!
echo ============================================================
echo.
echo Para parar tudo: STOP_ALL_SERVICES.bat
echo.
pause
