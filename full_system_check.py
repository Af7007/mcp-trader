#!/usr/bin/env python3
"""
Check Completo do Sistema - Chatbot até MT5
Identifica por que não está fechando posições corretamente
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))
from agents.manager import AgentManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_system():
    """Check completo do sistema"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🔍 CHECK COMPLETO DO SISTEMA                     ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # ========== 1. CHECK AGENT MANAGER ==========
    logger.info("=" * 60)
    logger.info("1️⃣  CHECK AGENT MANAGER")
    logger.info("=" * 60)
    
    try:
        manager = AgentManager()
        agents = manager.list_agents()
        logger.info(f"✅ Agent Manager inicializado")
        logger.info(f"   Agentes em memória: {len(agents)}")
        
        if agents:
            for agent in agents:
                logger.info(f"   • {agent.config.name} ({agent.config.id})")
                logger.info(f"     Status: {agent.status.value}")
                logger.info(f"     Trades: {agent.trades_opened} abertos, {agent.trades_closed} fechados")
        
        summary = manager.get_summary()
        logger.info(f"\n   Resumo:")
        logger.info(f"   • Total: {summary['total_agents']}")
        logger.info(f"   • Ativos: {summary['active']}")
        logger.info(f"   • Worker: {'Rodando' if summary['worker_running'] else 'Parado'}")
        
    except Exception as e:
        logger.error(f"❌ Erro no Agent Manager: {e}")
    
    # ========== 2. CHECK MT5 CONNECTION ==========
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  CHECK MT5 CONNECTION")
    logger.info("=" * 60)
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    logger.info("✅ MT5 conectado")
    
    # ========== 3. CHECK ACCOUNT ==========
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  CHECK ACCOUNT")
    logger.info("=" * 60)
    
    account = mt5.account_info()
    logger.info(f"✅ Conta: {account.login}")
    logger.info(f"   Servidor: {account.server}")
    logger.info(f"   Saldo: ${account.balance:.2f}")
    logger.info(f"   Equity: ${account.equity:.2f}")
    logger.info(f"   Margem Livre: ${account.margin_free:.2f}")
    logger.info(f"   Nível de Margem: {account.margin_level:.2f}%")
    
    # ========== 4. CHECK POSITIONS ==========
    logger.info("\n" + "=" * 60)
    logger.info("4️⃣  CHECK POSITIONS")
    logger.info("=" * 60)
    
    positions = mt5.positions_get()
    if positions:
        logger.info(f"⚠️  {len(positions)} posição(ões) aberta(s):")
        for pos in positions:
            logger.info(f"\n   Ticket: {pos.ticket}")
            logger.info(f"   Símbolo: {pos.symbol}")
            logger.info(f"   Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
            logger.info(f"   Volume: {pos.volume}")
            logger.info(f"   Preço Abertura: {pos.price_open:.5f}")
            logger.info(f"   Preço Atual: {pos.price_current:.5f}")
            logger.info(f"   Lucro/Prejuízo: ${pos.profit:.2f}")
            logger.info(f"   SL: {pos.sl}")
            logger.info(f"   TP: {pos.tp}")
            logger.info(f"   Comentário: {pos.comment}")
            logger.info(f"   Magic: {pos.magic}")
    else:
        logger.info("✅ Nenhuma posição aberta")
    
    # ========== 5. CHECK PENDING ORDERS ==========
    logger.info("\n" + "=" * 60)
    logger.info("5️⃣  CHECK PENDING ORDERS")
    logger.info("=" * 60)
    
    orders = mt5.orders_get()
    if orders:
        logger.warning(f"⚠️  {len(orders)} ordem(ns) pendente(s):")
        for order in orders:
            logger.info(f"\n   Ticket: {order.ticket}")
            logger.info(f"   Símbolo: {order.symbol}")
            logger.info(f"   Tipo: {order.type}")
            logger.info(f"   Volume: {order.volume}")
            logger.info(f"   Preço: {order.price_open:.5f}")
            logger.info(f"   Status: {order.state}")
            logger.info(f"   Comentário: {order.comment}")
    else:
        logger.info("✅ Nenhuma ordem pendente")
    
    # ========== 6. CHECK SYMBOLS ==========
    logger.info("\n" + "=" * 60)
    logger.info("6️⃣  CHECK SYMBOLS")
    logger.info("=" * 60)
    
    symbols = ["XAUUSDm", "EURUSDc", "GBPUSDc"]
    for symbol in symbols:
        info = mt5.symbol_info(symbol)
        if info:
            logger.info(f"\n✅ {symbol}:")
            logger.info(f"   Visível: {info.visible}")
            logger.info(f"   Negociável: {info.trade_mode}")
            logger.info(f"   Volume Min: {info.volume_min}")
            logger.info(f"   Volume Max: {info.volume_max}")
            logger.info(f"   Volume Step: {info.volume_step}")
            
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                logger.info(f"   Bid: {tick.bid:.5f}")
                logger.info(f"   Ask: {tick.ask:.5f}")
            else:
                logger.warning(f"   ⚠️  Não conseguiu obter tick")
        else:
            logger.error(f"❌ {symbol} não encontrado")
    
    # ========== 7. TEST CLOSE ORDER ==========
    logger.info("\n" + "=" * 60)
    logger.info("7️⃣  TEST CLOSE ORDER")
    logger.info("=" * 60)
    
    if positions:
        pos = positions[0]
        logger.info(f"\nTestando fechamento da posição #{pos.ticket}...")
        
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if pos.type == 0 else tick.ask
            
            logger.info(f"   Símbolo: {pos.symbol}")
            logger.info(f"   Tipo Atual: {'BUY' if pos.type == 0 else 'SELL'}")
            logger.info(f"   Tipo Fechamento: {'SELL' if pos.type == 0 else 'BUY'}")
            logger.info(f"   Preço: {close_price:.5f}")
            logger.info(f"   Volume: {pos.volume}")
            
            # Testar diferentes tipos de filling
            for filling_type, filling_name in [
                (mt5.ORDER_FILLING_FOK, "FOK (Fill or Kill)"),
                (mt5.ORDER_FILLING_IOC, "IOC (Immediate or Cancel)"),
                (mt5.ORDER_FILLING_RETURN, "RETURN (Return)"),
            ]:
                logger.info(f"\n   Testando {filling_name}...")
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": close_type,
                    "price": close_price,
                    "deviation": 100,
                    "magic": 0,
                    "comment": f"Test {filling_name}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_type,
                }
                
                result = mt5.order_send(request)
                
                if result is None:
                    logger.warning(f"   ⚠️  Retornou None")
                else:
                    logger.info(f"   Retcode: {result.retcode}")
                    logger.info(f"   Comment: {result.comment}")
                    logger.info(f"   Order: {result.order}")
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"   ✅ SUCESSO com {filling_name}!")
                    elif result.retcode == mt5.TRADE_RETCODE_PLACED:
                        logger.warning(f"   ⚠️  Ordem colocada (pendente)")
    
    # ========== 8. CHECK ACCOUNT RESTRICTIONS ==========
    logger.info("\n" + "=" * 60)
    logger.info("8️⃣  CHECK ACCOUNT RESTRICTIONS")
    logger.info("=" * 60)
    
    logger.info(f"Trade Allowed: {account.trade_allowed}")
    logger.info(f"Trade Expert Allowed: {account.trade_expert}")
    logger.info(f"Margin SO Mode: {account.margin_so_mode}")
    logger.info(f"Margin SO Call: {account.margin_so_call}")
    logger.info(f"Margin Level: {account.margin_level}%")
    
    # ========== 9. RECOMMENDATIONS ==========
    logger.info("\n" + "=" * 60)
    logger.info("9️⃣  RECOMENDAÇÕES")
    logger.info("=" * 60)
    
    issues = []
    
    if positions:
        issues.append("❌ Ainda há posições abertas")
    
    if orders:
        issues.append("❌ Há ordens pendentes")
    
    if not account.trade_allowed:
        issues.append("❌ Trading não permitido na conta")
    
    if account.margin_level < 100 and account.margin_level > 0:
        issues.append("❌ Nível de margem baixo")
    
    if not issues:
        logger.info("✅ Sistema OK - Nenhum problema detectado")
    else:
        for issue in issues:
            logger.info(issue)
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ CHECK CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    check_system()
