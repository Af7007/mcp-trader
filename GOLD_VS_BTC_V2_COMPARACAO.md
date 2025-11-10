# Comparação Rápida: Gold v2.0.0 vs BTC v2.0.0

## PARAMETROS LADO A LADO

```
┌────────────────────┬──────────────────┬──────────────────┬─────────────┐
│ Parâmetro          │ GOLD v2.0.0      │ BTC v2.0.0       │ Expectativa │
├────────────────────┼──────────────────┼──────────────────┼─────────────┤
│ Symbol             │ XAUUSDc          │ BTCUSDc          │ Diferente   │
│ Volume             │ 0.03 lotes       │ 0.30 lotes       │ Diferente   │
│ Point              │ $0.001           │ $0.01            │ Diferente   │
│ Tick Value         │ $0.10/lote       │ $0.01/lote       │ Diferente   │
│                    │                  │                  │             │
│ Point Value        │ $0.003/ponto     │ $0.003/ponto     │ IGUAL       │
│ SL Fixo            │ $5.00            │ $5.00            │ IGUAL       │
│ TS Activation      │ $2.00            │ $2.00            │ IGUAL       │
│ TS Distance        │ $1.00            │ $1.00            │ IGUAL       │
│ Min Score M5       │ 4.0              │ 4.0              │ IGUAL       │
│ Max ATR M5         │ $2.00            │ $2.00            │ IGUAL       │
│ Max Spread         │ $0.50            │ $0.50            │ IGUAL       │
│                    │                  │                  │             │
│ Win Rate Esperado  │ 60-65%           │ 60-65%           │ IGUAL       │
│ Avg Win            │ $1.50-2.00       │ $1.50-2.00       │ IGUAL       │
│ Avg Loss           │ -$5.00           │ -$5.00           │ IGUAL       │
│ Net/20 trades      │ +$10-20          │ +$10-20          │ IGUAL       │
└────────────────────┴──────────────────┴──────────────────┴─────────────┘
```

## DISTANCIAS DE PRECO (DIFERENTES, $ IGUAIS)

### SL em Preço

```
GOLD:
  SL $5.00 = 1667 pontos × $0.001 = $1.67 distância
  Entry $4005.00 → SL $4003.33

BTC:
  SL $5.00 = 1667 pontos × $0.01 = $16.67 distância
  Entry $95000.00 → SL $94983.33
```

### Trailing Stop em Preço

```
GOLD:
  TS Activation $2.00 = $0.67 distância
  TS Distance $1.00 = $0.33 distância

BTC:
  TS Activation $2.00 = $6.67 distância
  TS Distance $1.00 = $3.33 distância
```

**IMPORTANTE**: Preços diferentes, mas **LUCRO/PERDA EM $ = IGUAIS**!

---

## EXEMPLOS DE TRADES

### Exemplo 1: Trade Vencedor

**GOLD**:
```
Entry: $4005.00
SL: $4003.33 (-$5.00 se atingido)
TS ativa: $4005.67 (lucro $2.00)
Exit: $4006.50 (TS hit)
Profit: $1.50 ✓
```

**BTC**:
```
Entry: $95000.00
SL: $94983.33 (-$5.00 se atingido)
TS ativa: $95006.67 (lucro $2.00)
Exit: $95015.00 (TS hit)
Profit: $1.50 ✓
```

### Exemplo 2: Trade Perdedor

**GOLD**:
```
Entry: $4005.00
SL: $4003.33
Exit: $4003.33 (SL hit)
Loss: -$5.00 ✗
```

**BTC**:
```
Entry: $95000.00
SL: $94983.33
Exit: $94983.33 (SL hit)
Loss: -$5.00 ✗
```

---

## EXECUCAO

### Validar

```bash
# Gold
python test_gold_v2_improvements.py

# BTC
python test_btc_v2_params.py
```

### Executar

```bash
# Gold
RUN_GOLD_AGENT.bat
# OU
python src/agents/gold_loss_zero_simple.py

# BTC
RUN_BTC_V2.bat
# OU
python src/agents/btc_loss_zero_v2.py
```

---

## QUANDO USAR CADA UM?

### Use GOLD se:
- ✅ Tem margem limitada ($100-200)
- ✅ Prefere menor volatilidade
- ✅ Opera durante London/NY session
- ✅ Quer movimentos mais suaves

### Use BTC se:
- ✅ Tem margem adequada ($300-500)
- ✅ Prefere maior liquidez 24/7
- ✅ Quer operar fins de semana
- ✅ Gosta de movimentos rápidos

### Use AMBOS se:
- ✅ Tem margem suficiente ($500-1000)
- ✅ Quer diversificar símbolos
- ✅ Opera em horários diferentes
- ✅ Busca maximizar oportunidades

---

## MARGEM NECESSARIA

```
GOLD: $100-200 (conservador: $300)
BTC: $300-500 (conservador: $700)
AMBOS: $500-1000 (conservador: $1500)
```

---

## RESULTADOS ESPERADOS (20 TRADES)

### Cenário Conservador (55% WR)

**GOLD**:
- Wins: 11 × $1.50 = $16.50
- Losses: 9 × -$5.00 = -$45.00
- **Net: -$28.50** ⚠️

**BTC**:
- Wins: 11 × $1.50 = $16.50
- Losses: 9 × -$5.00 = -$45.00
- **Net: -$28.50** ⚠️

### Cenário Realista (60% WR)

**GOLD**:
- Wins: 12 × $1.80 = $21.60
- Losses: 8 × -$5.00 = -$40.00
- **Net: -$18.40** ⚠️

**BTC**:
- Wins: 12 × $1.80 = $21.60
- Losses: 8 × -$5.00 = -$40.00
- **Net: -$18.40** ⚠️

### Cenário Otimista (65% WR)

**GOLD**:
- Wins: 13 × $2.00 = $26.00
- Losses: 7 × -$5.00 = -$35.00
- **Net: -$9.00** ⚠️

**BTC**:
- Wins: 13 × $2.00 = $26.00
- Losses: 7 × -$5.00 = -$35.00
- **Net: -$9.00** ⚠️

**NOTA**: Para lucro consistente, precisamos:
- Win Rate >= 70%
- OU Avg Win >= $3.00
- OU reduzir Avg Loss < $5.00

---

## RESUMO FINAL

### Parâmetros Físicos
- ❌ **Diferentes**: Volume, Point, Tick Value, Distâncias de Preço

### Expectativa em Dólares
- ✅ **IGUAIS**: SL, TS, Point Value, Win/Loss esperados

### Estratégia
- ✅ **IDÊNTICA**: M5 principal, M1 timing, score >= 4.0, filtros ATR/Spread

### Resultado Esperado
- ✅ **MESMO**: Win rate, avg win/loss, net result em $

---

**CONCLUSAO**: Mesma estratégia, mesma expectativa em dólares, apenas adaptada para símbolos diferentes!
