@echo off
cls
echo ============================================================
echo    AGENTES MULTIPLOS - BTC + GOLD
echo ============================================================
echo.
echo  ATENCAO: Este script vai iniciar 2 agentes simultaneos!
echo.
echo  Agente 1: BTCUSDm  (0.02 lots)
echo  Agente 2: XAUUSDm  (0.01 lots)
echo.
echo  Cada agente:
echo    - Target Profit: $2 por operacao
echo    - Limite Diario: 20 operacoes CADA
echo    - SL Dinamico: 1.5x ATR
echo    - Hedge: Automatico em reversao
echo.
echo ============================================================
echo.

echo.
echo Verificando ambiente...
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
echo ============================================================
echo    INICIANDO AGENTES
echo ============================================================
echo.
echo  Agente BTC: Janela separada sera aberta
echo  Agente GOLD: Janela separada sera aberta
echo.
echo  Para parar UM agente: Feche a janela correspondente
echo  Para parar TODOS: Execute STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Iniciar agente BTC em janela separada
start "BTC_AGENT - BTCUSDm" cmd /k "echo AGENTE BTC INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py BTCUSDm --volume 0.02"

timeout /t 2 /nobreak >nul

REM Iniciar agente GOLD em janela separada
start "GOLD_AGENT - XAUUSDm" cmd /k "echo AGENTE GOLD INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py XAUUSDm --volume 0.01"

echo.
echo ============================================================
echo    2 AGENTES INICIADOS!
echo ============================================================
echo.
echo  Verifique as janelas abertas:
echo    - BTC_AGENT - BTCUSDm
echo    - GOLD_AGENT - XAUUSDm
echo.
echo  Para parar todos os agentes: STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.
pause
