#!/usr/bin/env python3
"""
Script para iniciar o MT5 MCP Server em modo HTTP
Permite conexões via HTTP na porta 8000
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def start_mt5_server_http():
    """Inicia o MT5 MCP Server em modo HTTP"""
    logger.info("🚀 Iniciando MT5 MCP Server em modo HTTP (porta 8000)...")
    
    try:
        # Usar fastmcp para iniciar o servidor em modo HTTP
        cmd = [
            sys.executable,
            "-m", "fastmcp",
            "run",
            "src.mcp_mt5.main:mcp",
            "--host", "127.0.0.1",
            "--port", "8000"
        ]
        
        logger.info(f"Comando: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info("✅ MT5 MCP Server iniciado")
        logger.info("📍 Listening on http://127.0.0.1:8000")
        logger.info("\n💡 Dica: Deixe este terminal aberto")
        logger.info("   Abra outro terminal para executar os testes\n")
        
        # Manter o processo rodando
        process.wait()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return False


if __name__ == "__main__":
    try:
        start_mt5_server_http()
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor parado pelo usuário")
        sys.exit(0)
