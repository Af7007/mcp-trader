#!/usr/bin/env python3
"""
Agent Manager - Gerencia o ciclo de vida dos agentes
Criar, monitorar, pausar, retomar, deletar agentes
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import threading
import time
import sys
from pathlib import Path

# Suportar import como módulo ou script direto
try:
    from .generator import AgentGenerator, AgentConfig
    from .hedge_agent import HedgeAgent
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from generator import AgentGenerator, AgentConfig
    try:
        from hedge_agent import HedgeAgent
    except ImportError:
        HedgeAgent = None  # Fallback para quando não há implementação

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Status de um agente"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


class AgentEvent(str, Enum):
    """Tipos de eventos de agente"""
    CREATED = "created"
    STARTED = "started"
    PAUSED = "paused"
    RESUMED = "resumed"
    STOPPED = "stopped"
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    ERROR = "error"
    DELETED = "deleted"


class AgentHistory:
    """Histórico de eventos de um agente"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.events: List[Dict] = []
    
    def add_event(self, event_type: AgentEvent, details: Dict = None):
        """Adicionar evento ao histórico"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type.value,
            'details': details or {}
        }
        self.events.append(event)
        logger.info(f"📝 Evento registrado: {event_type.value} para agente {self.agent_id}")
    
    def get_events(self, limit: int = 10) -> List[Dict]:
        """Obter últimos eventos"""
        return self.events[-limit:]
    
    def get_all_events(self) -> List[Dict]:
        """Obter todos os eventos"""
        return self.events


class ManagedAgent:
    """Agente gerenciado com estado e histórico"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.ACTIVE
        self.history = AgentHistory(config.id)
        self.started_at = datetime.now()
        self.paused_at = None
        self.stopped_at = None
        self.trades_opened = 0
        self.trades_closed = 0
        self.total_profit = 0.0
        self.errors = []

        # Agente de hedge especializado (se disponível)
        self.hedge_agent = None
        if (HedgeAgent and
            hasattr(config, 'strategy') and
            config.strategy in ['HEDGE_PAIR', 'BASKET_HEDGE']):
            try:
                self.hedge_agent = HedgeAgent(config)
                logger.info(f"🎯 Hedge Agent integrado: {config.name}")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao criar Hedge Agent: {e}")

        # Registrar criação
        self.history.add_event(AgentEvent.CREATED, {
            'name': config.name,
            'symbol': config.symbol,
            'indicators': [ind.type.value for ind in config.indicators],
            'strategy': getattr(config, 'strategy', 'SINGLE_ASSET')
        })
    
    def pause(self):
        """Pausar agente"""
        if self.status == AgentStatus.ACTIVE:
            self.status = AgentStatus.PAUSED
            self.paused_at = datetime.now()
            self.history.add_event(AgentEvent.PAUSED)
            logger.info(f"⏸️  Agente {self.config.id} pausado")
    
    def resume(self):
        """Retomar agente"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.ACTIVE
            self.paused_at = None
            self.history.add_event(AgentEvent.RESUMED)
            logger.info(f"▶️  Agente {self.config.id} retomado")
    
    def stop(self):
        """Parar agente"""
        self.status = AgentStatus.STOPPED
        self.stopped_at = datetime.now()
        self.history.add_event(AgentEvent.STOPPED)
        logger.info(f"⏹️  Agente {self.config.id} parado")
    
    def record_trade_opened(self, ticket: int, entry_price: float, volume: float):
        """Registrar abertura de trade"""
        self.trades_opened += 1
        self.history.add_event(AgentEvent.TRADE_OPENED, {
            'ticket': ticket,
            'entry_price': entry_price,
            'volume': volume
        })
        logger.info(f"🟢 Agente {self.config.id}: Trade aberto #{ticket}")
    
    def record_trade_closed(self, ticket: int, exit_price: float, profit: float):
        """Registrar fechamento de trade"""
        self.trades_closed += 1
        self.total_profit += profit
        self.history.add_event(AgentEvent.TRADE_CLOSED, {
            'ticket': ticket,
            'exit_price': exit_price,
            'profit': profit
        })
        logger.info(f"🔴 Agente {self.config.id}: Trade fechado #{ticket} | Lucro: ${profit:.2f}")
    
    def record_error(self, error_message: str):
        """Registrar erro"""
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'message': error_message
        })
        self.history.add_event(AgentEvent.ERROR, {'message': error_message})
        logger.error(f"❌ Agente {self.config.id}: Erro - {error_message}")
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do agente"""
        uptime = datetime.now() - self.started_at
        
        return {
            'id': self.config.id,
            'name': self.config.name,
            'symbol': self.config.symbol,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'trades_opened': self.trades_opened,
            'trades_closed': self.trades_closed,
            'total_profit': self.total_profit,
            'errors_count': len(self.errors),
            'indicators': [ind.type.value for ind in self.config.indicators]
        }


