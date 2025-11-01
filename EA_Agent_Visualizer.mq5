//+------------------------------------------------------------------+
//|                                    EA_Agent_Visualizer_Simple.mq5 |
//|                            Expert Advisor para Visualizar Sinais |
//|                        https://github.com/Af7007/mcp-trader       |
//+------------------------------------------------------------------+
#property copyright "Trading System Agent"
#property link      "https://github.com/Af7007/mcp-trader"
#property version   "1.00"
#property strict

//--- Input parameters
input int    RSI_Period = 14;           // Período RSI
input double RSI_Overbought = 70.0;     // RSI Sobrecomprado
input double RSI_Oversold = 30.0;       // RSI Sobrevendido

input int    MACD_Fast = 12;            // MACD EMA Rápida
input int    MACD_Slow = 26;            // MACD EMA Lenta
input int    MACD_Signal = 9;           // MACD Signal

input int    SMA_Fast = 20;             // SMA Rápida
input int    SMA_Slow = 50;             // SMA Lenta

input double Hedge_Trigger = 4.0;       // Trigger do Hedge ($)
input double Hedge_TP = 4.0;           // TP do Hedge ($)

input bool   Show_Signals = true;      // Mostrar Sinais
input bool   Show_Hedge_Zones = true;   // Mostrar Zonas de Hedge

//--- Variables
datetime last_bar_time = 0;
double last_rsi = 0;
double last_macd = 0;
double last_macd_signal = 0;
string signal_text = "";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    //--- Set trade parameters
    MqlTradeRequest request;
    MqlTradeResult result;
    
    //--- Set position size
    double lot_size = 0.01;
    
    //--- Set stop loss and take profit
    double sl_points = 0;
    double tp_points = 0;
    
    Print("Expert Advisor Agent Visualizer inicializado para ", Symbol());
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    //---
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
    double rsi = CalculateRSI(RSI_Period);
    double macd = CalculateMACD(MACD_Fast, MACD_Slow);
    double macd_signal = CalculateMACDSignal(MACD_Fast, MACD_Slow, MACD_Signal);
    double sma_fast = iMA(Symbol(), Period(), SMA_Fast, 0, MODE_SMA, PRICE_CLOSE, 1);
    double sma_slow = iMA(Symbol(), Period(), SMA_Slow, 0, MODE_SMA, PRICE_CLOSE, 1);
    
    double current_price = iClose(Symbol(), Period(), 1);
    
    //--- Generate signals based on agent logic
    string signal = GenerateSignal(rsi, macd, macd_signal, sma_fast, sma_slow, current_price);
    
    //--- Display information
    if(Show_Signals)
    {
        string info = StringFormat(
            "EUR Agent Status - RSI: %.2f | MACD: %.2f | Price: %.5f | Signal: %s",
            rsi, macd, current_price, signal
        );
        Comment(info);
    }
    
    //--- Plot hedge zones if enabled
    if(Show_Hedge_Zones)
    {
        PlotHedgeZones();
    }
    
    //--- Update previous values
    last_rsi = rsi;
    last_macd = macd;
    last_macd_signal = macd_signal;
}

//+------------------------------------------------------------------+
//| Calculate RSI                                                    |
//+------------------------------------------------------------------+
double CalculateRSI(int period)
{
    double rsi = iRSI(Symbol(), Period(), period, PRICE_CLOSE, 1);
    return rsi;
}

//+------------------------------------------------------------------+
//| Calculate MACD                                                   |
//+------------------------------------------------------------------+
double CalculateMACD(int fast, int slow)
{
    double macd_main = iMACD(Symbol(), Period(), fast, slow, MACD_Signal, PRICE_CLOSE, MODE_MAIN, 1);
    double macd_signal = iMACD(Symbol(), Period(), fast, slow, MACD_Signal, PRICE_CLOSE, MODE_SIGNAL, 1);
    
    last_macd = macd_main;
    last_macd_signal = macd_signal;
    
    return macd_main;
}

//+------------------------------------------------------------------+
//| Calculate MACD Signal                                            |
//+------------------------------------------------------------------+
double CalculateMACDSignal(int fast, int slow, int signal)
{
    return last_macd_signal;
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
    if(rsi < 30) buy_signals += 2;
    else if(rsi > 70) sell_signals += 2;
    else if(rsi < 45) buy_signals += 1;
    else if(rsi > 55) sell_signals += 1;
    
    //--- MACD signals
    if(macd > macd_signal) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Trend signals (SMA)
    if(sma_fast > sma_slow) buy_signals += 1;
    else sell_signals += 1;
    
    //--- Price vs SMA signals
    if(price > sma_fast) buy_signals += 0.5;
    else sell_signals += 0.5;
    
    //--- Determine final signal
    if(buy_signals >= 3)
    {
        signal_text = "BUY";
        if(Show_Signals) PlotSignal("BUY", price, clrLime);
        return "BUY";
    }
    else if(sell_signals >= 3)
    {
        signal_text = "SELL";
        if(Show_Signals) PlotSignal("SELL", price, clrRed);
        return "SELL";
    }
    else
    {
        signal_text = "NEUTRAL";
        return "NEUTRAL";
    }
}

