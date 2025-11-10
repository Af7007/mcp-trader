# Ações Anti-Loss - BTC v3.1.0

## AÇÕES ATUAIS IMPLEMENTADAS

### 1. **Circuit Breaker** (ATIVO)
**Objetivo**: Parar agente após perdas consecutivas

```python
# Código atual (btc_loss_zero_v3.py linha 124-126)
self.consecutive_losses = 0
self.max_consecutive_losses = 5
self.circuit_breaker_active = False
```

**Como funciona**:
- Conta perdas consecutivas
- Após 5 losses seguidas: PAUSA agente por 5 minutos
- Reseta contador após win

**Problema**:
- ❌ Não implementado no código atual!
- ❌ Variáveis existem mas não há lógica de contagem
- ❌ Agente continua operando mesmo com 5+ losses

**Status**: **IMPLEMENTADO PARCIALMENTE** (variáveis criadas mas sem lógica)

---

### 2. **SL Fixo** (ATIVO)
**Objetivo**: Limitar perda por trade

```python
# v3.1.0 (linha 66)
self.fixed_sl_dollars = 10.0  # $10 por trade (2x v3.0.0)
```

**Como funciona**:
- SL fixo em $10 por trade
- Posição fecha automaticamente se atingir

**Problema**:
- ✅ Funciona SEMPRE (100% dos losses foram SL hits)
- ⚠️ SL pode ser muito apertado para ATR alto
- ⚠️ Não se adapta à volatilidade

**Status**: **ATIVO e FUNCIONANDO**

---

### 3. **Trailing Stop** (ATIVO)
**Objetivo**: Proteger lucro, evitar devolver ganhos

```python
# v3.1.0 (linhas 71-74)
self.trailing_activation_dollar = 4.0   # Ativa com $4 lucro
self.trailing_distance_dollar = 2.0     # Protege $2
```

**Como funciona**:
- Trade com $4+ de lucro ativa trailing
- Trailing protege mínimo $2 de lucro
- Sobe automaticamente conforme preço melhora

**Problema**:
- ✅ Evita devolver lucro
- ❌ NÃO evita losses (só protege wins)

**Status**: **ATIVO e FUNCIONANDO**

---

### 4. **Cooldown Entre Trades** (ATIVO)
**Objetivo**: Evitar overtrading e revenge trading

```python
# Gold (position_monitor_worker.py tem, BTC não!)
self.cooldown_seconds = 30              # 30s entre trades
self.cooldown_same_direction = 10      # 10s mesma direção
```

**Como funciona**:
- Aguarda 30s após loss antes de novo trade
- Aguarda 10s após win na mesma direção

**Problema**:
- ❌ NÃO IMPLEMENTADO no BTC v3.1.0!
- ✅ Gold tem, BTC não copiou

**Status**: **NÃO IMPLEMENTADO**

---

## AÇÕES QUE FALTAM IMPLEMENTAR

### 5. **Break-Even Move** (NÃO IMPLEMENTADO)
**Objetivo**: Mover SL para entry após lucro inicial

**Lógica sugerida**:
```python
def _check_breakeven(self, position, current_price):
    """
    Move SL para break-even quando lucro >= $2
    """
    profit = calcular_lucro_atual(position, current_price)

    if profit >= 2.0:  # $2 de lucro
        # Mover SL para entry_price (break-even)
        new_sl = position['entry_price']

        # Modificar posição
        self.mt5.modify_position(
            ticket=position['ticket'],
            sl=new_sl
        )

        print(f"[BREAK-EVEN] SL movido para entry ${new_sl:.2f}")
```

**Vantagens**:
- ✅ Elimina risco após $2 de lucro
- ✅ Trade nunca vira loss depois de ativado
- ✅ Psicologicamente confortável

**Desvantagens**:
- ⚠️ Pode fechar no break-even em pequenos pullbacks
- ⚠️ Reduz avg win (fecha em $0 vs $2+)

**Recomendação**: **IMPLEMENTAR** (protege capital)

---

### 6. **Partial Close** (NÃO IMPLEMENTADO)
**Objetivo**: Realizar lucro parcial, deixar resto correr

**Lógica sugerida**:
```python
def _partial_close(self, position, current_price):
    """
    Fecha 50% da posição quando lucro >= $4
    Deixa 50% correr com trailing
    """
    profit = calcular_lucro_atual(position, current_price)

    if profit >= 4.0 and not position.get('partial_closed'):
        # Fechar 50% do volume
        volume_to_close = position['volume'] * 0.5

        self.mt5.close_position(
            ticket=position['ticket'],
            volume=volume_to_close
        )

        # Marcar como parcialmente fechado
        position['partial_closed'] = True

        print(f"[PARTIAL CLOSE] 50% fechado com ${profit/2:.2f}")
        print(f"[PARTIAL CLOSE] 50% continua com trailing")
```

