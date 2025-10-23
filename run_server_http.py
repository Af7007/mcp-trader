#!/usr/bin/env python3
"""
Script simples para iniciar MT5 MCP Server em modo HTTP
Usa FastMCP com uvicorn
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
        
        # Usar FastMCP com uvicorn
        import uvicorn
        
        # FastMCP expõe um app ASGI
        app = mcp.app if hasattr(mcp, 'app') else mcp
        
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
