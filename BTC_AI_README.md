# BTC AI AGENT - Trading com LLM Sem Indicadores Tradicionais

## Conceito

Este agente é uma abordagem REVOLUCIONÁRIA ao trading de BTC:
- **SEM RSI, MACD, Bollinger Bands, SMA** ou outros indicadores técnicos tradicionais
- Usa **LLM local (Ollama)** para analisar CONTEXTO DE MERCADO
- Baseado no Gold AI Agent que está funcionando

## Por Que Sem Indicadores?

### Problema com Indicadores Tradicionais:
1. **Paralisia por Análise**: Muitos indicadores criam conflitos
2. **Timing Ruim**: Indicadores atrasados fazem entrar tarde demais
3. **Mercado Muda**: BTC não segue padrões técnicos clássicos
4. **Saturação de Sinais**: Score alto mas entrada errada

### Solução com LLM:
1. **Contexto Holístico**: LLM vê o "quadro completo"
2. **Análise de Padrão**: Reconhece reversões e momentum
3. **Timing Melhor**: Decide baseado em movimento recente
4. **Adapt**ativo: LLM ajusta para diferentes condições

## Configuração

### Parâmetros Conservadores:
```
Volume: 0.05 lotes (ULTRA CONSERVADOR)
SL: $20.00 (amplo espaço para timing)
Trailing: Ativa $4, protege $2
Circuit Breaker: 3 perdas consecutivas
Break-Even: Move SL para entry após $2 lucro
Cooldown: 30s entre trades
```

### O Que o LLM Analisa:
- Momentum de preço (últimas 5-10 velas)
- Tendência de curto prazo (subindo/descendo?)
- Volume relativo (alto/baixo comparado à média)
- Horário do dia (sessões de mercado)
- Padrões de reversão (topos/fundos)

## Como Funciona

### 1. Coleta de Dados
```python
# Busca últimas velas M5
rates_m5 = get_rates(timeframe="M5", count=20)

# Calcula informações de contexto
price_change = (current - open) / open * 100
recent_high = max(last_10_candles)
recent_low = min(last_10_candles)
```

### 2. Prompt para LLM
```
Você é um trader profissional de Bitcoin.

DADOS DE MERCADO:
- Preço atual: $103,500
- Mudança 5min: +0.15%
- Máxima recente: $103,600
- Mínima recente: $103,400
- Momentum: SUBINDO (3 velas verdes)
- Horário: 14:30 UTC (sessão NY)

ANÁLISE: Deve comprar (BUY), vender (SELL) ou aguardar (HOLD)?

Responda APENAS: BUY, SELL ou HOLD
```

### 3. Decisão
- **BUY**: LLM vê oportunidade de alta
- **SELL**: LLM vê oportunidade de baixa  
- **HOLD**: LLM prefere aguardar melhor momento

### 4. Proteção
- SL fixo $20 protege de grandes perdas
- Trailing captura lucros quando preço favorável
- Break-Even elimina risco após $2 lucro
- Circuit Breaker para após 3 perdas

## Vantagens vs BTC v3.2.0 (com indicadores)

| Aspecto | BTC v3.2.0 | BTC AI |
|---------|------------|--------|
| **Indicadores** | RSI, MACD, BB, SMA | NENHUM |
| **Decisão** | Score >= 4.5 | LLM contexto |
| **Timing** | Pode atrasar | Mais rápido |
| **Adaptação** | Fixo | LLM adapta |
| **Complexidade** | Alta | Média |
| **Entrada Errada** | Frequente | Menos |

## Como Usar

### 1. Iniciar Ollama
```batch
ollama serve
```

### 2. Verificar Modelo
```batch
ollama list
# Deve mostrar llama3.2:1b
```

### 3. Executar Agente
```batch
RUN_BTC_AI.bat
```

## Monitoramento

### O Que Observar:
1. **Decisões da IA**: BUY/SELL/HOLD e justificativa
2. **Tempo de Resposta**: < 2 segundos ideal
3. **Erros da IA**: Circuit breaker após 5 erros
4. **Win Rate**: Deve ser > 60% com LLM

### Logs da IA:
```
[IA] Consultando LLM para decisão...
[IA] Decisão: BUY (confiança: alta)
[IA] Razão: Momentum forte + sessão NY ativa
[IA] Tempo de resposta: 1.2s
```

## Fallback

Se Ollama falhar ou IA errar muito:
- Agente usa **método tradicional simples**
- Busca tendência M5 (5/8 velas mesmo sentido)
- Confirma com M1 (2 velas consecutivas)
- Mantém todas as proteções (SL, trailing, etc)

## Comparação com Gold AI

### Semelhanças:
- Mesma arquitetura (IA + Trailing)
- Mesmo modelo LLM (llama3.2:1b)
- Mesmas proteções (circuit breaker, break-even)

### Diferenças:
- **Symbol**: XAUUSDc → BTCUSDc
- **Volume**: 0.02 → 0.05 (BTC menos volátil por lote)
- **SL**: $5 → $20 (BTC precisa mais espaço)
- **Prompt**: Adaptado para BTC (não ouro)

## Próximos Passos

### Teste Inicial (24h):
1. Executar `RUN_BTC_AI.bat`
2. Observar primeiras 5-10 trades
3. Verificar win rate
4. Comparar com BTC v3.2.0

### Se Win Rate < 55%:
- Ajustar temperatura LLM (0.1 → 0.2)
- Modificar prompt (mais conservador)
- Aumentar SL ($20 → $25)

### Se Win Rate > 65%:
- Manter configuração
- Considerar aumentar volume (0.05 → 0.10)
- Documentar padrões de sucesso

## Conclusão

**BTC AI Agent** elimina a "paralisia por análise" dos indicadores tradicionais e deixa o LLM decidir baseado em CONTEXTO DE MERCADO.

É uma aposta que **simplicidade + LLM > complexidade de indicadores**.

Vamos testar!
