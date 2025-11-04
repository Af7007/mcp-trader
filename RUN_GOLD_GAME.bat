@echo off
echo ================================================
echo GOLD LOSS ZERO GAME - PWA Gamificado
echo ================================================
echo.
echo Iniciando servidor web com o jogo...
echo.
echo Acesse: http://localhost:3000/game
echo.
echo Pressione Ctrl+C para parar
echo ================================================
echo.

uv run python run_game_server.py

pause
