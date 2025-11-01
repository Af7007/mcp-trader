@echo off
cls
echo ============================================================
echo    VERIFICAR TRADES SALVOS NO BANCO DE DADOS
echo ============================================================
echo.

python check_database.py

echo.
echo ============================================================
pause
