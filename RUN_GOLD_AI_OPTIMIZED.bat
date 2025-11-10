@echo off
cls
echo ============================================================
echo    GOLD AI AGENT - OTIMIZADO PARA MERCADO CHOPPY
echo ============================================================
echo.
echo  ATENCAO: Este agente opera com DINHEIRO REAL!
echo.
echo  Configuracao OTIMIZADA:
echo    - Simbolo: XAUUSDc (Ouro)
echo    - Volume: 0.02 lots
echo    - SL Reduzido: $2.50 (de $5.00 - menos risco)
echo    - Trailing: Ativa em $2.00, protege $1.50, sobe $1.00 a cada $2.00
echo    - IA: Ollama Local (llama3.2:1b)
echo    - FILTROS ADICIONAIS:
echo      * Momentum minimo: 0.5%% (evita mercado choppy)
echo      * Volatilidade maxima: $6.00 (evita erratico)
echo      * Validacao M5: OBRIGATORIA (trend following)
echo.
echo  Melhorias vs versao anterior:
echo    - SL 50%% menor ($2.50 vs $5.00) = menos perdas
echo    - Trailing mais largo ($2.00 vs $1.50) = mais espaco
echo    - Filtro momentum evita mercados choppy
echo    - Filtro volatilidade evita mercados erraticos
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
echo    INICIANDO GOLD AI AGENT - VERSAO OTIMIZADA
echo ============================================================
echo.
echo IA: Ollama (Local) - Sem custos de API
echo Estrategia: IA + Trailing Stop + Filtros Anti-Choppy
echo.
echo Para PARAR, pressione Ctrl+C
echo.
echo ============================================================
echo.

timeout /t 3 /nobreak >nul

REM Executar agente com parametros otimizados
title GOLD_AI_AGENT - XAUUSDc (OTIMIZADO)
uv run python src\agents\gold_ai_agent_optimized.py ^
    --symbol XAUUSDc ^
    --volume 0.02 ^
    --fixed-sl-dollars 2.5 ^
    --trailing-activation 2.0 ^
    --trailing-distance 1.5 ^
    --min-momentum 0.5 ^
    --max-volatility 6.0 ^
    --model-name llama3.2:1b

echo.
echo ============================================================
echo    GOLD AI AGENT ENCERRADO
echo ============================================================
echo.
pause
