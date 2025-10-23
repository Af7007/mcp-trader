@echo off
echo ============================================================
echo    PARANDO TODOS OS SERVICOS DO TRADING CHATBOT
echo ============================================================
echo.

echo Encerrando todos os processos Python...
taskkill /F /IM python.exe 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ✓ Todos os servicos foram encerrados com sucesso!
) else (
    echo.
    echo Nenhum servico Python estava rodando.
)

echo.
echo ============================================================
timeout /t 3
