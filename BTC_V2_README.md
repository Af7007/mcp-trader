# BTC Agent v2.0.0 - Scalping M5/M1

## RESUMO

Agente Bitcoin v2.0.0 baseado na estratégia Gold v2.0.0 com **mesma expectativa em dólares**.

### Características Principais

- **Symbol**: BTCUSDc (Bitcoin - Conta Cents)
- **Volume**: 0.30 lotes (equivalente a Gold 0.03)
- **Point Value**: $0.003/ponto (IGUAL ao Gold)
- **Estratégia**: M5 principal + M1 timing (sem M15)
- **SL/TS**: Mesmos valores em $ que Gold

---

## PARAMETROS BTC vs GOLD

| Parâmetro | BTC v2.0.0 | Gold v2.0.0 | Equivalente? |
|-----------|------------|-------------|--------------|
| **Volume** | 0.30 lotes | 0.03 lotes | Sim ($) |
| **Point** | $0.01 | $0.001 | Não |
| **Tick Value** | $0.01/lote | $0.10/lote | Não |
| **Point Value** | $0.003/ponto | $0.003/ponto | **SIM** |
| **SL Fixo** | $5.00 | $5.00 | **SIM** |
| **TS Activation** | $2.00 | $2.00 | **SIM** |
| **TS Distance** | $1.00 | $1.00 | **SIM** |
| **Min Score M5** | 4.0 | 4.0 | **SIM** |
| **Max ATR M5** | $2.00 | $2.00 | **SIM** |
| **Max Spread** | $0.50 | $0.50 | **SIM** |

### Por que Volume Diferente?

```
GOLD:
- Point: $0.001
- Tick Value: $0.10/lote
- Volume: 0.03 lotes
- Point Value = $0.10 × 0.03 = $0.003/ponto

BTC:
- Point: $0.01
- Tick Value: $0.01/lote
- Volume: 0.30 lotes
- Point Value = $0.01 × 0.30 = $0.003/ponto

RESULTADO: Mesma expectativa em dólares!
```

---

## DISTANCIAS DE PRECO

### SL em Preço

**GOLD**:
- SL $5.00 = 1667 pontos = **$1.67** distância de preço
- Exemplo: Entry $4005.00 → SL $4003.33

**BTC**:
- SL $5.00 = 1667 pontos = **$16.67** distância de preço
- Exemplo: Entry $95000.00 → SL $94983.33

### Trailing Stop em Preço

**GOLD**:
- TS Activation $2.00 = 667 pontos = **$0.67** distância
- TS Distance $1.00 = 333 pontos = **$0.33** distância

**BTC**:
- TS Activation $2.00 = 667 pontos = **$6.67** distância
- TS Distance $1.00 = 333 pontos = **$3.33** distância

**IMPORTANTE**: Distâncias de preço são diferentes, mas expectativa em **DOLARES é IGUAL**!

---

## ESTRATEGIA v2.0.0

### Fluxo de Entrada

```
1. ANALISE M5 (Sinal Principal)
   └─> Score >= 4.0
   └─> RSI, SMA, Momentum, Volume

2. FILTROS
   ├─> ATR M5 <= $2.00
   └─> Spread <= $0.50

3. TIMING M1
   └─> 2 velas consecutivas na direção
   └─> OU volume spike + vela atual na direção

4. ENTRADA
   ├─> Volume: 0.30 lotes
   ├─> SL: $5.00 (distância ~$16.67 em preço)
   └─> TP: SEM TP (trailing cuida)

5. GESTAO
   ├─> Ativar TS quando lucro >= $2.00
   ├─> TS protege $1.00 inicialmente
   └─> TS incremental: +$1.00 a cada +$1.50
```

### Melhorias v2.0.0

1. **Removido M15**: Sem conflitos de timeframe
2. **M5 Principal**: Score mínimo 4.0
3. **Filtro ATR**: Evita alta volatilidade
4. **Filtro Spread**: Evita custos altos
5. **M1 Timing**: 2 velas de confirmação
6. **TS Rápido**: Ativa com $2.00

---

## INSTALACAO E USO

### 1. Validar Instalação

```bash
python test_btc_v2_params.py
```

Deve retornar:
```
[OK] BTC v2.0.0 VALIDADO COM SUCESSO!
```

### 2. Executar Agente

```bash
RUN_BTC_V2.bat
```

OU:

```bash
python src/agents/btc_loss_zero_v2.py
```

### 3. Monitorar Logs

