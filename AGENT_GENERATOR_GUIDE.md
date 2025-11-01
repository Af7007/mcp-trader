# 🤖 Agent Generator - Guia de Uso

## 📋 O que é?

O **Agent Generator** cria agentes de trading a partir de **linguagem natural**. Você descreve o que quer em português/inglês e o sistema cria um agente configurado automaticamente!

---

## 🎯 Exemplos de Comandos

### Exemplo 1: RSI Simples
```
"Crie agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
```

**Resultado:**
- ✅ Símbolo: XAUUSDm
- ✅ Indicador: RSI
- ✅ Take Profit: $3.00
- ✅ Stop Loss: $1.00
- ✅ Volume: 0.1 lots

### Exemplo 2: Bollinger Bands
```
"Agente EURUSD com Bollinger Bands período 20, volume 0.05, TP 50, SL 20"
```

**Resultado:**
- ✅ Símbolo: EURUSDc
- ✅ Indicador: Bollinger Bands (período 20)
- ✅ Take Profit: 50
- ✅ Stop Loss: 20
- ✅ Volume: 0.05 lots

### Exemplo 3: Múltiplos Indicadores
```
"Criar agente GBPUSD com RSI e MA 50, compre quando RSI < 30 e preço > MA, volume 0.1"
```

**Resultado:**
- ✅ Símbolo: GBPUSDc
- ✅ Indicadores: RSI + Moving Average (período 50)
- ✅ Condições: RSI < 30 AND Preço > MA
- ✅ Volume: 0.1 lots

---

## 📊 Símbolos Suportados

| Símbolo | Descrição |
|---------|-----------|
| EURUSD | Euro/Dólar |
| GBPUSD | Libra/Dólar |
| USDJPY | Dólar/Iene |
| USDCAD | Dólar/Dólar Canadense |
| AUDUSD | Dólar Australiano/Dólar |
| NZDUSD | Dólar Neozelandês/Dólar |
| XAUUSD | Ouro/Dólar |
| XAGUSD | Prata/Dólar |
| BTCUSD | Bitcoin/Dólar |
| ETHUSD | Ethereum/Dólar |

**Nota:** Todos os símbolos são automaticamente convertidos para versão cents (com "c" no final)

---

## 📈 Indicadores Suportados

| Indicador | Descrição | Parâmetro |
|-----------|-----------|-----------|
| RSI | Relative Strength Index | período (default: 14) |
| BOLLINGER | Bollinger Bands | período (default: 20) |
| MA | Moving Average | período (default: 50) |
| EMA | Exponential Moving Average | período (default: 12) |
| MACD | MACD | - |
| ATR | Average True Range | período (default: 14) |
| STOCHASTIC | Stochastic | período (default: 14) |

---

## 💰 Parâmetros Extraídos

### Take Profit (TP)
```
"TP $3"        → $3.00
"TP 50"        → 50 pips
"TP 100"       → 100 pips
```

### Stop Loss (SL)
```
"SL $1"        → $1.00
"SL 20"        → 20 pips
"SL 50"        → 50 pips
```

### Volume
```
"volume 0.1"   → 0.1 lots
"0.05"         → 0.05 lots
"1.0"          → 1.0 lots
```

### Timeframe
```
"M5"           → 5 minutos
"M15"          → 15 minutos
"M30"          → 30 minutos
"H1"           → 1 hora (60 minutos)
"H4"           → 4 horas
"D1"           → 1 dia
```

---

## 🚀 Como Usar

### Opção 1: Usar Diretamente em Python

```python
from src.agents.generator import AgentGenerator

# Criar gerador
generator = AgentGenerator()

# Criar agente
agent = generator.create_agent(
    "Crie agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
)

# Acessar informações
print(f"ID: {agent.id}")
print(f"Nome: {agent.name}")
print(f"Símbolo: {agent.symbol}")
print(f"Volume: {agent.volume}")
print(f"TP: ${agent.take_profit}")
print(f"SL: ${agent.stop_loss}")
print(f"Indicadores: {[ind.type.value for ind in agent.indicators]}")

# Listar todos os agentes
for agent in generator.list_agents():
    print(f"  • {agent.name}")

# Deletar agente
generator.delete_agent(agent.id)

# Exportar configuração
config = generator.export_agent(agent.id)
```

### Opção 2: Usar via Chatbot

```
💬 Você: criar agente EURUSD com RSI, TP $2, SL $0.5, volume 0.1
🤖 Bot: Agente criado com sucesso!
```

---

## 📊 Estrutura do Agente

```python
@dataclass
class AgentConfig:
    id: str                          # ID único (ex: "5091b3c6")
    name: str                        # Nome (ex: "XAUUSDm_RSI_20251022_172910")
    symbol: str                      # Símbolo (ex: "XAUUSDm")
    order_type: OrderType            # BUY, SELL, ou BUY_SELL
    volume: float                    # Volume em lots (ex: 0.1)
    indicators: List[Indicator]      # Lista de indicadores
    take_profit: Optional[float]     # TP em dólares
    stop_loss: Optional[float]       # SL em dólares
    trailing_stop: Optional[float]   # Trailing stop
    max_positions: int               # Máximo de posições abertas
    timeframe: int                   # Timeframe em minutos
    status: str                      # "active", "paused", "stopped"
    created_at: datetime             # Data de criação
```

---

## 🎯 Exemplos Avançados

### Exemplo 1: Agente com Múltiplos Indicadores
```
"Criar agente EURUSD com RSI período 14, Bollinger Bands período 20, 
compre quando RSI < 30 E preço < Bollinger Lower, 
venda quando RSI > 70 E preço > Bollinger Upper,
volume 0.1, TP $50, SL $20, timeframe H1"
```

### Exemplo 2: Agente com Trailing Stop
```
"Agente GBPUSD com MA 50 e EMA 12, 
volume 0.05, TP $100, SL $30, trailing stop 20 pips"
```

### Exemplo 3: Agente com Múltiplas Posições
```
"Criar agente XAUUSD com RSI e MACD, 
máximo 3 posições abertas, volume 0.1, TP $5, SL $2"
```

---

## 🔍 Padrões Reconhecidos

O Agent Generator reconhece automaticamente:

- **Símbolos:** EURUSD, GBPUSD, XAUUSD, etc
- **Indicadores:** RSI, Bollinger, MA, EMA, MACD, ATR, Stochastic
- **Parâmetros:** período, threshold, TP, SL, volume, timeframe
- **Operações:** comprar, vender, buy, sell
- **Valores:** $3, 50 pips, 0.1 lots, H1, M15, etc

---

## 📝 Notas Importantes

1. **Símbolos:** Sempre use nomes conhecidos (EURUSD, GBPUSD, XAUUSD, etc)
2. **Volume:** Mínimo 0.01 lots, máximo 10 lots
3. **TP/SL:** Em dólares (ex: $3) ou pips (ex: 50)
4. **Timeframe:** Default é H1 (60 minutos)
5. **Indicadores:** Default é RSI se nenhum for especificado

---

## 🚀 Próximos Passos

1. **Strategy Engine** - Interpretar sinais dos indicadores
2. **Agent Manager** - Gerenciar múltiplos agentes
3. **Worker** - Executar trades automaticamente
4. **Notifications** - Notificar sobre eventos

---

**Pronto para criar seus agentes!** 🎉
