@echo off
cls
echo ============================================================
echo    TODOS OS AGENTES FOREX - GBP + EUR + JPY
echo ============================================================
echo.
echo  ATENCAO: Este script vai iniciar 3 agentes Forex simultaneos!
echo.
echo  Agente 1: GBPUSDc  (Libra - 0.10 lots)
echo  Agente 2: EURUSDc  (Euro - 0.10 lots)
echo  Agente 3: USDJPYc  (Yen - 0.10 lots)
echo.
echo  Cada agente:
echo    - Target Profit: $2 por operacao
echo    - Limite Diario: 20 operacoes CADA
echo    - SL Dinamico: 1.5x ATR
echo    - Hedge: Automatico em reversao
echo.
echo  Total: Ate 60 operacoes por dia (20 x 3 pares)
echo.
echo ============================================================
echo.

set /p CONFIRM="Confirma iniciar 3 AGENTES FOREX simultaneos com DINHEIRO REAL? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operacao cancelada.
    pause
    exit /b 0
)

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
echo    INICIANDO AGENTES FOREX
echo ============================================================
echo.
echo  Agentes serao iniciados em janelas separadas
echo.
echo  Para parar UM agente: Feche a janela correspondente
echo  Para parar TODOS: Execute STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Iniciar agente GBP em janela separada
start "GBP_AGENT - GBPUSDc" cmd /k "echo AGENTE GBP INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py GBPUSDc --volume 0.10"

timeout /t 2 /nobreak >nul

REM Iniciar agente EUR em janela separada
start "EUR_AGENT - EURUSDc" cmd /k "echo AGENTE EUR INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py EURUSDc --volume 0.10"

timeout /t 2 /nobreak >nul

REM Iniciar agente JPY em janela separada
start "JPY_AGENT - USDJPYc" cmd /k "echo AGENTE JPY INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py USDJPYc --volume 0.10"

echo.
echo ============================================================
echo    3 AGENTES FOREX INICIADOS!
echo ============================================================
echo.
echo  Verifique as janelas abertas:
echo    - GBP_AGENT - GBPUSDc
echo    - EUR_AGENT - EURUSDc
echo    - JPY_AGENT - USDJPYc
echo.
echo  Para parar todos os agentes: STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.
pause
