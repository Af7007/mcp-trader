#!/usr/bin/env pwsh
<#
Script para iniciar MT5 MCP Server em modo HTTP
Usa FastMCP CLI com a configuração correta
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║     Iniciando MT5 MCP Server em modo HTTP (porta 8000)    ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Ativar ambiente virtual
Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "✅ Ambiente virtual ativado" -ForegroundColor Green
Write-Host ""

# Iniciar servidor
Write-Host "🚀 Iniciando MT5 MCP Server..." -ForegroundColor Yellow
Write-Host "📍 Listening on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Dica: Deixe este terminal aberto" -ForegroundColor Cyan
Write-Host "   Abra outro terminal para executar os testes" -ForegroundColor Cyan
Write-Host ""

python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
