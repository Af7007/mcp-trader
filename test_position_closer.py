#!/usr/bin/env python3
"""
Teste do MT5PositionCloser
Demonstra como usar a classe para fechar posições
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))
from core.mt5_position_closer import MT5PositionCloser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Teste do position closer"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🧪 TESTE: MT5 Position Closer                    ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # Criar position closer
    closer = MT5PositionCloser(max_retries=3, retry_delay=0.5)
    
    # Verificar posições abertas
    positions = mt5.positions_get()
    
    if not positions:
        logger.info("✅ Nenhuma posição aberta para testar")
        mt5.shutdown()
        return
    
    logger.info(f"📊 Encontradas {len(positions)} posição(ões)")
    logger.info("")
    
    # Teste 1: Fechar posição específica
    if positions:
        logger.info("=" * 60)
        logger.info("TESTE 1: Fechar posição específica")
        logger.info("=" * 60)
        
        pos = positions[0]
        result = closer.close_position(pos.ticket, "Teste do position closer")
        
        logger.info("")
        logger.info(f"Resultado:")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Message: {result['message']}")
        logger.info(f"  Order: {result['order']}")
    
    # Teste 2: Fechar todas as posições
    logger.info("")
    logger.info("=" * 60)
    logger.info("TESTE 2: Fechar todas as posições")
    logger.info("=" * 60)
    
    result = closer.close_all_positions("Teste - fechar todas")
    
    logger.info("")
    logger.info(f"Resultado:")
    logger.info(f"  Total: {result['total']}")
    logger.info(f"  Fechadas: {result['closed']}")
    logger.info(f"  Falhadas: {result['failed']}")
    
    mt5.shutdown()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ TESTE CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
