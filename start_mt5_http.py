#!/usr/bin/env python3
"""
Inicia o MT5 MCP Server em modo HTTP na porta 8000
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Iniciando MT5 MCP Server em modo HTTP")
    logger.info("=" * 60)

    # Set environment variables for HTTP mode
    os.environ['MT5_MCP_TRANSPORT'] = 'http'
    os.environ['MT5_MCP_HOST'] = '127.0.0.1'
    os.environ['MT5_MCP_PORT'] = '8000'

    logger.info(f"📡 Transport: HTTP")
    logger.info(f"🌐 Host: 127.0.0.1")
    logger.info(f"🔌 Port: 8000")
    logger.info("")
    logger.info("⚠️  IMPORTANTE: Certifique-se que o MT5 Terminal está aberto!")
    logger.info("=" * 60)

    try:
        # Import and run the MCP server
        from mcp_mt5 import main
        main()
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar MT5 MCP Server: {e}", exc_info=True)
        sys.exit(1)
