# GOLD LOSS ZERO - CONFIGURAÇÃO E PARÂMETROS

**Data:** 2025-11-02
**Versão:** 1.0
**Símbolo:** XAUUSDc (Gold - Conta Cents)

---

## 📊 VISÃO GERAL

O agente **Gold Loss Zero** é otimizado especificamente para trading de **XAUUSDc** (ouro em conta cents), usando a mesma estratégia trailing stop do BTC mas com parâmetros ajustados para as características únicas do mercado de ouro.

### Por que Parâmetros Diferentes?

| Característica | BTC | GOLD |
|----------------|-----|------|
| **Volatilidade** | Alta (~100+ pts) | Média (~60 pts) |
| **Preço médio** | ~$110,000 | ~$2,600 |
| **Movimento típico** | $44/0.04% | $0.78/0.03% |
| **Velocidade** | Muito rápido | Moderado |
| **Horários** | 24/7 | 23/5 (fecha fim de semana) |

---

## ⚙️ CONFIGURAÇÃO GOLD

### Parâmetros Principais

```python
# src/agents/gold_loss_zero_simple.py

class GoldLossZeroSimple:
    def __init__(
        self,
        symbol: str = "XAUUSDc",
        volume: float = 0.01,                          # 0.01 lotes
        check_interval: int = 15,                      # 15 segundos
        stop_loss_atr_multiplier: float = 1.5,         # SL: ATR × 1.5
        trailing_activation_atr_multiplier: float = 0.4,  # Trailing ativa: ATR × 0.4
        trailing_distance_atr_multiplier: float = 0.3,    # Trailing dist: ATR × 0.3
```

### Comparação BTC vs GOLD

| Parâmetro | BTC (v1.3) | GOLD | Motivo |
|-----------|------------|------|--------|
| **Volume** | 0.03 | **0.01** | Conta cents, menor exposição |
| **SL Multiplier** | 1.2 | **1.5** | Gold precisa mais espaço |
| **Trailing Ativa** | 0.3 | **0.4** | Gold move mais devagar |
| **Trailing Dist** | 0.2 | **0.3** | Proteção conservadora |
| **ATR Mínimo** | 80 pts | **60 pts** | Volatilidade menor |
| **Momentum** | 0.04% | **0.03%** | Gold move menos |

---

## 📈 CÁLCULOS DETALHADOS

### ATR (Average True Range)

```python
def _calculate_atr_simple(self, rates) -> float:
    if len(rates) < 14:
        return 60.0  # Fallback para Gold

    true_ranges = []
    for i in range(1, len(rates)):
        high_low = rates[i]['high'] - rates[i]['low']
        high_close = abs(rates[i]['high'] - rates[i - 1]['close'])
        low_close = abs(rates[i]['low'] - rates[i - 1]['close'])
        true_range = max(high_low, high_close, low_close)
        true_ranges.append(true_range)

    atr = sum(true_ranges) / len(true_ranges)
    return max(atr, 60.0)  # Mínimo 60 pontos
```

**Exemplo com Gold @ $2,600:**
- ATR calculado: 65 pontos
- SL: 65 × 1.5 = **97.5 pontos** (~$9.75)
- Trailing ativa: 65 × 0.4 = **26 pontos** ($2.60 de lucro)
- Trailing distância: 65 × 0.3 = **19.5 pontos** (margem de segurança)

### Momentum

```python
MOMENTUM_BUY = 0.03   # 0.03% de movimento
MOMENTUM_SELL = -0.03
```

**Exemplo:**
- Gold @ $2,600
- Movimento necessário: $2,600 × 0.03% = **$0.78**
- Para BTC @ $110k: $110k × 0.04% = **$44**

Gold precisa movimento menor porque é mais estável.

---

## 🎯 ESTRATÉGIA LOSS ZERO

### Fluxo de Operação

```
1. ANÁLISE (a cada 15s)
   ├─ Calcular ATR (mínimo 60 pontos)
   ├─ Verificar momentum (0.03%)
   ├─ Confirmar tendência (M5 + M15)
   └─ Validar horário (evita rollover)

2. ENTRADA
   ├─ Volume: 0.01 lotes
   ├─ SL: ATR × 1.5 (~60-90 pontos)
   └─ TP: Sem TP fixo

3. TRAILING ATIVA
   ├─ Condição: Lucro >= ATR × 0.4
   ├─ Distância: ATR × 0.3
   └─ Atualiza a cada tick

4. SAÍDA
   └─ Trailing stop acionado (sempre lucro!)
```

### Confirmações para Entrada

O agente precisa de **2 de 3** confirmações:

#### Confirmação 1: Tendência + Momentum
```python
if uptrend and momentum_5m > 0.03%:
    confirmations += 1
```

#### Confirmação 2: Momentum Forte
```python
if momentum_5m > 0.045%:  # 0.03% × 1.5
    confirmations += 1
```

#### Confirmação 3: Volatilidade + Volume
```python
if high_volatility and volume_spike and price_above_avg:
    confirmations += 1
```

#### Validação Final: M15
```python
if confirmations >= 2:
    if M15_confirma_tendencia:
        ABRIR TRADE ✓
```

---

## 🚀 EXECUTAR GOLD AGENT

### Opção 1: Batch File (Recomendado)
```batch
EXECUTAR_LOSS_ZERO_GOLD.bat
```

### Opção 2: Linha de Comando
```bash
python EXECUTAR_LOSS_ZERO.py --live --symbol XAUUSDc
```

### Opção 3: Python Direto
```python
from src.agents.gold_loss_zero_simple import GoldLossZeroSimple

agent = GoldLossZeroSimple(symbol="XAUUSDc")
agent.run()
```

---

## 📊 EXPECTATIVAS DE PERFORMANCE

