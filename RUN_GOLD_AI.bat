@echo off
cls
echo ============================================================
echo    GOLD AI AGENT - IA Local + Trailing Stop
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: XAUUSDc (Ouro)
echo    - Volume: 0.02 lots (ajustavel)
echo    - SL DINAMICO: ATR * 150 (min $4, max $10) - Adapta a volatilidade
echo    - PROTECAO PROGRESSIVA v1.4.0 (Worker 20ms):
echo       * $1 lucro -^> Break-even (protege $0)
echo       * $3 lucro -^> Trailing (protege $1)
echo       * $5 lucro -^> Trailing (protege $3)
echo       * Formula: protecao = lucro - $2
echo    - IA: Ollama Local (llama3.2:1b)
echo    - Estrategia: IA decide entrada + Trailing Stop protege lucro
echo    - Fallback: Metodo tradicional se IA falhar
echo.
echo  Caracteristicas da IA:
echo    - Analise completa: Preco, momentum, volume, tendencia
echo    - Contexto horario e situacional
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
taskkill /F /FI "WINDOWTITLE eq GOLD_AI*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO GOLD AI AGENT
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
title GOLD_AI_AGENT - XAUUSDc (Trailing Otimizado)
uv run python src\agents\gold_ai_agent.py --symbol XAUUSDc --volume 0.02 --fixed-sl-dollars 5.0 --model-name llama3.2:1b

echo.
echo ============================================================
echo    GOLD AI AGENT ENCERRADO
echo ============================================================
echo.