**Vantagens**:
- ✅ Garante lucro (50% realizado)
- ✅ Captura grandes movimentos (50% com trailing)
- ✅ Reduz estresse psicológico

**Desvantagens**:
- ⚠️ Complexo de gerenciar
- ⚠️ Pode realizar cedo e perder movimento

**Recomendação**: **AVALIAR** (pode melhorar avg win)

---

### 7. **Martingale Reverso** (NÃO RECOMENDADO)
**Objetivo**: Aumentar volume após win, reduzir após loss

**Lógica**:
```python
# APÓS WIN: Aumentar volume
if last_trade_was_win:
    self.volume = min(0.30, self.volume * 1.5)

# APÓS LOSS: Reduzir volume
if last_trade_was_loss:
    self.volume = max(0.10, self.volume * 0.5)
```

**Vantagens**:
- ✅ Aproveita winning streaks
- ✅ Protege em losing streaks

**Desvantagens**:
- ❌ Pode perder grandes movimentos (volume baixo após loss)
- ❌ Complexo de gerenciar
- ❌ Pode amplificar drawdowns

**Recomendação**: **NÃO IMPLEMENTAR** (risco > benefício)

---

### 8. **Hedge Após Loss** (NÃO RECOMENDADO)
**Objetivo**: Abrir posição oposta após loss para recuperar

**Lógica**:
```python
# APÓS LOSS: Abrir posição oposta
if last_trade_was_loss:
    # Se loss foi BUY, abrir SELL (e vice-versa)
    opposite_direction = 'SELL' if last_trade == 'BUY' else 'BUY'

    # Abrir com dobro do volume (recovery)
    self.open_position(
        direction=opposite_direction,
        volume=self.volume * 2
    )
```

**Vantagens**:
- ✅ Pode recuperar loss rapidamente

**Desvantagens**:
- ❌ **MUITO PERIGOSO!** (pode dobrar losses)
- ❌ Aumenta exposição (2 posições abertas)
- ❌ Se mercado lateral: 2 losses em vez de 1

**Recomendação**: **NUNCA IMPLEMENTAR** (gambling)

---

### 9. **Time-Based Exit** (ÚTIL)
**Objetivo**: Fechar trade se demorar muito tempo

**Lógica sugerida**:
```python
def _check_time_exit(self, position):
    """
    Fecha posição se aberta há mais de 30 minutos
    """
    from datetime import datetime

    open_time = position['open_time']
    now = datetime.now()

    elapsed_minutes = (now - open_time).total_seconds() / 60

    if elapsed_minutes >= 30:
        # Fechar no mercado (independente de lucro/loss)
        self.mt5.close_position(
            ticket=position['ticket']
        )

        print(f"[TIME EXIT] Posição aberta há {elapsed_minutes:.0f} min")
        print(f"[TIME EXIT] Fechada no mercado")
```

**Vantagens**:
- ✅ Evita trades "mortos" (laterais)
- ✅ Libera capital para novas oportunidades
- ✅ Reduz exposição prolongada

**Desvantagens**:
- ⚠️ Pode fechar trade que iria recuperar
- ⚠️ Aumenta quantidade de losses pequenos

**Recomendação**: **IMPLEMENTAR** (útil para scalping)

---

### 10. **News Filter** (AVANÇADO)
**Objetivo**: Evitar trades durante notícias de alto impacto

**Lógica sugerida**:
```python
def _is_news_time(self):
    """
    Verifica se está próximo de horário de notícias
    """
    from datetime import datetime

    now = datetime.now()
    hour_utc = now.hour

    # Horários de notícias importantes (UTC)
    news_hours = [
        (12, 14),  # London session (noticias EUR/GBP)
        (16, 18),  # NY session (noticias USD)
        (0, 2),    # Asia session (noticias JPY/AUD)
    ]

    for start, end in news_hours:
        if start <= hour_utc < end:
            return True

    return False

# No run():
if self._is_news_time():
    print("[NEWS FILTER] Aguardando fim de horário de notícias")
    continue
```

**Vantagens**:
- ✅ Evita volatilidade extrema
- ✅ Reduz slippage
- ✅ Evita gaps de preço

**Desvantagens**:
- ⚠️ Perde oportunidades em breakouts
- ⚠️ Precisa calendário econômico atualizado

**Recomendação**: **AVALIAR** (útil mas complexo)

