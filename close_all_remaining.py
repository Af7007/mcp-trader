#!/usr/bin/env python3
"""Encerrar TODAS as posições abertas"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_all():
    """Encerrar todas as posições"""
    
    logger.info("\n🔒 ENCERRANDO TODAS AS POSIÇÕES\n")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    positions = mt5.positions_get()
    if not positions:
        logger.info("✅ Nenhuma posição aberta")
        mt5.shutdown()
        return
    
    logger.info(f"📊 {len(positions)} posição(ões) para encerrar:\n")
    
    closed = 0
    for pos in positions:
        logger.info(f"Encerrando #{pos.ticket} ({pos.symbol} {'BUY' if pos.type == 0 else 'SELL'})...")
        
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            logger.error(f"   ❌ Erro ao obter preço")
            continue
        
        order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
        price = tick.bid if pos.type == 0 else tick.ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 0,
            "comment": "Limpeza final",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"   ✅ Encerrada! Novo ticket: {result.order}\n")
            closed += 1
        else:
            logger.error(f"   ❌ Falha (retcode: {result.retcode if result else 'None'})\n")
    
    # Verificar resultado
    positions_after = mt5.positions_get()
    logger.info("=" * 60)
    logger.info(f"✅ Encerrradas: {closed}/{len(positions)}")
    logger.info(f"📊 Posições restantes: {len(positions_after) if positions_after else 0}")
    
    if not positions_after:
        logger.info("\n🎉 TODAS AS POSIÇÕES FORAM ENCERRRADAS!")
    
    mt5.shutdown()


if __name__ == "__main__":
    close_all()
