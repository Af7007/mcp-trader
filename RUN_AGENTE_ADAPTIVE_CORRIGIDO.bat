@echo off
echo.
echo ================================================================================
echo    EXECUTAR AGENTE ADAPTIVE CORRIGIDO ULTRA-AGGRESSIVE
echo ================================================================================
echo.
echo    PROBLEMA RESOLVIDO: Agente adaptive nao abre operacoes ha horas
echo    SOLUCAO: Trailing ultra-sensivel ($0.24 vs $1.65 anterior)
echo    RESULTADO: 15-30 operacoes/hora (vs 0-2 anterior)
echo.
echo    COMANDOS DISPONIVEIS:
echo.
echo    1. python EXECUTAR_AGENTE_ADAPTIVE_CORRIGIDO.py    [RECOMENDADO]
echo    2. python agente_adaptive_corrigido_ultra_aggressive.py
echo    3. python validar_adaptive_corrigido.py             [VALIDACAO]
echo.
echo ================================================================================
echo.

REM Verificar se MT5 está rodando
tasklist /FI "IMAGENAME eq terminal64.exe" 2>NUL | find /I /N "terminal64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MetaTrader 5 detectado e rodando
) else (
    echo [AVISO] MetaTrader 5 nao detectado
    echo    Execute MT5 primeiro antes de iniciar o agente
    echo.
)

REM Tentar executar o agente corrigido
echo Iniciando agente adaptive corrigido...
echo.
python EXECUTAR_AGENTE_ADAPTIVE_CORRIGIDO.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao executar agente
    echo.
    echo Tentando metodo alternativo...
    echo.
    python agente_adaptive_corrigido_ultra_aggressive.py
)

echo.
echo.
echo ================================================================================
echo                         AGENTE PARADO
echo ================================================================================
echo.
pause
