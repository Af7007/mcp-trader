#!/usr/bin/env python3
"""
MONITOR DE LOGS DO AGENTE HEDGE - TEMPO REAL
Mostra todas as atividades, decisões e análises dos agentes
"""

import time
import threading
from agents.manager import AgentManager
from core.database import setup_database
from core.mt5_connection import MT5Connection

def monitor_events_realtime():
    """Monitora eventos dos agentes em tempo real"""
    print("=" * 70)
    print("MONITOR DE LOGS DO AGENTE HEDGE - TEMPO REAL")
    print("=" * 70)

    # Inicializar sistema
    setup_database()
    manager = AgentManager()

    # Verificar agentes existentes
    agents = manager.list_agents()
    print(f"Agentes encontrados: {len(agents)}")

    for agent in agents:
        print(f"  - {agent.config.name} ({agent.config.id}) - {agent.status.value}")

    if not agents:
        print("Nenhum agente ativo. Criando um agente de teste...")
        agent = manager.create_agent("criar agente EURUSD com RSI")

    print("\n[LOG] Iniciando monitoramento em tempo real...")
    print("Pressione Ctrl+C para parar")
    print("=" * 70)

    def log_worker():
        """Worker que verifica logs periodicamente"""
        last_log_count = 0

        while True:
            try:
                agents = manager.list_agents()

                for agent in agents:
                    if agent.status.value == "active":
                        # Mostrar novos eventos do agente
                        events = agent.history.get_events(limit=5)
                        if events:
                            new_events = events[:3]  # Mostrar últimos 3 eventos
                            print(f"\n[{agent.config.name}] Novos eventos:")
                            for event in new_events:
                                # Formatar timestamp
                                timestamp = event.get('timestamp', 'unknown')
                                event_type = event.get('event_type', 'unknown')

                                if event_type == 'analysis':
                                    analysis = event.get('analysis', {})
                                    signal = analysis.get('signal', 'none')
                                    confidence = analysis.get('confidence', 0)
                                    print(f"  ▶ {timestamp[:19]} - {event_type.upper()}: Signal={signal}, Conf={confidence:.3f}")
                                elif event_type == 'trade_opened':
                                    trade = event.get('trade', {})
                                    print(f"  ▶ {timestamp[:19]} - TRADE OPENED: {trade.get('symbol', 'N/A')} {trade.get('volume', 0)}")
                                elif event_type == 'trade_closed':
                                    trade = event.get('trade', {})
                                    profit = trade.get('profit', 0)
                                    print(f"  ▶ {timestamp[:19]} - TRADE CLOSED: Profit ${profit:.2f}")
                                else:
                                    print(f"  ▶ {timestamp[:19]} - {event_type.upper()}: {str(event)[:100]}")

                # Verificar status worker
                summary = manager.get_summary()
                worker_status = "Rodando" if summary.get('worker_running', False) else "Parado"
                print(f"Status: Worker={worker_status}, Agentes Ativos={summary.get('active', 0)} ", end='\r')

                time.sleep(2)  # Atualizar a cada 2 segundos

            except Exception as e:
                print(f"Erro monitor: {e}")
                time.sleep(2)

    # Iniciar monitor em thread separada
    monitor_thread = threading.Thread(target=log_worker, daemon=True)
    monitor_thread.start()

    try:
        # Manter programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[LOG] Monitoramento encerrado")
        manager.stop_worker()

