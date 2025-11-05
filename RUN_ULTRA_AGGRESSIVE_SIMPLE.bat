@echo off
echo ============================================================
echo    GOLD ULTRA-AGGRESSIVE - EXECUCAO DIRETA
echo ============================================================
echo.
echo Executando: python gold_ultra_agressivo_teste.py
echo.
echo Configuracao:
echo   - Trailing ativa: ~$1.50 (vs $5+ original)
echo   - Volume: 0.05 (vs 0.01 original)
echo   - Check: 5s (vs 15s original)
echo   - SEM auto-learning (configuracoes fixas)
echo.
echo Para PARAR: Ctrl+C
echo ============================================================
echo.

REM Verifica se o arquivo Python existe
if not exist "gold_ultra_agressivo_teste.py" (
    echo ERRO: Arquivo gold_ultra_agressivo_teste.py nao encontrado!
    pause
    exit /b 1
)

REM Executa o script Python diretamente
python gold_ultra_agressivo_teste.py

echo.
echo ============================================================
echo    AGENTE ULTRA-AGGRESSIVE ENCERRADO
echo ============================================================
pause
