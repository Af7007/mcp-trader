#!/usr/bin/env python3
"""
Diagnóstico de agentes e posições
Verifica agentes em memória, posições abertas, e threads rodando
"""

import sys
import logging
import threading
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))
from agents.manager import AgentManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose():
    """Executar diagnóstico"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🔍 DIAGNÓSTICO DE AGENTES E POSIÇÕES             ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # 1. Verificar MT5
    logger.info("=" * 60)
    logger.info("1️⃣  VERIFICANDO MT5")
    logger.info("=" * 60)
    
    if mt5.initialize():
        account = mt5.account_info()
        logger.info(f"✅ MT5 conectado")
        logger.info(f"   Conta: {account.login}")
        logger.info(f"   Saldo: ${account.balance:.2f}")
        
        # Verificar posições abertas
        positions = mt5.positions_get()
        if positions:
            logger.info(f"\n📊 Posições Abertas: {len(positions)}")
            for pos in positions:
                logger.info(f"   • Ticket: {pos.ticket}")
                logger.info(f"     Símbolo: {pos.symbol}")
                logger.info(f"     Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
                logger.info(f"     Volume: {pos.volume}")
                logger.info(f"     Preço de Abertura: {pos.price_open:.5f}")
                logger.info(f"     Preço Atual: {pos.price_current:.5f}")
                logger.info(f"     Lucro/Prejuízo: ${pos.profit:.2f}")
                logger.info(f"     SL: {pos.sl}")
                logger.info(f"     TP: {pos.tp}")
        else:
            logger.info("✅ Nenhuma posição aberta")
        
        mt5.shutdown()
    else:
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # 2. Verificar Agent Manager
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  VERIFICANDO AGENT MANAGER")
    logger.info("=" * 60)
    
    manager = AgentManager()
    agents = manager.list_agents()
    
    if agents:
        logger.info(f"✅ Agentes em Memória: {len(agents)}")
        for agent in agents:
            logger.info(f"\n   • {agent.config.name}")
            logger.info(f"     ID: {agent.config.id}")
            logger.info(f"     Status: {agent.status.value}")
            logger.info(f"     Símbolo: {agent.config.symbol}")
            logger.info(f"     Trades Abertos: {agent.trades_opened}")
            logger.info(f"     Trades Fechados: {agent.trades_closed}")
            logger.info(f"     Lucro Total: ${agent.total_profit:.2f}")
    else:
        logger.info("✅ Nenhum agente em memória")
    
    # 3. Verificar Threads
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  VERIFICANDO THREADS")
    logger.info("=" * 60)
    
    threads = threading.enumerate()
    logger.info(f"Total de Threads: {len(threads)}")
    for thread in threads:
        logger.info(f"   • {thread.name} (daemon={thread.daemon})")
    
    if manager.is_running:
        logger.info(f"\n⚠️  Worker está rodando!")
        logger.info(f"   Thread: {manager.worker_thread.name if manager.worker_thread else 'N/A'}")
    else:
        logger.info(f"\n✅ Worker não está rodando")
    
    # 4. Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO")
    logger.info("=" * 60)
    
    summary = manager.get_summary()
    logger.info(f"Total de Agentes: {summary['total_agents']}")
    logger.info(f"  • Ativos: {summary['active']}")
    logger.info(f"  • Pausados: {summary['paused']}")
    logger.info(f"  • Parados: {summary['stopped']}")
    logger.info(f"Worker: {'Rodando' if summary['worker_running'] else 'Parado'}")
    logger.info(f"Total de Trades: {summary['total_trades']}")
    logger.info(f"Lucro Total: ${summary['total_profit']:.2f}")
    
    # 5. Recomendações
    logger.info("\n" + "=" * 60)
    logger.info("💡 RECOMENDAÇÕES")
    logger.info("=" * 60)
    
    if positions and not agents:
        logger.warning("⚠️  Há posições abertas mas nenhum agente em memória!")
        logger.info("   → Posições podem ter sido abertas manualmente")
        logger.info("   → Feche manualmente no MT5 ou via chatbot")
    
    if manager.is_running and not agents:
        logger.warning("⚠️  Worker está rodando mas sem agentes!")
        logger.info("   → Pare o worker: manager.stop_worker()")
    
    if agents and not summary['worker_running']:
        logger.warning("⚠️  Há agentes mas worker não está rodando!")
        logger.info("   → Inicie o worker: manager.start_worker()")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ DIAGNÓSTICO CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    diagnose()
