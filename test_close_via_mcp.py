#!/usr/bin/env python3
"""
Teste de Fechamento via MCP MT5 Server
Usa a ferramenta close_position do MCP
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))
from mcp_mt5.main import close_position, positions_get, close_all_positions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Testar fechamento via MCP"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🧪 TESTE: Fechamento via MCP MT5 Server              ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # 1. Verificar posições
    logger.info("=" * 60)
    logger.info("1️⃣  POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = positions_get()
    if not positions:
        logger.warning("⚠️  Nenhuma posição aberta!")
        mt5.shutdown()
        return
    
    logger.info(f"✅ {len(positions)} posição(ões):")
    for pos in positions:
        logger.info(f"   • #{pos.ticket}: {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume}")
    
    # 2. Testar fechamento da primeira posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  FECHANDO PRIMEIRA POSIÇÃO VIA MCP")
    logger.info("=" * 60)
    logger.info("")
    
    pos = positions[0]
    logger.info(f"Fechando posição #{pos.ticket}...")
    
    try:
        result = close_position(pos.ticket, comment="Teste via MCP")
        
        logger.info(f"\n✅ Resultado:")
        logger.info(f"   Retcode: {result.retcode}")
        logger.info(f"   Comment: {result.comment}")
        logger.info(f"   Order: {result.order}")
        logger.info(f"   Deal: {result.deal}")
        
        if result.retcode == 10009:  # TRADE_RETCODE_DONE
            logger.info(f"\n✅ SUCESSO! Posição fechada!")
        else:
            logger.warning(f"\n⚠️  Retcode: {result.retcode}")
    
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    
    # 3. Verificar posições após fechamento
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  POSIÇÕES APÓS FECHAMENTO")
    logger.info("=" * 60)
    
    positions_after = positions_get()
    if positions_after:
        logger.info(f"✅ Ainda há {len(positions_after)} posição(ões):")
        for pos in positions_after:
            logger.info(f"   • #{pos.ticket}: {pos.symbol}")
    else:
        logger.info("✅ Nenhuma posição aberta")
    
    # 4. Opção: Fechar todas as posições
    logger.info("\n" + "=" * 60)
    logger.info("4️⃣  FECHANDO TODAS AS POSIÇÕES VIA MCP")
    logger.info("=" * 60)
    logger.info("")
    
    try:
        results = close_all_positions(comment="Limpeza via MCP")
        
        logger.info(f"✅ {len(results)} posição(ões) fechada(s):")
        for result in results:
            logger.info(f"   • Order: {result.order}, Retcode: {result.retcode}")
    
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    
    # 5. Verificar resultado final
    logger.info("\n" + "=" * 60)
    logger.info("5️⃣  RESULTADO FINAL")
    logger.info("=" * 60)
    
    positions_final = positions_get()
    if positions_final:
        logger.warning(f"⚠️  Ainda há {len(positions_final)} posição(ões) abertas")
    else:
        logger.info("✅ Todas as posições foram fechadas!")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTE CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
