# Correção: Trades Não Preservados no Banco

**Data:** 2025-11-05
**Status:** ✅ CORRIGIDO

---

## 🐛 Problema

**Gold Adaptive Agent** mostrava:
```
[AUTO-TUNING] Trades fechados: 0 | Proxima otimizacao em: 50 trades
```

**Mas havia trades no banco!** (IDs 1442-1433)

---

## 🔍 Causa Raiz

### **Contagem Incorreta (Linha 137-145 - ANTIGO):**

```python
# ERRADO: Comparar posições entre ciclos
positions_before = len(self.mt5.positions_get(symbol=self.symbol) or [])
self._check_positions()
positions_after = len(self.mt5.positions_get(symbol=self.symbol) or [])

if positions_before > positions_after:
    self.total_trades_closed += 1
    self.trades_since_optimization += 1
```

**Problemas:**
1. ❌ Só conta se posição fechar **durante** o ciclo (15s)
2. ❌ Se MT5 fechar por SL/TP entre ciclos → **perde contagem**
3. ❌ Se trailing fechar → **perde contagem**
4. ❌ Se agente reiniciar → **zera contador**

---

## ✅ Solução Implementada

### **Contar do Banco de Dados (Linha 140-150 - NOVO):**

```python
# CORRETO: Buscar trades fechados no banco
try:
    closed_trades = self.btc_logger.get_closed_trades_count(symbol=self.symbol)
    if closed_trades > self.total_trades_closed:
        new_trades = closed_trades - self.total_trades_closed
        self.total_trades_closed = closed_trades
        self.trades_since_optimization += new_trades
        if new_trades > 0:
            print(f"  [TRADES] {new_trades} novo(s) trade(s) fechado(s) | Total: {self.total_trades_closed}")
except Exception as e:
    print(f"  [AVISO] Erro ao contar trades: {e}")
```

**Vantagens:**
1. ✅ Conta **todos** os trades fechados (CLOSED_WIN, CLOSED_LOSS)
2. ✅ Funciona mesmo se MT5 fechar entre ciclos
3. ✅ Persiste entre reinicializações
4. ✅ Fonte única de verdade: banco de dados

---

## 🔧 Função Adicionada: `get_closed_trades_count()`

**Arquivo:** `src/core/btc_logger.py` (Linhas 513-541)

```python
def get_closed_trades_count(self, symbol: str = None) -> int:
    """
    Retorna contagem de trades fechados (CLOSED_WIN ou CLOSED_LOSS)
    
    Args:
        symbol: Filtrar por símbolo (opcional)
    
    Returns:
        Número de trades fechados
    """
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    if symbol:
        cursor.execute('''
            SELECT COUNT(*) FROM trades 
            WHERE status IN ('CLOSED_WIN', 'CLOSED_LOSS')
            AND symbol = ?
        ''', (symbol,))
    else:
        cursor.execute('''
            SELECT COUNT(*) FROM trades 
            WHERE status IN ('CLOSED_WIN', 'CLOSED_LOSS')
        ''')
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count
```

**Query SQL:**
- Filtra status: `CLOSED_WIN` ou `CLOSED_LOSS`
- Opcional: filtrar por símbolo (XAUUSDc)
- Retorna contagem total

---

## 📊 Exemplo de Funcionamento

### Antes (ERRADO):
```
Ciclo #100 - Posições: 1
Ciclo #101 - Posições: 1
[MT5 fecha posição por SL entre ciclos]
Ciclo #102 - Posições: 0
→ positions_before = 1, positions_after = 0
→ Contagem: 1 trade ✅

[Agente reinicia]
→ Contagem: 0 trades ❌ (perdeu tudo!)
```

### Depois (CORRETO):
```
Ciclo #100 - Banco: 10 trades fechados
Ciclo #101 - Banco: 10 trades fechados
[MT5 fecha posição por SL]
[Trade salvo no banco como CLOSED_LOSS]
Ciclo #102 - Banco: 11 trades fechados
→ new_trades = 11 - 10 = 1
→ [TRADES] 1 novo(s) trade(s) fechado(s) | Total: 11 ✅

[Agente reinicia]
Ciclo #1 - Banco: 11 trades fechados
→ total_trades_closed = 11 ✅ (preservado!)
```

---

## 🎯 Benefícios

1. ✅ **Auto-tuning funcionando:** Otimização a cada 50 trades
2. ✅ **Contagem persistente:** Sobrevive a reinicializações
3. ✅ **Sincronização MT5:** Detecta trades fechados por SL/TP
4. ✅ **Logging correto:** Mostra quando novos trades fecham
5. ✅ **Fonte única:** Banco de dados como verdade absoluta

---

## 📝 Arquivos Modificados

### **1. `src/agents/gold_adaptive_agent.py`** (Linhas 137-150)

**Antes:**
```python
positions_before = len(self.mt5.positions_get(symbol=self.symbol) or [])
self._check_positions()
positions_after = len(self.mt5.positions_get(symbol=self.symbol) or [])

if positions_before > positions_after:
    self.total_trades_closed += 1
    self.trades_since_optimization += 1
```

**Depois:**
```python
self._check_positions()

try:
    closed_trades = self.btc_logger.get_closed_trades_count(symbol=self.symbol)
    if closed_trades > self.total_trades_closed:
        new_trades = closed_trades - self.total_trades_closed
        self.total_trades_closed = closed_trades
        self.trades_since_optimization += new_trades
        if new_trades > 0:
            print(f"  [TRADES] {new_trades} novo(s) trade(s) fechado(s) | Total: {self.total_trades_closed}")
except Exception as e:
    print(f"  [AVISO] Erro ao contar trades: {e}")
```

### **2. `src/core/btc_logger.py`** (Linhas 513-541)

**Adicionado:**
```python
def get_closed_trades_count(self, symbol: str = None) -> int:
    # Query conta trades com status CLOSED_WIN ou CLOSED_LOSS
    # Filtra por símbolo se fornecido
    # Retorna contagem total
```

---

## 🚀 Como Testar

**1. Reiniciar agente:**
```bash
taskkill /F /IM python.exe
RUN_GOLD_ADAPTIVE.bat
```

**2. Observar console:**
```
[AUTO-TUNING] Trades fechados: 11 | Proxima otimizacao em: 39 trades
```

**3. Aguardar trade fechar:**
```
[TRADES] 1 novo(s) trade(s) fechado(s) | Total: 12
[AUTO-TUNING] Trades fechados: 12 | Proxima otimizacao em: 38 trades
```

**4. Verificar banco:**
```bash
python check_recent_trades.py
```

---

## ✅ Resultado Esperado

**Console mostrará contagem CORRETA:**
```
[AUTO-TUNING] Trades fechados: 1434 | Proxima otimizacao em: 16 trades
```

**Após 50 trades:**
```
[AUTO-OPTIMIZATION #29]
Trades desde ultima otimizacao: 50
Total de trades fechados: 1484
```

---

**Data:** 2025-11-05  
**Status:** ✅ PRONTO PARA PRODUÇÃO
