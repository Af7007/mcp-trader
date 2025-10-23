#!/usr/bin/env python3
"""
DEMONSTRACAO: CHATBOT GERENCIA HEDGE - VERSAO LIMPA
"""

from agents.manager import AgentManager
from core.database import setup_database

def main():
    print("=" * 60)
    print("CHATBOT GERENCIA HEDGE - DEMONSTRACAO")
    print("=" * 60)

    # Inicializar sistema
    setup_database()
    manager = AgentManager()

    print("\nCOMANDOS DISPONIVEIS:")
    print("  'criar agente EURUSD com RSI' - Criar agente")
    print("  'listar agentes' - Ver agentes")
    print("  'iniciar worker' - Iniciar monitoramento")
    print("  'parar worker' - Parar monitoramento")
    print("  'pausar agente <ID>' - Pausar agente")
    print("  'retomar agente <ID>' - Retomar agente")
    print("  'resumo' - Ver resumo do sistema")
    print("  'sair' - Sair")
    print("=" * 60)

    worker_running = False

    try:
        while True:
            command = input("\nVoce: ").strip().lower()

            if command == 'sair':
                break

            elif command == 'ajuda':
                print("Digite um comando da lista acima")

            elif 'criar agente' in command:
                print("Criando agente...")
                agent = manager.create_agent(command.replace('criar ', ''))
                if agent:
                    print("OK - Agente criado!")
                    print(f"  Nome: {agent.config.name}")
                    print(f"  ID: {agent.config.id}")
                    print(f"  Tipo: {getattr(agent.config, 'strategy', 'SINGLE_ASSET')}")
                else:
                    print("Erro - Nao foi possivel criar agente")

            elif command == 'listar agentes':
                agents = manager.list_agents()
                if agents:
                    print(f"Encontrei {len(agents)} agente(s):")
                    for agent in agents:
                        print(f"  - {agent.config.name} ({agent.config.id}) - {agent.status.value}")
                else:
                    print("Nenhum agente criado")

            elif command == 'iniciar worker':
                if not worker_running:
                    manager.start_worker(check_interval=30)
                    worker_running = True
                    print("Worker iniciado")
                else:
                    print("Worker ja esta rodando")

            elif command == 'parar worker':
                if worker_running:
                    manager.stop_worker()
                    worker_running = False
                    print("Worker parado")
                else:
                    print("Worker nao esta rodando")

            elif command.startswith('pausar agente '):
                agent_id = command.split()[-1]
                if manager.pause_agent(agent_id):
                    print(f"Agente {agent_id} pausado")
                else:
                    print(f"Agente {agent_id} nao encontrado")

            elif command.startswith('retomar agente '):
                agent_id = command.split()[-1]
                if manager.resume_agent(agent_id):
                    print(f"Agente {agent_id} retomado")
                else:
                    print(f"Agente {agent_id} nao encontrado")

            elif command == 'resumo':
                summary = manager.get_summary()
                print("Resumo do sistema:")
                print(f"  Total agentes: {summary['total_agents']}")
                print(f"  Ativos: {summary['active']}")
                print(f"  Pausados: {summary['paused']}")
                print(f"  Total trades: {summary['total_trades']}")
                print(f"  Worker: {'Rodando' if summary['worker_running'] else 'Parado'}")

            else:
                print(f"Comando '{command}' nao reconhecido")

    except KeyboardInterrupt:
        print("\nAte logo!")

if __name__ == "__main__":
    main()
