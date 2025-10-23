@echo off
cls
echo ============================================================
echo    TODOS OS AGENTES - COMPLETO
echo ============================================================
echo.
echo  ATENCAO: Este script vai iniciar 5 agentes simultaneos!
echo.
echo  Crypto/Commodities:
echo    1. BTCUSDc  (Bitcoin - 0.02 lots)
echo    2. XAUUSDc  (Ouro - 0.01 lots)
echo.
echo  Forex:
echo    3. GBPUSDc  (Libra - 0.10 lots)
echo    4. EURUSDc  (Euro - 0.10 lots)
echo    5. USDJPYc  (Yen - 0.10 lots)
echo.
echo  Cada agente:
echo    - Target Profit: $2 por operacao
echo    - Limite Diario: 20 operacoes CADA
echo    - SL Dinamico: 1.5x ATR
echo    - Hedge: Automatico em reversao
echo.
echo  Total: Ate 100 operacoes por dia (20 x 5 simbolos)
echo.
echo ============================================================
echo.
echo  ⚠️  AVISO: Certifique-se de ter MARGEM SUFICIENTE!
echo     Margem recomendada: $5,000+ livre
echo.
echo ============================================================
echo.

set /p CONFIRM="Confirma iniciar 5 AGENTES simultaneos com DINHEIRO REAL? (S/N): "
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
echo    INICIANDO TODOS OS AGENTES
echo ============================================================
echo.
echo  5 janelas separadas serao abertas
echo.
echo  Para parar UM agente: Feche a janela correspondente
echo  Para parar TODOS: Execute STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Iniciar agente BTC
start "BTC_AGENT - BTCUSDc" cmd /k "echo AGENTE BTC INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py BTCUSDc 0.02"
timeout /t 2 /nobreak >nul

REM Iniciar agente GOLD
start "GOLD_AGENT - XAUUSDc" cmd /k "echo AGENTE GOLD INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py XAUUSDc 0.01"
timeout /t 2 /nobreak >nul

REM Iniciar agente GBP
start "GBP_AGENT - GBPUSDc" cmd /k "echo AGENTE GBP INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py GBPUSDc 0.10"
timeout /t 2 /nobreak >nul

REM Iniciar agente EUR
start "EUR_AGENT - EURUSDc" cmd /k "echo AGENTE EUR INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py EURUSDc 0.10"
timeout /t 2 /nobreak >nul

REM Iniciar agente JPY
start "JPY_AGENT - USDJPYc" cmd /k "echo AGENTE JPY INICIADO && echo. && uv run python src\agents\btc_hedge_agent.py USDJPYc 0.10"

echo.
echo ============================================================
echo    5 AGENTES INICIADOS COM SUCESSO!
echo ============================================================
echo.
echo  Verifique as janelas abertas:
echo    - BTC_AGENT - BTCUSDc
echo    - GOLD_AGENT - XAUUSDc
echo    - GBP_AGENT - GBPUSDc
echo    - EUR_AGENT - EURUSDc
echo    - JPY_AGENT - USDJPYc
echo.
echo  Para visualizar trades: VER_TRADES.bat
echo  Para parar todos: STOP_ALL_AGENTS.bat
echo.
echo ============================================================
echo.
pause
