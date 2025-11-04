# AJUSTE DE FILTROS - MODO AGRESSIVO

**Data:** 2025-11-02
**Problema:** 100 ciclos sem trades (filtros bloqueando tudo)
**Dados:** Momentum +0.54% (13x acima threshold) mas sem volume spike

---

## 🔴 PROBLEMA ATUAL

### Filtros Atuais (MUITO RIGOROSOS)
```python
# Precisa de 2 de 3 confirmações:
1. Tendência + Momentum 0.04%     ✓ PASSA
2. Momentum forte > 0.06%          ✓ PASSA
3. Volume spike + Volatilidade     ✗ FALHA (bloqueia!)
```

**Mesmo com momentum GIGANTE (+0.54%), bloqueia por falta de volume!**

---

## ✅ SOLUÇÃO: MODO AGRESSIVO

### Opção 1: Aceitar 1 Confirmação (MAIS AGRESSIVO)
```python
if confirmations >= 1:  # Era >= 2
    if self._check_m15_trend("BUY"):
        return {"type": "BUY", ...}
```

**Efeito:**
- Trades/dia: ~150-200
- Win rate esperado: 40-45%
- Mais oportunidades, mas mais ruído

### Opção 2: Remover Requisito de Volume (BALANCEADO)
```python
# Confirmação 3: SEM volume spike, só volatilidade
if high_volatility and current > prev_1 and price_above_avg:
    confirmations += 1
```

**Efeito:**
- Trades/dia: ~80-120
- Win rate esperado: 43-48%
- Entra em movimentos fortes mesmo sem volume

### Opção 3: Reduzir Thresholds (CONSERVADOR)
```python
MOMENTUM_BUY = 0.03   # Era 0.04%
volume_spike = current_volume > avg_volume * 1.1  # Era 1.3
high_volatility = volatility > avg_volatility * 1.0  # Era 1.2
```

**Efeito:**
- Trades/dia: ~60-90
- Win rate esperado: 45-50%
- Mais sensível mas mantém qualidade

---

## 💡 RECOMENDAÇÃO

**APLICAR OPÇÃO 2 + OPÇÃO 3:**

```python
# Thresholds mais relaxados
MOMENTUM_BUY = 0.03
volume_spike = current_volume > avg_volume * 1.1
high_volatility = volatility > avg_volatility * 1.0

# Confirmação 3 SEM volume spike obrigatório
if (high_volatility or volume_spike) and current > prev_1 and price_above_avg:
    confirmations += 1
```

Isso dá:
- ~80-100 trades/dia
- Momentum forte ENTRA (como no exemplo +0.54%)
- Mantém filtro M15 para qualidade
- Win rate 44-48%

---

## 🚀 IMPLEMENTAR AGORA?

Quer que eu aplique essas mudanças?