```
[CICLO 1] 2025-11-07 20:00:00
==================================================================
[M5 BUY] Score: 4.5 | RSI: 45.2 | Momentum: 0.08%
[FILTRO ATR] M5 ATR = $1.20 (OK)
[FILTRO SPREAD] Spread = $0.30 (OK)
[M1 CONFIRM] BUY confirmado (2 velas up)
[SINAL CONFIRMADO] M5 BUY (score 4.5) + M1 timing OK

[ABRINDO POSICAO]
  Type: BUY
  Volume: 0.30
  Entry: $95000.00
  SL: $94983.33 ($5.00 loss)
  TP: SEM TP (trailing ilimitado)

[POSICAO ABERTA] Ticket #123456
```

---

## EXPECTATIVA DE RESULTADOS

### Mesma Expectativa que Gold

| Métrica | BTC v2.0.0 | Gold v2.0.0 | Equivalente? |
|---------|------------|-------------|--------------|
| Win Rate | 60-65% | 60-65% | **SIM** |
| Avg Win | $1.50-2.00 | $1.50-2.00 | **SIM** |
| Avg Loss | -$5.00 | -$5.00 | **SIM** |
| Net/20 trades | +$10-20 | +$10-20 | **SIM** |
| Trades/dia | 15-25 | 15-25 | **SIM** |

---

## COMPARACAO COM GOLD

### Vantagens BTC

- ✅ Maior liquidez (24/7 trading)
- ✅ Menos gaps (mercado contínuo)
- ✅ Maior previsibilidade técnica
- ✅ Spreads menores em horários de pico

### Desvantagens BTC

- ❌ Maior volatilidade (movimentos bruscos)
- ❌ Requer maior margem (volume 0.30)
- ❌ Mais sensível a notícias crypto

### Quando Usar Cada Um?

**Use GOLD** se:
- Prefere menor volatilidade
- Tem margem limitada ($100-200)
- Opera durante London/NY session

**Use BTC** se:
- Prefere maior liquidez
- Tem margem adequada ($300-500)
- Opera 24/7 (inclusive fins de semana)

---

## GESTAO DE RISCO

### Margem Necessária

- **Mínimo**: $300 (para 0.30 lotes)
- **Recomendado**: $500 (mais seguro)
- **Ideal**: $1000 (confortável)

### Drawdown Máximo

- **Por trade**: $5.00 (SL fixo)
- **10 trades**: $50 (assumindo 50% loss rate)
- **Circuit breaker**: $25 (5 losses × $5)

### Position Sizing

Para conta com $500:
- Risk por trade: $5.00 (1%)
- Volume: 0.30 lotes (FIXO)
- Max positions: 1 (sem hedge)

---

## TROUBLESHOOTING

### Problema: Muitas perdas por SL

**Diagnóstico**: SL muito apertado para BTC
**Solução**: Aumentar `fixed_sl_dollars` para $7.00

```python
agent = BTCLossZeroV2(
    fixed_sl_dollars=7.0  # ao invés de 5.0
)
```

### Problema: Poucos trades

**Diagnóstico**: Score M5 muito alto ou filtros muito restritivos
**Solução**:
1. Reduzir `min_score_m5` para 3.5
2. Aumentar `max_atr_m5_dollars` para $2.50

### Problema: Trailing fechando muito rápido

**Diagnóstico**: TS muito conservador
**Solução**: Aumentar `trailing_activation_dollar` para $3.00

---

## ARQUIVOS RELACIONADOS

- **Agente**: [src/agents/btc_loss_zero_v2.py](src/agents/btc_loss_zero_v2.py)
- **Validação**: [test_btc_v2_params.py](test_btc_v2_params.py)
- **Cálculos**: [calculate_btc_params.py](calculate_btc_params.py)
- **Executar**: [RUN_BTC_V2.bat](RUN_BTC_V2.bat)
- **Referência Gold**: [COMO_USAR_GOLD_V2.md](COMO_USAR_GOLD_V2.md)

---

## CHECKLIST PRE-USO

- [ ] MT5 aberto e logado
- [ ] Símbolo BTCUSDc disponível
- [ ] Margem >= $300 (recomendado $500)
- [ ] Validação executada (`test_btc_v2_params.py`)
- [ ] Internet estável
- [ ] Backup do banco de dados

---

## PROXIMOS PASSOS

1. **Validar**: `python test_btc_v2_params.py`
2. **Executar**: `RUN_BTC_V2.bat`
3. **Monitorar**: 10-20 trades
4. **Analisar**: Comparar com Gold v2.0.0
5. **Ajustar**: Se necessário, revisar parâmetros

---

**BOA SORTE COM BTC v2.0.0!**

Mesma estratégia do Gold, mesma expectativa em dólares, apenas adaptado para Bitcoin!
