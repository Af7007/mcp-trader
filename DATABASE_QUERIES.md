# Database Queries Guide - btc_trading_logs.db

## Visão Geral

O banco de dados armazena:
- **trades**: Cada ordem aberta (BUY/SELL)
- **trailing_stops**: Ativações e atualizações de trailing stops
- **cycles**: Análise de mercado a cada ciclo
- **strategy_performance**: Estatísticas de performance

As tabelas `trades` e `trailing_stops` estão **linkadas pelo trade_id**:
```
trades (id, ticket, ...) 1---< trailing_stops (trade_id, ticket, ...)
```

---

## Queries Essenciais

### 1. Ver todas as ordens (trades)

```sql
SELECT
  id as trade_id,
  ticket,
  symbol,
  trade_type,
  entry_price,
  sl_price,
  status,
  profit_loss,
  timestamp
FROM trades
ORDER BY timestamp DESC
LIMIT 20;
```

**Resultado esperado:**
```
trade_id | ticket    | symbol   | trade_type | entry_price | sl_price  | status | profit_loss | timestamp
---------|-----------|----------|------------|-------------|-----------|--------|-------------|-------------------
42       | 114435061 | XAUUSDc  | BUY        | 3984.20     | 3981.40   | OPEN   | NULL        | 2025-11-06...
41       | 114434956 | XAUUSDc  | SELL       | 3985.50     | 3989.20   | CLOSED | 2.50        | 2025-11-06...
```

---

### 2. Ver trailing stops de uma ordem específica

```sql
SELECT
  id,
  ticket,
  action,
  old_sl_price,
  new_sl_price,
  profit_dinheiro,
  trailing_distance_dinheiro,
  timestamp
FROM trailing_stops
WHERE trade_id = 42  -- Substituir pelo trade_id desejado
ORDER BY timestamp;
```

**Resultado esperado:**
```
id | ticket    | action    | old_sl_price | new_sl_price | profit_dinheiro | trailing_distance_dinheiro | timestamp
---|-----------|-----------|--------------|--------------|-----------------|--------------------------|-------------------
15 | 114435061 | ACTIVATED | NULL         | 3984.00      | 1.02            | 0.50                     | 2025-11-06 20:33:45
16 | 114435061 | MOVED_UP  | 3984.00      | 3984.50      | 2.10            | 1.50                     | 2025-11-06 20:33:47
17 | 114435061 | MOVED_UP  | 3984.50      | 3985.00      | 3.15            | 2.50                     | 2025-11-06 20:33:49
```

---

### 3. Histórico completo de uma ordem (trade + trailing)

```sql
SELECT
  t.id as trade_id,
  t.ticket,
  t.entry_price,
  t.sl_price,
  t.status,
  ts.id as trailing_id,
  ts.action,
  ts.new_sl_price,
  ts.profit_dinheiro,
  ts.timestamp
FROM trades t
LEFT JOIN trailing_stops ts ON t.id = ts.trade_id
WHERE t.ticket = 114435061  -- Substituir pelo ticket desejado
ORDER BY ts.timestamp;
```

---

### 4. Estatísticas de uma sessão

```sql
SELECT
  COUNT(*) as total_trades,
  SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_trades,
  SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
  SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
  ROUND(SUM(profit_loss), 2) as total_profit,
  ROUND(AVG(profit_loss), 2) as avg_profit,
  ROUND(SUM(CASE WHEN profit_loss > 0 THEN profit_loss ELSE 0 END), 2) as total_wins,
  ROUND(SUM(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END), 2) as total_losses
FROM trades
WHERE symbol = 'XAUUSDc'
  AND date(timestamp) = date('now');  -- Apenas hoje
```

**Resultado esperado:**
```
total_trades | closed_trades | winning_trades | losing_trades | total_profit | avg_profit
-------------|---------------|----------------|---------------|--------------|----------
42           | 40            | 28             | 12            | 125.50       | 2.98
```

---

### 5. Trades com mais trailing updates

```sql
SELECT
  t.id as trade_id,
  t.ticket,
  t.symbol,
  t.entry_price,
  COUNT(ts.id) as trailing_updates,
  SUM(CASE WHEN ts.action = 'ACTIVATED' THEN 1 ELSE 0 END) as activations,
  SUM(CASE WHEN ts.action IN ('MOVED_UP', 'MOVED_DOWN') THEN 1 ELSE 0 END) as movements,
  t.profit_loss
FROM trades t
LEFT JOIN trailing_stops ts ON t.id = ts.trade_id
GROUP BY t.id
HAVING trailing_updates > 0
ORDER BY trailing_updates DESC;
```

---

### 6. Performance do trailing stop

