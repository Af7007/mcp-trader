#!/usr/bin/env python3
"""
Fechar posições abertas - VERSÃO CORRIGIDA
Usa close_position_by_ticket em vez de abrir nova posição
"""

import logging
import MetaTrader5 as mt5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_position_by_ticket(ticket):
    """Fechar posição específica pelo ticket"""
    
    # Obter posição
    position = None
    positions = mt5.positions_get()
    
    for pos in positions:
        if pos.ticket == ticket:
            position = pos
            break
    
    if not position:
        logger.error(f"❌ Posição {ticket} não encontrada")
        return False
    
    logger.info(f"Fechando posição #{ticket}...")
    logger.info(f"  Símbolo: {position.symbol}")
    logger.info(f"  Tipo: {'BUY' if position.type == 0 else 'SELL'}")
    logger.info(f"  Volume: {position.volume}")
    
    # Obter preço atual
    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        logger.error(f"❌ Não conseguiu obter preço")
        return False
    
    # Determinar tipo de ordem para fechar
    # Se é BUY, vender; se é SELL, comprar
    close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
    close_price = tick.bid if position.type == 0 else tick.ask
    
    logger.info(f"  Preço de fechamento: {close_price:.5f}")
    
    # Criar requisição de fechamento
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": close_type,
        "price": close_price,
        "position": ticket,  # IMPORTANTE: especificar ticket da posição
        "deviation": 20,
        "magic": 0,
        "comment": f"Fechamento da posição {ticket}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Enviar ordem
    result = mt5.order_send(request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"  ✅ Posição fechada!")
        logger.info(f"     Novo ticket: {result.order}")
        return True
    else:
        logger.error(f"  ❌ Falha: {result.comment}")
        logger.error(f"     Retcode: {result.retcode}")
        return False


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
    
    # Fechar cada posição
    for pos in positions:
        if close_position_by_ticket(pos.ticket):
            closed_count += 1
        else:
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
