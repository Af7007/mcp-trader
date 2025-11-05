@echo off
cls
echo ============================================================
echo    GOLD ADAPTIVE AGENT - MODO AGRESSIVO v2.0
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao AGRESSIVA:
echo    - Simbolo: XAUUSDc (Ouro)
echo    - Volume: 0.02 lots
echo    - Estrategia: CONSERVADOR + LUCROS GRANDES
echo.
echo  Parametros Otimizados:
echo    - SL: ~$7-8 (um pouco maior para defender posicao)
echo    - Quick TP: Trailing ativa em ~$1 de lucro
echo    - Target: Busca lucros de $5, $7, $10+
echo    - Trailing Distance: Maior (~$3) para capturar movimentos
echo.
echo  Filosofia:
echo    "Trades conservadores e assertivos, quando acerta vai longe!"
echo.
echo  Expectativa (24h):
echo    - Trades: 10-15 (conservador na entrada)
echo    - Win rate: 70-75%%
echo    - Profit medio: $3-5 (com varios $7-10+)
echo    - Drawdown: Menor (menos trades)
echo.
echo ============================================================
echo.

echo.
echo Verificando MT5...
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Parando processos antigos...
taskkill /F /FI "WINDOWTITLE eq GOLD_*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO GOLD ADAPTIVE - MODO AGRESSIVO
echo ============================================================
echo.
echo Estrategia: Quick TP em $1, Target $5+
echo Auto-tuning: ATIVO
echo.
echo Para PARAR, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente em modo agressivo
title GOLD_AGGRESSIVE - XAUUSDc
python -c "from src.agents.gold_adaptive_agent import GoldAdaptiveAgent; agent = GoldAdaptiveAgent(symbol='XAUUSDc', volume=0.02, aggressive_profit_mode=True); agent.run()"

echo.
echo ============================================================
echo    AGENTE AGRESSIVO ENCERRADO
echo ============================================================
echo.
pause
