# 🔄 MCP Client vs MT5 Native - Tipos de Retorno

**Data**: 2025-11-01 14:00 UTC
**Status**: ✅ DOCUMENTADO E CORRIGIDO
**Problema**: Confusão entre dicts (MCP) e objetos (MT5 nativo)

---

## 🎯 Problema Identificado

O código estava misturando duas formas de acessar resultados MT5:
1. **MCP Client** (wrapper HTTP) → retorna **dicts**
2. **MT5 Nativo** (biblioteca Python) → retorna **objetos**

Isso causava erros alternados:
- `'OrderSendResult' object has no attribute 'get'`
- `'dict' object has no attribute 'retcode'`

---

## 📊 Diferenças Fundamentais

### MCP Client (self.mt5)

```python
from core.mt5_mcp_client import get_mt5_client

mt5 = get_mt5_client()  # Wrapper MCP via HTTP

# Chamadas MCP retornam DICTS
result = mt5.buy_market(symbol="BTCUSDc", volume=0.01)
# result = {'retcode': 10009, 'order': 123456, ...}  ← DICT!

# Acesso: usar .get()
if result.get('retcode') == 10009:  ✅
    ticket = result.get('order')    ✅
```

### MT5 Nativo (import MetaTrader5)

```python
import MetaTrader5 as mt5

mt5.initialize()

# Chamadas MT5 nativas retornam OBJETOS
request = {"action": mt5.TRADE_ACTION_DEAL, ...}
result = mt5.order_send(request)
# result = OrderSendResult(retcode=10009, order=123456, ...)  ← OBJETO!

# Acesso: usar atributos diretos
if result.retcode == 10009:  ✅
    ticket = result.order    ✅
```

---

## 🔧 Regras de Uso no Código

### Usar `.get()` (MCP Client - DICTS)

| Método | Tipo de Retorno | Acesso |
|--------|-----------------|--------|
| `self.mt5.buy_market()` | **dict** | `result.get('retcode')` ✅ |
| `self.mt5.sell_market()` | **dict** | `result.get('order')` ✅ |
| `self.mt5.close_position()` | **dict** | `result.get('retcode')` ✅ |
| `self.mt5.positions_get()` | **list of dicts** | `pos.get('ticket')` ✅ |
| `self.mt5.copy_rates_from_pos()` | **list of dicts** | `rate.get('close')` ✅ |

### Usar Atributos (MT5 Nativo - OBJETOS)

| Método | Tipo de Retorno | Acesso |
|--------|-----------------|--------|
| `mt5.order_send()` | **OrderSendResult** | `result.retcode` ✅ |
| `mt5.order_check()` | **OrderCheckResult** | `result.retcode` ✅ |
| `mt5.symbol_info()` | **SymbolInfo** | `info.bid` ✅ |
| `mt5.account_info()` | **AccountInfo** | `account.balance` ✅ |

---

## 📝 Locais Corrigidos no Código

### 1. `_open_position()` - Lines 258, 260, 287

```python
# Usa self.mt5.buy_market() e self.mt5.sell_market()
# Esses métodos são do MCP → retornam DICT

# ✅ CORRETO (dict)
if result and result.get('retcode') == 10009:
    self.entry_ticket = result.get('order')
```

**Por quê dict?** Porque `self.mt5.buy_market()` chama o MCP server via HTTP.

### 2. `_close_position_with_profit()` - Line 436

```python
# Usa self.mt5.close_position()
# Esse método é do MCP → retorna DICT

# ✅ CORRETO (dict)
if result and result.get('retcode') == 10009:
```

**Por quê dict?** Porque `self.mt5.close_position()` chama o MCP server.

### 3. `_update_position_sl()` - Line 419

```python
# Usa mt5.order_send() DIRETO (import MetaTrader5)
# Esse método é NATIVO → retorna OBJETO

import MetaTrader5 as mt5
result = mt5.order_send(request)

# ✅ CORRETO (objeto)
if result and result.retcode == 10009:
```

**Por quê objeto?** Porque `mt5.order_send()` chama MT5 diretamente, não via MCP.

