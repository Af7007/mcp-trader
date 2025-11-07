@echo off
cls
echo ============================================================
echo    GBP AI AGENT - IA Local + Trailing Stop (Forex)
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: GBPUSDc (British Pound)
echo    - Volume: 0.03 lots
echo    - SL Fixo: $4.00
echo    - Trailing Step: $1.5
echo    - IA: Ollama Local (llama3.2:1b)
echo    - Estrategia: IA decide entrada + Trailing Stop protege lucro
echo    - Fallback: Metodo tradicional se IA falhar
echo.
echo  Caracteristicas da IA:
echo    - Analise completa: Preco, momentum, volume, tendencia
echo    - Contexto horario e sessoes Forex
echo    - Decisoes BUY/SELL/HOLD baseadas em IA
echo    - Logging detalhado de performance da IA
echo.
echo ============================================================
echo.

echo.
echo Verificando Ollama...
echo.

REM Verificar se Ollama esta rodando
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Ollama nao parece estar rodando na porta 11434
    echo Verifique se o Ollama esta iniciado.
    echo.
    echo Para iniciar Ollama, execute: ollama serve
    echo.
    pause
)

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Parando processos antigos...
taskkill /F /FI "WINDOWTITLE eq GBP_AI*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO GBP AI AGENT
echo ============================================================
echo.
echo IA: Ollama (Local) - Sem custos de API
echo Estrategia: Inteligencia Artificial + Trailing Stop
echo Fallback: Metodo tradicional se IA falhar
echo.
echo Para PARAR, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente
title GBP_AI_AGENT - GBPUSDc
uv run python src\agents\gbp_ai_agent.py --symbol GBPUSDc --volume 0.03 --fixed-sl-dollars 4.0 --trailing-step-dollar 1.5 --model-name llama3.2:1b

echo.
echo ============================================================
echo    GBP AI AGENT ENCERRADO
echo ============================================================
echo.
