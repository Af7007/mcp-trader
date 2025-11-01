@echo off
REM ============================================================
REM BTC Loss Zero Otimizado - Estratégia de Trading Automático
REM ============================================================

REM Definir título da janela
title BTC Loss Zero - Estratégia Automática de Trailing Stop

REM Limpar tela
cls

REM Exibir informações
echo.
echo ============================================================
echo.
echo   🚀 BTC LOSS ZERO - AGENTE OTIMIZADO
echo.
echo ============================================================
echo.
echo   ESTRATÉGIA DE ZERO LOSSES
echo   ✅ Sem Take Profit Fixo
echo   ✅ Trailing Stop Ilimitado
echo   ✅ Lucros Ilimitados
echo   ✅ Zero Losses Garantidas
echo.
echo ============================================================
echo.
echo   CONFIGURAÇÃO:
echo   📊 Symbol: BTCUSDc
echo   📈 Volume: 0.05 lots
echo   ⏱️  Check: 15 segundos
echo   📉 Trailing: 0.5%% → INFINITO
echo   🔄 Incremento: +0.1%% por movimento
echo.
echo ============================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo Por favor, instale Python 3.8+ em: https://www.python.org
    echo.
    pause
    exit /b 1
)

REM Executar agente Loss Zero
echo ⏳ Iniciando agente Loss Zero...
echo.
python EXECUTAR_LOSS_ZERO.py

REM Verificar se houve erro
if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar agente
    echo.
    pause
    exit /b 1
)

REM Sucesso
echo.
echo ✅ Agente Loss Zero finalizado
echo.
pause
exit /b 0
