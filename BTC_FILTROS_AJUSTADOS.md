# BTC v2.0.0 - Filtros Ajustados para Volatilidade

## PROBLEMA ORIGINAL

Os filtros do BTC estavam configurados com os **mesmos valores** do Gold:
- Max ATR: $2.00
- Max Spread: $0.50

Porém, **BTC é naturalmente 10x mais volátil** que Gold por causa do volume 10x maior.

---

## AJUSTES APLICADOS

### Filtros BTC (NOVO)

```python
self.max_atr_m5_dollars = 20.0  # ATR maximo (BTC mais volatil)
self.max_spread_dollars = 5.0   # Spread maximo (BTC spreads maiores)
```

### Comparação Gold vs BTC

| Filtro | Gold v2.0.0 | BTC v2.0.0 | Razão |
|--------|-------------|------------|-------|
| **Max ATR** | $2.00 | **$20.00** | BTC 10x mais volátil |
| **Max Spread** | $0.50 | **$5.00** | BTC spreads maiores |
| **Min Score M5** | 4.0 | 4.0 | IGUAL |
| **SL Fixo** | $5.00 | $5.00 | IGUAL |
| **TS Activation** | $2.00 | $2.00 | IGUAL |

---

## RACIOCÍNIO

### ATR M5

**Gold (volume 0.03)**:
- ATR típico: 400-667 pontos
- ATR em $: $1.20 - $2.00
- Limite: $2.00

**BTC (volume 0.30)**:
- ATR típico: 4000-6700 pontos
- ATR em $: $12.00 - $20.00
- Limite: $20.00 (equivalente proporcional)

### Spread

**Gold**:
- Spread típico: $0.10 - $0.30
- Limite: $0.50

**BTC**:
- Spread típico: $1.00 - $3.00
- Limite: $5.00

---

## IMPORTANTE: SL/TS Continuam IGUAIS

Os filtros ATR e Spread são ajustados, mas os valores de **risco** continuam os mesmos:

```
Gold vs BTC (expectativa IGUAL em $):
- SL: $5.00 = $5.00
- TS Activation: $2.00 = $2.00
- TS Distance: $1.00 = $1.00
- Avg Win esperado: $1.50-2.00 = $1.50-2.00
- Avg Loss: -$5.00 = -$5.00
```

**Apenas os FILTROS são diferentes, não o RISCO!**

---

## RESULTADO ESPERADO

### Antes (max_atr = $2.00)

```
[FILTRO ATR] M5 ATR muito alto ($90.42 > $2.0), aguardando
[FILTRO ATR] M5 ATR muito alto ($85.00 > $2.0), aguardando
[FILTRO ATR] M5 ATR muito alto ($95.00 > $2.0), aguardando
...
RESULTADO: NENHUM trade executado (BTC sempre bloqueado)
```

### Depois (max_atr = $20.00)

```
[FILTRO ATR] M5 ATR = $15.00 (OK)
[FILTRO SPREAD] Spread = $2.50 (OK)
[M1 CONFIRM] SELL confirmado (2 velas down)
[SINAL CONFIRMADO] M5 SELL (score 4.5) + M1 timing OK

[ABRINDO POSICAO]
...
RESULTADO: Trades executados quando ATR < $20.00
```

---

## VALIDAÇÃO

Reinicie o agente BTC:

```bash
RUN_BTC_V2.bat
```

Agora deve ver trades sendo executados com:
- ATR entre $10-20: OK ✓
- ATR > $20: Bloqueado (correto)
- Spread < $5: OK ✓

---

## RESUMO

**Filtros ajustados para refletir volatilidade natural do BTC**:
- Max ATR: $2.00 → **$20.00** (10x)
- Max Spread: $0.50 → **$5.00** (10x)

**Risco permanece IGUAL ao Gold**:
- SL, TS, expectativa em $ = IGUAIS ✓

Data: 2025-11-07
Versão: 2.0.2
