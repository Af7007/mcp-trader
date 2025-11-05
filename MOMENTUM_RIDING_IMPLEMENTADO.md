# Momentum Riding - Aproveitar a Onda

**Data:** 2025-11-04
**Status:** ✅ IMPLEMENTADO

---

## 🎯 Conceito

**Momentum Riding:** Fazer trades consecutivos na **mesma direção** quando está **ganhando**, aproveitando a onda do mercado!

---

## 🔥 Como Funciona

### Regra de Ouro:
```
WIN na mesma direção → Cooldown REDUZIDO (15s)
WIN em direção oposta → Cooldown NORMAL (120s)
LOSS → Cooldown NORMAL (120s) + Sem streak
```

---

## 📊 Exemplo Prático

### Cenário: Onda de SELL

```
19:00:00 - SELL abre em $3935
19:01:30 - SELL fecha com +$1.20 ✅ (WIN #1)
         → last_trade_was_win = True
         → consecutive_wins_same_direction = 1
         → Cooldown reduzido: 15 segundos!

19:01:45 - [ONDA] Aguardando 0s para próximo SELL (win streak: 1)
19:01:45 - [ONDA] Aproveitando momentum! Abrindo SELL consecutivo (win #2)
19:01:45 - SELL abre em $3934.80

19:03:00 - SELL fecha com +$1.50 ✅ (WIN #2)
         → consecutive_wins_same_direction = 2
         → Cooldown: 15 segundos!

19:03:15 - [ONDA] Aproveitando momentum! Abrindo SELL consecutivo (win #3)
19:03:15 - SELL abre em $3933.50

19:04:20 - SELL fecha com +$1.80 ✅ (WIN #3)
         → 🔥 WIN STREAK: 3 SELL consecutivos!
         → Total ganho: $4.50 em 4 minutos!

19:04:35 - [ONDA] Aproveitando momentum! Abrindo SELL consecutivo (win #4)
         ...

RESULTADO: Aproveitou a queda! 🚀
```

---

## ⚡ Tabela de Cooldowns

| Situação | Último Trade | Streak | Cooldown | Exemplo |
|----------|--------------|--------|----------|---------|
| **ONDA!** | WIN (mesma dir) | 1+ | **15s** ⚡ | SELL→SELL |
| Mudança Win | WIN (outra dir) | 0 | 120s + 5min | SELL→BUY |
| Após Loss | LOSS | 0 | 120s | Qualquer |
| Mudança Loss | LOSS (outra dir) | 0 | 120s + 5min | SELL→BUY |

---

## 🔍 Lógica Implementada

### 1. Variáveis de Rastreamento (Linhas 115-118)

```python
self.cooldown_same_direction = 15  # 15 segundos (aproveita onda!)
self.last_trade_was_win = False
self.consecutive_wins_same_direction = 0
```

### 2. Cooldown Dinâmico (Linhas 496-520)

```python
if is_same_direction and self.last_trade_was_win:
    # APROVEITANDO A ONDA!
    cooldown_to_use = 15  # Reduzido!
    print(f"[ONDA] Aproveitando momentum! Win #{streak + 1}")
else:
    # Direção diferente ou loss
    cooldown_to_use = 120  # Normal
```

### 3. Rastreamento de Wins (Linhas 684-699)

```python
if is_win:
    # Incrementar win streak se mesma direção
    if mesma_direção_que_anterior:
        consecutive_wins_same_direction += 1
        print(f"🔥 WIN STREAK: {streak} ({tipo})")
    else:
        consecutive_wins_same_direction = 1
else:
    consecutive_wins_same_direction = 0  # Resetar
```

---

## 🎯 Vantagens

1. **Aproveita Tendências Fortes:** Entra múltiplas vezes quando mercado está em movimento
2. **Cooldown Inteligente:** Rápido quando ganhando, lento quando perdendo
3. **Maximiza Lucros:** Pega onda completa ao invés de só 1 trade
4. **Proteção:** Se perder, para imediatamente (cooldown volta para 120s)
5. **Win Streak Visível:** Console mostra quantos wins consecutivos

---

## 📊 Comparação

### Antes (SEM Momentum Riding):
```
19:00 - SELL +$1.20 ✅
19:02 - Aguarda 120s...
19:02 - Aguarda 120s...
19:04 - BUY abre (perdeu a onda SELL!)
TOTAL: $1.20 ganho
```

### Depois (COM Momentum Riding):
```
19:00 - SELL +$1.20 ✅
19:00 - Aguarda 15s...
19:00 - SELL +$1.50 ✅
19:01 - Aguarda 15s...
19:01 - SELL +$1.80 ✅
19:01 - Aguarda 15s...
19:02 - SELL +$2.00 ✅
TOTAL: $6.50 ganho 🔥
```

**5x mais lucro aproveitando a onda!**

---

## ⚠️ Proteções

1. **Só ativa se WIN:** Loss reseta tudo
2. **Mesma direção:** BUY→SELL não aproveita
3. **Cooldown mínimo:** 15s evita overtrading
4. **Circuit Breaker:** 5 losses consecutivas = pausa total
5. **Filtro de mudança:** Trocar direção = 5 minutos espera

---

## 🧪 Console Output Esperado

```
[POSIÇÃO FECHADA PELO MT5] Ticket: 112620001
   Resultado: [WIN]
   🔥 WIN STREAK na mesma direção: 1 (SELL)

[ONDA] Aguardando 10s para próximo SELL (win streak: 1)
[ONDA] Aguardando 5s para próximo SELL (win streak: 1)
[ONDA] Aproveitando momentum! Abrindo SELL consecutivo (win #2)

[POSIÇÃO ABERTA]: SELL $3934.20
   Volume: 0.01 lotes
   Trailing ativa com: 1680 pts = $1.68 lucro

... (mais trades na mesma direção)

🔥 WIN STREAK na mesma direção: 4 (SELL)
```

---

## 📝 Arquivos Modificados

**`src/agents/gold_loss_zero_simple.py`**

| Linhas | Mudança | Descrição |
|--------|---------|-----------|
| 115 | Adicionado | `cooldown_same_direction = 15` |
| 117-118 | Adicionado | Variáveis de rastreamento de wins |
| 496-520 | Modificado | Cooldown dinâmico (15s vs 120s) |
| 684-699 | Adicionado | Rastreamento de win streaks |

---

## 🚀 Como Usar

**Reinicie:**
```bash
taskkill /F /IM python.exe
RUN_GOLD_ADAPTIVE.bat
```

**Aguarde:**
1. Trade fecha com WIN
2. Mercado continua na mesma direção
3. **15 segundos depois**: Abre próximo trade!
4. Se WIN novamente: Repete!
5. Se LOSS: Para (cooldown 120s)

---

## 🎯 Expectativa

**Trades com Momentum:**
- 3-5 trades consecutivos em tendências fortes
- $3-10 lucro total por onda
- Win rate mantido (mesma estratégia)

**Proteção:**
- Se perder 1 trade: Para imediatamente
- Não alterna BUY/SELL freneticamente
- Circuit breaker continua ativo

---

**Resultado:** Sistema aproveita ondas fortes enquanto mantém proteções! 🚀🔥

---

**Data:** 2025-11-04  
**Status:** ✅ PRONTO PARA TESTES
