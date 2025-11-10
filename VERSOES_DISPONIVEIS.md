# Versoes Disponiveis - Gold e BTC Trading Bots

## GOLD (XAUUSDc)

### v2.0.0 - Analise Tecnica M5+M1
**Arquivo**: `src/agents/gold_loss_zero_simple.py`
**Executar**: `RUN_GOLD_AGENT.bat`

**Parametros**:
- Volume: 0.03 lotes
- SL: $5.00 fixo
- TS Activation: $2.00
- TS Distance: $1.00
- Min Score M5: 4.0
- Max ATR: $2.00
- Max Spread: $0.50

**Estrategia**:
- M5 principal (RSI, MACD, SMA, Momentum, Volume)
- M1 timing (2 velas consecutivas)
- SEM M15 (removido - conflitava com scalping)
- Filtros: ATR e Spread

**Quando Usar**:
- Custo zero
- Internet instavel
- Velocidade maxima
- Tendencias claras

---

## BTC (BTCUSDc)

### v2.0.0 - Analise Tecnica (Copia do Gold)
**Arquivo**: `src/agents/btc_loss_zero_v2.py`
**Executar**: `RUN_BTC_V2.bat`

**Parametros**:
- Volume: 0.30 lotes (10x Gold)
- SL: $5.00 fixo (mesma expectativa)
- TS Activation: $2.00
- TS Distance: $1.00
- Min Score M5: 4.0
- Max ATR: $20.00 (ajustado para BTC)
- Max Spread: $5.00 (ajustado para BTC)

**Estrategia**:
- Identica ao Gold v2.0.0
- Indicadores: RSI, MACD, SMA, Momentum, Volume
- M5 principal + M1 timing
- Filtros ajustados para volatilidade BTC

**Quando Usar**:
- Mesmas condicoes que Gold v2.0.0
- Prefere liquidez 24/7
- Opera fins de semana

---

### v3.0.0 - Analise por IA (Claude Haiku)
**Arquivo**: `src/agents/btc_ai_agent.py`
**Executar**: `RUN_BTC_AI.bat`

**Parametros**:
- Volume: 0.30 lotes
- SL: $5.00 fixo
- TS Activation: $2.00
- TS Distance: $1.00
- Min Score M5: 4.0 (score da IA)
- Filtros: Mesmos do v2.0.0

**Estrategia**:
- IA analisa velas M5 diretamente
- SEM indicadores tecnicos
- IA reconhece padroes (martelo, engolfo, pin bar)
- IA explica decisao
- Fallback para tecnico se API falhar

**Quando Usar**:
- Mercado lateral/complexo
- Quer reconhecer padroes graficos
- Pode pagar ~$3/mes
- Internet estavel
- Busca win rate 5-10% maior

**Custo**:
- ~$0.001/analise
- 100 trades/dia = $3/mes
- Tier free: 50 req/min (suficiente)

---

## Comparacao Lado a Lado

| Caracteristica | Gold v2.0.0 | BTC v2.0.0 | BTC v3.0.0 (IA) |
|---------------|-------------|------------|-----------------|
| **Analise** | Tecnica | Tecnica | IA (Claude) |
| **Indicadores** | RSI, MACD, SMA | RSI, MACD, SMA | NENHUM |
| **Volume** | 0.03 | 0.30 | 0.30 |
| **SL** | $5.00 | $5.00 | $5.00 |
| **Max ATR** | $2.00 | $20.00 | $20.00 |
| **Custo** | $0 | $0 | ~$3/mes |
| **Velocidade** | < 1ms | < 1ms | ~500ms |
| **Offline** | Sim | Sim | Nao |
| **Padroes** | Nao | Nao | Sim |
| **Win Rate Esperado** | 60-65% | 60-65% | 65-70% |

---

## Expectativa em Dolares (TODAS IGUAIS)

```
Gold v2.0.0 = BTC v2.0.0 = BTC v3.0.0

SL: $5.00
TS Activation: $2.00
TS Distance: $1.00
Avg Win: $1.50-2.00
Avg Loss: -$5.00
Point Value: $0.003/ponto
```

**Diferenca**: Apenas METODO de analise (Tecnico vs IA), NAO expectativa em $!

---

