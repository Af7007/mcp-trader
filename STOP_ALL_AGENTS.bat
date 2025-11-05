@echo off
cls
echo ============================================================
echo    PARAR TODOS OS AGENTES
echo ============================================================
echo.
echo  Este script vai parar TODOS os agentes em execucao
echo.
echo ============================================================
echo.
echo Parando...
echo Parando todos os processos Python...
echo.

taskkill /F /IM python.exe 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ Todos os agentes foram parados!
) else (
    echo ⚠️  Nenhum agente em execucao encontrado.
)

echo.
echo ============================================================
echo.
pause