```sql
SELECT
  SUM(CASE WHEN action = 'ACTIVATED' THEN 1 ELSE 0 END) as total_activations,
  AVG(profit_dinheiro) as avg_profit_at_activation,
  MIN(profit_dinheiro) as min_profit_at_activation,
  MAX(profit_dinheiro) as max_profit_at_activation
FROM trailing_stops
WHERE action = 'ACTIVATED'
  AND DATE(timestamp) = DATE('now');
```

---

### 7. Ordens sem trailing (sem ativar)

```sql
SELECT
  id,
  ticket,
  entry_price,
  sl_price,
  status,
  profit_loss,
  timestamp
FROM trades t
WHERE NOT EXISTS (
  SELECT 1 FROM trailing_stops ts
  WHERE ts.trade_id = t.id
  AND ts.action = 'ACTIVATED'
)
  AND symbol = 'XAUUSDc'
ORDER BY timestamp DESC;
```

---

## Usando com Python

### Conectar ao banco

```python
import sqlite3

conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

# Ativar foreign keys
cursor.execute('PRAGMA foreign_keys = ON')
```

### Buscar trades e trailing stops

```python
# Buscar trade específico com seu histórico de trailing
cursor.execute('''
  SELECT
    t.*,
    ts.id as trailing_id,
    ts.action,
    ts.new_sl_price,
    ts.profit_dinheiro
  FROM trades t
  LEFT JOIN trailing_stops ts ON t.id = ts.trade_id
  WHERE t.ticket = ?
  ORDER BY ts.timestamp
''', (114435061,))

for row in cursor.fetchall():
  print(row)
```

### Atualizar status de um trade

```python
from datetime import datetime

cursor.execute('''
  UPDATE trades
  SET
    status = 'CLOSED',
    exit_price = ?,
    exit_reason = ?,
    profit_loss = ?,
    exit_timestamp = ?
  WHERE id = ?
''', (3987.50, 'TP', 2.50, datetime.now(), 42))

conn.commit()
```

### Estatísticas de sessão

```python
cursor.execute('''
  SELECT
    COUNT(*) as total,
    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(profit_loss), 2) as profit
  FROM trades
  WHERE symbol = 'XAUUSDc'
''')

total, wins, profit = cursor.fetchone()
print(f"Total: {total}, Wins: {wins}, Profit: ${profit}")
```

---

## Schema Completo

### Tabela: trades
```sql
CREATE TABLE trades (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  cycle_id INTEGER,
  ticket INTEGER UNIQUE,
  magic_number INTEGER,
  symbol TEXT,
  trade_type TEXT,          -- BUY/SELL
  entry_price REAL,
  sl_price REAL,
  tp_price REAL,
  volume REAL,
  strength TEXT,
  reason TEXT,
  comment TEXT,
  status TEXT,              -- OPEN/CLOSED/FAILED
  exit_price REAL,
  exit_reason TEXT,
  profit_loss REAL,
  agent_version TEXT
)
```

### Tabela: trailing_stops
```sql
CREATE TABLE trailing_stops (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  trade_id INTEGER,         -- FK -> trades(id)
  ticket INTEGER,
  symbol TEXT,
  action TEXT,              -- ACTIVATED/MOVED_UP/MOVED_DOWN
  old_sl_price REAL,
  new_sl_price REAL,
  current_price REAL,
  profit_pontos REAL,
  profit_dinheiro REAL,
  trailing_distance_pontos REAL,
  trailing_distance_dinheiro REAL,
  reason TEXT,
  agent_version TEXT
)
```

---

## Dicas

1. **Sempre use WHERE para filtrar** - O banco pode ficar grande rápido
   ```sql
   SELECT * FROM trades WHERE DATE(timestamp) = DATE('now');  -- Apenas hoje
   ```

2. **Vincular trades e trailing** - Use LEFT JOIN para manter ordens sem trailing
   ```sql
   LEFT JOIN trailing_stops ON trades.id = trailing_stops.trade_id
   ```

3. **Análise de gaps** - Ver quanto tempo entre entrada e ativação de trailing
   ```sql
   SELECT
     t.ticket,
     MIN(ts.timestamp) - t.timestamp as gap_seconds
   FROM trades t
   JOIN trailing_stops ts ON t.id = ts.trade_id
   WHERE ts.action = 'ACTIVATED'
   GROUP BY t.id;
   ```

4. **Performance do worker** - Ver frequência de updates
   ```sql
   SELECT
     trade_id,
     COUNT(*) as updates_per_trade,
     COUNT(*) * 0.02 as estimated_seconds_monitoring
   FROM trailing_stops
   GROUP BY trade_id;
   ```

---

**Status**: ✓ Database completamente linkado com order IDs
