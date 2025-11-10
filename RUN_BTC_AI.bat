@echo off
cls
echo ============================================================
echo    BTC AI AGENT - IA Local SEM INDICADORES
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao:
echo    - Simbolo: BTCUSDc (Bitcoin)
echo    - Volume: 0.05 lots (ULTRA CONSERVADOR)
echo    - SL Fixo: $8.00 (timing mais preciso)
echo    - Trailing: Ativa em $4.00, protege $2.00
echo    - Circuit Breaker: 3 perdas consecutivas
echo    - Break-Even: Move SL para entry apos $1.50 lucro
echo    - Cooldown: 30s entre trades
echo.
echo  DIFERENCIAL - SEM INDICADORES TRADICIONAIS:
echo    - Sem RSI, MACD, Bollinger Bands, SMA
echo    - IA (Ollama) analisa CONTEXTO DE MERCADO
echo    - LLM decide entrada baseado em:
echo       * Momentum de preco (ultimas velas)
echo       * Tendencia de curto prazo
echo       * Volume relativo
echo       * Horario do dia
echo       * Reversoes de padrao
echo.
echo  IA Configuration:
echo    - Modelo: llama3.2:1b (Ollama Local)
echo    - Temperatura: 0.3 (RAPIDO - respostas em 2-3s!)
echo    - Timeout: 5s (decisoes ageis)
echo    - Fallback: Metodo simples se IA falhar
echo    - Circuit Breaker IA: 5 erros consecutivos
echo.
echo ============================================================
echo.

echo Verificando Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Ollama nao parece estar rodando
    echo Para iniciar: ollama serve
    pause
) else (
    echo [OK] Ollama rodando
    echo.
    echo Pre-carregando modelo na memoria para respostas RAPIDAS...
    curl -s http://localhost:11434/api/generate -d "{\"model\": \"llama3.2:1b\", \"prompt\": \"Ready\", \"stream\": false}" >nul 2>&1
    echo [OK] Modelo carregado! Decisoes IA em ~2s!
)

echo Parando processos antigos...
taskkill /F /FI "WINDOWTITLE eq BTC_AI*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo    INICIANDO BTC AI AGENT
echo ============================================================
echo.
echo Para PARAR, pressione Ctrl+C
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

title BTC_AI_AGENT - BTCUSDc (LLM SEM Indicadores)
uv run python src\agents\btc_ai_agent.py --symbol BTCUSDc --volume 0.05 --fixed-sl-dollars 8.0 --model-name llama3.2:1b

echo.
echo ============================================================
echo    BTC AI AGENT ENCERRADO
echo ============================================================
echo.
pause
