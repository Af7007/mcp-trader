#!/usr/bin/env python3
"""
Teste de Fechamento de Ordem
Diagnóstico do problema de fechamento
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
    """Testar fechamento de ordem"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🧪 TESTE: Fechamento de Ordem                    ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # 1. Verificar posições abertas
    logger.info("=" * 60)
    logger.info("1️⃣  VERIFICANDO POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = mt5.positions_get()
    if not positions:
        logger.warning("⚠️  Nenhuma posição aberta!")
        mt5.shutdown()
        return
    
    logger.info(f"✅ Encontradas {len(positions)} posição(ões):")
    for pos in positions:
        logger.info(f"\n   Ticket: {pos.ticket}")
        logger.info(f"   Símbolo: {pos.symbol}")
        logger.info(f"   Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
        logger.info(f"   Volume: {pos.volume}")
        logger.info(f"   Preço Abertura: {pos.price_open:.5f}")
        logger.info(f"   Preço Atual: {pos.price_current:.5f}")
        logger.info(f"   Lucro/Prejuízo: ${pos.profit:.2f}")
    
    # 2. Testar fechamento
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  TESTANDO FECHAMENTO")
    logger.info("=" * 60)
    
    pos = positions[0]
    logger.info(f"\nFechando posição #{pos.ticket}...")
    
    # Obter preço atual
    tick = mt5.symbol_info_tick(pos.symbol)
    if not tick:
        logger.error("❌ Não conseguiu obter preço")
        mt5.shutdown()
        return
    
    logger.info(f"Preço Bid: {tick.bid:.5f}")
    logger.info(f"Preço Ask: {tick.ask:.5f}")
    
    # Determinar tipo de ordem para fechar
    close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
    close_price = tick.bid if pos.type == 0 else tick.ask
    
    logger.info(f"\nTipo atual: {'BUY' if pos.type == 0 else 'SELL'}")
    logger.info(f"Tipo fechamento: {'SELL' if pos.type == 0 else 'BUY'}")
    logger.info(f"Preço fechamento: {close_price:.5f}")
    
    # Criar requisição
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "type": close_type,
        "price": close_price,
        "deviation": 100,
        "magic": 0,
        "comment": "Teste de fechamento",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    logger.info(f"\nRequisição:")
    for key, value in request.items():
        logger.info(f"  {key}: {value}")
    
    # Enviar ordem
    logger.info(f"\nEnviando ordem...")
    result = mt5.order_send(request)
    
    if result is None:
        logger.error("❌ order_send retornou None")
    else:
        logger.info(f"✅ Resultado:")
        logger.info(f"   Retcode: {result.retcode}")
        logger.info(f"   Comment: {result.comment}")
        logger.info(f"   Order: {result.order}")
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"\n✅ SUCESSO! Posição fechada!")
        elif result.retcode == mt5.TRADE_RETCODE_PLACED:
            logger.warning(f"\n⚠️  Ordem colocada (pendente)")
        else:
            logger.error(f"\n❌ FALHA! Retcode: {result.retcode}")
    
    # 3. Verificar posições após fechamento
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  VERIFICANDO POSIÇÕES APÓS FECHAMENTO")
    logger.info("=" * 60)
    
    positions_after = mt5.positions_get()
    if positions_after:
        logger.info(f"✅ Ainda há {len(positions_after)} posição(ões) abertas")
        for pos in positions_after:
            logger.info(f"   • Ticket: {pos.ticket}, Símbolo: {pos.symbol}")
    else:
        logger.info("✅ Nenhuma posição aberta")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTE CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
