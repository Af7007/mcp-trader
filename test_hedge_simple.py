#!/usr/bin/env python3
from src.agents.manager import AgentManager

print('TESTE SIMPLES DO SISTEMA DE HEDGE')
print('=' * 50)

try:
    # Criar manager
    manager = AgentManager()
    print('Agent Manager inicializado')

    # Criar agente de hedge
    agent = manager.create_agent('Criar agente de hedge entre EURUSD e GBPUSD com RSI')

    if agent:
        print('Agente de hedge criado!')
        print('   Nome: {}'.format(agent.config.name))
        print('   Estrategia: {}'.format(getattr(agent.config, 'strategy', 'UNKNOWN')))
        print('   Simbolos: {}'.format(getattr(agent.config, 'hedge_symbols', [])))

        if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
            print('   Hedge Agent integrado!')
            print('   Tipo: {}'.format(agent.hedge_agent.hedge_type.value))
        else:
            print('   Hedge Agent não integrado')
    else:
        print('Falha ao criar agente')

    print('Agentes totais: {}'.format(len(manager.list_agents())))

except Exception as e:
    print('ERRO: {}'.format(e))
    import traceback
    traceback.print_exc()
