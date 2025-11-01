//+------------------------------------------------------------------+
//|                                     EA_Agent_Visualizer_Fixed.mq5 |
//|                            Copyright 2025, Trading System Agent |
//+------------------------------------------------------------------+
#property copyright "Trading System Agent"
#property link      "https://github.com/Af7007/mcp-trader"
#property version   "1.00"

//--- Input parameters
input int    RSI_Period = 14;           // RSI Period
input int    MACD_Fast = 12;            // MACD Fast EMA
input int    MACD_Slow = 26;            // MACD Slow EMA
input int    MACD_Signal = 9;           // MACD Signal
input int    SMA_Fast = 20;             // Fast SMA
input int    SMA_Slow = 50;             // Slow SMA
input bool   Show_Signals = true;       // Show Trading Signals
input bool   Show_Hedge_Zones = true;   // Show Hedge Zones

//--- Variables
datetime last_bar_time = 0;
string current_signal = "NEUTRAL";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("Agent Visualizer EA initialized for ", Symbol());
    
    //--- Enable timer for periodic updates
    EventSetTimer(5); // Update every 5 seconds
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
{
    //--- Check for new bar
    datetime current_time = iTime(Symbol(), Period(), 0);
    if(current_time <= last_bar_time) return;
    last_bar_time = current_time;
    
    //--- Calculate indicators and generate signals
    AnalyzeMarket();
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
    //--- Update display on timer
    UpdateDisplay();
}

//+------------------------------------------------------------------+
//| Analyze Market and Generate Signals                              |
//+------------------------------------------------------------------+
void AnalyzeMarket()
{
    //--- Get current values
    double rsi = GetRSI();
    double macd_main = GetMACDMain();
    double macd_signal = GetMACDSignal();
    double sma_fast = GetSMA(SMA_Fast);
    double sma_slow = GetSMA(SMA_Slow);
    double current_price = iClose(Symbol(), Period(), 0);
    
    //--- Generate trading signal
    string signal = GenerateTradingSignal(rsi, macd_main, macd_signal, sma_fast, sma_slow, current_price);
    current_signal = signal;
    
    //--- Plot signal if conditions are met
    if(Show_Signals && (signal == "BUY" || signal == "SELL"))
    {
        PlotSignal(signal, current_price, signal == "BUY" ? clrLime : clrRed);
    }
    
    //--- Plot hedge zones
    if(Show_Hedge_Zones)
    {
        PlotHedgeZones();
    }
}

//+------------------------------------------------------------------+
//| Get RSI Value                                                   |
//+------------------------------------------------------------------+
double GetRSI()
{
    double rsi_buffer[];
    ArraySetAsSeries(rsi_buffer, true);
    
    if(CopyBuffer(iRSI(Symbol(), Period(), RSI_Period, PRICE_CLOSE), 0, 0, 2, rsi_buffer) <= 0)
        return 50.0; // Default value if error
    
    return rsi_buffer[0];
}

//+------------------------------------------------------------------+
//| Get MACD Main Line                                              |
//+------------------------------------------------------------------+
double GetMACDMain()
{
    double macd_buffer[];
    ArraySetAsSeries(macd_buffer, true);
    
    if(CopyBuffer(iMACD(Symbol(), Period(), MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE, MODE_MAIN), 0, 0, 2, macd_buffer) <= 0)
        return 0.0;
    
    return macd_buffer[0];
}

//+------------------------------------------------------------------+
//| Get MACD Signal Line                                            |
//+------------------------------------------------------------------+
double GetMACDSignal()
{
    double signal_buffer[];
    ArraySetAsSeries(signal_buffer, true);
    
    if(CopyBuffer(iMACD(Symbol(), Period(), MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE, MODE_SIGNAL), 0, 0, 2, signal_buffer) <= 0)
        return 0.0;
    
    return signal_buffer[0];
}

//+------------------------------------------------------------------+
//| Get SMA Value                                                   |
//+------------------------------------------------------------------+
double GetSMA(int period)
{
    double sma_buffer[];
    ArraySetAsSeries(sma_buffer, true);
    
    if(CopyBuffer(iMA(Symbol(), Period(), period, 0, MODE_SMA, PRICE_CLOSE), 0, 0, 2, sma_buffer) <= 0)
        return 0.0;
    
    return sma_buffer[0];
}

//+------------------------------------------------------------------+
//| Generate Trading Signal                                         |
//+------------------------------------------------------------------+
string GenerateTradingSignal(double rsi, double macd_main, double macd_signal, 
                           double sma_fast, double sma_slow, double price)
{
    int buy_signals = 0;
    int sell_signals = 0;
    
    //--- RSI signals
    if(rsi < 30) buy_signals += 2;
    else if(rsi > 70) sell_signals += 2;
    else if(rsi < 45) buy_signals += 1;
    else if(rsi > 55) sell_signals += 1;
    
    //--- MACD signals
    if(macd_main > macd_signal) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Trend signals
    if(sma_fast > sma_slow) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Price vs SMA
    if(price > sma_fast) buy_signals += 0.5;
    else sell_signals += 0.5;
    
    //--- Determine signal
    if(buy_signals >= 3) return "BUY";
    else if(sell_signals >= 3) return "SELL";
    else return "NEUTRAL";
}

