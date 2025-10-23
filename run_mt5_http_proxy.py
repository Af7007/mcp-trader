#!/usr/bin/env python3
"""
Servidor HTTP Proxy para MT5 MCP
Funciona como intermediário entre HTTP e o servidor STDIO MT5 MCP
"""

import sys
import os
import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Criar app FastAPI
app = FastAPI(title="MT5 MCP HTTP Proxy")

# Variável global para armazenar o processo do servidor MCP
mcp_process = None


async def call_mcp_tool(tool_name: str, arguments: dict) -> Any:
    """Chama uma ferramenta MCP via STDIO"""
    try:
        # Importar o MCP
        from mcp_mt5.main import mcp
        
        # Chamar ferramenta diretamente
        logger.info(f"Chamando ferramenta: {tool_name}")
        
        # Obter a ferramenta
        tool = mcp._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Ferramenta '{tool_name}' não encontrada")
        
        # Executar ferramenta
        result = tool.fn(**arguments)
        
        logger.info(f"Resultado: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao chamar ferramenta: {e}", exc_info=True)
        raise


@app.post("/mcp")
async def mcp_endpoint(request: dict) -> dict:
    """Endpoint MCP HTTP"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            result = await call_mcp_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        else:
            raise ValueError(f"Método '{method}' não suportado")
            
    except Exception as e:
        logger.error(f"Erro: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


@app.get("/health")
async def health():
    """Health check"""
    try:
        from mcp_mt5.main import mcp
        result = await call_mcp_tool("health", {})
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def main():
    """Inicia o servidor"""
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     Iniciando MT5 MCP HTTP Proxy (porta 8000)             ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    logger.info("✅ Servidor HTTP Proxy iniciado")
    logger.info("📍 Listening on http://127.0.0.1:8000")
    logger.info("")
    logger.info("💡 Dica: Deixe este terminal aberto")
    logger.info("   Abra outro terminal para executar os testes")
    logger.info("")
    
    # Iniciar servidor FastAPI
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor parado pelo usuário")
        sys.exit(0)
