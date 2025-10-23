#!/usr/bin/env python3
"""
Script para iniciar MT5 MCP Server em modo HTTP com wrapper ASGI correto
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FastMCPASGI:
    """Wrapper ASGI para FastMCP"""
    
    def __init__(self, mcp):
        self.mcp = mcp
    
    async def __call__(self, scope, receive, send):
        """Handle ASGI requests"""
        if scope["type"] == "http":
            # Rotear para o endpoint MCP
            if scope["path"] == "/mcp":
                # Usar o FastMCP como SSE endpoint
                await self.handle_mcp(scope, receive, send)
            else:
                # Retornar 404
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })
        else:
            await send({
                "type": "http.response.start",
                "status": 400,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"Bad Request",
            })
    
    async def handle_mcp(self, scope, receive, send):
        """Handle MCP requests"""
        try:
            # Ler o corpo da requisição
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if not message.get("more_body", False):
                        break
                elif message["type"] == "http.disconnect":
                    return
            
            # Processar requisição MCP
            import json
            request_data = json.loads(body.decode())
            
            # Chamar ferramenta MCP
            tool_name = request_data.get("params", {}).get("name")
            arguments = request_data.get("params", {}).get("arguments", {})
            
            logger.info(f"Chamando ferramenta MCP: {tool_name}")
            
            # Executar ferramenta
            result = await self.mcp.call_tool(tool_name, arguments)
            
            # Retornar resultado
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": result
            }
            
            response_body = json.dumps(response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar MCP: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            response_body = json.dumps(error_response).encode()
            
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })


def main():
    """Inicia o servidor"""
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     Iniciando MT5 MCP Server em modo HTTP (porta 8000)    ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")

    try:
        # Importar FastMCP
        from mcp_mt5.main import mcp
        
        logger.info("✅ Módulo MT5 MCP importado com sucesso")
        logger.info("")
        logger.info("🚀 Iniciando servidor...")
        logger.info("📍 Listening on http://127.0.0.1:8000")
        logger.info("")
        logger.info("💡 Dica: Deixe este terminal aberto")
        logger.info("   Abra outro terminal para executar os testes")
        logger.info("")
        
        # Usar uvicorn com wrapper ASGI
        import uvicorn
        
        # Criar aplicação ASGI
        app = FastMCPASGI(mcp)
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar: {e}")
        logger.info("")
        logger.info("Solução: Instale uvicorn")
        logger.info("  pip install uvicorn")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor parado pelo usuário")
        sys.exit(0)