//+------------------------------------------------------------------+
//| Plot Signal on Chart                                            |
//+------------------------------------------------------------------+
void PlotSignal(string signal_type, double price, color arrow_color)
{
    string object_name = "Signal_" + TimeToString(TimeCurrent(), TIME_SECONDS);
    
    if(ObjectCreate(0, object_name, OBJ_ARROW, 0, TimeCurrent(), price))
    {
        // Use different arrow codes for BUY/SELL
        int arrow_code = (signal_type == "BUY") ? 233 : 234; // Up/Down arrows
        ObjectSetInteger(0, object_name, OBJPROP_ARROWCODE, arrow_code);
        ObjectSetInteger(0, object_name, OBJPROP_COLOR, arrow_color);
        ObjectSetInteger(0, object_name, OBJPROP_WIDTH, 3);
        ObjectSetInteger(0, object_name, OBJPROP_BACK, false);
    }
}

//+------------------------------------------------------------------+
//| Plot Hedge Zones                                                |
//+------------------------------------------------------------------+
void PlotHedgeZones()
{
    double price = iClose(Symbol(), Period(), 0);
    
    //--- Hedge trigger line (-$4)
    string trigger_name = "Hedge_Trigger";
    if(ObjectFind(0, trigger_name) < 0)
    {
        if(ObjectCreate(0, trigger_name, OBJ_HLINE, 0, 0, price - 4.0))
        {
            ObjectSetInteger(0, trigger_name, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, trigger_name, OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, trigger_name, OBJPROP_WIDTH, 2);
        }
    }
    else
    {
        ObjectMove(0, trigger_name, 0, price - 4.0);
    }
    
    //--- Hedge TP line (+$4)
    string tp_name = "Hedge_TP";
    if(ObjectFind(0, tp_name) < 0)
    {
        if(ObjectCreate(0, tp_name, OBJ_HLINE, 0, 0, price + 4.0))
        {
            ObjectSetInteger(0, tp_name, OBJPROP_COLOR, clrGreen);
            ObjectSetInteger(0, tp_name, OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, tp_name, OBJPROP_WIDTH, 2);
        }
    }
    else
    {
        ObjectMove(0, tp_name, 0, price + 4.0);
    }
    
    //--- Add labels
    PlotLabels();
}

//+------------------------------------------------------------------+
//| Plot Labels                                                     |
//+------------------------------------------------------------------+
void PlotLabels()
{
    double price = iClose(Symbol(), Period(), 0);
    
    //--- Trigger label
    string trigger_label = "Trigger_Label";
    if(ObjectFind(0, trigger_label) < 0)
    {
        if(ObjectCreate(0, trigger_label, OBJ_TEXT, 0, TimeCurrent(), price - 4.0))
        {
            ObjectSetString(0, trigger_label, OBJPROP_TEXT, "HEDGE TRIGGER: -$4.0");
            ObjectSetInteger(0, trigger_label, OBJPROP_COLOR, clrYellow);
            ObjectSetInteger(0, trigger_label, OBJPROP_FONTSIZE, 8);
        }
    }
    else
    {
        ObjectMove(0, trigger_label, 0, TimeCurrent(), price - 4.0);
    }
    
    //--- TP label
    string tp_label = "TP_Label";
    if(ObjectFind(0, tp_label) < 0)
    {
        if(ObjectCreate(0, tp_label, OBJ_TEXT, 0, TimeCurrent(), price + 4.0))
        {
            ObjectSetString(0, tp_label, OBJPROP_TEXT, "HEDGE TP: +$4.0");
            ObjectSetInteger(0, tp_label, OBJPROP_COLOR, clrGreen);
            ObjectSetInteger(0, tp_label, OBJPROP_FONTSIZE, 8);
        }
    }
    else
    {
        ObjectMove(0, tp_label, 0, TimeCurrent(), price + 4.0);
    }
}

//+------------------------------------------------------------------+
//| Update Display                                                  |
//+------------------------------------------------------------------+
void UpdateDisplay()
{
    double rsi = GetRSI();
    double macd_main = GetMACDMain();
    double price = iClose(Symbol(), Period(), 0);
    
    string display = "=== AGENT VISUALIZER ===\n";
    display += "Symbol: " + Symbol() + "\n";
    display += "RSI: " + DoubleToString(rsi, 2) + "\n";
    display += "MACD: " + DoubleToString(macd_main, 4) + "\n";
    display += "Signal: " + current_signal + "\n";
    display += "Price: " + DoubleToString(price, 5) + "\n";
    display += "Time: " + TimeToString(TimeCurrent(), TIME_MINUTES) + "\n";
    
    Comment(display);
}

//+------------------------------------------------------------------+
//| Clean up old signals                                            |
//+------------------------------------------------------------------+
void CleanupOldSignals()
{
    int total_objects = ObjectsTotal(0);
    
    for(int i = total_objects - 1; i >= 0; i--)
    {
        string obj_name = ObjectName(0, i);
        if(StringFind(obj_name, "Signal_") >= 0)
        {
            datetime obj_time = (datetime)ObjectGetInteger(0, obj_name, OBJPROP_TIME);
            if(TimeCurrent() - obj_time > 3600) // Remove signals older than 1 hour
            {
                ObjectDelete(0, obj_name);
            }
        }
    }
}
