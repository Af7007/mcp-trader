# 🏗️ Arquitetura MCP Centralizada

## 📋 Visão Geral

Todo o sistema agora usa **UMA ÚNICA CONEXÃO** com o MetaTrader 5 através do **MCP Server**. Isso garante:

✅ **Sem conflitos** - Apenas uma conexão ativa com MT5
✅ **Centralizado** - Toda comunicação passa pelo MCP
✅ **Confiável** - Gerenciamento consistente de estado
✅ **Escalável** - Fácil adicionar novos componentes

---

## 🔧 Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    APLICAÇÕES                           │
│  ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Web Dashboard│  │  Worker  │  │ Chatbot/Agents  │  │
│  └──────┬──────┘  └────┬─────┘  └────────┬─────────┘  │
│         │              │                   │             │
│         └──────────────┼───────────────────┘             │
│                        │                                 │
└────────────────────────┼─────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   MT5 MCP Client (Singleton)  │  ← Única instância
         │   src/core/mt5_mcp_client.py  │
         └───────────────┬───────────────┘
                         │
                         ▼ HTTP (porta 8000)
         ┌───────────────────────────────┐
         │     MT5 MCP Server            │
         │     (FastMCP)                 │
         └───────────────┬───────────────┘
                         │
                         ▼ DLL
         ┌───────────────────────────────┐
         │   MetaTrader 5 Terminal       │
         └───────────────────────────────┘
```

---

## 📁 Arquivos Principais

### 1. Cliente MCP (Centralizado)
**`src/core/mt5_mcp_client.py`**
- Classe `MT5MCPClient` - Cliente para comunicação com MCP
- Função `get_mt5_client()` - Retorna instância singleton
- **TODOS os componentes usam este cliente!**

### 2. MT5 MCP Server
**`src/mcp_mt5/main.py`**
- Servidor FastMCP que conecta ao MT5 Terminal
- Expõe ferramentas (tools) via HTTP
- Porta: **8000**

### 3. Componentes que Usam o Cliente

**Worker** (`src/core/main.py`)
```python
from core.mt5_mcp_client import get_mt5_client

mt5_client = get_mt5_client()
positions = mt5_client.positions_get()
```

**Web App** (`src/web/app.py`)
```python
from core.mt5_mcp_client import get_mt5_client

mt5_client = get_mt5_client()
account = mt5_client.get_account_info()
```

**Agentes** (quando implementados)
```python
from core.mt5_mcp_client import get_mt5_client

mt5_client = get_mt5_client()
symbol_info = mt5_client.get_symbol_info("EURUSD")
```

---

## 🚀 Como Iniciar

### Passo 1: Certifique-se que o MT5 está aberto e logado

### Passo 2: Inicie o MT5 MCP Server

**Terminal 1:**
```powershell
cd C:\mcp-trader
uv run python start_mt5_http.py
```

Aguarde ver:
```
🚀 Iniciando MT5 MCP Server em modo HTTP
🌐 Host: 127.0.0.1
🔌 Port: 8000
```

### Passo 3: Teste a conexão MCP

**Terminal 2:**
```powershell
cd C:\mcp-trader
uv run python test_mcp_connection.py
```

Você deve ver 6 testes passando:
- ✅ Health Check
- ✅ Conexão verificada
- ✅ Informações da conta
- ✅ Posições abertas
- ✅ Símbolos disponíveis
- ✅ Informações de símbolo

### Passo 4: Inicie os outros serviços

**Terminal 3 - Web Dashboard:**
```powershell
uv run python run_simple_web.py
```

**Terminal 4 - Worker (opcional):**
```powershell
uv run python src\core\main.py
```

---

## 📡 API do Cliente MCP

### Account Information
```python
mt5_client = get_mt5_client()

# Informações da conta
account = mt5_client.get_account_info()
print(f"Saldo: ${account['balance']}")

# Informações do terminal
terminal = mt5_client.get_terminal_info()

# Versão do MT5
version = mt5_client.get_version()
```

### Symbols
```python
# Todos os símbolos
symbols = mt5_client.get_symbols()

# Símbolos por grupo
forex = mt5_client.get_symbols(group="Forex*")

# Informações de um símbolo
eurusd = mt5_client.get_symbol_info("EURUSD")
print(f"Bid: {eurusd['bid']}, Ask: {eurusd['ask']}")

# Último tick
tick = mt5_client.get_symbol_info_tick("EURUSD")
```

### Market Data
```python
# Barras de preço
rates = mt5_client.copy_rates_from_pos(
    symbol="EURUSD",
    timeframe="H1",
    start_pos=0,
    count=100
)
```

### Trading
```python
# Posições abertas
positions = mt5_client.positions_get()
for pos in positions:
    print(f"{pos['symbol']}: {pos['profit']}")

# Posição específica
position = mt5_client.positions_get(ticket=123456)

# Ordens pendentes
orders = mt5_client.orders_get()

# Histórico de deals
deals = mt5_client.history_deals_get(
    position=123456
)
```

### Trading Operations
```python
# Comprar
result = mt5_client.buy_market(
    symbol="EURUSD",
    volume=0.01,
    sl=1.0800,
    tp=1.0900,
    comment="Compra via MCP"
)

# Vender
result = mt5_client.sell_market(
    symbol="EURUSD",
    volume=0.01,
    sl=1.0900,
    tp=1.0800
)

# Fechar posição
result = mt5_client.close_position(ticket=123456)
```

### Health Check
```python
# Verificar saúde do servidor
health = mt5_client.health()

# Verificar se está conectado
if mt5_client.is_connected():
    print("MCP conectado!")
```

---

## ✅ Vantagens desta Arquitetura

1. **Singleton Pattern**: Apenas uma instância do cliente
2. **Centralização**: Todas as chamadas passam pelo mesmo ponto
3. **Consistência**: Estado compartilhado entre componentes
4. **Debugging**: Fácil adicionar logging centralizado
5. **Manutenção**: Mudanças no cliente afetam todos os componentes
6. **Escalabilidade**: Fácil adicionar novos componentes

---

## 🔧 Troubleshooting

### Erro: "Connection refused"
**Problema**: MT5 MCP Server não está rodando
**Solução**: Execute `python start_mt5_http.py`

### Erro: "Not Acceptable (406)"
**Problema**: Servidor não está em modo HTTP
**Solução**: Verifique se `start_mt5_http.py` está configurado para HTTP

### Erro: "MT5 initialization failed"
**Problema**: MT5 Terminal não está aberto
**Solução**: Abra o MetaTrader 5 e faça login

### Timeout
**Problema**: MT5 não responde
**Solução**:
1. Verifique se MT5 está logado
2. Reinicie o MT5 Terminal
3. Reinicie o MCP Server

---

## 📝 Adicionar Novo Componente

Para adicionar um novo componente que precisa acessar o MT5:

```python
# No seu novo componente
from core.mt5_mcp_client import get_mt5_client

# Obter cliente (singleton)
mt5_client = get_mt5_client()

# Usar o cliente
account = mt5_client.get_account_info()
positions = mt5_client.positions_get()
```

**É isso!** Não precisa se preocupar com conexão, inicialização, ou conflitos.

---

## 🎯 Próximos Passos

1. ✅ Cliente MCP centralizado criado
2. ✅ Worker atualizado
3. ✅ Web App atualizado
4. ⏳ Agentes precisam ser atualizados (quando implementados)
5. ⏳ Adicionar métricas e monitoring
6. ⏳ Adicionar cache para reduzir chamadas

---

**Documentação criada em:** 23/10/2025
**Versão:** 1.0
