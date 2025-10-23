#!/usr/bin/env python3
"""
Teste de Fechamento Correto
Usando o método apropriado do MT5
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_position_correct(ticket: int) -> bool:
    """Fechar posição usando o método correto"""
    
    logger.info(f"🔒 Fechando posição #{ticket}...")
    
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
    
    logger.info(f"   Símbolo: {position.symbol}")
    logger.info(f"   Tipo: {'BUY' if position.type == 0 else 'SELL'}")
    logger.info(f"   Volume: {position.volume}")
    
    # Obter preço
    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        logger.error("❌ Não conseguiu obter preço")
        return False
    
    # Tipo de ordem para fechar
    close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
    close_price = tick.bid if position.type == 0 else tick.ask
    
    logger.info(f"   Preço fechamento: {close_price:.5f}")
    
    # MÉTODO CORRETO: Usar TRADE_ACTION_DEAL com tipo oposto
    # MAS: Não enviar como nova ordem, e sim como fechamento
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": close_type,
        "price": close_price,
        "deviation": 100,
        "magic": 0,
        "comment": f"Fechamento da posição {ticket}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  # Fill or Kill
    }
    
    logger.info(f"\n   Enviando ordem de fechamento...")
    result = mt5.order_send(request)
    
    if result is None:
        logger.error("❌ order_send retornou None")
        return False
    
    logger.info(f"   Retcode: {result.retcode}")
    logger.info(f"   Comment: {result.comment}")
    logger.info(f"   Order: {result.order}")
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"   ✅ Posição fechada com sucesso!")
        return True
    else:
        logger.error(f"   ❌ Falha ao fechar (retcode: {result.retcode})")
        return False


def main():
    """Testar fechamento correto"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🧪 TESTE: Fechamento Correto de Ordem                ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # Verificar posições
    logger.info("=" * 60)
    logger.info("1️⃣  POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = mt5.positions_get()
    if not positions:
        logger.warning("⚠️  Nenhuma posição aberta!")
        mt5.shutdown()
        return
    
    logger.info(f"✅ {len(positions)} posição(ões):")
    for pos in positions:
        logger.info(f"   • #{pos.ticket}: {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume}")
    
    # Testar fechamento da primeira posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  TESTANDO FECHAMENTO")
    logger.info("=" * 60)
    logger.info("")
    
    pos = positions[0]
    success = close_position_correct(pos.ticket)
    
    # Verificar resultado
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  POSIÇÕES APÓS FECHAMENTO")
    logger.info("=" * 60)
    
    positions_after = mt5.positions_get()
    if positions_after:
        logger.info(f"✅ Ainda há {len(positions_after)} posição(ões):")
        for pos in positions_after:
            logger.info(f"   • #{pos.ticket}: {pos.symbol}")
    else:
        logger.info("✅ Nenhuma posição aberta")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✅ FECHAMENTO REALIZADO COM SUCESSO!")
    else:
        logger.info("❌ FALHA AO FECHAR POSIÇÃO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
