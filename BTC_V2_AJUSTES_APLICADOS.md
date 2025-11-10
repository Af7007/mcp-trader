# BTC v2.0.0 → v2.0.1 - Ajustes Aplicados

**Data**: 2025-11-08
**Motivo**: Agente rodou 2h sem operacoes

---

## DIAGNOSTICO REALIZADO

### Problema Reportado
```
Usuario: "RUN_BTC_V2.bat rodou por 2h sem nenhuma operacao"
```

### Investigacao (debug_btc_blocking.py)
```
Passo 1: Conexao MT5 → OK
Passo 2: Simbolo BTCUSDc → OK
Passo 3: Dados M5 (50 velas) → OK
Passo 4: Indicadores M5 calculados → OK
Passo 5: Score M5 = 3.5 → BLOQUEADO (min era 4.0)
Passo 6: Spread = $18.00 → BLOQUEADO (max era $5.00)
Passo 7: M1 timing → Nao chegou a verificar
```

---

## BLOQUEIOS IDENTIFICADOS

### Bloqueio #1: Score M5 Insuficiente
```
ANTES:
  Min Score M5: 4.0
  Score Atual: 3.5
  Resultado: BLOQUEADO

Razao:
  - Mercado lateral (sem tendencia clara)
  - RSI neutro (62.6)
  - Momentum baixo (+0.24%)
  - Faltava 0.5 pontos
```

### Bloqueio #2: Spread Alto
```
ANTES:
  Max Spread: $5.00
  Spread Atual: $18.00
  Resultado: BLOQUEADO

Razao:
  - Conta Cent (spreads maiores)
  - Horario Asia (baixa liquidez)
  - Demo account (spreads aumentados)
```

---

## AJUSTES APLICADOS

### Ajuste #1: Reduzir Score Minimo
```
ANTES:
  self.min_score_m5 = 4.0

DEPOIS:
  self.min_score_m5 = 3.5

Impacto:
  + Permite trades em mercado lateral
  + Mais oportunidades de entrada
  - Pode reduzir win rate (sinais menos fortes)
```

**Arquivo**: `src/agents/btc_loss_zero_v2.py` (linha 109)

**Atualizacoes Relacionadas**:
- Linha 11: Comentario header
- Linha 182: Mensagem de inicializacao
- Linha 193: Print estrategia
- Linha 726: Docstring _get_simple_signal()
- Linha 788: Docstring _analyze_m5_trend()
- Linha 813, 847: Comentarios de score
- Linha 838, 872: Validacao score

---

### Ajuste #2: Aumentar Limite de Spread
```
ANTES:
  self.max_spread_dollars = 5.0

DEPOIS:
  self.max_spread_dollars = 20.0

Impacto:
  + Aceita spreads tipicos de BTC
  + Permite operar em horarios de baixa liquidez
  - Custo maior por trade ($18 vs $5)
```

**Arquivo**: `src/agents/btc_loss_zero_v2.py` (linha 111)

**Atualizacoes Relacionadas**:
- Linha 14: Comentario header
- Linha 194-195: Print estrategia (ATR e Spread)

---

## COMPARACAO: ANTES vs DEPOIS

### Parametros Alterados

| Parametro | ANTES (v2.0.0) | DEPOIS (v2.0.1) | Mudanca |
|-----------|----------------|-----------------|---------|
| **Min Score M5** | 4.0 | 3.5 | -12.5% |
| **Max Spread** | $5.00 | $20.00 | +300% |
| **Max ATR** | $20.00 | $20.00 | - |

### Parametros Mantidos

| Parametro | Valor | Motivo |
|-----------|-------|--------|
| Volume | 0.30 | Equivalencia $ com Gold |
| SL Fixo | $5.00 | Mesma expectativa |
| TS Activation | $2.00 | Otimo para scalping |
| TS Distance | $1.00 | Protecao adequada |
| Max ATR | $20.00 | Ja ajustado para BTC |

