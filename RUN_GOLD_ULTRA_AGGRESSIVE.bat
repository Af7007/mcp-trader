@echo off
cls
echo ============================================================
echo    GOLD ULTRA-AGGRESSIVE AGENT - SEM AUTO-LEARNING
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: XAUUSDc (Ouro)
echo    - Volume: 0.05 lots
echo    - Estrategia: Trailing Stop ULTRA-AGGRESSIVO
echo    - AUTO-TUNING: DESABILITADO (configuracoes fixas)
echo.
echo  Configuracoes Ultra-Aggressive:
echo    - Trailing ativa: ~$1.50 lucro (78% menor que conservador)
echo    - Cooldown: 5 segundos (vs 120s original)
echo    - Check interval: 5s (vs 15s original)
echo    - Volume: 0.05 (vs 0.01 original)
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
taskkill /F /FI "WINDOWTITLE eq GOLD*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO GOLD ULTRA-AGGRESSIVE AGENT
echo ============================================================
echo.
echo Configuracao ULTRA-AGGRESSIVA FIXA
echo Auto-tuning: DESABILITADO
echo Parada voluntaria apenas com Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente ultra-agressivo SEM auto-learning
title GOLD_ULTRA_AGGRESSIVE - XAUUSDc
uv run python src\agents\gold_adaptive_agent_SEM_EMOJIS_ULTRA_AGRESSIVO.py --symbol XAUUSDc --volume 0.05 --no-auto-tuning

echo.
echo ============================================================
echo    AGENTE ULTRA-AGGRESSIVE ENCERRADO
echo ============================================================
echo.
