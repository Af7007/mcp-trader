#!/usr/bin/env python3
"""
Fechar todas as posições abertas no MT5
Útil para limpeza e sincronização
"""

import logging
import MetaTrader5 as mt5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_all_positions():
    """Fechar todas as posições abertas"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🔒 FECHANDO TODAS AS POSIÇÕES ABERTAS            ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return False
    
    # Obter posições abertas
    positions = mt5.positions_get()
    
    if not positions:
        logger.info("✅ Nenhuma posição aberta")
        mt5.shutdown()
        return True
    
    logger.info(f"📊 Encontradas {len(positions)} posição(ões) aberta(s)")
    logger.info("")
    
    closed_count = 0
    failed_count = 0
    
    for pos in positions:
        logger.info(f"Fechando posição #{pos.ticket}...")
        logger.info(f"  Símbolo: {pos.symbol}")
        logger.info(f"  Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
        logger.info(f"  Volume: {pos.volume}")
        logger.info(f"  Preço Atual: {pos.price_current:.5f}")
        
        # Preparar requisição para fechar
        symbol = pos.symbol
        volume = pos.volume
        order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
        
        # Obter preço atual
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            logger.error(f"  ❌ Não conseguiu obter preço de {symbol}")
            failed_count += 1
            continue
        
        price = tick.bid if pos.type == 0 else tick.ask
        
        # Criar requisição de fechamento
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": 10,
            "magic": 0,
            "comment": "Fechamento via script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Enviar ordem
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"  ✅ Posição fechada!")
            logger.info(f"     Preço de fechamento: {price:.5f}")
            logger.info(f"     Novo ticket: {result.order}")
            closed_count += 1
        else:
            logger.error(f"  ❌ Falha ao fechar: {result.comment}")
            failed_count += 1
        
        logger.info("")
    
    mt5.shutdown()
    
    # Resumo
    logger.info("=" * 60)
    logger.info("📊 RESUMO")
    logger.info("=" * 60)
    logger.info(f"Total de posições: {len(positions)}")
    logger.info(f"Fechadas com sucesso: {closed_count}")
    logger.info(f"Falhadas: {failed_count}")
    logger.info("")
    
    if failed_count == 0:
        logger.info("✅ Todas as posições foram fechadas!")
    else:
        logger.warning(f"⚠️  {failed_count} posição(ões) falharam")
    
    return failed_count == 0


if __name__ == "__main__":
    success = close_all_positions()
    exit(0 if success else 1)
