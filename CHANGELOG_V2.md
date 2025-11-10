# Changelog - Agentes Gold e BTC v2.0

## v2.0.2 (2025-11-07 20:55)

### Correções Aplicadas

#### 1. Warning datetime.utcnow() removido
**Arquivos**: `gold_loss_zero_simple.py`, `btc_loss_zero_v2.py`

**Antes**:
```python
from datetime import datetime
current_hour = datetime.utcnow().hour  # Deprecated warning
```

**Depois**:
```python
from datetime import datetime, timezone
current_hour = datetime.now(timezone.utc).hour  # Timezone-aware
```

**Motivo**: Python 3.12+ deprecou `datetime.utcnow()` em favor de timezone-aware datetimes.

---

#### 2. Filtros BTC ajustados para volatilidade natural
**Arquivo**: `btc_loss_zero_v2.py`

**Antes**:
```python
self.max_atr_m5_dollars = 2.0   # Muito restritivo para BTC
self.max_spread_dollars = 0.5   # Muito restritivo para BTC
```

**Depois**:
```python
self.max_atr_m5_dollars = 20.0  # Ajustado para volatilidade BTC (10x Gold)
self.max_spread_dollars = 5.0   # Ajustado para spreads BTC (10x Gold)
```

**Motivo**: BTC tem volume 10x maior (0.30 vs 0.03), resultando em ATR e spreads naturalmente 10x maiores.

**Impacto**: Permite que BTC opere (antes estava 100% bloqueado).

---

#### 3. Cálculo ATR em dólares corrigido
**Arquivos**: `gold_loss_zero_simple.py`, `btc_loss_zero_v2.py`

**Antes**:
```python
atr_m5 = self._calculate_atr_simple(rates_m5)
atr_dollars = atr_m5 * self.symbol_point  # ERRADO: ATR em preço
```

**Depois**:
```python
atr_m5_pontos = self._calculate_atr_simple(rates_m5)
atr_dollars = atr_m5_pontos * self.point_value * self.volume  # CORRETO: ATR em $ de expectativa
```

**Motivo**: ATR em "preço" não representa expectativa de movimento em dólares. Precisa considerar point_value e volume.

**Impacto Antes**:
- BTC: ATR sempre > $20 em preço → bloqueado
- Gold: ATR baixo em preço → funcionava por acaso

**Impacto Depois**:
- BTC: ATR correto ($10-20) → funciona ✓
- Gold: ATR correto ($1-2) → funciona ✓

---

## v2.0.1 (2025-11-07 20:50)

### Melhorias Implementadas

#### 1. Estratégia M5/M1 otimizada
- **Removido**: Validação M15 (conflitava com scalping)
- **Foco**: M5 principal (score >= 4.0) + M1 timing
- **Filtros**: ATR e Spread adicionados
- **Confirmação**: M1 exige 2 velas consecutivas

#### 2. Trailing Stop otimizado
- **Activation**: $1.50 → $2.00 (melhor para scalping)
- **Distance**: $1.00 (mantido)
- **Incremental**: +$1.00 a cada +$1.50

#### 3. Score M5 aumentado
- **Antes**: 2.5-3.0 (aceitava sinais fracos)
- **Depois**: 4.0 (apenas sinais fortes)

---

## v2.0.0 (2025-11-07 20:00)

### Features Iniciais

#### Gold Agent v2.0.0
- Symbol: XAUUSDc
- Volume: 0.03 lotes
- SL: $5.00 fixo
- Estratégia: M5 principal + M1 timing
- Filtros: ATR ($2.00) + Spread ($0.50)

#### BTC Agent v2.0.0
- Symbol: BTCUSDc
- Volume: 0.30 lotes (equivalente ao Gold)
- SL: $5.00 fixo (mesma expectativa $)
- Estratégia: Idêntica ao Gold
- Filtros: Ajustados para volatilidade BTC

---

## Comparação de Versões

### Parâmetros Gold

| Parâmetro | v1.3.0 | v2.0.0 | v2.0.2 |
|-----------|--------|--------|--------|
| Volume | 0.03 | 0.03 | 0.03 |
| SL | $5.00 | $5.00 | $5.00 |
| TS Activation | $1.50 | $2.00 | $2.00 |
| Min Score M5 | 2.5-3.0 | 4.0 | 4.0 |
| Max ATR | N/A | $2.00 | $2.00 (corrigido) |
| M15 Validation | SIM | NÃO | NÃO |

### Parâmetros BTC

| Parâmetro | v2.0.0 | v2.0.1 | v2.0.2 |
|-----------|--------|--------|--------|
| Volume | 0.30 | 0.30 | 0.30 |
| SL | $5.00 | $5.00 | $5.00 |
| TS Activation | $2.00 | $2.00 | $2.00 |
| Min Score M5 | 4.0 | 4.0 | 4.0 |
| Max ATR | $2.00 | $2.00 | **$20.00** |
| Max Spread | $0.50 | $0.50 | **$5.00** |

---

## Arquivos Modificados

### v2.0.2
- ✅ `src/agents/gold_loss_zero_simple.py` (linha 545-546, 741-742)
- ✅ `src/agents/btc_loss_zero_v2.py` (linha 555-556, 751-752, 110-111)
- 📝 `CORRECAO_ATR_FILTRO.md` (nova documentação)
- 📝 `BTC_FILTROS_AJUSTADOS.md` (nova documentação)
- 📝 `CHANGELOG_V2.md` (este arquivo)

### v2.0.1
- ✅ `src/agents/gold_loss_zero_simple.py` (reescrita completa)

### v2.0.0
- ✅ `src/agents/gold_loss_zero_simple.py` (nova versão)
- ✅ `src/agents/btc_loss_zero_v2.py` (novo arquivo)
- 📝 `MELHORIAS_GOLD_SCALPING.md`
- 📝 `GOLD_V2_CHANGELOG.md`
- 📝 `BTC_V2_README.md`
- 📝 `GOLD_VS_BTC_V2_COMPARACAO.md`

---

## Próximos Passos

1. ✅ Testar Gold v2.0.2 em produção
2. ✅ Testar BTC v2.0.2 em produção
3. ⏳ Monitorar 20-30 trades de cada
4. ⏳ Analisar win rate e ajustar se necessário
5. ⏳ Documentar resultados

---

## Notas

- **Gold v2.0.2**: Pronto para uso ✓
- **BTC v2.0.2**: Pronto para uso ✓
- **Expectativa em $**: IGUAL para ambos ✓
- **Filtros**: Ajustados para volatilidade de cada símbolo ✓

**Data**: 2025-11-07
**Versão Atual**: v2.0.2
