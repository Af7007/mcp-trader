# 🤖 Agent Manager - Guia Completo

## O que é?

O **Agent Manager** gerencia o **ciclo de vida completo** dos agentes:
- ✅ Criar agentes
- ✅ Monitorar em tempo real
- ✅ Pausar/Retomar
- ✅ Parar/Deletar
- ✅ Histórico de eventos
- ✅ Estatísticas

---

## 🎯 Ciclo de Vida do Agente

```
CRIADO → ATIVO → PAUSADO → ATIVO → PARADO → DELETADO
```

### Estados

| Estado | Descrição |
|--------|-----------|
| **ACTIVE** | Agente monitorando e executando trades |
| **PAUSED** | Agente pausado, não executa trades |
| **STOPPED** | Agente parado, aguardando ação |
| **ERROR** | Agente com erro |
| **COMPLETED** | Agente completou sua tarefa |

---

## 📊 Como Usar

### 1️⃣ Criar Agente

```python
from src.agents.manager import AgentManager

manager = AgentManager()

# Criar agente
agent = manager.create_agent(
    "Criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
)

print(f"Agente criado: {agent.config.name}")
print(f"ID: {agent.config.id}")
print(f"Status: {agent.status.value}")
```

### 2️⃣ Listar Agentes

```python
# Listar todos os agentes
all_agents = manager.list_agents()
for agent in all_agents:
    print(f"  • {agent.config.name} - {agent.status.value}")

# Listar apenas agentes ativos
from src.agents.manager import AgentStatus
active_agents = manager.list_agents(AgentStatus.ACTIVE)
```

### 3️⃣ Iniciar Worker

O **worker** monitora os agentes em tempo real:

```python
# Iniciar worker (verifica agentes a cada 30 segundos)
manager.start_worker(check_interval=30)

# ... agentes rodando ...

# Parar worker
manager.stop_worker()
```

### 4️⃣ Pausar Agente

```python
# Pausar agente (não executa mais trades)
manager.pause_agent(agent.config.id)

# Retomar agente
manager.resume_agent(agent.config.id)
```

### 5️⃣ Parar Agente

```python
# Parar agente (encerra monitoramento)
manager.stop_agent(agent.config.id)
```

### 6️⃣ Deletar Agente

```python
# Deletar agente (remove do sistema)
manager.delete_agent(agent.config.id)
```

### 7️⃣ Obter Estatísticas

```python
# Estatísticas de um agente
stats = manager.get_agent_stats(agent.config.id)
print(f"Trades abertos: {stats['trades_opened']}")
print(f"Trades fechados: {stats['trades_closed']}")
print(f"Lucro total: ${stats['total_profit']:.2f}")

# Estatísticas de todos os agentes
all_stats = manager.get_all_stats()
for stat in all_stats:
    print(f"{stat['name']}: ${stat['total_profit']:.2f}")

# Resumo do sistema
summary = manager.get_summary()
print(f"Total de agentes: {summary['total_agents']}")
print(f"Ativos: {summary['active']}")
print(f"Lucro total: ${summary['total_profit']:.2f}")
```

### 8️⃣ Obter Histórico

```python
# Últimos 10 eventos
history = manager.get_agent_history(agent.config.id, limit=10)
for event in history:
    print(f"{event['timestamp']}: {event['type']}")
    print(f"  Detalhes: {event['details']}")
```

---

## 🔄 Fluxo Completo

```python
from src.agents.manager import AgentManager, AgentStatus
import time

# 1. Criar manager
manager = AgentManager()

# 2. Criar agentes
agent1 = manager.create_agent(
    "Criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
)
agent2 = manager.create_agent(
    "Criar agente EURUSD com Bollinger Bands, TP $2, SL $0.5, volume 0.05"
)

# 3. Iniciar worker
manager.start_worker(check_interval=30)

# 4. Monitorar agentes
print("Agentes rodando:")
for agent in manager.list_agents():
    print(f"  • {agent.config.name} ({agent.status.value})")

# 5. Pausar agente se necessário
manager.pause_agent(agent1.config.id)
print(f"Agente {agent1.config.id} pausado")

# 6. Retomar agente
manager.resume_agent(agent1.config.id)
print(f"Agente {agent1.config.id} retomado")

# 7. Obter estatísticas
summary = manager.get_summary()
print(f"Total de agentes: {summary['total_agents']}")
print(f"Lucro total: ${summary['total_profit']:.2f}")

# 8. Parar worker
manager.stop_worker()

# 9. Deletar agente
manager.delete_agent(agent1.config.id)
print(f"Agente {agent1.config.id} deletado")
```

---

## 📈 Eventos Registrados

Cada agente registra eventos automaticamente:

| Evento | Descrição |
|--------|-----------|
| **CREATED** | Agente criado |
| **STARTED** | Agente iniciado |
| **PAUSED** | Agente pausado |
| **RESUMED** | Agente retomado |
| **STOPPED** | Agente parado |
| **TRADE_OPENED** | Trade aberto |
| **TRADE_CLOSED** | Trade fechado |
| **ERROR** | Erro ocorreu |
| **DELETED** | Agente deletado |

---

## 🎯 Exemplo: Monitorar Agente

```python
manager = AgentManager()

# Criar agente
agent = manager.create_agent(
    "Criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
)

# Iniciar worker
manager.start_worker(check_interval=5)

# Monitorar por 60 segundos
for i in range(12):
    stats = manager.get_agent_stats(agent.config.id)
    print(f"\n[{i*5}s] Status: {stats['status']}")
    print(f"  Trades abertos: {stats['trades_opened']}")
    print(f"  Trades fechados: {stats['trades_closed']}")
    print(f"  Lucro: ${stats['total_profit']:.2f}")
    time.sleep(5)

# Parar worker
manager.stop_worker()
```

---

## 🛡️ Tratamento de Erros

```python
try:
    agent = manager.create_agent("Comando inválido")
    if not agent:
        print("Falha ao criar agente")
except Exception as e:
    print(f"Erro: {e}")

# Registrar erro manualmente
agent.record_error("Conexão perdida com MT5")

# Verificar erros
stats = manager.get_agent_stats(agent.config.id)
print(f"Erros: {stats['errors_count']}")
```

---

## 📊 Estatísticas Disponíveis

```python
stats = manager.get_agent_stats(agent.config.id)

# Informações básicas
stats['id']              # ID do agente
stats['name']            # Nome do agente
stats['symbol']          # Símbolo (ex: XAUUSDc)
stats['status']          # Status atual

# Timing
stats['started_at']      # Data/hora de início
stats['uptime_seconds']  # Tempo rodando em segundos

# Trading
stats['trades_opened']   # Total de trades abertos
stats['trades_closed']   # Total de trades fechados
stats['total_profit']    # Lucro total

# Erros
stats['errors_count']    # Total de erros

# Configuração
stats['indicators']      # Indicadores usados
```

---

## 🚀 Próximos Passos

1. **Strategy Engine** - Interpretar indicadores e gerar sinais
2. **Worker Integration** - Executar trades automaticamente
3. **Notifications** - Alertas em tempo real
4. **Dashboard** - Visualizar agentes
5. **Persistência** - Salvar agentes em banco de dados

---

**Agent Manager 100% Funcional!** ✅
