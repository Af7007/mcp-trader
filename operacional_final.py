#!/usr/bin/env python3
from src.agents.manager import AgentManager
from src.web.app import create_app
import threading
import time

def main():
    print("="*60)
    print("INICIALIZANDO SISTEMA OPERACIONAL DE HEDGE")
    print("="*60)

    try:
        print("1. Inicializando Agent Manager...")
        manager = AgentManager()
        print("   OK")

        print("2. Preparando Web App...")
        web_app = create_app()
        print("   OK")

        print("3. Criando agentes operacionais...")

        agent1 = manager.create_agent('Criar agente de hedge entre EURUSD e GBPUSD com RSI, volume 0.05')
        print(f"   EUR/GBP Hedge: {'OK' if agent1 else 'ERRO'}")

        agent2 = manager.create_agent('Criar agente de hedge entre XAUUSD e USDJPY com Bollinger Bands, volume 0.1')
        print(f"   Ouro/USDJPY Hedge: {'OK' if agent2 else 'ERRO'}")

        agent3 = manager.create_agent('Criar agente de hedge entre EURUSD, GBPUSD e XAUUSD com RSI, volume 0.03')
        print(f"   Basket Hedge: {'OK' if agent3 else 'ERRO'}")

        agents = manager.list_agents()
        print(f"   Total agentes criados: {len(agents)}")

        print("4. Iniciando worker de monitoramento...")
        manager.start_worker(check_interval=30)
        print("   OK - Worker ativo (30s)")

        print("5. Iniciando servidor web...")
        web_thread = threading.Thread(
            target=lambda: web_app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False),
            daemon=True
        )
        web_thread.start()
        print("   OK - Porta 3000")

        print("\n" + "="*60)
        print("AGENTE DE HEDGE OPERACIONAL ATIVO!")
        print("="*60)

        print("AGENTES ATIVOS:")
        for agent in agents:
            strategy = getattr(agent.config, 'strategy', 'UNKNOWN')
            symbols = getattr(agent.config, 'hedge_symbols', [agent.config.symbol])
            print(f"  • {agent.config.name} ({strategy}) - Simbolos: {symbols}")

        print("\nACESSE VIA WEB:")
        print("  • http://localhost:3000 (Interface)")
        print("  • http://localhost:3000/admin (Gerenciamento)")

        print("\nSISTEMA OPERANDO... (Ctrl+C para parar)")
        print("="*60)

        while True:
            try:
                summary = manager.get_summary()
                print(f"[MONITOR] {summary['total_agents']} agentes | {summary['active']} ativos | Trades: {summary['total_trades']}")
                time.sleep(60)
            except KeyboardInterrupt:
                print("\nParando...")
                manager.stop_worker()
                print("Sistema parado.")
                break

    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    main()
