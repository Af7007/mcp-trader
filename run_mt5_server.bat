@echo off
REM Script para iniciar MT5 MCP Server em modo HTTP
REM Usa FastMCP CLI com a configuração do fastmcp.json

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     Iniciando MT5 MCP Server em modo HTTP (porta 8000)    ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Ativar ambiente virtual
call .venv\Scripts\activate.bat

REM Iniciar servidor com FastMCP
echo Iniciando FastMCP server...
python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000

pause