//+------------------------------------------------------------------+
//| Plot Signal on Chart                                             |
//+------------------------------------------------------------------+
void PlotSignal(string signal_type, double price, color arrow_color)
{
    string object_name = "Signal_" + TimeToString(TimeCurrent(), TIME_SECONDS);
    
    if(ObjectCreate(0, object_name, OBJ_ARROW, 0, TimeCurrent(), price))
    {
        ObjectSetInteger(0, object_name, OBJPROP_ARROWCODE, 233); // Down arrow for SELL, up for BUY
        ObjectSetInteger(0, object_name, OBJPROP_COLOR, arrow_color);
        ObjectSetInteger(0, object_name, OBJPROP_WIDTH, 3);
        ObjectSetInteger(0, object_name, OBJPROP_BACK, false);
    }
}

//+------------------------------------------------------------------+
//| Plot Hedge Zones                                                 |
//+------------------------------------------------------------------+
void PlotHedgeZones()
{
    double current_price = iClose(Symbol(), Period(), 0);
    
    //--- Plot hedge trigger line
    string hedge_trigger_name = "Hedge_Trigger_" + Symbol();
    if(ObjectCreate(0, hedge_trigger_name, OBJ_HLINE, 0, 0, current_price - Hedge_Trigger))
    {
        ObjectSetInteger(0, hedge_trigger_name, OBJPROP_COLOR, clrYellow);
        ObjectSetInteger(0, hedge_trigger_name, OBJPROP_STYLE, STYLE_DASH);
        ObjectSetInteger(0, hedge_trigger_name, OBJPROP_WIDTH, 2);
    }
    
    //--- Plot hedge TP line
    string hedge_tp_name = "Hedge_TP_" + Symbol();
    if(ObjectCreate(0, hedge_tp_name, OBJ_HLINE, 0, 0, current_price + Hedge_TP))
    {
        ObjectSetInteger(0, hedge_tp_name, OBJPROP_COLOR, clrGreen);
        ObjectSetInteger(0, hedge_tp_name, OBJPROP_STYLE, STYLE_DASH);
        ObjectSetInteger(0, hedge_tp_name, OBJPROP_WIDTH, 2);
    }
    
    //--- Add text labels
    string label_trigger = "Label_Hedge_Trigger_" + Symbol();
    if(ObjectCreate(0, label_trigger, OBJ_TEXT, 0, TimeCurrent(), current_price - Hedge_Trigger))
    {
        ObjectSetString(0, label_trigger, OBJPROP_TEXT, "HEDGE TRIGGER: -$" + DoubleToString(Hedge_Trigger, 1));
        ObjectSetInteger(0, label_trigger, OBJPROP_COLOR, clrYellow);
        ObjectSetInteger(0, label_trigger, OBJPROP_FONTSIZE, 10);
    }
    
    string label_tp = "Label_Hedge_TP_" + Symbol();
    if(ObjectCreate(0, label_tp, OBJ_TEXT, 0, TimeCurrent(), current_price + Hedge_TP))
    {
        ObjectSetString(0, label_tp, OBJPROP_TEXT, "HEDGE TP: +$" + DoubleToString(Hedge_TP, 1));
        ObjectSetInteger(0, label_tp, OBJPROP_COLOR, clrGreen);
        ObjectSetInteger(0, label_tp, OBJPROP_FONTSIZE, 10);
    }
}

//+------------------------------------------------------------------+
//| Display Agent Status                                             |
//+------------------------------------------------------------------+
void DisplayAgentStatus()
{
    string status = "=== AGENT VISUALIZER STATUS ===\n";
    status += "Symbol: " + Symbol() + "\n";
    status += "RSI: " + DoubleToString(last_rsi, 2) + "\n";
    status += "MACD: " + DoubleToString(last_macd, 4) + "\n";
    status += "Signal: " + signal_text + "\n";
    status += "Hedge Trigger: -$" + DoubleToString(Hedge_Trigger, 1) + "\n";
    status += "Hedge TP: +$" + DoubleToString(Hedge_TP, 1) + "\n";
    
    Comment(status);
}

//+------------------------------------------------------------------+
//| Clean up old objects                                             |
//+------------------------------------------------------------------+
void CleanupObjects()
{
    //--- Remove old signal objects (keep only last 50)
    int total_objects = ObjectsTotal(0);
    for(int i = total_objects - 1; i >= 0; i--)
    {
        string obj_name = ObjectName(0, i);
        if(StringFind(obj_name, "Signal_") >= 0)
        {
            ObjectDelete(0, obj_name);
        }
    }
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
    //--- Display agent status every 10 seconds
    DisplayAgentStatus();
    
    //--- Clean up old objects periodically
    static datetime last_cleanup = 0;
    if(TimeCurrent() - last_cleanup > 3600) // Every hour
    {
        CleanupObjects();
        last_cleanup = TimeCurrent();
    }
}