---

## TESTE ANTES vs DEPOIS

### ANTES (v2.0.0) - Bloqueado
```
[5/7] Calculando SCORE M5 (minimo 4.0 para trade)...
  BUY Score: 3.5 [INSUFICIENTE]
  [BLOQUEIO] Nenhum score >= 4.0

[6/7] Verificando FILTROS de seguranca...
  Spread: $18.00
  Max Spread permitido: $5.00
  [BLOQUEIO SPREAD] Custo muito alto!

RESULTADO: NENHUM TRADE (2 bloqueios)
```

### DEPOIS (v2.0.1) - Liberado
```
[5/7] Calculando SCORE M5 (minimo 3.5 para trade)...
  BUY Score: 3.5 [OK]
  [M5 SINAL] BUY (score 3.5)

[6/7] Verificando FILTROS de seguranca...
  ATR M5: $0.60 [OK]
  Spread: $18.00
  Max Spread permitido: $20.00
  [OK] Spread dentro do limite

[7/7] Verificando timing M1...
  [BLOQUEIO M1] Aguardando 2 velas UP em M1

RESULTADO: AGUARDANDO M1 (proximo trade em 1-2 min)
```

---

## IMPACTO ESPERADO

### Positivo
```
+ Mais trades executados
+ Funciona em horarios de baixa liquidez
+ Aceita mercado lateral (score 3.5-4.0)
+ Compativel com conta Cent/Demo
```

### Negativo
```
- Custo maior por spread ($18 vs $5)
- Win rate pode cair ~5% (sinais menos fortes)
- Scalping dificultado (spread alto)
```

### Mitigacao
```
1. Operar em horarios de alta liquidez (spread < $15)
2. Monitorar win rate primeiras 20-30 trades
3. Se win rate < 55%, voltar score 4.0
4. Se spread continuar > $15, considerar Gold
```

---

## PROXIMOS PASSOS

### Imediato (Agora)
```
1. Executar: RUN_BTC_V2.bat
2. Aguardar primeiro trade (proximo 1-3 min)
3. Verificar se trade abre corretamente
```

### Monitoramento (24-48h)
```
1. Contar total de trades abertos
2. Medir win rate
3. Calcular avg win/loss
4. Comparar com Gold v2.0.0
```

### Ajustes Futuros (Se Necessario)
```
Se win rate < 55%:
  → Voltar min_score_m5 = 4.0

Se spread sempre > $15:
  → Focar em Gold (spreads menores)
  → OU operar BTC apenas 13:00-22:00 UTC

Se avg win < $2.00:
  → Aumentar TS activation para $3.00
  → Compensa spread alto
```

---

## ARQUIVOS MODIFICADOS

```
1. src/agents/btc_loss_zero_v2.py
   - Linha 109: min_score_m5 = 3.5
   - Linha 111: max_spread_dollars = 20.0
   - 8 linhas de comentarios/prints atualizados

2. debug_btc_blocking.py
   - Script de diagnostico criado
   - Valida todos os filtros em tempo real

3. ANALISE_BTC_PARAMETROS.md
   - Analise completa via MCP
   - Comparacao Gold vs BTC
   - Recomendacoes

4. BTC_V2_AJUSTES_APLICADOS.md
   - Este arquivo (documentacao)
```

---

## RESUMO EXECUTIVO

### O Que Foi Feito?
```
Reduzido score minimo de 4.0 para 3.5
Aumentado spread maximo de $5 para $20
```

### Por Que?
```
Score 4.0 muito restritivo para mercado lateral
Spread $5 impossivel em BTC (tipico $15-20)
```

### Resultado?
```
Agente agora FUNCIONA e esta pronto para operar
Aguardando apenas confirmacao M1 (1-2 min)
```

### Proximo Passo?
```
EXECUTAR: RUN_BTC_V2.bat
```

---

**BTC v2.0.1 PRONTO PARA OPERAR!**
