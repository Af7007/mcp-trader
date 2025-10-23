#!/usr/bin/env python3
"""
Fechar Posições - Método Correto baseado na Documentação MCP
Referência: https://github.com/Qoyyuum/mcp-metatrader5-server

O método correto é usar order_send() com tipo de ordem OPOSTO:
- Para fechar BUY → enviar SELL
- Para fechar SELL → enviar BUY
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_position_mcp_method(ticket: int, comment: str = "Fechamento automático") -> bool:
    """
    Fechar posição usando o método correto do MCP
    
    Baseado na documentação: https://github.com/Qoyyuum/mcp-metatrader5-server
    
    O método é:
    1. Obter posição pelo ticket
    2. Determinar tipo de ordem oposto (BUY → SELL, SELL → BUY)
    3. Enviar order_send() com tipo oposto
    4. Usar ORDER_FILLING_FOK (Fill or Kill)
    """
    
    logger.info(f"🔒 Fechando posição #{ticket} (método MCP)...")
    
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
    
    # 2. Obter preço atual
    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        logger.error(f"❌ Não conseguiu obter preço de {position.symbol}")
        return False
    
    # 3. Determinar tipo de ordem OPOSTO
    # Se posição é BUY (type=0), enviar SELL (type=1)
    # Se posição é SELL (type=1), enviar BUY (type=0)
    if position.type == mt5.POSITION_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        logger.info(f"   Tipo fechamento: SELL @ {price:.5f}")
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        logger.info(f"   Tipo fechamento: BUY @ {price:.5f}")
    
    # 4. Criar requisição conforme documentação MCP
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": order_type,
        "price": price,
        "deviation": 20,  # Conforme exemplo da documentação
        "magic": 0,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,  # Fill or Kill
    }
    
    logger.info(f"\n   Enviando order_send()...")
    
    # 5. Enviar ordem
    result = mt5.order_send(request)
    
    if result is None:
        logger.error("❌ order_send retornou None")
        return False
    
    logger.info(f"   Retcode: {result.retcode}")
    logger.info(f"   Comment: {result.comment}")
    logger.info(f"   Order: {result.order}")
    
    # 6. Verificar resultado
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"   ✅ Posição fechada com sucesso!")
        return True
    else:
        logger.error(f"   ❌ Falha ao fechar (retcode: {result.retcode})")
        return False


def main():
    """Testar fechamento correto baseado em documentação MCP"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🔒 FECHAR POSIÇÕES - MÉTODO CORRETO MCP              ║")
    logger.info("║     Baseado em: github.com/Qoyyuum/mcp-metatrader5-server║")
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
    
    logger.info(f"📊 Encontradas {len(positions)} posição(ões):")
    for pos in positions:
        logger.info(f"   • #{pos.ticket}: {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume}")
    
    # 2. Fechar cada posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  ENCERRANDO POSIÇÕES")
    logger.info("=" * 60)
    logger.info("")
    
    closed_count = 0
    failed_count = 0
    
    for pos in positions:
        if close_position_mcp_method(pos.ticket, "Fechamento via MCP"):
            closed_count += 1
        else:
            failed_count += 1
        logger.info("")
    
    # 3. Verificar resultado
    logger.info("=" * 60)
    logger.info("3️⃣  RESULTADO FINAL")
    logger.info("=" * 60)
    
    positions_after = mt5.positions_get()
    
    logger.info(f"\n📊 Resumo:")
    logger.info(f"   Total de posições: {len(positions)}")
    logger.info(f"   Encerrradas: {closed_count}")
    logger.info(f"   Falhadas: {failed_count}")
    logger.info(f"   Posições restantes: {len(positions_after) if positions_after else 0}")
    
    if positions_after:
        logger.warning(f"\n⚠️  Ainda há {len(positions_after)} posição(ões) abertas")
    else:
        logger.info("\n✅ TODAS AS POSIÇÕES FORAM ENCERRRADAS!")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ OPERAÇÃO CONCLUÍDA")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📚 Referência: https://github.com/Qoyyuum/mcp-metatrader5-server")
    logger.info("   Método: order_send() com tipo de ordem OPOSTO")
    logger.info("")


if __name__ == "__main__":
    main()
