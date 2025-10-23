#!/usr/bin/env python3
"""
Sistema operacional de hedge executavel
"""

from src.agents.manager import AgentManager
from src.web.app import create_app
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("="*60)
    print("INICIALIZANDO SISTEMA OPERACIONAL DE HEDGE")
    print("="*60)

    try:
        # Inicializar componentes
        print("1. Inicializando Agent Manager...")
        manager = AgentManager()
        print("   OK - Agent Manager inicializado")

        print("2. Preparando Web App...")
        web_app = create_app()
        print("   OK - Web App preparada")

        print("3. Criando agentes operacionais...")

        # Agente 1: Hedge EURUSD/GBPUSD (Principais pares)
        agent1 = manager.create_agent('Criar agente de hedge entre EURUSD e GBPUSD com RSI, volume 0.05')
        if agent1:
            print(f"   OK - EUR/GBP Hedge: {agent1.config.name}")
        else:
            print("   ERRO - EUR/GBP Hedge falhou")

        # Agente 2: Hedge XAUUSD/USDJPY (Ouro vs Dollar/Yen)
        agent2 = manager.create_agent('Criar agente de hedge entre XAUUSD e USDJPY com Bollinger Bands, volume 0.1')
        if agent2:
            print(f"   OK - Ouro/USDJPY Hedge: {agent2.config.name}")
        else:
            print("   ERRO - Ouro/USDJPY Hedge falhou")

        # Agente 3: Basket Hedge (EUR, GBP, Ouro)
        agent3 = manager.create_agent('Criar agente de hedge entre EURUSD, GBPUSD e XAUUSD com RSI, volume 0.03')
        if agent3:
            print(f"   OK - Basket Hedge: {agent3.config.name}")
        else:
            print("   ERRO - Basket Hedge falhou")

        num_agents = len(manager.list_agents())
        print(f"   Total agentes criados: {num_agents}")

        print("4. Iniciando worker de monitoramento...")
        manager.start_worker(check_interval=30)
        print("   OK - Worker iniciado (30s intervals)")

        print("5. Iniciando servidor web...")
        # Iniciar web server em thread
        web_thread = threading.Thread(
            target=lambda: web_app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False),
            daemon=True
        )
        web_thread.start()
        print("   OK - Servidor web iniciado na porta 3000")

        # Status final
        print("\n" + "="*60)
        print("SISTEMA OPERACIONAL ATIVO!")
        print("="*60)

        agents = manager.list_agents()
        print(f"AGENTES ATIVOS ({len(agents)}):")

        for agent in agents:
            strategy = getattr(agent.config, 'strategy', 'SINGLE_ASSET')
            hedge_symbols = getattr(agent.config, 'hedge_symbols', [])
            print(f"  • {agent.config.name}")
            print(f"    Status: {agent.status.value}")
            print(f"    Estrategia: {strategy}")
            print(f"    Simbolos: {', '.join(hedge_symbols) if hedge_symbols else agent.config.symbol}")
            print(f"    Volume: {agent.config.volume}")
            print(f"    ID: {agent.config.id}")

            if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
                print(f"    Tipo Hedge: {agent.hedge_agent.hedge_type.value}")

        print("
ACESSO AO SISTEMA:"        print("  • Interface Web: http://localhost:3000"        print("  • Painel Admin: http://localhost:3000/admin"        print("  • API REST: http://localhost:3000/api/agents"
        print("  • Logs: agent_hedge_operacional.log"

        print("
MONITORAMENTO ATIVO:"        print("  ✓ Correlação em tempo real"        print("  ✓ Recomendações de hedge inteligentes"        print("  ✓ Proteção automática contra risco"        print("  ✓ Gerenciamento remoto via web"

        print("
SISTEMA RODANDO... (Ctrl+C para parar)"        print("="*60)

        # Loop principal
        while True:
            try:
                summary = manager.get_summary()
                print(f"[MONITOR] {summary['total_agents']} agentes | {summary['active']} ativos | Trades: {summary['total_trades']} | Profit: ${summary['total_profit']:.2f}")
                time.sleep(60)  # Status a cada minuto
            except KeyboardInterrupt:
                print("\nParando sistema...")
                manager.stop_worker()
                print("Sistema parado.")
                break

    except Exception as e:
        print(f"ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
