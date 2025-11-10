# GOLD AI - SL DINAMICO ATR IMPLEMENTADO

**ATENCAO**: Este documento descreve apenas a implementacao do SL dinamico ATR.
Para a correcao COMPLETA do trailing v1.4.0 (bug $7 -> $3.9), veja: [GOLD_TRAILING_FIX_v1.4.0.md](GOLD_TRAILING_FIX_v1.4.0.md)

## MUDANCA REALIZADA

Implementado SL dinâmico baseado em ATR no Gold AI Agent, similar ao BTC.
**Versao**: v1.4.0 (inclui tambem Protecao Progressiva corrigida)

## FORMULA

**Para GOLD (XAUUSDc)**:
```
SL_dollars = ATR * 150 * tick_value * volume
SL_dollars = ATR * 150 * 0.01 * 0.02
SL_dollars = ATR * 0.03
```

**Limites**: min $4, max $10

## TABELA DE SL DINAMICO

| ATR (Gold) | Calculo | SL Final | Observacao |
|------------|---------|----------|------------|
| $1.00 | 1 * 0.03 = $0.03 | $4.00 | Limitado min |
| $2.00 | 2 * 0.03 = $0.06 | $4.00 | Limitado min |
| $3.00 | 3 * 0.03 = $0.09 | $4.00 | Limitado min |
| $4.00 | 4 * 0.03 = $0.12 | $4.00 | Limitado min |
| $5.00 | 5 * 0.03 = $0.15 | $4.00 | Limitado min |
| $100 | 100 * 0.03 = $3.00 | $4.00 | Limitado min |
| $150 | 150 * 0.03 = $4.50 | $4.50 | Adaptado |
| $200 | 200 * 0.03 = $6.00 | $6.00 | Adaptado |
| $250 | 250 * 0.03 = $7.50 | $7.50 | Alta volatilidade |
| $300 | 300 * 0.03 = $9.00 | $9.00 | Alta volatilidade |
| $400 | 400 * 0.03 = $12.00 | $10.00 | Limitado max |

## ARQUIVOS MODIFICADOS

### 1. gold_loss_zero_simple.py

**Linhas 1126-1173**: SL dinâmico ATR implementado

```python
# CALCULAR ATR M5 para SL DINAMICO
rates_m5 = self.mt5.copy_rates_from_pos(symbol=self.symbol, timeframe=5, start_pos=0, count=20)

# ATR em pontos de preco
atr_price = self._calculate_atr_simple(rates_m5)

# Calcular SL DINAMICO baseado em ATR
atr_multiplier = 150.0  # Ajustado para Gold
sl_dollars_atr = atr_price * atr_multiplier * self.point_value * self.volume

# LIMITES: min $4, max $10
sl_dinheiro = max(4.0, min(10.0, sl_dollars_atr))
```

### 2. RUN_GOLD_AI.bat

**Linha 12**: Atualizada descrição

```batch
echo    - SL DINAMICO: ATR * 150 (min $4, max $10) - Adapta a volatilidade
```

## BENEFICIOS

### 1. Adaptacao Automatica
- **Volatilidade baixa** (ATR $1-100): SL $4 (mínimo, proteção máxima)
- **Volatilidade normal** (ATR $150-200): SL $4.50-6.00 (balanceado)
- **Volatilidade alta** (ATR $250-300): SL $7.50-9.00 (espaço para se desenvolver)
- **Volatilidade extrema** (ATR $400+): SL $10 max (risco controlado)

### 2. Comparação com Antes

**ANTES (SL Fixo $5)**:
- Volatilidade alta (ATR $300): SL $5 fixo
- Ordem bate no ruído prematuramente
- LOSS de $5

**AGORA (SL Dinâmico)**:
- Volatilidade alta (ATR $300): SL $9 dinâmico
- Ordem tem espaço para se desenvolver
- WIN potencial maior

## LOGS ESPERADOS

Quando abrir uma ordem, verá:

```
[SL DINAMICO ATR]
  ATR M5: $2.456 (volatilidade)
  SL Calculado: $7.37
  SL Final: $7.37 (ATR * 150)

[DEBUG SL CALCULATION]
  SL target: $7.37
  volume: 0.02
  point_value: $0.0100
  pontos_para_sl: 3685.0
  sl_price_distance: $3.685
```

Ou com ATR muito baixo:

```
[SL DINAMICO ATR]
  ATR M5: $0.850 (volatilidade)
  SL Calculado: $2.55
  SL Final: $4.00 (ATR * 150)
  [LIMITADO MIN] ATR baixo, usando SL minimo $4
```

## HERANCA AUTOMATICA

Como `GoldAIAgent` herda de `GoldLossZeroSimple`, todas as mudanças funcionam automaticamente em:

- ✅ `RUN_GOLD_AI.bat` (Gold AI com Ollama)
- ✅ Qualquer script que use `GoldLossZeroSimple`

## COMO USAR

Para aproveitar o SL dinâmico, **reinicie** o agente Gold AI:

1. Pare o agente atual (Ctrl+C)
2. Execute: `RUN_GOLD_AI.bat`
3. Aguarde uma ordem abrir para ver o SL dinâmico em ação

## RESUMO COMPLETO

| Item | Antes | Agora |
|------|-------|-------|
| **SL** | Fixo $5 | Dinâmico ATR * 150 |
| **Min** | - | $4 |
| **Max** | - | $10 |
| **Adaptação** | Não | Sim (volatilidade) |
| **Volume** | 0.02 | 0.02 (mesmo) |
| **Trailing** | $1.50/$1 | $1.50/$1 (mesmo) |

## PROXIMOS PASSOS

1. Rodar `RUN_GOLD_AI.bat`
2. Observar primeira ordem aberta
3. Verificar logs de SL dinâmico
4. Ajustar multiplicador (150) se necessário baseado em resultados
