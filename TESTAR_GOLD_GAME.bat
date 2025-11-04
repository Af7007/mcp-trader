@echo off
echo ================================================
echo TESTE - Gold Loss Zero Game PWA
echo ================================================
echo.
echo Este script testa se tudo esta configurado
echo corretamente para rodar o Gold Loss Zero Game.
echo.
echo ================================================
echo.

echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)
echo OK
echo.

echo [2/5] Verificando MT5 MCP Client...
python -c "from core.mt5_direct_client import get_mt5_client; print('MT5 Client OK')"
if %errorlevel% neq 0 (
    echo ERRO: MT5 Client nao encontrado!
    pause
    exit /b 1
)
echo.

echo [3/5] Verificando Flask...
python -c "import flask; print(f'Flask {flask.__version__} OK')"
if %errorlevel% neq 0 (
    echo ERRO: Flask nao instalado!
    echo Execute: uv sync
    pause
    exit /b 1
)
echo.

echo [4/5] Verificando estrutura de arquivos...
if not exist "src\web\templates\game.html" (
    echo ERRO: game.html nao encontrado!
    pause
    exit /b 1
)
if not exist "src\web\static\css\game.css" (
    echo ERRO: game.css nao encontrado!
    pause
    exit /b 1
)
if not exist "src\web\static\js\game.js" (
    echo ERRO: game.js nao encontrado!
    pause
    exit /b 1
)
if not exist "src\web\game_api.py" (
    echo ERRO: game_api.py nao encontrado!
    pause
    exit /b 1
)
echo OK - Todos os arquivos presentes
echo.

echo [5/5] Verificando diretorios de assets...
if not exist "src\web\static\sounds" (
    echo AVISO: Pasta sounds/ nao existe, criando...
    mkdir "src\web\static\sounds"
)
if not exist "src\web\static\icons" (
    echo AVISO: Pasta icons/ nao existe, criando...
    mkdir "src\web\static\icons"
)
echo OK
echo.

echo ================================================
echo TUDO PRONTO!
echo ================================================
echo.
echo O Gold Loss Zero Game esta configurado corretamente.
echo.
echo Para iniciar:
echo   1. Certifique-se que MT5 esta aberto e logado
echo   2. Execute: RUN_GOLD_GAME.bat
echo   3. Acesse: http://localhost:3000/game
echo.
echo OPCIONAL (para melhor experiencia):
echo   - Adicione sons em: src\web\static\sounds\
echo   - Adicione icones em: src\web\static\icons\
echo   - Veja instrucoes nos arquivos README.md
echo.
echo ================================================
pause
