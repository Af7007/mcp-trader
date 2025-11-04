@echo off
echo ========================================
echo RESTART GAME SERVER - Clear Cache
echo ========================================
echo.

echo [1/3] Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul
echo [OK] Processes stopped
echo.

echo [2/3] Clearing browser cache files...
del /f /q "%TEMP%\*.*" >nul 2>&1
echo [OK] Temp files cleared
echo.

echo [3/3] Starting server with cache clear...
echo.
python run_game_server.py
