@echo off
cls
echo ============================================================
echo    AGENTE DE TRADING USDJPY (YEN) COM HEDGE
echo ============================================================
echo.
echo  ATENCAO: Este agente vai operar com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: USDJPYc (Yen Japones)
echo    - Volume: 0.10 lots
echo    - Target Profit: $2 por operacao
echo    - Limite Diario: 20 operacoes
echo    - SL Dinamico: 1.5x ATR
echo    - Hedge: Automatico em reversao
echo.
echo ============================================================
echo.

set /p CONFIRM="Confirma iniciar operacoes REAIS em USDJPY? (S/N): "
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

echo Parando processos Python antigos de JPY Agent...
taskkill /F /FI "WINDOWTITLE eq JPY_AGENT*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO AGENTE JPY HEDGE
echo ============================================================
echo.
echo Logs serao exibidos a cada 30 segundos...
echo.
echo Para PARAR o agente, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente com USDJPYc
REM Volume ajustado: 0.10 lots (forex usa volumes maiores)
title JPY_AGENT - USDJPYc
uv run python src\agents\btc_hedge_agent.py USDJPYc --volume 0.10

echo.
echo ============================================================
echo    AGENTE ENCERRADO
echo ============================================================
echo.
pause
