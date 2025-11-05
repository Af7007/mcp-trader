@echo off
cls
echo ============================================================
echo    GOLD ADAPTIVE AGENT - AUTO-LEARNING v2.0
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: XAUUSDc (Ouro)
echo    - Volume: 0.02 lots
echo    - Estrategia: Trailing Stop Loss Zero
echo    - AUTO-TUNING: HABILITADO
echo.
echo  Sistema de Aprendizado:
echo    - Analisa performance a cada 50 trades
echo    - Detecta regime de mercado (1 hora)
echo    - Ajusta parametros automaticamente
echo    - Protecoes: Validacao + Fallback
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
taskkill /F /FI "WINDOWTITLE eq GOLD_ADAPTIVE*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO GOLD ADAPTIVE AGENT
echo ============================================================
echo.
echo Auto-tuning: ATIVO
echo Otimizacao a cada: 50 trades
echo Deteccao de regime: A cada 60 minutos
echo.
echo Para PARAR, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente adaptativo
title GOLD_ADAPTIVE_AGENT - XAUUSDc
uv run python src\agents\gold_adaptive_agent.py --symbol XAUUSDc --volume 0.02

echo.
echo ============================================================
echo    AGENTE ADAPTATIVO ENCERRADO
echo ============================================================
echo.