class AgentManager:
    """Gerenciador de agentes"""
    
    def __init__(self):
        self.generator = AgentGenerator()
        self.agents: Dict[str, ManagedAgent] = {}
        self.worker_thread = None
        self.is_running = False
        logger.info("✅ Agent Manager inicializado")
    
    def create_agent(self, command: str) -> Optional[ManagedAgent]:
        """Criar novo agente"""
        config = self.generator.create_agent(command)
        if config:
            managed_agent = ManagedAgent(config)
            self.agents[config.id] = managed_agent
            logger.info(f"✅ Agente gerenciado criado: {config.name} ({config.id})")
            return managed_agent
        return None
    
    def get_agent(self, agent_id: str) -> Optional[ManagedAgent]:
        """Obter agente por ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self, status: Optional[AgentStatus] = None) -> List[ManagedAgent]:
        """Listar agentes, opcionalmente filtrados por status"""
        if status:
            return [a for a in self.agents.values() if a.status == status]
        return list(self.agents.values())
    
    def pause_agent(self, agent_id: str) -> bool:
        """Pausar agente"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.pause()
            return True
        return False
    
    def resume_agent(self, agent_id: str) -> bool:
        """Retomar agente"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.resume()
            return True
        return False
    
    def stop_agent(self, agent_id: str) -> bool:
        """Parar agente"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.stop()
            return True
        return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deletar agente"""
        agent = self.get_agent(agent_id)
        if agent:
            agent.history.add_event(AgentEvent.DELETED)
            del self.agents[agent_id]
            logger.info(f"🗑️  Agente deletado: {agent_id}")
            return True
        return False
    
    def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """Obter estatísticas de um agente"""
        agent = self.get_agent(agent_id)
        if agent:
            return agent.get_stats()
        return None
    
    def get_all_stats(self) -> List[Dict]:
        """Obter estatísticas de todos os agentes"""
        return [agent.get_stats() for agent in self.agents.values()]
    
    def get_agent_history(self, agent_id: str, limit: int = 10) -> Optional[List[Dict]]:
        """Obter histórico de um agente"""
        agent = self.get_agent(agent_id)
        if agent:
            return agent.history.get_events(limit)
        return None
    
    def start_worker(self, check_interval: int = 30):
        """Iniciar worker que monitora agentes"""
        if self.is_running:
            logger.warning("⚠️  Worker já está rodando")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            args=(check_interval,),
            daemon=True
        )
        self.worker_thread.start()
        logger.info(f"🚀 Worker iniciado (intervalo: {check_interval}s)")
    
    def stop_worker(self):
        """Parar worker"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("⏹️  Worker parado")
    
    def _worker_loop(self, check_interval: int):
        """Loop do worker que monitora agentes"""
        logger.info("🔄 Worker loop iniciado")
        
        while self.is_running:
            try:
                # Processar agentes ativos
                active_agents = self.list_agents(AgentStatus.ACTIVE)
                
                for agent in active_agents:
                    try:
                        # Aqui você implementaria a lógica de trading
                        # Por enquanto, apenas log
                        logger.debug(f"📊 Monitorando agente: {agent.config.name}")
                        
                    except Exception as e:
                        agent.record_error(str(e))
                
                # Aguardar próximo ciclo
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no worker loop: {e}")
                time.sleep(check_interval)
    
    def get_summary(self) -> Dict:
        """Obter resumo do sistema"""
        all_agents = self.agents.values()
        active = len([a for a in all_agents if a.status == AgentStatus.ACTIVE])
        paused = len([a for a in all_agents if a.status == AgentStatus.PAUSED])
        stopped = len([a for a in all_agents if a.status == AgentStatus.STOPPED])
        
        total_trades = sum(a.trades_opened for a in all_agents)
        total_profit = sum(a.total_profit for a in all_agents)
        
        return {
            'total_agents': len(self.agents),
            'active': active,
            'paused': paused,
            'stopped': stopped,
            'total_trades': total_trades,
            'total_profit': total_profit,
            'worker_running': self.is_running
        }


