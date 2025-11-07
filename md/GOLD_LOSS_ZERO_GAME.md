# GOLD LOSS ZERO GAME - Sistema de Predição M1

## Conceito

Sistema completamente novo de trading focado em **predição do próximo candle** (não indicadores tradicionais) com **trailing agressivo** e **múltiplas posições gerenciadas**.

## Características Principais

### 1. Timeframe: M1 (1 minuto)
- Trabalha em candles de 1 minuto
- Análise de momentum dos últimos 3 candles
- Foco em movimentos rápidos

### 2. Sistema de Predição (Não Indicadores!)
O sistema **não usa** RSI, MACD, Bollinger Bands ou outros indicadores tradicionais.

**Predição baseada em:**
- **Momentum dos últimos 3 candles M1**
  - Calcula variação % de cada candle
  - Identifica direção dominante (2 de 3)

- **Tendência recente**
  - Se 2+ candles têm momentum positivo → Tendência de ALTA
  - Se 2+ candles têm momentum negativo → Tendência de BAIXA

- **Confiança do sinal**
  - Baseada na força do momentum atual
  - Quanto maior o momentum, maior a confiança

**Exemplo:**
```
Candle 1: +0.05% (alta)
Candle 2: +0.03% (alta)
Candle 3: -0.01% (baixa)

Resultado: 2 de 3 positivos → SINAL DE BUY
Confiança: 5% (baseado no momentum atual)
```

### 3. Trailing Agressivo

#### SL Inicial: $2 fixo
- Toda posição abre com SL de $2
- Proteção inicial conservadora

#### Trailing Ativa Quando Positiva
- **Qualquer lucro > $0** ativa o trailing
- Primeiro movimento: **breakeven** (SL vai para preço de entrada)
- Garante que após positivar, nunca mais perde!

#### Trailing Sobe a Cada $0.10
```
Lucro $0.00 → SL no breakeven (nível 0)
Lucro $0.10 → SL sobe (nível 1)
Lucro $0.20 → SL sobe (nível 2)
Lucro $0.30 → SL sobe (nível 3)
... e assim por diante
```

**Exemplo Real:**
```
Posição BUY em $2,600.00
SL inicial: $2,500.00 (-$2.00)

Preço sobe para $2,605.00 → Lucro: $0.05
  ✓ TRAILING ATIVA
  → SL move para $2,600.00 (breakeven)

Preço sobe para $2,650.00 → Lucro: $1.00
  ↗ TRAILING SUBIU
  → SL agora em $2,645.00 (nível 10)
  → Lucro protegido: $0.90
```

### 4. Múltiplas Posições Simultâneas

#### Máximo: 3 posições ao mesmo tempo

#### REGRA CRÍTICA:
**Só abre nova ordem se TODAS as anteriores têm trailing positivo!**

```
Cenário 1 - Pode abrir:
  Posição A: ✓ Trailing ativo
  Posição B: ✓ Trailing ativo
  → Pode abrir Posição C

Cenário 2 - NÃO pode abrir:
  Posição A: ✓ Trailing ativo
  Posição B: ⏳ Aguardando trailing
  → Aguarda Posição B positivar
```

**Por que essa regra?**
- Evita acumular múltiplas posições negativas
- Garante que sistema só expande quando está ganhando
- Reduz risco exponencial

### 5. Worker MUITO Ativo

**Intervalo: 1 segundo** (vs. 15 segundos dos outros agentes)

**Por que tão ativo?**
- Captura movimentos de $0.10 rapidamente
- Atualiza trailing em tempo real
- Crucial para trailing agressivo funcionar

**O que o worker faz:**
```python
A cada 1 segundo:
1. Verifica TODAS as posições abertas
2. Calcula lucro atual de cada uma
3. Ativa trailing quando positiva
4. Sobe trailing a cada $0.10
5. Verifica se pode abrir nova posição
```

## Configuração

### Arquivo: `gold_loss_zero_game.py`

```python
GoldLossZeroGame(
    symbol="XAUUSDc",                # Gold
    volume=0.02,                     # 0.02 lotes
    sl_initial_dollars=2.0,          # $2 SL inicial
    trailing_step_dollars=0.10,      # Sobe a cada $0.10
    worker_interval=1.0,             # 1 segundo
    max_positions=3                  # Máx. 3 posições
)
```

### Parâmetros Ajustáveis

| Parâmetro | Valor Padrão | Descrição |
|-----------|--------------|-----------|
| `volume` | 0.02 | Volume por posição (lotes) |
| `sl_initial_dollars` | 2.0 | SL inicial em dólares |
| `trailing_step_dollars` | 0.10 | Step do trailing |
| `worker_interval` | 1.0 | Intervalo do worker (segundos) |
| `max_positions` | 3 | Máximo de posições simultâneas |

**Exemplo de ajuste mais agressivo:**
```python
volume=0.03,                     # Lote maior
trailing_step_dollars=0.05,      # Trailing mais agressivo (a cada $0.05)
worker_interval=0.5,             # Worker ainda mais ativo (0.5s)
max_positions=5                  # Até 5 posições
```

