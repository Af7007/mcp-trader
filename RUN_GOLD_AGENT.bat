@echo off
cls
echo ============================================================
echo    AGENTE DE TRADING XAUUSD (OURO) COM HEDGE
echo ============================================================
echo.
echo  ATENCAO: Este agente vai operar com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: XAUUSDm (Ouro)
echo    - Volume: 0.01 lots
echo    - Target Profit: $5 por operacao
echo    - Limite Diario: ILIMITADO (24/7)
echo    - SL Dinamico: ATR x 1.5
echo.
echo  Estrategia: Ordens Acertivas
echo    - Modo: SELL-ONLY (rejeita BUY)
echo    - TP: $5.0 por operacao
echo    - SL: ATR x 1.5 (dinamico)
echo    - Hedge: DESATIVADO (foco em qualidade)
echo.
echo ============================================================
echo.

set /p CONFIRM="Confirma iniciar operacoes REAIS em OURO? (S/N): "
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

echo Parando processos Python antigos de Gold Agent...
taskkill /F /FI "WINDOWTITLE eq GOLD_AGENT*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO AGENTE GOLD HEDGE
echo ============================================================
echo.
echo Logs serao exibidos a cada 30 segundos...
echo.
echo Para PARAR o agente, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente com XAUUSDm
REM Volume: 0.01 lots (conservador)
REM Estrategia: SELL-ONLY, Hedge DESATIVADO, SL dinamico (ATR x 1.5)
title GOLD_AGENT - XAUUSDm
uv run python src\agents\btc_hedge_agent.py XAUUSDm --volume 0.01

echo.
echo ============================================================
echo    AGENTE ENCERRADO
echo ============================================================
echo.
pause
