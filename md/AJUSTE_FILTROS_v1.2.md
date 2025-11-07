# AJUSTE DE FILTROS - v1.2 BALANCEADO

**Data:** 2025-11-02
**Problema:** Filtros muito rigorosos (200 ciclos sem nenhuma entrada)
**Solução:** Ajuste para meio termo balanceado

---

## 🔴 PROBLEMA IDENTIFICADO

**v1.1 (Muito Rigoroso):**
- 200 ciclos executados
- **0 entradas** (nenhum sinal gerado!)
- Filtros bloqueando TUDO

**Causa:**
- Momentum 0.05% era muito alto
- 3 confirmações era muito exigente
- M15 confirmando tornava quase impossível

---

## ✅ AJUSTES APLICADOS (v1.2)

### Mudanças nos Filtros

| Parâmetro | v1.0 (Original) | v1.1 (Muito Rigoroso) | v1.2 (BALANCEADO) |
|-----------|-----------------|----------------------|-------------------|
| **Momentum** | 0.03% | 0.05% | **0.04%** ⭐ |
| **Confirmações** | 2 | 3 | **2** ⭐ |
| **M15 Check** | Sim | Sim | Sim |
| **Horários bloqueados** | 4 períodos | 4 períodos | **Nenhum** ⭐ |

### O Que NÃO Mudou (Mantido v1.1)

✓ SL mínimo: **150 pontos** (protege de ruído)
✓ ATR padrão: **180 pontos**
✓ Volume máximo: **0.1 lotes**
✓ Trailing: **ATR × 0.6 / 0.4**

---

## 📊 EXPECTATIVA

### v1.0 (Original)
```
Trades/dia: ~200
Win rate: 38.4%
Resultado: -$684/dia
```

### v1.1 (Muito Rigoroso)
```
Trades/dia: 0
Win rate: N/A
Resultado: $0 (sem entradas!)
```

### v1.2 (BALANCEADO) - Esperado
```
Trades/dia: ~80-120
Win rate: 45-50%
Resultado: +$150 a +$300/dia
```

---

## 🎯 LÓGICA DO BALANCEAMENTO

### Por que 0.04% de Momentum?
- **0.03%** = Sinais demais, qualidade baixa (38% win rate)
- **0.05%** = Sem sinais (bloqueio total)
- **0.04%** = Meio termo ideal (~$44 de movimento em BTC $110k)

### Por que 2 Confirmações?
- **2** = Filtro razoável com M5 + M15 confirmando
- **3** = Quase impossível de satisfazer todas as condições

### Por que Remover Bloqueio de Horários?
- Com filtros melhores, não precisa evitar horários
- Opera 24/7 aproveitando todas as oportunidades
- SL maior já protege contra volatilidade

---

## 🔍 SISTEMA DE CONFIRMAÇÕES

Para abrir um trade, o agente precisa de **2 de 3** confirmações:

### Confirmação 1: Tendência + Momentum
```python
if uptrend and momentum_5m > 0.04%:
    confirmations += 1
```

### Confirmação 2: Momentum Forte
```python
if momentum_5m > 0.06%:  # 0.04% × 1.5
    confirmations += 1
```

### Confirmação 3: Volatilidade + Volume
```python
if high_volatility and volume_spike and price_above_avg:
    confirmations += 1
```

### Validação Final: M15
```python
if confirmations >= 2:
    if M15_confirma_tendencia:
        ABRIR TRADE ✓
```

---

## 📈 COMPARAÇÃO DETALHADA

### Configuração Completa v1.2

```
✓ Volume: 0.01 lotes (padrão), máx 0.1
✓ SL: 150-360 pontos (ATR × 2.0)
✓ ATR mínimo: 150 pontos
✓ ATR padrão: 180 pontos
✓ Momentum: 0.04% (balanceado)
✓ Confirmações: 2 de 3
✓ M15 validação: Sim
✓ Trailing ativa: ATR × 0.6
✓ Trailing distância: ATR × 0.4
✓ Horários: 24/7 (sem bloqueios)
✓ Circuit breaker: 5 perdas consecutivas
✓ Cooldown: 30s entre trades
```

---

## 🧪 COMO VALIDAR

### Após 1 Hora
- [ ] Pelo menos 3-5 sinais gerados
- [ ] Volume sempre ≤ 0.1 lotes
- [ ] SL sempre ≥ 150 pontos

### Após 24 Horas
- [ ] 80-120 trades executados
- [ ] Win rate ≥ 42%
- [ ] Resultado ≥ breakeven ou positivo

### Após 48 Horas
- [ ] Win rate ≥ 45%
- [ ] R/R ratio ≥ 1.2:1
- [ ] Lucro acumulado positivo

---

## ⚠️ SINAIS DE ALERTA

### Se MUITO POUCOS Sinais (< 50/dia)
→ Reduzir momentum para 0.035%

### Se MUITOS Sinais (> 150/dia)
→ Aumentar momentum para 0.045%

### Se Win Rate < 40%
→ Voltar para 3 confirmações

### Se Win Rate > 55%
→ Pode relaxar filtros um pouco mais

---

## 📝 HISTÓRICO DE VERSÕES

### v1.0 (Original)
- Momentum: 0.03%
- Confirmações: 2
- SL: 80 pontos
- Win rate: 38.4%
- Resultado: -$684/dia

### v1.1 (Muito Rigoroso)
- Momentum: 0.05%
- Confirmações: 3
- SL: 150 pontos
- Win rate: N/A
- Resultado: 0 trades

### v1.2 (BALANCEADO) ⭐
- Momentum: 0.04%
- Confirmações: 2
- SL: 150 pontos
- Win rate: Esperado 45-50%
- Resultado: Esperado +$150-300/dia

---

## 🚀 EXECUTAR v1.2

```bash
python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc
```

Ou:
```bash
TESTAR_CORRECOES.bat
```

---

**Status:** ✅ Ajustes aplicados
**Versão:** 1.2 BALANCEADO
**Pronto para testes!**