**Exemplo de ajuste mais conservador:**
```python
volume=0.01,                     # Lote menor
trailing_step_dollars=0.20,      # Trailing menos agressivo (a cada $0.20)
worker_interval=2.0,             # Worker menos ativo (2s)
max_positions=2                  # Apenas 2 posições
```

## Execução

### 1. Via Batch File (Recomendado)
```batch
RUN_GOLD_LOSS_ZERO_GAME.bat
```

### 2. Via Python Direto
```bash
python src\agents\gold_loss_zero_game.py
```

### 3. Com Parâmetros Customizados
Edite o arquivo `gold_loss_zero_game.py` na linha 462:
```python
agent = GoldLossZeroGame(
    symbol="XAUUSDc",
    volume=0.02,  # Ajuste aqui
    # ... outros parâmetros
)
```

## Output Esperado

### Inicialização
```
============================================================
GOLD LOSS ZERO GAME - Sistema de Predição M1
============================================================
Symbol: XAUUSDc
Volume: 0.02 lotes
SL Inicial: $2.00
Trailing Step: $0.10
Worker Interval: 1.0s (MUITO ATIVO)
Max Posições Simultâneas: 3

ESTRATÉGIA:
1. Predição do próximo candle M1
2. SL fixo de $2.0
3. Trailing ativa quando positiva
4. Trailing sobe a cada $0.10
5. Nova ordem só se todas têm trailing positivo
============================================================

[14:30:25] INICIANDO Gold Loss Zero Game...
Worker ativo a cada 1.0s
```

### Durante Execução
```
[14:30:30] Ciclo #5 | Posições: 0/3 | P&L: $0.00

============================================================
[14:30:35] NOVA POSIÇÃO ABERTA
============================================================
Ticket: 123456
Tipo: BUY
Preço: $2,600.00
Volume: 0.02
SL Inicial: $2,500.00 ($2.00)
Confiança: 5.2%
Posições Ativas: 1/3
============================================================

[14:30:40] ✓ TRAILING ATIVADO - Ticket 123456
  SL movido para BREAKEVEN: $2,600.00
  Lucro atual: $0.03

[14:30:45] ↗ TRAILING SUBIU - Ticket 123456
  Nível: 0 → 1
  SL: $2,600.00 → $2,605.00
  Lucro: $0.12

[14:30:50] ✅ POSIÇÃO FECHADA COM LUCRO - Ticket 123456
  Resultado: $0.15
  Total P&L: $0.15
```

## Diferenças vs. Outros Sistemas

| Característica | Gold Loss Zero Game | BTC/Gold Loss Zero Simple |
|----------------|---------------------|---------------------------|
| Timeframe | M1 (1 minuto) | M5 + M15 (5 e 15 minutos) |
| Análise | Predição de momentum | Indicadores (RSI, MACD, BB) |
| SL | $2 fixo | ATR × 1.5 (dinâmico) |
| Trailing | A cada $0.10 | ATR × 0.3 (dinâmico) |
| Múltiplas posições | Sim (até 3) | Não (apenas 1) |
| Worker | 1 segundo | 2 segundos (via worker thread) |
| Foco | Agressivo, rápido | Conservador, confirmação múltipla |

## Estatísticas

O sistema rastreia automaticamente:
- Total de trades
- Vitórias / Perdas
- Win rate %
- Total P&L

**Ver ao finalizar (Ctrl+C):**
```
============================================================
ESTATÍSTICAS FINAIS - Gold Loss Zero Game
============================================================
Total de Trades: 15
Vitórias: 10
Perdas: 5
Win Rate: 66.7%
Total P&L: $1.50
============================================================
```

## Riscos e Considerações

### Riscos
1. **Alta frequência** - Muitas operações por dia
2. **Slippage** - Em M1, spread pode impactar
3. **Múltiplas posições** - Exposição aumenta com 3 posições
4. **Worker ativo** - Consome mais recursos

### Mitigações
1. **SL fixo de $2** - Perda máxima conhecida
2. **Trailing agressivo** - Protege lucro rapidamente
3. **Regra de trailing positivo** - Não expande quando perdendo
4. **Volume baixo (0.02)** - Exposição controlada

## Melhorias Futuras

### Sistema de Predição Mais Sofisticado
- Machine Learning para prever próximo candle
- Análise de padrões de candles (engulfing, doji, etc.)
- Volume profile

### Trailing Dinâmico
- Step variável baseado em volatilidade
- Trailing mais agressivo em trends fortes
- Trailing mais conservador em lateralização

### Gestão de Risco Avançada
- Circuit breaker por drawdown
- Máximo de perdas consecutivas
- Redução de volume após perdas

## Suporte

Para dúvidas ou problemas:
1. Verificar logs no console
2. Conferir posições no MT5
3. Ajustar parâmetros conforme necessário
4. Testar em conta demo primeiro!

---

**Desenvolvido para trading agressivo em M1 com foco em predição e trailing incremental.**
