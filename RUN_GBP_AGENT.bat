@echo off
cls
echo ============================================================
echo    AGENTE DE TRADING GBPUSD (LIBRA) COM HEDGE
echo ============================================================
echo.
echo  ATENCAO: Este agente vai operar com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: GBPUSDc (Libra Esterlina)
echo    - Volume: 0.10 lots
echo    - Target Profit: $2 por operacao
echo    - Limite Diario: 20 operacoes
echo    - SL Dinamico: 1.5x ATR
echo    - Hedge: Automatico em reversao
echo.
echo ============================================================
echo.

set /p CONFIRM="Confirma iniciar operacoes REAIS em GBPUSD? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operacao cancelada.
    pause
    exit /b 0
)

echo.
echo Verificando MT5...
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Parando processos Python antigos de GBP Agent...
taskkill /F /FI "WINDOWTITLE eq GBP_AGENT*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO AGENTE GBP HEDGE
echo ============================================================
echo.
echo Logs serao exibidos a cada 30 segundos...
echo.
echo Para PARAR o agente, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente com GBPUSDc
title GBP_AGENT - GBPUSDc
uv run python src\agents\btc_hedge_agent.py GBPUSDc 0.10

echo.
echo ============================================================
echo    AGENTE ENCERRADO
echo ============================================================
echo.
pause
