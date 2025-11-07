# Gold AI Agent - Documentação Completa

## Visão Geral

O **Gold AI Agent** é um agente de trading híbrido que combina:
- **Inteligência Artificial Local** (Ollama) para decisões de entrada
- **Trailing Stop Comprovado** (Gold Loss Zero Simple) para proteção de lucro

## Características Principais

### 🤖 Inteligência Artificial
- **Modelo Local**: Ollama com llama3.2:1b
- **Sem Custos**: Funciona offline, sem API key
- **Análise Completa**: Preço, momentum, volume, tendência
- **Contexto Inteligente**: Horários, sessão, histórico de decisões

### 🛡️ Trailing Stop
- **Proteção Comprovada**: Herdado do Gold Loss Zero Simple
- **Ativação**: $1.00 de lucro
- **Distância**: $0.50 inicial, sobe $1.00 por nível
- **Zero Loss**: Impossível perder após ativação

### 🔄 Sistema Híbrido
- **IA Decide**: Entrada (BUY/SELL/HOLD)
- **Trailing Protege**: Gestão de risco automática
- **Fallback**: Método tradicional se IA falhar
- **Monitoramento**: Logs detalhados de performance

## Arquitetura

```
┌─────────────────────┐
│   MT5 Direct Client │
│   (Dados de Mercado)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Data Formatter    │
│   (Prepara dados    │
│    para IA)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Ollama Client     │
│   (IA Local)        │
│   llama3.2:1b       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Decision Parser   │
│   (Interpreta IA)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Trade Execution   │
│   + Trailing Stop   │
│   (Gold Loss Zero)  │
└─────────────────────┘
```

## Vantagens da Solução

### ✅ IA Local (Ollama)
- **Privacidade**: Dados não saem do computador
- **Custo Zero**: Sem mensalidade de API
- **Controle Total**: Modelo e parâmetros sob controle
- **Offline**: Funciona sem internet
- **Personalizável**: Pode ser treinado com dados específicos

### ✅ Trailing Stop Comprovado
- **Zero Loss**: Sistema testado e aprovado
- **Lucro Protegido**: Ativação automática
- **Worker Thread**: Monitoramento em tempo real
- **Multi-Posição**: Suporte a múltiplas operações

### ✅ Sistema Híbrido
- **IA + Tradicional**: Melhor dos dois mundos
- **Fallback Automático**: Nunca fica sem trading
- **Monitoramento**: Performance da IA rastreada
- **Flexível**: IA pode ser desabilitada

## Comparação com Agentes Anteriores

| Característica | Gold Adaptive | Gold AI Agent |
|---------------|---------------|---------------|
| **Decisões** | Regras fixas | IA Local (Ollama) |
| **Proteção** | Trailing Stop | Trailing Stop |
| **Custo** | Grátis | Grátis (IA local) |
| **Personalização** | Parâmetros | IA treinável |
| **Fallback** | N/A | Método tradicional |
| **Tempo de Resposta** | <1s | 5-10s (IA) |
| **Confiabilidade** | Alta | Alta + IA |

## Instalação e Configuração

### 1. Pré-requisitos
```bash
# Instalar Ollama (se não tiver)
winget install Ollama.Ollama

# Iniciar Ollama
ollama serve

# Verificar se está rodando
ollama list
```

### 2. Dependências Python
```bash
# Instalar requests (se necessário)
pip install requests
```

### 3. Execução
```bash
# Método 1: Usando batch file
RUN_GOLD_AI.bat

# Método 2: Linha de comando
uv run python src/agents/gold_ai_agent.py --symbol XAUUSDc --volume 0.02

# Método 3: Com opções customizadas
uv run python src/agents/gold_ai_agent.py \
    --symbol XAUUSDc \
    --volume 0.02 \
    --model-name llama3.2:1b \
    --ai-temperature 0.1
```

## Parâmetros de Configuração

### IA (Ollama)
- `--model-name`: Nome do modelo (padrão: llama3.2:1b)
- `--ai-host`: Host do Ollama (padrão: localhost)
- `--ai-port`: Porta do Ollama (padrão: 11434)
- `--ai-temperature`: Criatividade da IA (0-1, padrão: 0.1)
- `--ai-disabled`: Desabilitar IA e usar método tradicional

### Trading
- `--symbol`: Símbolo para trading (padrão: XAUUSDc)
- `--volume`: Volume em lotes (padrão: 0.02)

## Monitoramento e Logs

### Informações Exibidas
```
[AGENTE] GOLD AI AGENT | Ciclo #15 | 13:48:30
===============================================================
[AGENTE]:
   Estado: LOSS ZERO (Trailing ilimitado)
   Volume: 0.02
   Trailing Ativo: NAO
   🤖 IA: ONLINE
      Última decisão: BUY
      Decisões: BUY=3 | SELL=1 | HOLD=2
===============================================================
```

### Decisões da IA
```
🤖 DECISÃO DA IA:
   Ação: BUY
   Confiança: 0.80
   Raciocínio: IA recomenda compra
   Tempo de resposta: 5.23s
   Preço: $2,650.50
   Momentum 3m: -0.125%
   Volume: 1,250
📊 Estatísticas IA (6 decisões):
   BUY: 50.0% | SELL: 16.7% | HOLD: 33.3%
⏱️ Tempo médio de resposta: 5.67s
```

## Casos de Uso

### ✅ Use Gold AI Agent se:
- Quer IA para decisões de entrada
- Mantém trailing stop comprovado
- Prefere solução local (sem API)
- Quer monitorar performance da IA
- Precisa de fallback confiável

### ❌ Use Agente Tradicional se:
- Precisa de decisões ultra-rápidas (<1s)
- Não quer dependência de IA
- Tem problema com latência
- Prefere previsibilidade total

## Resolução de Problemas

### IA não responde
```bash
# Verificar se Ollama está rodando
ollama serve

# Verificar modelo disponível
ollama list

# Testar manualmente
ollama run llama3.2:1b "Analyze: XAUUSD price 2650, momentum -0.1%, volume high"
```

### Erro de conexão
```bash
# Usar versão sem IA
uv run python src/agents/gold_ai_agent.py --ai-disabled

# Ou usar agente tradicional
RUN_GOLD_ADAPTIVE.bat
```

### Performance lenta
- Aumente a temperatura da IA (0.2-0.3)
- Use modelo menor (se disponível)
- Reduza frequência de consulta da IA

## Desenvolvimento Futuro

### Melhorias Planejadas
- [ ] **Fine-tuning**: Treinar modelo com dados específicos
- [ ] **Ensemble**: Múltiplos modelos votando
- [ ] **Backtesting**: Simular decisões da IA
- [ ] **A/B Testing**: IA vs Tradicional
- [ ] **Sentiment**: Análise de sentimento de mercado

### Integrações
- [ ] **Telegram**: Notificações de decisões da IA
- [ ] **Dashboard**: Interface web para monitoramento
- [ ] **Database**: Histórico de decisões da IA
- [ ] **Alerts**: Sistema de alertas customizados

## Conclusão

O **Gold AI Agent** representa a evolução natural do sistema de trading, combinando:
- **Inteligência Artificial** para decisões mais inteligentes
- **Trailing Stop Comprovado** para proteção de capital
- **Sistema Híbrido** com fallback automático
- **IA Local** sem custos ou dependências externas

É a solução ideal para quem quer a **melhor tecnologia disponível** com **máxima confiabilidade** e **custo zero**.
