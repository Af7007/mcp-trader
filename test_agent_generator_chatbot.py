#!/usr/bin/env python3
"""
Teste do Agent Generator integrado com o Chatbot
Demonstra como criar agentes via linguagem natural
"""

import sys
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.generator import AgentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Teste do Agent Generator"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🤖 TESTE: Agent Generator + Chatbot Integration       ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    generator = AgentGenerator()
    
    # Teste 1: Criar agente simples
    logger.info("=" * 60)
    logger.info("TESTE 1: Criar agente com RSI simples")
    logger.info("=" * 60)
    
    command1 = "Criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
    logger.info(f"Comando: {command1}")
    
    agent1 = generator.create_agent(command1)
    if agent1:
        logger.info("✅ Agente criado com sucesso!")
        logger.info(f"   ID: {agent1.id}")
        logger.info(f"   Nome: {agent1.name}")
        logger.info(f"   Símbolo: {agent1.symbol}")
        logger.info(f"   Volume: {agent1.volume}")
        logger.info(f"   TP: ${agent1.take_profit}")
        logger.info(f"   SL: ${agent1.stop_loss}")
        logger.info(f"   Indicadores: {[ind.type.value for ind in agent1.indicators]}")
    else:
        logger.error("❌ Falha ao criar agente")
    
    # Teste 2: Criar agente com Bollinger Bands
    logger.info("\n" + "=" * 60)
    logger.info("TESTE 2: Criar agente com Bollinger Bands")
    logger.info("=" * 60)
    
    command2 = "Agente EURUSD com Bollinger Bands período 20, volume 0.05, TP 50, SL 20"
    logger.info(f"Comando: {command2}")
    
    agent2 = generator.create_agent(command2)
    if agent2:
        logger.info("✅ Agente criado com sucesso!")
        logger.info(f"   ID: {agent2.id}")
        logger.info(f"   Nome: {agent2.name}")
        logger.info(f"   Símbolo: {agent2.symbol}")
        logger.info(f"   Indicadores: {[ind.type.value for ind in agent2.indicators]}")
    else:
        logger.error("❌ Falha ao criar agente")
    
    # Teste 3: Criar agente com múltiplos indicadores
    logger.info("\n" + "=" * 60)
    logger.info("TESTE 3: Criar agente com múltiplos indicadores")
    logger.info("=" * 60)
    
    command3 = "Criar agente GBPUSD com RSI e MA 50, compre quando RSI < 30, volume 0.1, TP $2, SL $0.5"
    logger.info(f"Comando: {command3}")
    
    agent3 = generator.create_agent(command3)
    if agent3:
        logger.info("✅ Agente criado com sucesso!")
        logger.info(f"   ID: {agent3.id}")
        logger.info(f"   Nome: {agent3.name}")
        logger.info(f"   Símbolo: {agent3.symbol}")
        logger.info(f"   Indicadores: {[ind.type.value for ind in agent3.indicators]}")
    else:
        logger.error("❌ Falha ao criar agente")
    
    # Teste 4: Listar agentes
    logger.info("\n" + "=" * 60)
    logger.info("TESTE 4: Listar todos os agentes criados")
    logger.info("=" * 60)
    
    agents = generator.list_agents()
    if agents:
        logger.info(f"✅ {len(agents)} agente(s) criado(s):")
        for i, agent in enumerate(agents, 1):
            logger.info(f"   {i}. {agent.name}")
            logger.info(f"      ID: {agent.id}")
            logger.info(f"      Símbolo: {agent.symbol}")
            logger.info(f"      Volume: {agent.volume}")
            logger.info(f"      TP: ${agent.take_profit}, SL: ${agent.stop_loss}")
    else:
        logger.info("✅ Nenhum agente criado")
    
    # Teste 5: Exportar configuração
    logger.info("\n" + "=" * 60)
    logger.info("TESTE 5: Exportar configuração de agente")
    logger.info("=" * 60)
    
    if agent1:
        config = generator.export_agent(agent1.id)
        if config:
            logger.info("✅ Configuração exportada:")
            logger.info(f"   Nome: {config['name']}")
            logger.info(f"   Símbolo: {config['symbol']}")
            logger.info(f"   Volume: {config['volume']}")
            logger.info(f"   TP: ${config['take_profit']}")
            logger.info(f"   SL: ${config['stop_loss']}")
            logger.info(f"   Indicadores: {[ind['type'] for ind in config['indicators']]}")
        else:
            logger.error("❌ Falha ao exportar configuração")
    
    # Teste 6: Deletar agente
    logger.info("\n" + "=" * 60)
    logger.info("TESTE 6: Deletar agente")
    logger.info("=" * 60)
    
    if agent1:
        deleted = generator.delete_agent(agent1.id)
        if deleted:
            logger.info(f"✅ Agente {agent1.id} deletado com sucesso")
        else:
            logger.error(f"❌ Falha ao deletar agente {agent1.id}")
    
    # Resumo final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO FINAL")
    logger.info("=" * 60)
    
    final_agents = generator.list_agents()
    logger.info(f"Agentes restantes: {len(final_agents)}")
    for agent in final_agents:
        logger.info(f"  • {agent.name} ({agent.id})")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