### Operações
- **Trades/dia:** 50-80 (menos que BTC)
- **Duração média:** 20-40 min (mais longo que BTC)
- **Win rate alvo:** 45-50%
- **R/R ratio:** >1.3:1

### Lucro Esperado (0.01 lotes)
```
Por trade:
- Lucro médio: $8-12
- Perda média SL: $6-9
- Lucro por win: ~$10

Por dia (50% win rate):
- 60 trades × 50% = 30 wins
- 30 wins × $10 = $300
- 30 losses × $7 = -$210
- Lucro líquido: ~$90/dia
```

---

## ⚠️ PROTEÇÕES E LIMITES

### Circuit Breaker
```python
max_consecutive_losses = 5  # Para após 5 perdas seguidas
circuit_breaker_cooldown = 1800  # 30 min de pausa
```

### Volume
```python
def _validate_volume(self, volume: float) -> float:
    if volume > 0.1:
        return 0.1  # Máximo 0.1 lotes
    return max(volume, 0.01)  # Mínimo 0.01 lotes
```

### Cooldown
```python
cooldown_seconds = 30  # 30s entre trades
```

### Horários Bloqueados
Sem bloqueios de horário (opera 24h), mas evita:
- Sexta 23:00 - Segunda 01:00 UTC (mercado fechado)
- Automaticamente detectado pelo MT5

---

## 🔍 MONITORAMENTO

### Indicadores no Log

Cada ciclo mostra:
```
[GOLD] Analisando...
  Preco: 2605.50
  ATR: 65.0 pontos
  SL seria: 97.5 pontos
  Trailing ativa: 26.0 pontos
  Momentum M5: +0.025%
  Confirmacoes: 1/3
  Status: Aguardando mais confirmacoes
```

### Sinais de Alerta

**Se MUITO POUCOS trades (< 30/dia):**
- Reduzir momentum para 0.025%
- Reduzir confirmações necessárias

**Se MUITOS trades (> 100/dia):**
- Aumentar momentum para 0.035%
- Exigir 3 confirmações

**Se Win Rate < 40%:**
- Aumentar SL multiplier para 1.8
- Aumentar trailing activation para 0.5

**Se Win Rate > 55%:**
- Pode reduzir SL para 1.3
- Aumentar volume para 0.02

---

## 📝 DIFERENÇAS TÉCNICAS vs BTC

### 1. Cálculo de Preço
```python
# BTC: usa digits para conversão
point_value = 10 ** symbol_info.digits

# GOLD: conta cents, ponto = $0.01
# XAUUSDc @ 2605.50 = $26.05 real
```

### 2. Spread
```python
# BTC: spread ~5-10 pontos
# GOLD cents: spread ~3-5 pontos (menor)
```

### 3. Slippage
```python
# BTC: deviation=20 (volatilidade alta)
# GOLD: deviation=10 (mais estável)
```

---

## 🧪 TESTAR CONFIGURAÇÃO

### 1. Verificar Symbol Info
```python
from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()
info = mt5.symbol_info("XAUUSDc")

print(f"Volume min: {info.volume_min}")  # 0.01
print(f"Volume max: {info.volume_max}")  # 500.0
print(f"Stop level: {info.trade_stops_level}")  # pontos mínimos SL
print(f"Spread: {info.spread}")  # spread atual
```

### 2. Testar ATR
```python
rates = mt5.copy_rates_from_pos("XAUUSDc", "M5", 0, 14)
agent = GoldLossZeroSimple()
atr = agent._calculate_atr_simple(rates)
print(f"ATR atual: {atr} pontos")
```

### 3. Dry Run (Sem Trades)
```python
# Comentar linha de order_send em _execute_trade
# Rodar por 1 hora para ver sinais gerados
```

---

## 📚 ARQUIVOS RELACIONADOS

- `src/agents/gold_loss_zero_simple.py` - Código do agente Gold
- `src/agents/btc_loss_zero_simple.py` - Código do agente BTC (referência)
- `EXECUTAR_LOSS_ZERO.py` - Executor universal (auto-detecção)
- `EXECUTAR_LOSS_ZERO_GOLD.bat` - Batch file Gold
- `AJUSTE_FILTROS_v1.2.md` - Histórico de ajustes (BTC)

---

## ❓ FAQ

### P: Posso rodar BTC e Gold simultaneamente?
**R:** Sim! São agentes independentes. Use terminais separados:
```batch
# Terminal 1
python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc

# Terminal 2
python EXECUTAR_LOSS_ZERO.py --live --symbol XAUUSDc
```

### P: Por que Gold usa volume menor?
**R:** Conta cents + menor volatilidade = menor exposição necessária. 0.01 lotes em Gold é equivalente a ~0.03 em BTC em termos de risco.

### P: Posso aumentar o volume?
**R:** Sim, mas recomendado manter ≤ 0.05 para conta cents. Acima disso, o risco aumenta demais.

### P: Gold opera fim de semana?
**R:** Não. Mercado de ouro fecha sexta ~23h e reabre segunda ~01h UTC. O agente aguarda automaticamente.

### P: Posso usar XAUUSDm (micro)?
**R:** Sim! Apenas mude o símbolo no comando. Os parâmetros são os mesmos.

---

## 🎯 PRÓXIMOS PASSOS

1. **Executar:** `EXECUTAR_LOSS_ZERO_GOLD.bat`
2. **Monitorar:** Primeiras 2 horas para validar sinais
3. **Ajustar:** Se necessário, após 24h de dados
4. **Escalar:** Se win rate > 45%, considere aumentar volume

---

**Status:** ✅ Pronto para uso
**Versão:** 1.0
**Última atualização:** 2025-11-02

**Boa sorte com o trading! 🚀📈**