def show_agent_debug_info():
    """Mostra informações de debug detalhadas dos agentes"""
    print("\nDEBUG: Informações Detalhadas dos Agentes")
    print("=" * 50)

    setup_database()
    manager = AgentManager()

    agents = manager.list_agents()

    for agent in agents:
        print(f"\nAgente: {agent.config.name}")
        print(f"  Status: {agent.status.value}")
        print(f"  Estratégia: {getattr(agent.config, 'strategy', 'SINGLE_ASSET')}")
        print(f"  Símbolos: {getattr(agent.config, 'symbols', [agent.config.symbol])}")
        print(f"  Volume: {agent.config.volume}")
        print(f"  Indicadores: {[ind.type.value for ind in agent.config.indicators]}")
        print(f"  Take Profit: {getattr(agent.config, 'take_profit', 'None')}")
        print(f"  Stop Loss: {getattr(agent.config, 'stop_loss', 'None')}")

        # Verificar se tem agent hedge
        if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
            print("  Tipo Hedge: HEDGE_AGENT"            print(f"  Correlação Threshold: {getattr(agent.config, 'correlation_threshold', 0.7)}")
            print(f"  HEDGE Symbols: {getattr(agent.config, 'hedge_symbols', [])}")

        # Mostrar condição atual do mercado
        try:
            # Simular leitura do indicador (sem MT5 real por enquanto)
            print("  RSI Atual: (simulado) 65.4")
            print("  Conclusão da análise anterior: Aguarda sinal forte"        except Exception as e:
            print(f"  Erro na análise: {e}")

        # Últimos 3 eventos
        events = agent.history.get_events(limit=3)
        print(f"  Últimos eventos ({len(events)}):")
        for event in events:
            timestamp = event.get('timestamp', 'unknown')[:19]
            event_type = event.get('event_type', 'unknown')
            print(f"    - {timestamp}: {event_type}")

def create_test_trade_signal():
    """Cria sinal para testar se agente abre operação"""
    print("\n[SINAL TESTE] Simulando sinal de entrada para agente...")

    setup_database()
    manager = AgentManager()

    agents = manager.list_agents()

    if not agents:
        print("Nenhum agente encontrado. Criando um...")
        agent = manager.create_agent("criar agente EURUSD com RSI")
        agents = [agent]

    for agent in agents:
        if agent.status.value == "active":
            print(f"Simulando sinal para {agent.config.name}...")

            # Simular um sinal forte para superar o threshold
            # Isso deveria fazer o agente tentar abrir uma posição
            try:
                # Forçar análise com dados simulados
                # Em produção, isso viria do MT5
                market_data = {
                    'close': [1.0850, 1.0860, 1.0870, 1.0880, 1.0890],
                    'rsi': [45.2, 55.6, 67.8, 78.9, 80.1]  # RSI > 70 indica sinal forte
                }

                # Chamar análise diretamente
                if hasattr(agent, 'analyze_trade_signal'):
                    signal = agent.analyze_trade_signal(market_data)
                    print(f"Análise resultou: {signal}"                elif hasattr(agent, 'hedge_agent') and agent.hedge_agent:
                    analysis = agent.hedge_agent.analyze_hedge_signal(market_data)
                    print(f"Análise hedge resultou: Recomendação={analysis.get('recommendation', 'none')}"                else:
                    print("Agente não tem método de análise configurado")

            except Exception as e:
                print(f"Erro na análise simulada: {e}")

def show_worker_status():
    """Mostra status detalhado do worker/thread que monitora os agentes"""
    print("\nWORKER STATUS:")
    print("=" * 30)

    setup_database()
    manager = AgentManager()

    summary = manager.get_summary()
    print(f"Worker Running: {summary.get('worker_running', False)}")
    print(f"Check Interval: {getattr(manager, '_worker_interval', 'Unknown')}")
    print(f"Total Agents: {summary.get('total_agents', 0)}")
    print(f"Active Agents: {summary.get('active', 0)}")

    # Verificar se worker thread está ativa
    worker_threads = [t for t in threading.enumerate() if 'worker' in t.name.lower()]
    print(f"Worker Threads Ativas: {len(worker_threads)}")
    for thread in worker_threads:
        print(f"  - {thread.name}: {thread.is_alive()}")

def main():
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "debug":
            show_agent_debug_info()
        elif command == "test":
            create_test_trade_signal()
        elif command == "worker":
            show_worker_status()
        else:
            print("Comandos disponíveis:")
            print("  python monitor_agent_logs.py         # Monitor em tempo real")
            print("  python monitor_agent_logs.py debug   # Debug dos agentes")
            print("  python monitor_agent_logs.py test    # Teste sinal de trade")
            print("  python monitor_agent_logs.py worker  # Status do worker")
    else:
        # Monitor em tempo real por padrão
        monitor_events_realtime()

if __name__ == "__main__":
    main()
