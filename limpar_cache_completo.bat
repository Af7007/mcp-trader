@echo off
echo ===============================
echo LIMPEZA COMPLETA DE CACHE
echo ===============================
echo.

echo 1. Limpando cache DNS...
ipconfig /flushdns

echo.
echo 2. Parando servidor web se ativo...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

echo.
echo 3. Limpando cache de navegador (Chrome)...
taskkill /f /im chrome.exe 2>nul
rmdir /s /q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache" 2>nul

echo.
echo 4. Limpando cache do Flask/Python...
del /s /q "__pycache__\*.pyc" 2>nul
del /s /q "src\web\__pycache__\*.pyc" 2>nul
rmdir /s /q "__pycache__" 2>nul
rmdir /s /q "src\web\__pycache__" 2>nul

echo.
echo 5. Limpeza concluida!
echo.
echo AGORA REINICIE O SERVIDOR:
echo python run_game_server.py
echo.
pause