# Exemplos de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = AgentManager()
    
    # Criar agentes
    print("\n" + "="*60)
    print("Criando agentes...")
    print("="*60)
    
    agent1 = manager.create_agent(
        "Criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
    )
    agent2 = manager.create_agent(
        "Criar agente EURUSD com Bollinger Bands, TP $2, SL $0.5, volume 0.05"
    )

    # Criar agente de hedge
    agent3 = manager.create_agent(
        "Criar agente de hedge entre EURUSD e GBPUSD com correlação, volume 0.05"
    )

    # Criar agente de hedge multi-ativo
    agent4 = manager.create_agent(
        "Criar agente de hedge entre EURUSD, GBPUSD e XAUUSD com RSI, volume 0.1"
    )
    
    # Listar agentes
    print("\n" + "="*60)
    print("Agentes criados:")
    print("="*60)
    for agent in manager.list_agents():
        print(f"  • {agent.config.name} ({agent.config.id})")
        print(f"    Status: {agent.status.value}")
    
    # Iniciar worker
    print("\n" + "="*60)
    print("Iniciando worker...")
    print("="*60)
    manager.start_worker(check_interval=5)
    
    # Simular eventos
    print("\n" + "="*60)
    print("Simulando eventos...")
    print("="*60)
    
    if agent1:
        agent1.record_trade_opened(123456, 2050.50, 0.1)
        time.sleep(2)
        agent1.record_trade_closed(123456, 2053.50, 3.00)
    
    # Pausar agente
    print("\n" + "="*60)
    print("Pausando agente...")
    print("="*60)
    if agent1:
        manager.pause_agent(agent1.config.id)
    
    # Obter estatísticas
    print("\n" + "="*60)
    print("Estatísticas:")
    print("="*60)
    
    summary = manager.get_summary()
    print(f"Total de agentes: {summary['total_agents']}")
    print(f"  • Ativos: {summary['active']}")
    print(f"  • Pausados: {summary['paused']}")
    print(f"  • Parados: {summary['stopped']}")
    print(f"Total de trades: {summary['total_trades']}")
    print(f"Lucro total: ${summary['total_profit']:.2f}")
    
    # Obter histórico
    print("\n" + "="*60)
    print("Histórico do agente:")
    print("="*60)
    if agent1:
        history = manager.get_agent_history(agent1.config.id)
        for event in history:
            print(f"  • {event['timestamp']}: {event['type']}")
            if event['details']:
                for key, value in event['details'].items():
                    print(f"    - {key}: {value}")
    
    # Retomar agente
    print("\n" + "="*60)
    print("Retomando agente...")
    print("="*60)
    if agent1:
        manager.resume_agent(agent1.config.id)
    
    # Parar worker
    print("\n" + "="*60)
    print("Parando worker...")
    print("="*60)
    manager.stop_worker()
    
    print("\n✅ Teste concluído!")
