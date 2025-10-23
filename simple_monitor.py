#!/usr/bin/env python3
"""
MONITOR SIMPLES - Verificar por que agente não abre operações
"""

from agents.manager import AgentManager
from core.database import setup_database

def check_agents():
    setup_database()
    manager = AgentManager()

    agents = manager.list_agents()
    print(f"Agentes encontrados: {len(agents)}")

    for agent in agents:
        print(f"\nAgente: {agent.config.name}")
        print(f"  Status: {agent.status.value}")
        print(f"  Simbolo: {agent.config.symbol}")
        print(f"  Volume: {agent.config.volume}")
        print(f"  Indicadores: {len(agent.config.indicators)}")
        print(f"  Eventos na historia: {len(agent.history.get_events())}")

        # Verificar se tem hedge_agent
        if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
            print("  TEM HEDGE_AGENT!")
            print(f"  Tipo Hedge: {agent.hedge_agent.hedge_type.value}")
            print(f"  Simbolos Hedge: {getattr(agent.config, 'hedge_symbols', [])}")
        else:
            print("  AGENTE NORMAL (sem hedge)")
        # Verificar trabalhador
        summary = manager.get_summary()
        print(f"\nWorker Status: {summary.get('worker_running', False) if summary else 'Desconhecido'}")

def test_agent_execution():
    setup_database()
    manager = AgentManager()

    agents = manager.list_agents()
    print(f"Testando execução de {len(agents)} agentes...")

    for agent in agents:
        if agent.status.value == "active":
            print(f"\nTestando agente {agent.config.name}...")
            try:
                # Forçar análise
                market_data = {'close': [1.08, 1.085, 1.09], 'rsi': [65, 70, 75]}

                if hasattr(agent, 'analyze_trade_signal'):
                    result = agent.analyze_trade_signal(market_data)
                    print(f"  Analise trade: {result}")
                elif hasattr(agent, 'hedge_agent'):
                    analysis = agent.hedge_agent.analyze_hedge_signal(market_data)
                    print(f"  Analise hedge: {analysis.get('recommendation', 'none')}")
                else:
                    print("  ERRO: Agente não tem método de análise!"
            except Exception as e:
                print(f"  ERRO: {e}")

        else:
            print(f"Agente {agent.config.name} está {agent.status.value}")

def start_worker_test():
    setup_database()
    manager = AgentManager()

    print("Iniciando worker...")
    manager.start_worker(check_interval=10)
    print("Worker iniciado. Aguardando...")

    import time
    time.sleep(15)

    print("Parando worker...")
    manager.stop_worker()
    print("Worker parado")

def main():
    import sys

    print("=" * 50)
    print("MONITOR SIMPLES DO AGENTE HEDGE")
    print("=" * 50)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            check_agents()
        elif command == "test":
            test_agent_execution()
        elif command == "worker":
            start_worker_test()
        else:
            print("Comandos: check, test, worker")
    else:
        check_agents()

if __name__ == "__main__":
    main()
