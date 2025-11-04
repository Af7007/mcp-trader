@echo off
echo ========================================
echo STOP AND START GAME SERVER
echo ========================================
echo.

echo [1/2] Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul
echo [OK] Python processes stopped
echo.

echo [2/2] Starting game server...
echo.
python run_game_server.py
