@echo off
cls
echo ============================================================
echo    TESTE DE INTEGRACAO - TELEGRAM
echo ============================================================
echo.
echo  Este script testa se a integracao com Telegram esta
echo  funcionando corretamente.
echo.
echo  Antes de rodar, configure no .env:
echo    - TELEGRAM_BOT_TOKEN (obtenha em @BotFather)
echo    - TELEGRAM_CHAT_ID (seu canal ou grupo)
echo    - TELEGRAM_ENABLED=true
echo.
echo ============================================================
echo.

REM Verifica se esta no diretorio correto
if not exist "pyproject.toml" (
    echo ERRO: Execute este script a partir de C:\mcp-trader
    pause
    exit /b 1
)

echo Instalando dependencias (python-telegram-bot)...
uv pip install python-telegram-bot >nul 2>&1

echo.
echo Executando testes...
echo.

uv run python test_telegram.py

echo.
pause
