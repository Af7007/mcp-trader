# EA VISUALIZER - GUIA COMPLETO

## 🎯 OBJETIVO

Criar um Expert Advisor (EA) para MetaTrader 5 que visualize em tempo real todos os sinais e indicadores do agente de trading Python.

## 📋 FUNCIONALIDADES DO EA

### Visualização de Indicadores
- **RSI**: Linha vermelha mostrando overbought/oversold
- **MACD**: Linha azul e linha laranja (signal)
- **SMA20**: Linha amarela (trend rápido)
- **SMA50**: Linha roxa (trend lento)
- **Bollinger Bands**: Linhas cinzas pontilhadas

### Sinais de Trading
- **Seta Verde**: Sinal BUY detectado
- **Seta Vermelha**: Sinal SELL detectado
- **Hedge Zones**: Linhas amarelas (trigger) e verdes (TP)

### Informações em Tempo Real
- Status do agente na tela
- Valores dos indicadores
- Sinais ativos
- Zonas de hedge

## 🔧 IMPLEMENTAÇÃO PASSO A PASSO

### PASSO 1: Criar o EA no MetaEditor

1. **Abrir MetaEditor** (F4 no MetaTrader 5)
2. **Criar Novo EA**: File → New → Expert Advisor
3. **Nome**: `Agent_Visualizer`
4. **Template**: Selecionar "Expert Advisor (EA)"

### PASSO 2: Código Base do EA

