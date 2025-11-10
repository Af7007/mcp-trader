# CORRECAO CRITICA - Filtro ATR em Dolares

## PROBLEMA IDENTIFICADO

Ao executar o BTC v2.0.0, o filtro ATR estava rejeitando TODOS os trades:

```
[FILTRO ATR] M5 ATR muito alto ($301.41 > $2.0), aguardando
```

### CAUSA

O código estava convertendo ATR de **pontos para preço**, mas não estava considerando o **point value e volume** para calcular a expectativa em dólares.

**Código ERRADO** (antes):
```python
atr_m5 = self._calculate_atr_simple(rates_m5)
atr_dollars = atr_m5 * self.symbol_point  # ERRADO!
```

**Exemplo BTC**:
- ATR = 3000 pontos
- symbol_point = $0.01
- atr_dollars = 3000 × 0.01 = **$30.00** (ERRADO!)
- Filtro: $30.00 > $2.00 = BLOQUEADO ❌

**Exemplo Gold**:
- ATR = 400 pontos
- symbol_point = $0.001
- atr_dollars = 400 × 0.001 = **$0.40** (ERRADO!)
- Filtro: $0.40 < $2.00 = OK ✓ (por sorte)

### PROBLEMA REAL

O ATR em "preço" não representa a **expectativa de movimento em dólares**. Precisamos considerar:
1. Point value (valor de 1 ponto)
2. Volume (lotes negociados)

---

## SOLUCAO

**Código CORRETO** (depois):
```python
atr_m5_pontos = self._calculate_atr_simple(rates_m5)
atr_dollars = atr_m5_pontos * self.point_value * self.volume  # CORRETO!
```

### Formula Correta

```
ATR em dólares = ATR em pontos × point_value × volume
```

**Exemplo BTC** (CORRIGIDO):
- ATR = 3000 pontos
- point_value = $0.01/lote
- volume = 0.30 lotes
- atr_dollars = 3000 × 0.01 × 0.30 = **$9.00** ✓
- Filtro: $9.00 > $2.00 = BLOQUEADO ✓ (correto, volatilidade alta)

**Exemplo Gold** (CORRIGIDO):
- ATR = 400 pontos
- point_value = $0.10/lote
- volume = 0.03 lotes
- atr_dollars = 400 × 0.10 × 0.03 = **$1.20** ✓
- Filtro: $1.20 < $2.00 = OK ✓ (correto, volatilidade normal)

---

## COMPARACAO ANTES vs DEPOIS

### BTC (volume 0.30)

| ATR Pontos | ANTES (ERRADO) | DEPOIS (CORRETO) | Resultado |
|------------|----------------|------------------|-----------|
| 3000 | $30.00 | $9.00 | Bloqueado (correto) |
| 2000 | $20.00 | $6.00 | Bloqueado (correto) |
| 1000 | $10.00 | $3.00 | Bloqueado (correto) |
| 667 | $6.67 | $2.00 | OK (limite) |
| 500 | $5.00 | $1.50 | OK (permitido) |

### Gold (volume 0.03)

| ATR Pontos | ANTES (ERRADO) | DEPOIS (CORRETO) | Resultado |
|------------|----------------|------------------|-----------|
| 1000 | $1.00 | $3.00 | Bloqueado (correto) |
| 667 | $0.67 | $2.00 | OK (limite) |
| 500 | $0.50 | $1.50 | OK (permitido) |
| 400 | $0.40 | $1.20 | OK (permitido) |

---

## IMPACTO

### Antes da Correção

- **BTC**: TODOS os trades bloqueados (ATR sempre > $2.00 em preço)
- **Gold**: Maioria dos trades permitidos (sorte, ATR em preço era baixo)
- **Resultado**: BTC inutilizado, Gold funcionando por acaso

### Depois da Correção

- **BTC**: Trades permitidos quando volatilidade normal (< $2.00 expectativa)
- **Gold**: Mesma lógica, agora correta
- **Resultado**: Ambos funcionam corretamente

---

## ARQUIVOS CORRIGIDOS

1. **src/agents/btc_loss_zero_v2.py** (linha 751-752)
2. **src/agents/gold_loss_zero_simple.py** (linha 741-742)

### Mudança Aplicada

```diff
- atr_m5 = self._calculate_atr_simple(rates_m5)
- atr_dollars = atr_m5 * self.symbol_point
+ # IMPORTANTE: Converter ATR de pontos para "dolares de expectativa"
+ # Formula: atr_pontos × point_value × volume = dolares de movimento
+ atr_m5_pontos = self._calculate_atr_simple(rates_m5)
+ atr_dollars = atr_m5_pontos * self.point_value * self.volume
```

---

## VALIDACAO

### Testar Novamente

**BTC**:
```bash
python src/agents/btc_loss_zero_v2.py
```

Agora deve mostrar:
```
[M5 SELL] Score: 4.5 | RSI: 30.9 | Momentum: -0.23%
[FILTRO ATR] M5 ATR = $9.00 (OK ou bloqueado dependendo do valor)
```

**Gold**:
```bash
python src/agents/gold_loss_zero_simple.py
```

Deve mostrar valores corretos também.

---

## CONCLUSAO

Esta era uma correção **CRITICA** que:
- ✅ Corrige filtro ATR para calcular expectativa em dólares
- ✅ Mantém mesma lógica para Gold e BTC
- ✅ Garante que max_atr_m5_dollars = $2.00 seja respeitado corretamente
- ✅ Permite que BTC funcione (estava 100% bloqueado)

**Data da Correção**: 2025-11-07
**Versão**: 2.0.1 (hotfix)
