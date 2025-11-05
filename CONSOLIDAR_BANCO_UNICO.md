# CONSOLIDACAO - BANCO DE DADOS UNICO

**Data:** 2025-11-04
**Objetivo:** Usar apenas `btc_trading_logs.db` para todos os registros

---

## SITUACAO ATUAL

Existem **3 bancos diferentes**:

| Banco | Tamanho | Uso |
|-------|---------|-----|
| **btc_trading_logs.db** | 16 MB | BTCLogger (principal) - 1333 trades |
| trading_bot.db | 68 KB | database.py (chatbot) |
| trading.db | 32 KB | game_api.py (web game) |

---

## DECISAO

**Manter apenas:** `btc_trading_logs.db`

**Razoes:**
1. Ja tem 1333 trades registrados
2. Possui todas as tabelas necessarias:
   - `trades` - Trades executados
   - `cycles` - Ciclos de analise
   - `trailing_stops` - Historico de trailing
   - `strategy_performance` - Performance de estrategias
3. E o banco usado pelo agente Gold atual
4. Tem estrutura completa e otimizada

---

## ARQUIVOS QUE USAM BANCOS

### 1. BTCLogger (JA USA btc_trading_logs.db) ✓

**Arquivo:** `src/core/btc_logger.py`
```python
def __init__(self, db_path: str = "btc_trading_logs.db"):
```

**Usado por:**
- `src/agents/gold_loss_zero_simple.py`
- `src/agents/btc_hedge_agent.py`

**Status:** ✓ JA CORRETO

### 2. Database Module (USA trading_bot.db)

**Arquivo:** `src/core/database.py`
```python
DB_FILE = "trading_bot.db"  # MUDAR PARA btc_trading_logs.db
```

**Usado por:**
- Chatbot
- Agentes antigos

**Acao:** Alterar para usar btc_trading_logs.db

### 3. Game API (USA trading.db)

**Arquivo:** `src/web/game_api.py`
```python
# Usa trading.db para game_history
```

**Status:** Separado (ok para manter game isolado)

---

## CORRECOES NECESSARIAS

### ✓ Ja Corrigido: BTCLogger retorna trade_id

```python
def log_trade(self, trade_data: dict, cycle_id: int = None):
    # ...
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return trade_id  # AGORA RETORNA!
```

### Opcional: Unificar database.py (se necessario)

Se voce quiser que o chatbot tambem use o mesmo banco:

```python
# src/core/database.py (linha 13)
# ANTES:
DB_FILE = "trading_bot.db"

# DEPOIS:
DB_FILE = "btc_trading_logs.db"
```

**NOTA:** Isso requer adicionar as tabelas do chatbot ao btc_trading_logs.db ou migrar dados.

---

## RESUMO

### CONFIGURACAO RECOMENDADA (ATUAL)

1. **btc_trading_logs.db** - Agentes de trading (Gold, BTC, etc)
   - 1333 trades
   - Trailing stops
   - Ciclos de analise
   - Performance

2. **trading.db** - Game web apenas
   - Historico do jogo
   - Separado do trading real

3. **trading_bot.db** - Chatbot (opcional)
   - Pode ser migrado para btc_trading_logs.db se necessario

---

## VERIFICACAO

### Verificar qual banco esta sendo usado:

```bash
# Ver trades recentes
python check_recent_trades.py

# Ver todos os bancos
python check_all_databases.py

# Ver config atual do Gold agent
grep -n "btc_logger" src/agents/gold_loss_zero_simple.py
```

### Resultado esperado:

```
[GOLD] Usando banco: btc_trading_logs.db
[DB] Trade registrado - ID: 1334
```

---

## STATUS ATUAL

✓ **Gold Agent** usa `btc_trading_logs.db` corretamente
✓ **BTCLogger** retorna trade_id agora
✓ **Trailing stops** serao salvos com trade_id correto
✓ **Trades** estao sendo salvos (1333 registros)

**Problema resolvido:** Usuario pensou que trades nao estavam sendo salvos, mas estavam em `btc_trading_logs.db` (nao em `trading.db`).

---

## COMANDOS UTEIS

### Ver trades recentes:
```bash
python check_recent_trades.py
```

### Query SQL direta:
```bash
sqlite3 btc_trading_logs.db "SELECT COUNT(*) FROM trades"
sqlite3 btc_trading_logs.db "SELECT * FROM trades ORDER BY id DESC LIMIT 5"
```

### Backup do banco:
```bash
copy btc_trading_logs.db btc_trading_logs_backup_20251104.db
```

---

## CONCLUSAO

**Banco principal:** `btc_trading_logs.db`
**Status:** ✓ FUNCIONANDO CORRETAMENTE
**Trades salvos:** 1333 registros
**Correcao aplicada:** log_trade retorna trade_id

Nao e necessario consolidar os outros bancos a menos que voce queira unificar tudo em um unico arquivo. O sistema atual esta funcional.