```mql5
//+------------------------------------------------------------------+
//|                                             Agent_Visualizer.mq5 |
//|                            Copyright 2025, Trading System Agent |
//+------------------------------------------------------------------+
#property copyright "Trading System Agent"
#property version   "1.00"

//--- Input parameters
input int    RSI_Period = 14;           // RSI Period
input double RSI_Overbought = 70.0;     // RSI Overbought
input double RSI_Oversold = 30.0;       // RSI Oversold
input int    MACD_Fast = 12;            // MACD Fast EMA
input int    MACD_Slow = 26;            // MACD Slow EMA
input int    MACD_Signal = 9;           // MACD Signal
input int    SMA_Fast = 20;             // Fast SMA
input int    SMA_Slow = 50;             // Slow SMA
input bool   Show_Signals = true;       // Show Trading Signals
input bool   Show_Hedge_Zones = true;   // Show Hedge Zones

//--- Variables
datetime last_bar_time = 0;
double last_rsi = 0;
string current_signal = "NEUTRAL";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("Agent Visualizer initialized for ", Symbol());
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
{
    //--- Check for new bar
    if(iTime(Symbol(), Period(), 0) <= last_bar_time) return;
    last_bar_time = iTime(Symbol(), Period(), 0);
    
    //--- Calculate indicators
    double rsi = iRSI(Symbol(), Period(), RSI_Period, PRICE_CLOSE, 1);
    double macd_main = iMACD(Symbol(), Period(), MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE, MODE_MAIN, 1);
    double macd_signal = iMACD(Symbol(), Period(), MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE, MODE_SIGNAL, 1);
    double sma_fast = iMA(Symbol(), Period(), SMA_Fast, 0, MODE_SMA, PRICE_CLOSE, 1);
    double sma_slow = iMA(Symbol(), Period(), SMA_Slow, 0, MODE_SMA, PRICE_CLOSE, 1);
    double current_price = iClose(Symbol(), Period(), 1);
    
    //--- Generate signals
    string signal = GenerateSignal(rsi, macd_main, macd_signal, sma_fast, sma_slow, current_price);
    current_signal = signal;
    
    //--- Display status
    DisplayStatus(rsi, macd_main, macd_signal, current_price, signal);
    
    //--- Plot hedge zones
    if(Show_Hedge_Zones) PlotHedgeZones();
    
    //--- Update last values
    last_rsi = rsi;
}

//+------------------------------------------------------------------+
//| Generate Trading Signal                                          |
//+------------------------------------------------------------------+
string GenerateSignal(double rsi, double macd, double macd_signal, 
                     double sma_fast, double sma_slow, double price)
{
    int buy_signals = 0;
    int sell_signals = 0;
    
    //--- RSI signals
    if(rsi < RSI_Oversold) buy_signals += 2;
    else if(rsi > RSI_Overbought) sell_signals += 2;
    else if(rsi < 45) buy_signals += 1;
    else if(rsi > 55) sell_signals += 1;
    
    //--- MACD signals
    if(macd > macd_signal) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Trend signals
    if(sma_fast > sma_slow) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Price vs SMA
    if(price > sma_fast) buy_signals += 0.5;
    else sell_signals += 0.5;
    
    //--- Determine signal
    if(buy_signals >= 3)
    {
        if(Show_Signals) PlotSignal("BUY", price, clrLime);
        return "BUY";
    }
    else if(sell_signals >= 3)
    {
        if(Show_Signals) PlotSignal("SELL", price, clrRed);
        return "SELL";
    }
    else return "NEUTRAL";
}

//+------------------------------------------------------------------+
//| Plot Signal on Chart                                             |
//+------------------------------------------------------------------+
void PlotSignal(string signal_type, double price, color arrow_color)
{
    string obj_name = "Signal_" + TimeToString(TimeCurrent(), TIME_SECONDS);
    
    if(ObjectCreate(0, obj_name, OBJ_ARROW, 0, TimeCurrent(), price))
    {
        ObjectSetInteger(0, obj_name, OBJPROP_ARROWCODE, 233);
        ObjectSetInteger(0, obj_name, OBJPROP_COLOR, arrow_color);
        ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, 3);
    }
}

//+------------------------------------------------------------------+
//| Plot Hedge Zones                                                 |
//+------------------------------------------------------------------+
void PlotHedgeZones()
{
    double price = iClose(Symbol(), Period(), 0);
    
    //--- Hedge trigger line (-$4)
    string trigger_name = "Hedge_Trigger_" + Symbol();
    if(ObjectCreate(0, trigger_name, OBJ_HLINE, 0, 0, price - 4.0))
    {
        ObjectSetInteger(0, trigger_name, OBJPROP_COLOR, clrYellow);
        ObjectSetInteger(0, trigger_name, OBJPROP_STYLE, STYLE_DASH);
    }
    
    //--- Hedge TP line (+$4)
    string tp_name = "Hedge_TP_" + Symbol();
    if(ObjectCreate(0, tp_name, OBJ_HLINE, 0, 0, price + 4.0))
    {
        ObjectSetInteger(0, tp_name, OBJPROP_COLOR, clrGreen);
        ObjectSetInteger(0, tp_name, OBJPROP_STYLE, STYLE_DASH);
    }
}

//+------------------------------------------------------------------+
//| Display Agent Status                                             |
//+------------------------------------------------------------------+
void DisplayStatus(double rsi, double macd, double macd_signal, double price, string signal)
{
    string status = "=== AGENT VISUALIZER ===\n";
    status += "Symbol: " + Symbol() + "\n";
    status += "RSI: " + DoubleToString(rsi, 2) + "\n";
    status += "MACD: " + DoubleToString(macd, 4) + "\n";
    status += "Signal: " + signal + "\n";
    status += "Price: " + DoubleToString(price, 5) + "\n";
    
    Comment(status);
}
```

### PASSO 3: Compilar e Testar

1. **Compilar**: F7 ou botão Compile
2. **Testar**: F5 para iniciar Strategy Tester
3. **Visualizar**: Attach ao gráfico EURUSD M15

## 🎨 PERSONALIZAÇÃO

### Cores dos Indicadores
- **RSI**: Vermelho (`clrRed`)
- **MACD**: Azul (`clrBlue`)
- **MACD Signal**: Laranja (`clrOrange`)
- **SMA20**: Amarelo (`clrYellow`)
- **SMA50**: Roxo (`clrPurple`)
- **Bollinger**: Cinza (`clrGray`)

### Tipos de Plotagem
- **Linha**: `DRAW_LINE`
- **Seta**: `DRAW_ARROW`
- **Histograma**: `DRAW_HISTOGRAM`

