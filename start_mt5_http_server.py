#!/usr/bin/env python3
"""
Script para iniciar MT5 MCP Server em modo HTTP
Contorna o problema do fastmcp não ter __main__
"""

import sys
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Inicia o servidor MT5 MCP em modo HTTP"""
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     Iniciando MT5 MCP Server em modo HTTP (porta 8000)    ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")

    try:
        from fastmcp import FastMCP
        from mcp_mt5.main import mcp
        
        logger.info("✅ Módulos importados com sucesso")
        logger.info("")
        logger.info("🚀 Iniciando servidor FastMCP...")
        logger.info("📍 Listening on http://127.0.0.1:8000")
        logger.info("")
        logger.info("💡 Dica: Deixe este terminal aberto")
        logger.info("   Abra outro terminal para executar os testes")
        logger.info("")
        
        # Iniciar servidor em modo HTTP
        # FastMCP detecta automaticamente a porta via variável de ambiente
        import os
        os.environ["FASTMCP_HOST"] = "127.0.0.1"
        os.environ["FASTMCP_PORT"] = "8000"
        
        # Usar uvicorn para servir o FastMCP em HTTP
        import uvicorn
        from fastmcp.server.asgi import ASGIServer
        
        # Criar aplicação ASGI
        app = ASGIServer(mcp)
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        logger.info("")
        logger.info("Solução: Instale as dependências")
        logger.info("  pip install uvicorn")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor parado pelo usuário")
        sys.exit(0)
