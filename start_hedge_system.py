#!/usr/bin/env python3
"""
Inicialização do Sistema de Agentes de Hedge
Inicia a plataforma completa com agentes de hedge
"""

import logging
import time
from src.agents.manager import AgentManager
from src.web.app import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_hedge_system():
    """Configura e inicia o sistema de agentes de hedge"""

    print('🎯 INICIALIZANDO SISTEMA DE AGENTES DE HEDGE')
    print('=' * 60)

    # 1. Inicializar Agent Manager
    print('1️⃣ Inicializando Agent Manager...')
    try:
        agent_manager = AgentManager()
        logger.info('✅ Agent Manager inicializado')
        print('   ✅ Agent Manager operacional')
    except Exception as e:
        logger.error(f'❌ Erro ao inicializar Agent Manager: {e}')
        return False

    # 2. Criar agentes de hedge de exemplo
    print('\n2️⃣ Criando agentes de hedge de exemplo...')

    hedge_commands = [
        {
            'name': 'Euro vs Libra',
            'command': 'Criar agente de hedge entre EURUSD e GBPUSD com RSI, volume 0.05',
        },
        {
            'name': 'Ouro vs Dollar',
            'command': 'Criar agente de hedge entre XAUUSD e USDJPY com Bollinger Bands, volume 0.1',
        },
        {
            'name': 'Cesta de Ativos',
            'command': 'Criar agente de hedge entre EURUSD, GBPUSD e XAUUSD com RSI, volume 0.03',
        }
    ]

    agents_created = []
    for agent_config in hedge_commands:
        try:
            agent = agent_manager.create_agent(agent_config['command'])
            if agent:
                agents_created.append(agent)
                strategy = getattr(agent.config, 'strategy', 'SINGLE_ASSET')
                print(f'   ✅ {agent_config["name"]}: {agent.config.name} ({strategy})')
            else:
                print(f'   ⚠️ {agent_config["name"]}: Falhou criar agente')
        except Exception as e:
            logger.error(f'Erro ao criar agente {agent_config["name"]}: {e}')
            print(f'   ❌ {agent_config["name"]}: Erro - {e}')

    print(f'\n   📊 Total de agentes criados: {len(agents_created)}')

    # 3. Iniciar servidor web
    print('\n3️⃣ Iniciando servidor web...')

    try:
        app = create_app()
        print('   ✅ Servidor web preparado')
        print('\n🚀 SISTEMA DE HEDGE OPERACIONAL!')
        print('=' * 60)
        print('📊 Agentes ativos:')
        for agent in agent_manager.list_agents():
            strategy = getattr(agent.config, 'strategy', 'SINGLE_ASSET')
            hedge_symbols = getattr(agent.config, 'hedge_symbols', [])
            print(f'  • {agent.config.name} ({strategy}): {", ".join(hedge_symbols) if hedge_symbols else agent.config.symbol}')

        print('
🌐 APIs disponíveis:'        print('  • Interface Web: http://localhost:3000'        print('  • Admin Panel: http://localhost:3000/admin'        print('  • API Create Hedge: POST /api/agents/create-hedge'        print('  • API Hedge Analysis: GET /api/agents/<id>/hedge-analysis'
        print('  • Worker Control: POST /api/agents/worker/toggle'

        # Executar o servidor web (execute no processo principal)
        print('
⏳ Iniciando servidor web na porta 3000...'        app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)

    except Exception as e:
        logger.error(f'Erro ao iniciar servidor web: {e}')
        print(f'❌ Erro ao iniciar servidor: {e}')
        return False

def main():
    """Função principal"""
    try:
        success = setup_hedge_system()
        if success:
            logger.info('Sistema de hedge iniciado com sucesso!')
        else:
            logger.error('Falha na inicialização do sistema')
            return 1
    except KeyboardInterrupt:
        print('\n⏹️ Inicialização interrompida pelo usuário')
        return 0
    except Exception as e:
        logger.error(f'Erro inesperado: {e}')
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