### Sinais Visuais
- **BUY**: Seta verde para cima (`clrLime`)
- **SELL**: Seta vermelha para baixo (`clrRed`)
- **Hedge**: Linhas tracejadas (`STYLE_DASH`)

## 🔗 INTEGRAÇÃO COM AGENTE PYTHON

### 1. Ler Dados do JSON
```mql5
string ReadAgentData()
{
    string file_path = "C:/mcp-trader/agent_data.json";
    int file = FileOpen(file_path, FILE_READ|FILE_TXT);
    if(file != INVALID_HANDLE)
    {
        string data = FileReadString(file);
        FileClose(file);
        return data;
    }
    return "";
}
```

### 2. Parse JSON (Simplificado)
```mql5
void UpdateFromAgentData()
{
    string json_data = ReadAgentData();
    if(json_data != "")
    {
        // Parse JSON e atualizar visualizações
        // Exemplo: mostrar hedge status do agente
    }
}
```

## 📊 INDICADORES PERSONALIZADOS

### RSI Customizado
- **Período**: 14
- **Overbought**: 70
- **Oversold**: 30
- **Cor**: Vermelho

### MACD Customizado
- **Fast**: 12
- **Slow**: 26
- **Signal**: 9
- **Cor**: Azul/Laranja

### Bollinger Bands
- **Período**: 20
- **Desvio**: 2.0
- **Cor**: Cinza

## 🖥️ INSTALAÇÃO

### 1. MetaTrader 5
- Baixar do site oficial
- Instalar na pasta `C:\Program Files\MetaTrader 5\`

### 2. EA Files
- Salvar EA em: `C:\Users\[User]\AppData\Roaming\MetaQuotes\Terminal\[ID]\MQL5\Experts\`
- Compilar no MetaEditor
- Attach ao gráfico

### 3. Configuração
- Timeframe: M15 (recomendado)
- Símbolo: EURUSD, BTCUSD, XAUUSD
- Permitir trading automatizado: OFF

## 📈 MONITORAMENTO

### Dashboard em Tempo Real
- **Top-Left**: RSI value
- **Top-Center**: Current signal (BUY/SELL/NEUTRAL)
- **Top-Right**: Price
- **Chart**: Visual signals + hedge zones

### Alertas
- BUY signal detected
- SELL signal detected
- Hedge zone reached
- Signal strength indicator

## 🎯 VANTAGENS

### Para Trading
- Visualização clara dos sinais
- Confirmação visual das decisões
- Hedge zones sempre visíveis
- Multiple timeframe analysis

### Para Análise
- Backtest visual
- Pattern recognition
- Signal validation
- Performance tracking

## 🔧 TROUBLESHOOTING

### EA não aparece
- Verificar se foi compilado sem erros
- Confirmar instalação no diretório correto
- Reiniciar MetaTrader 5

### Indicadores não funcionam
- Verificar se Symbol() está correto
- Confirmar timeframe adequado
- Testar com dados históricos

### Sinais não aparecem
- Verificar lógica de geração
- Confirmar thresholds (3+ sinais)
- Testar em diferentes timeframes

## 📚 RECURSOS ADICIONAIS

### Links Úteis
- [MQL5 Documentation](https://docs.mql5.com/)
- [MetaTrader 5 Guide](https://www.metatrader5.com/en/help)
- [MQL5 Community](https://www.mql5.com/)

### Exemplos de EA
- Base code no arquivo `EAtrader.mq5` existente
- Modifications para cada agente (BTC, GOLD, EUR, etc.)

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Instalar MetaTrader 5
- [ ] Criar EA no MetaEditor
- [ ] Implementar código base
- [ ] Compilar EA sem erros
- [ ] Attach ao gráfico M15
- [ ] Testar visualização de indicadores
- [ ] Verificar sinais BUY/SELL
- [ ] Configurar hedge zones
- [ ] Integrar com dados do agente Python
- [ ] Otimizar performance

**O EA estará pronto para visualizar todos os sinais e decisões do agente em tempo real!**
