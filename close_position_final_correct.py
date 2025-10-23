#!/usr/bin/env python3
"""
Fechar Posição - VERSÃO FINAL CORRIGIDA
Usa "position": ticket para indicar qual posição fechar
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_position_correct(ticket: int) -> bool:
    """
    Fechar posição CORRETAMENTE
    
    A chave é usar "position": ticket na requisição
    para indicar qual posição está sendo fechada
    """
    
    logger.info(f"🔒 Fechando posição #{ticket}...")
    
    # 1. Obter posição
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
    
    # 2. Obter preço
    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        logger.error(f"❌ Não conseguiu obter preço")
        return False
    
    # 3. Determinar tipo oposto
    if position.type == mt5.POSITION_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    
    logger.info(f"   Tipo fechamento: {'SELL' if position.type == 0 else 'BUY'} @ {price:.5f}")
    
    # 4. IMPORTANTE: Usar "position": ticket para fechar a posição específica
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": order_type,
        "price": price,
        "position": ticket,  # ⭐ CHAVE: Especificar qual posição fechar
        "deviation": 10,
        "magic": 0,
        "comment": "Fechamento correto",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    logger.info(f"\n   Enviando order_send com position={ticket}...")
    
    # 5. Enviar ordem
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
        logger.error(f"   ❌ Falha (retcode: {result.retcode})")
        return False


def main():
    """Testar fechamento correto"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🔒 FECHAR POSIÇÃO - VERSÃO FINAL CORRIGIDA           ║")
    logger.info("║     Usando: \"position\": ticket                           ║")
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
    
    positions = mt5.positions_get()
    if not positions:
        logger.info("✅ Nenhuma posição aberta")
        mt5.shutdown()
        return
    
    logger.info(f"📊 {len(positions)} posição(ões):\n")
    for pos in positions:
        logger.info(f"   • #{pos.ticket}: {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume}")
    
    # 2. Fechar cada posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  ENCERRANDO POSIÇÕES")
    logger.info("=" * 60)
    logger.info("")
    
    closed = 0
    for pos in positions:
        if close_position_correct(pos.ticket):
            closed += 1
        logger.info("")
    
    # 3. Verificar resultado
    logger.info("=" * 60)
    logger.info("3️⃣  RESULTADO FINAL")
    logger.info("=" * 60)
    
    positions_after = mt5.positions_get()
    
    logger.info(f"\n📊 Resumo:")
    logger.info(f"   Total inicial: {len(positions)}")
    logger.info(f"   Encerrradas: {closed}")
    logger.info(f"   Posições restantes: {len(positions_after) if positions_after else 0}")
    
    if not positions_after:
        logger.info("\n🎉 TODAS AS POSIÇÕES FORAM ENCERRRADAS!")
    else:
        logger.warning(f"\n⚠️  Ainda há {len(positions_after)} posição(ões)")
        for pos in positions_after:
            logger.info(f"   • #{pos.ticket}: {pos.symbol}")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTE CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