## Resultados Esperados (20 trades)

### Cenario Conservador (55% WR)

| Versao | Wins | Losses | Net |
|--------|------|--------|-----|
| Gold v2.0.0 | 11 × $1.50 | 9 × -$5.00 | -$28.50 |
| BTC v2.0.0 | 11 × $1.50 | 9 × -$5.00 | -$28.50 |
| BTC v3.0.0 | 11 × $1.50 | 9 × -$5.00 | -$28.50 - $0.02 (API) |

### Cenario Realista (60% WR)

| Versao | Wins | Losses | Net |
|--------|------|--------|-----|
| Gold v2.0.0 | 12 × $1.80 | 8 × -$5.00 | -$18.40 |
| BTC v2.0.0 | 12 × $1.80 | 8 × -$5.00 | -$18.40 |
| BTC v3.0.0 | 12 × $1.80 | 8 × -$5.00 | -$18.40 - $0.02 (API) |

### Cenario Otimista (65% WR) - Meta da IA

| Versao | Wins | Losses | Net |
|--------|------|--------|-----|
| Gold v2.0.0 | 13 × $2.00 | 7 × -$5.00 | -$9.00 |
| BTC v2.0.0 | 13 × $2.00 | 7 × -$5.00 | -$9.00 |
| **BTC v3.0.0** | **13 × $2.00** | **7 × -$5.00** | **-$9.00 - $0.02 (API)** |

**NOTA**: Para lucro consistente, precisamos:
- Win Rate >= 70%, OU
- Avg Win >= $3.00, OU
- Reduzir Avg Loss < $5.00

---

## Escolher Versao

### Comece com Gold v2.0.0
1. Teste 20-30 trades
2. Analise win rate e net result
3. Se win rate < 60%: considere outras opcoes

### Se quiser testar BTC
1. Use v2.0.0 primeiro (identico ao Gold, custo zero)
2. Compare 20-30 trades com Gold
3. Se resultados similares: BTC funciona

### Se quiser testar IA
1. Configure API Key (ver QUICK_START_AI.md)
2. Execute v3.0.0 por 20-30 trades
3. Compare com v2.0.0
4. Se win rate melhorar 5%+: vale o custo

---

## Execucao

**Gold v2.0.0**:
```batch
RUN_GOLD_AGENT.bat
```

**BTC v2.0.0** (Tecnico):
```batch
RUN_BTC_V2.bat
```

**BTC v3.0.0** (IA):
```batch
RUN_BTC_AI.bat
```

**Comparacao Paralela** (Tecnico vs IA):
```
Terminal 1: RUN_BTC_V2.bat
Terminal 2: RUN_BTC_AI.bat
```

---

## Documentacao Completa

- **CHANGELOG_V2.md**: Historico de mudancas v2.0.x
- **GOLD_V2_CHANGELOG.md**: Mudancas especificas do Gold
- **COMO_USAR_GOLD_V2.md**: Guia de uso Gold v2.0.0
- **BTC_V2_README.md**: Guia de uso BTC v2.0.0
- **BTC_AI_README.md**: Guia de uso BTC v3.0.0 (IA)
- **COMPARACAO_TECNICO_VS_IA.md**: Comparacao detalhada
- **QUICK_START_AI.md**: Configuracao rapida IA
- **GOLD_VS_BTC_V2_COMPARACAO.md**: Gold vs BTC detalhado
- **CORRECAO_ATR_FILTRO.md**: Correcao filtro ATR
- **BTC_FILTROS_AJUSTADOS.md**: Ajuste filtros BTC

---

## Resumo Final

**3 versoes disponiveis**:
1. Gold v2.0.0 (Tecnico) - Custo zero, M5+M1 scalping
2. BTC v2.0.0 (Tecnico) - Mesma estrategia, simbolo diferente
3. BTC v3.0.0 (IA) - Claude Haiku, reconhece padroes

**Mesma expectativa em $** para todas!

**Escolha baseada em**:
- Custo (zero vs $3/mes)
- Internet (estavel ou nao)
- Win rate desejado (60-65% vs 65-70%)
- Simbolo preferido (Gold vs BTC)

**Proximo passo**: Escolha uma versao e execute 20-30 trades para validar!