---

## 🤔 Por Que Essa Diferença Existe?

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│ AGENTE BTC LOSS ZERO                                │
│                                                     │
│  [1] self.mt5 = get_mt5_client()                   │
│       ↓                                             │
│  [2] MCP Client (HTTP Wrapper)                     │
│       ↓                                             │
│  [3] MCP Server (JSON over HTTP)                   │
│       ↓                                             │
│  [4] MetaTrader5 Python Library                    │
│       ↓                                             │
│  [5] MT5 Terminal                                   │
└─────────────────────────────────────────────────────┘

PROBLEMA:
- MCP Server converte objetos MT5 → JSON (dicts)
- JSON é enviado via HTTP
- MCP Client recebe JSON e retorna como dict
```

**Resultado:**
- `self.mt5.*` → passa pelo MCP → **dicts**
- `mt5.*` direto → não passa pelo MCP → **objetos**

---

## ✅ Como Identificar Qual Usar?

### Regra Simples

```python
# Se usa self.mt5 → MCP → dict → .get()
result = self.mt5.buy_market(...)
if result.get('retcode') == 10009:  ✅

# Se importa MetaTrader5 → Nativo → objeto → .atributo
import MetaTrader5 as mt5
result = mt5.order_send(...)
if result.retcode == 10009:  ✅
```

### Dica Visual

```python
# ❓ Como saber?
# Olhe como foi obtido:

# [A] Via self.mt5
result = self.mt5.alguma_coisa()
# → Acesso: result.get('chave')

# [B] Via import direto
import MetaTrader5 as mt5
result = mt5.alguma_coisa()
# → Acesso: result.atributo
```

---

## 🔄 Exemplo Prático Completo

### Cenário: Abrir Posição e Atualizar SL

```python
class BTCLossZeroOtimizado:
    def __init__(self):
        # MCP Client
        self.mt5 = get_mt5_client()

    def _open_position(self, signal):
        # Usar MCP → retorna dict
        result = self.mt5.buy_market(
            symbol="BTCUSDc",
            volume=0.01,
            sl=110000,
            tp=110100
        )

        # ✅ DICT - usar .get()
        if result and result.get('retcode') == 10009:
            ticket = result.get('order')  # dict access
            logger.info(f"Posição aberta: {ticket}")

    def _update_position_sl(self, ticket, new_sl):
        # Importar MT5 nativo
        import MetaTrader5 as mt5

        # Usar MT5 direto → retorna objeto
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": new_sl,
        }

        result = mt5.order_send(request)

        # ✅ OBJETO - usar atributo
        if result and result.retcode == 10009:  # object access
            logger.info(f"SL atualizado para {new_sl}")
```

---

## 📋 Checklist de Validação

Ao adicionar novo código MT5:

- [ ] Identifiquei se usa `self.mt5` ou `import MetaTrader5`?
- [ ] Se `self.mt5` → usar `.get()` para acessar resultados
- [ ] Se `import MetaTrader5` → usar `.atributo` para acessar resultados
- [ ] Testei o código para garantir sem AttributeError?
- [ ] Documentei no código qual tipo está sendo usado?

---

## 🎯 Resumo Visual

```
╔═══════════════════════════════════════════════════════════╗
║ GUIA RÁPIDO: MCP vs MT5                                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  self.mt5 (MCP Client)                                   ║
║  ├─ Retorna: DICT                                        ║
║  └─ Acesso: result.get('retcode')  ✅                    ║
║                                                           ║
║  import MetaTrader5 as mt5 (Nativo)                      ║
║  ├─ Retorna: OBJETO                                      ║
║  └─ Acesso: result.retcode  ✅                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🚀 Status Atual

✅ **Código Corrigido**
✅ **Testes Passando (6/6)**
✅ **Documentação Completa**
✅ **Padrão Estabelecido**

**Regra de Ouro:**
- MCP → Dict → `.get()`
- MT5 Nativo → Objeto → `.atributo`

---

**Documento criado**: 2025-11-01 14:00 UTC
**Versão**: 1.0 (Definitivo)
