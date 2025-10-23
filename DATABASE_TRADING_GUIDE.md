# 📊 Database + Trading Operations - Guia Completo

## O que foi Implementado

### 1️⃣ Database (SQLite)

**Arquivo:** `src/core/database.py`

**Tabelas:**
- `trades` - Histórico de trades (ticket, símbolo, volume, preços, status, resultado)

**Funções:**
- `setup_database()` - Criar tabelas
- `create_trade()` - Registrar novo trade
- `update_trade_status()` - Atualizar status (open/closed)
- `get_open_trades()` - Listar trades abertos

### 2️⃣ Trading Operations

**Arquivo:** `src/core/trading_operations.py`

**Classe:** `TradingOperations`

**Métodos:**
- `open_buy_order()` - Abrir ordem de compra
- `open_sell_order()` - Abrir ordem de venda
- `close_position()` - Fechar posição

---

## 🎯 Comandos do Chatbot

### Abrir Ordem de Compra

```
💬 Você: comprar EURUSD 0.1
🟢 Abrindo BUY: EURUSDc 0.1 lots
   ✅ Ordem de compra executada!
      Ticket: 105654221
      Preço: 1.16108

💬 Você: comprar XAUUSD 0.01 SL 4100 TP 4110
🟢 Abrindo BUY: XAUUSDc 0.01 lots
   ✅ Ordem de compra executada!
      Ticket: 105654222
      Preço: 4102.50
```

### Abrir Ordem de Venda

```
💬 Você: vender EURUSD 0.1
🔴 Abrindo SELL: EURUSDc 0.1 lots
   ✅ Ordem de venda executada!
      Ticket: 105654223
      Preço: 1.16100

💬 Você: vender GBPUSD 0.05 SL 1.34 TP 1.33
🔴 Abrindo SELL: GBPUSDc 0.05 lots
   ✅ Ordem de venda executada!
      Ticket: 105654224
      Preço: 1.33595
```

### Fechar Posição

```
💬 Você: fechar 105654221
🔒 Fechando posição #105654221...
   ✅ Posição fechada!
      Novo ticket: 105654872
```

### Fechar Todas as Posições

```
💬 Você: fechar tudo
🔒 Fechando TODAS as posições...
   ✅ Resultado:
      Total: 3
      Fechadas: 3
      Falhadas: 0
```

---

## 📊 Banco de Dados

### Tabela: trades

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    ticket INTEGER UNIQUE,
    symbol TEXT,
    volume REAL,
    entry_price REAL,
    sl_price REAL,
    tp_price REAL,
    status TEXT,           -- 'open' ou 'closed'
    result REAL,           -- Lucro/Prejuízo
    open_time TIMESTAMP,
    close_time TIMESTAMP,
    reason TEXT            -- 'tp', 'sl', 'manual', 'worker'
);
```

### Exemplos de Registros

```
ticket=105654221, symbol=EURUSDc, volume=0.1, entry_price=1.16108
status=open, open_time=2025-10-22 17:52:00

ticket=105654221, symbol=EURUSDc, volume=0.1, entry_price=1.16108
status=closed, result=+50.00, reason=manual, close_time=2025-10-22 17:55:00
```

---

## 🔧 Como Usar

### 1. Inicializar Database

```python
from src.core.database import setup_database

setup_database()  # Criar tabelas
```

### 2. Abrir Ordem

```python
from src.core.trading_operations import TradingOperations
import MetaTrader5 as mt5

mt5.initialize()
ops = TradingOperations()

# Comprar
result = ops.open_buy_order("EURUSDc", 0.1, sl=1.16000, tp=1.16200)
print(f"Ticket: {result['ticket']}")
print(f"Preço: {result['price']:.5f}")

# Vender
result = ops.open_sell_order("GBPUSDc", 0.05)
print(f"Ticket: {result['ticket']}")
```

### 3. Fechar Posição

```python
result = ops.close_position(105654221)
if result['success']:
    print(f"Fechada! Novo ticket: {result['order']}")
```

### 4. Consultar Trades

```python
from src.core.database import get_open_trades

trades = get_open_trades()
for trade in trades:
    print(f"Ticket: {trade['ticket']}, Símbolo: {trade['symbol']}, Volume: {trade['volume']}")
```

---

## 📈 Fluxo Completo

```
1. Usuário: "comprar EURUSD 0.1"
   ↓
2. Chatbot extrai: símbolo=EURUSD, volume=0.1
   ↓
3. TradingOperations.open_buy_order()
   - Obter preço atual
   - Enviar ordem ao MT5
   - Registrar no BD
   ↓
4. Resultado:
   - Ticket: 105654221
   - Preço: 1.16108
   - Status: open (no BD)
   ↓
5. Usuário: "fechar 105654221"
   ↓
6. MT5PositionCloser.close_position()
   - Fechar no MT5
   - Atualizar BD (status=closed)
   ↓
7. Resultado: Posição fechada
```

---

## 🎯 Sintaxe dos Comandos

### Comprar

```
comprar <SÍMBOLO> <VOLUME> [SL <PREÇO>] [TP <PREÇO>]

Exemplos:
  comprar EURUSD 0.1
  comprar XAUUSD 0.01 SL 4100 TP 4110
  comprar GBPUSD 0.05 TP 1.34
```

### Vender

```
vender <SÍMBOLO> <VOLUME> [SL <PREÇO>] [TP <PREÇO>]

Exemplos:
  vender EURUSD 0.1
  vender XAUUSD 0.01 SL 4110 TP 4100
  vender GBPUSD 0.05 SL 1.34
```

### Fechar

```
fechar <TICKET>
fechar tudo

Exemplos:
  fechar 105654221
  fechar tudo
```

---

## 📊 Todos os Comandos

```
📊 Informações:
  • 'saldo' - Ver saldo
  • 'posições' - Ver posições
  • 'preço EURUSD' - Ver preço
  • 'resumo' - Ver resumo

🤖 Agentes:
  • 'criar agente EURUSD com RSI' - Criar
  • 'listar agentes' - Listar
  • 'pausar agente <ID>' - Pausar
  • 'retomar agente <ID>' - Retomar
  • 'parar agente <ID>' - Parar
  • 'deletar agente <ID>' - Deletar
  • 'stats agente <ID>' - Stats

⚙️  Worker:
  • 'iniciar worker' - Iniciar
  • 'parar worker' - Parar

💰 Trading:
  • 'comprar EURUSD 0.1' - Comprar
  • 'vender EURUSD 0.1' - Vender
  • 'fechar 123456' - Fechar
  • 'fechar tudo' - Fechar todas

🛠️  Utilitários:
  • 'ajuda' - Ajuda
  • 'sair' - Sair
```

---

## ✨ Destaques

- ✅ Persistência em SQLite
- ✅ Histórico de trades
- ✅ Integração com MT5
- ✅ Retry automático
- ✅ Tratamento de erros robusto
- ✅ Logging detalhado

---

**Database + Trading Operations 100% Integrados!** ✅
