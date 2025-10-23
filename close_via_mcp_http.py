#!/usr/bin/env python3
"""
Fechar Posição via MCP MT5 Server (HTTP)
Conecta ao MCP Server rodando na porta 8000
"""

import logging
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL do MCP Server
MCP_URL = "http://localhost:8000"


def get_positions():
    """Obter posições abertas via MCP"""
    try:
        response = requests.post(
            f"{MCP_URL}/tools/positions_get",
            json={},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter posições: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Erro de conexão: {e}")
        return None


def close_position(ticket: int, comment: str = "Fechamento via script"):
    """Fechar posição via MCP"""
    try:
        response = requests.post(
            f"{MCP_URL}/tools/close_position",
            json={
                "ticket": ticket,
                "comment": comment
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao fechar posição: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro de conexão: {e}")
        return None


def close_all_positions(comment: str = "Limpeza via script"):
    """Fechar todas as posições via MCP"""
    try:
        response = requests.post(
            f"{MCP_URL}/tools/close_all_positions",
            json={
                "comment": comment
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao fechar posições: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erro de conexão: {e}")
        return None


def main():
    """Testar fechamento via MCP HTTP"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🧪 TESTE: Fechamento via MCP HTTP                    ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # 1. Verificar posições
    logger.info("=" * 60)
    logger.info("1️⃣  OBTENDO POSIÇÕES VIA MCP")
    logger.info("=" * 60)
    logger.info("")
    
    positions = get_positions()
    if not positions:
        logger.error("❌ Falha ao obter posições")
        return
    
    if isinstance(positions, list) and len(positions) == 0:
        logger.warning("⚠️  Nenhuma posição aberta!")
        return
    
    logger.info(f"✅ Posições obtidas:")
    if isinstance(positions, list):
        for pos in positions:
            logger.info(f"   • #{pos.get('ticket')}: {pos.get('symbol')} {pos.get('volume')}")
    else:
        logger.info(f"   {positions}")
    
    # 2. Fechar primeira posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  FECHANDO PRIMEIRA POSIÇÃO")
    logger.info("=" * 60)
    logger.info("")
    
    if isinstance(positions, list) and len(positions) > 0:
        ticket = positions[0].get('ticket')
        logger.info(f"Fechando posição #{ticket}...")
        
        result = close_position(ticket, "Teste via MCP HTTP")
        if result:
            logger.info(f"✅ Resultado:")
            logger.info(json.dumps(result, indent=2))
        else:
            logger.error("❌ Falha ao fechar posição")
    
    # 3. Opção: Fechar todas
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  FECHANDO TODAS AS POSIÇÕES")
    logger.info("=" * 60)
    logger.info("")
    
    logger.info("Fechando todas as posições...")
    results = close_all_positions("Limpeza via MCP HTTP")
    if results:
        logger.info(f"✅ Resultado:")
        logger.info(json.dumps(results, indent=2))
    else:
        logger.error("❌ Falha ao fechar posições")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTE CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
