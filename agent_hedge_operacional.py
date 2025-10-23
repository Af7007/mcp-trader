#!/usr/bin/env python3
"""
AGENTE DE HEDGE OPERACIONAL
Sistema completo com agentes reais de Hedge trabalhando
com os melhores índices do mercado financeiro
"""

import logging
import time
import threading
from datetime import datetime
from src.agents.manager import AgentManager
from src.web.app import create_app
import os
import signal
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('agent_hedge_operacional.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class OperationalHedgeAgent:
    """Sistema operacional completo de agentes de hedge"""

    def __init__(self):
        self.manager = None
        self.web_app = None
        self.worker_thread = None
        self.running = False
        logger.info("=== INICIALIZANDO SISTEMA OPERACIONAL DE HEDGE ===")

    def initialize_system(self):
        """Inicializa todos os componentes do sistema"""
        logger.info("1. Inicializando componentes do sistema...")

        try:
            # 1. Agent Manager
            self.manager = AgentManager()
            logger.info("   ✓ Agent Manager inicializado")

            # 2. Web App
            self.web_app = create_app()
            logger.info("   ✓ Web App preparada")

            return True

        except Exception as e:
            logger.error(f"   ✗ Erro na inicialização: {e}")
            return False

    def create_operational_agents(self):
        """Cria agentes operacionais de hedge baseados nos melhores índices"""
        logger.info("2. Criando agentes operacionais de hedge...")

        operational_agents = [
            {
                'command': 'Criar agente de hedge entre EURUSD e GBPUSD com RSI, volume 0.05',
                'description': 'Hedge EUR/GBP - Pares principais com alta correlação',
                'strategy': 'CORRELATION_HEDGE'
            },
            {
                'command': 'Criar agente de hedge entre XAUUSD e USDJPY com Bollinger Bands, volume 0.1',
                'description': 'Hedge Ouro/USDJPY - Proteção contra inflação',
                'strategy': 'PROTECTIVE_HEDGE'
            },
            {
                'command': 'Criar agente de hedge entre EURUSD, GBPUSD e XAUUSD com RSI, volume 0.03',
                'description': 'Basket Hedge - Diversificação múltipla',
                'strategy': 'MARKET_NEUTRAL'
            }
        ]

        created_agents = []

        for i, agent_config in enumerate(operational_agents, 1):
            try:
                logger.info(f"   Criando agente {i}: {agent_config['description']}")

                agent = self.manager.create_agent(agent_config['command'])

                if agent:
                    created_agents.append({
                        'agent': agent,
                        'config': agent_config,
                        'id': agent.config.id
                    })

                    strategy = getattr(agent.config, 'strategy', 'UNKNOWN')
                    hedge_symbols = getattr(agent.config, 'hedge_symbols', [])
                    logger.info(f"   ✓ '{agent.config.name}' - {strategy} - Simbolos: {hedge_symbols}")
                else:
                    logger.error(f"   ✗ Falha ao criar agente {i}")

            except Exception as e:
                logger.error(f"   ✗ Erro criando agente {i}: {e}")

        logger.info(f"   Total agentes criados: {len(created_agents)}")
        return created_agents

    def start_worker_monitoring(self):
        """Inicia monitoramento contínuo dos agentes"""
        logger.info("3. Iniciando monitoramento operacional...")

        try:
            # Iniciar worker do manager (monitora agentes ativos)
            self.manager.start_worker(check_interval=30)  # Verifica a cada 30 segundos
            logger.info("   ✓ Worker principal iniciado (30s interval)")

            # Iniciar thread de monitoramento adicional
            self.worker_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.running = True
            self.worker_thread.start()
            logger.info("   ✓ Thread de monitoramento adicional iniciada")

        except Exception as e:
            logger.error(f"   ✗ Erro ao iniciar monitoramento: {e}")
            return False

        return True

    def monitoring_loop(self):
        """Loop de monitoramento contínuo dos agentes de hedge"""
        logger.info("=== MONITORAMENTO OPERACIONAL INICIADO ===")
        logger.info("Monitorando agentes de hedge a cada 60 segundos...")

        while self.running:
            try:
                # Obter estatísticas atuais
                summary = self.manager.get_summary()

                logger.info(f"[MONITOR] Agentes: {summary['total_agents']} ativos | "
                          f"Trades: {summary['total_trades']} | Profit: ${summary['total_profit']:.2f}")

                # Verificar estado dos agentes hedge
                active_agents = self.manager.list_agents()

                for agent in active_agents:
                    if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
                        # Log do estado do hedge agent
                        logger.debug(f"[HEDGE] {agent.config.name}: {agent.status.value} - "
                                   f"Corr: {getattr(agent.config, 'correlation_threshold', 'N/A')}")

                # Aguardar próximo ciclo
                time.sleep(60)

            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(60)

    def start_web_interface(self):
        """Inicia interface web para gerenciamento"""
        logger.info("4. Preparando interface web para gerenciamento remoto...")

        try:
            port = int(os.getenv('PORT', '3000'))
            host = os.getenv('HOST', '0.0.0.0')

            logger.info(f"   Servidor web configurado: {host}:{port}")
            logger.info("   Endpoints disponíveis:")
            logger.info("     • http://localhost:3000/admin - Interface de gerenciamento")
            logger.info("     • http://localhost:3000/api/agents - API REST")
            logger.info("     • POST /api/agents/create-hedge - Criar novos agentes")
            logger.info("     • GET /api/agents/{id}/hedge-analysis - Análise de hedge")

            # Iniciar servidor web em thread separada
            web_thread = threading.Thread(
                target=lambda: self.web_app.run(host=host, port=port, debug=False, use_reloader=False),
                daemon=True
            )
            web_thread.start()

            logger.info("   ✓ Servidor web iniciado")

        except Exception as e:
            logger.error(f"   ✗ Erro ao iniciar servidor web: {e}")
            # Mesmo com erro na web, sistema pode continuar

    def show_system_status(self):
        """Exibe status completo do sistema"""
        print("\n" + "="*80)
        print("🎯 AGENTE DE HEDGE OPERACIONAL - SISTEMA ATIVO")
        print("="*80)

        # Agentes ativos
        agents = self.manager.list_agents()
        print(f"\n📊 AGENTES ATIVOS ({len(agents)}):")

        for agent in agents:
            strategy = getattr(agent.config, 'strategy', 'SINGLE_ASSET')
            hedge_symbols = getattr(agent.config, 'hedge_symbols', [])
            status = agent.status.value

            print(f"  • {agent.config.name}")
            print(f"    Status: {status} | Estratégia: {strategy}")
            print(f"    Símbolos: {', '.join(hedge_symbols) if hedge_symbols else agent.config.symbol}")
            print(f"    Volume: {agent.config.volume}")
            print(f"    ID: {agent.config.id}")

            if hasattr(agent, 'hedge_agent') and agent.hedge_agent:
                print(f"    Tipo de Hedge: {agent.hedge_agent.hedge_type.value}")
                print(f"    Threshold Correlação: {getattr(agent.config, 'correlation_threshold', 'N/A')}")

        # Estatísticas gerais
        summary = self.manager.get_summary()
        print("
📈 ESTATÍSTICAS GERAIS:"        print(f"  • Agentes Totais: {summary['total_agents']}")
        print(f"  • Agentes Ativos: {summary['active']}")
        print(f"  • Trades Realizados: {summary['total_trades']}")
        print(f"  • Lucro Total: ${summary['total_profit']:.2f}")

        # Acesso ao sistema
        print("
🌐 ACESSO AO SISTEMA:"        print("  • Interface Web: http://localhost:3000")
        print("  • Painel Admin: http://localhost:3000/admin")
        print("  • API REST: http://localhost:3000/api/agents")
        print("  • Log Arquivo: agent_hedge_operacional.log")

        print("
🔄 MONITORAMENTO:"        print("  • Worker Principal: Ativo (30s interval)")
        print("  • Monitoramento Hedge: Ativo (60s interval)")
        print("  • Servidor Web: Ativo")

        print("
🎯 FUNCIONALIDADES OPERACIONAIS:"        print("  ✓ Análise de correlação em tempo real"        print("  ✓ Recomendações inteligentes de hedge"        print("  ✓ Proteção automática contra risco"        print("  ✓ Gerenciamento remoto via web"        print("  ✓ Logs detalhados de operações"        print("  ✓ Monitoramento contínuo de performance"

        print("
⏳ SISTEMA OPERANDO..."        print("   Pressione Ctrl+C para parar"        print("="*80)

    def run_system(self):
        """Executa o sistema operacional completo"""
        try:
            # 1. Inicializar componentes
            if not self.initialize_system():
                logger.error("Falha critica na inicializacao")
                return False

            # 2. Criar agentes operacionais
            operational_agents = self.create_operational_agents()
            if not operational_agents:
                logger.warning("Nenhum agente operacional criado, mas sistema continua...")

            # 3. Iniciar monitoramento
            if not self.start_worker_monitoring():
                logger.error("Falha ao iniciar monitoramento")
                return False

            # 4. Iniciar interface web
            self.start_web_interface()

            # 5. Mostrar status do sistema
            self.show_system_status()

            # 6. Manter sistema rodando
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Interrupcao do usuario detectada")
            self.shutdown()

        except Exception as e:
            logger.error(f"Erro critico no sistema: {e}")
            self.shutdown()
            return False

        return True

    def shutdown(self):
        """Desliga o sistema operacional"""
        logger.info("=== DESLIGANDO SISTEMA OPERACIONAL ===")

        self.running = False

        # Parar worker do manager
        if self.manager:
            try:
                self.manager.stop_worker()
                logger.info("Worker principal parado")
            except:
                pass

        # Aguardar threads terminarem
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
            logger.info("Thread de monitoramento parada")

        logger.info("Sistema operacional desligado")
        print("
🛑 Sistema operacional parado"        sys.exit(0)

# Handler para sinais do sistema
def signal_handler(signum, frame):
    print("
📴 Sinal de interrupcao recebido"    if 'operational_agent' in globals():
        operational_agent.shutdown()
    else:
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Instancia global
operational_agent = None

def main():
    """Função principal"""
    global operational_agent

    # Verificar se já está rodando
    pid_file = 'agent_hedge_pid.txt'
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            try:
                old_pid = int(f.read().strip())
                os.kill(old_pid, 0)  # Verifica se processo ainda existe
                print("Sistema ja esta rodando (PID: {})".format(old_pid))
                print("Use 'kill {}' para parar ou remova {}.format(old_pid, pid_file))
                return 1
            except (OSError, ValueError):
                # Processo não existe mais, limpar arquivo
                os.remove(pid_file)

    try:
        # Criar e salvar PID
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))

        # Inicializar e executar sistema
        operational_agent = OperationalHedgeAgent()
        success = operational_agent.run_system()

        # Limpar PID se sucesso
        if os.path.exists(pid_file):
            os.remove(pid_file)

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        if os.path.exists(pid_file):
            os.remove(pid_file)
        return 1

if __name__ == "__main__":
    exit(main())