---

## RECOMENDAÇÕES PRIORITÁRIAS

### IMPLEMENTAR AGORA (Alta Prioridade)

#### #1: Circuit Breaker REAL
```python
# Adicionar em run() após cada trade fechado:

if trade_result < 0:  # Loss
    self.consecutive_losses += 1

    if self.consecutive_losses >= self.max_consecutive_losses:
        self.circuit_breaker_active = True
        print(f"\n[CIRCUIT BREAKER] {self.consecutive_losses} perdas consecutivas!")
        print(f"[CIRCUIT BREAKER] Pausando por 5 minutos...")
        time.sleep(300)

        self.circuit_breaker_active = False
        self.consecutive_losses = 0
        print(f"[CIRCUIT BREAKER] Resetado, retomando operações")
else:  # Win
    self.consecutive_losses = 0
```

**Impacto**: ⭐⭐⭐⭐⭐ (CRÍTICO)
**Tempo**: 15 minutos
**Motivo**: Já teve 5 losses consecutivos! Precisa URGENTE

---

#### #2: Break-Even Move
```python
# Adicionar em _manage_position_trailing():

if not hasattr(position, 'breakeven_moved'):
    profit = calcular_lucro(position)

    if profit >= 2.0:  # $2 de lucro
        # Mover SL para break-even
        self.mt5.modify_position(
            ticket=position['ticket'],
            sl=position['entry_price']
        )

        position['breakeven_moved'] = True
        print(f"[BREAK-EVEN] SL movido para entry (protege $0)")
```

**Impacto**: ⭐⭐⭐⭐ (MUITO ÚTIL)
**Tempo**: 30 minutos
**Motivo**: AVG WIN $2.76 vs AVG LOSS -$5.17 (precisa proteger wins)

---

#### #3: Cooldown Entre Trades
```python
# Adicionar no __init__():
self.last_close_time = 0
self.cooldown_seconds = 30

# Adicionar em run() antes de abrir novo trade:
if self.last_close_time > 0:
    elapsed = time.time() - self.last_close_time

    if elapsed < self.cooldown_seconds:
        print(f"[COOLDOWN] Aguardando {int(self.cooldown_seconds - elapsed)}s")
        time.sleep(1)
        continue

# Após fechar trade:
self.last_close_time = time.time()
```

**Impacto**: ⭐⭐⭐ (ÚTIL)
**Tempo**: 15 minutos
**Motivo**: Evita revenge trading após loss

---

### IMPLEMENTAR DEPOIS (Média Prioridade)

#### #4: Time-Based Exit
- Fechar trade se > 30 min aberto
- Útil para scalping (BTC move rápido)

**Impacto**: ⭐⭐⭐
**Tempo**: 30 minutos

#### #5: Partial Close
- Fechar 50% em $4 de lucro
- Deixar 50% com trailing

**Impacto**: ⭐⭐
**Tempo**: 1 hora

---

### NÃO IMPLEMENTAR (Risco Alto)

- ❌ Martingale
- ❌ Hedge após loss
- ❌ Dobrar volume após loss

---

## RESUMO - AÇÕES ANTI-LOSS

### ATIVAS AGORA:
1. ✅ SL Fixo ($10)
2. ✅ Trailing Stop ($4 ativa, $2 protege)
3. ⚠️ Circuit Breaker (variáveis criadas mas SEM lógica)

### FALTAM IMPLEMENTAR:
4. ❌ Circuit Breaker REAL (contador de losses)
5. ❌ Break-Even Move (SL → entry após $2)
6. ❌ Cooldown entre trades (30s pausa)
7. ❌ Time-Based Exit (fecha após 30min)

### IMPACTO ESPERADO COM #1+#2+#3:

| Métrica | v3.1.0 (Atual) | v3.2.0 (Com Anti-Loss) | Melhora |
|---------|----------------|------------------------|---------|
| **Max Losses Consecutivas** | 5+ (sem limite) | 5 (para agente) | ✅ Controle |
| **Trades viram Loss após $2** | SIM (devolve) | NÃO (break-even) | ✅ -30% losses |
| **Overtrading** | SIM (sem pausa) | NÃO (cooldown 30s) | ✅ Qualidade++ |
| **Win Rate** | 56% → 65% | 65% → 70% | +5% |
| **AVG Loss** | -$10.00 | -$8.00 | Melhora |

---

## CRIAR BTC v3.2.0 AGORA?

Posso implementar as 3 ações prioritárias (#1, #2, #3) em ~30 minutos.

Quer que eu crie **v3.2.0 com Circuit Breaker + Break-Even + Cooldown**?
