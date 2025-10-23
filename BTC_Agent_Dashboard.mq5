//+------------------------------------------------------------------+
//|                                         BTC_Agent_Dashboard.mq5 |
//|                         Dashboard Visual para Agente Python     |
//|                                    Mostra análises e posições   |
//+------------------------------------------------------------------+
#property copyright "BTC Hedge Agent"
#property link      ""
#property version   "1.00"
#property indicator_chart_window
#property indicator_plots 0

//--- Inputs
input string InpDataFile = "C:\\mcp-trader\\agent_data.json"; // Arquivo de dados do agente
input int    InpUpdateInterval = 5; // Intervalo de atualização (segundos)
input bool   InpShowPanel = true;   // Mostrar painel de informações
input bool   InpShowIndicators = true; // Mostrar indicadores no gráfico
input bool   InpShowSignals = true;    // Mostrar sinais de compra/venda
input color  InpPanelColor = clrDarkSlateGray; // Cor do painel
input int    InpPanelX = 10; // Posição X do painel
input int    InpPanelY = 30; // Posição Y do painel

//--- Variáveis globais
datetime ExtLastUpdate = 0;

//--- Estrutura de dados do agente
struct AgentData
{
   string agent_name;
   string state;
   string symbol;
   int daily_trades;
   int max_daily_trades;
   double total_profit;
   int winning_streak;
   bool hedge_active;
   int positions_count;

   // Indicadores
   double current_price;
   string trend;
   double rsi;
   double macd;
   double atr;
   double sma_20;
   double sma_50;
   double bb_upper;
   double bb_middle;
   double bb_lower;

   // Posições
   int position_tickets[20];
   string position_types[20];
   double position_volumes[20];
   double position_profits[20];
   double total_position_profit;
};

AgentData ExtAgentData;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("🤖 BTC Agent Dashboard inicializado");
   Print("📁 Lendo dados de: ", InpDataFile);

   EventSetTimer(InpUpdateInterval);

   // Primeira atualização
   UpdateDashboard();

   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   DeleteAllObjects();
   Print("Dashboard finalizado");
}

//+------------------------------------------------------------------+
//| Timer function                                                    |
//+------------------------------------------------------------------+
void OnTimer()
{
   UpdateDashboard();
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
{
   return(rates_total);
}

//+------------------------------------------------------------------+
//| Atualiza o dashboard                                             |
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   ExtLastUpdate = TimeCurrent();

   // Ler dados do arquivo JSON
   if(ReadAgentData())
   {
      // Desenhar painel
      if(InpShowPanel)
         DrawPanel();

      // Desenhar indicadores
      if(InpShowIndicators)
         DrawIndicators();

      // Desenhar sinais
      if(InpShowSignals)
         DrawSignals();

      ChartRedraw();
   }
}

//+------------------------------------------------------------------+
//| Lê dados do arquivo JSON do agente                               |
//+------------------------------------------------------------------+
bool ReadAgentData()
{
   int file_handle = FileOpen(InpDataFile, FILE_READ|FILE_TXT|FILE_ANSI);

   if(file_handle == INVALID_HANDLE)
   {
      Print("⚠️ Não foi possível abrir arquivo: ", InpDataFile);
      return false;
   }

   string json_content = "";
   while(!FileIsEnding(file_handle))
   {
      json_content += FileReadString(file_handle);
   }

   FileClose(file_handle);

   if(StringLen(json_content) < 10)
   {
      Print("⚠️ Arquivo JSON vazio");
      return false;
   }

   // Parse JSON
   ParseJSON(json_content);

   return true;
}

//+------------------------------------------------------------------+
//| Parse dados JSON simples                                         |
//+------------------------------------------------------------------+
void ParseJSON(string json)
{
   // Extrair campos principais
   ExtAgentData.agent_name = ExtractJSONString(json, "agent");
   ExtAgentData.state = ExtractJSONString(json, "state");
   ExtAgentData.symbol = ExtractJSONString(json, "symbol");
   ExtAgentData.daily_trades = (int)ExtractJSONDouble(json, "daily_trades");
   ExtAgentData.max_daily_trades = (int)ExtractJSONDouble(json, "max_daily_trades");
   ExtAgentData.total_profit = ExtractJSONDouble(json, "total_profit");
   ExtAgentData.winning_streak = (int)ExtractJSONDouble(json, "winning_streak");
   ExtAgentData.hedge_active = ExtractJSONBool(json, "hedge_active");
   ExtAgentData.positions_count = (int)ExtractJSONDouble(json, "positions_count");

   // Indicadores
   ExtAgentData.current_price = ExtractJSONDouble(json, "current_price");
   ExtAgentData.trend = ExtractJSONString(json, "trend");
   ExtAgentData.rsi = ExtractJSONDouble(json, "rsi");
   ExtAgentData.macd = ExtractJSONDouble(json, "macd");
   ExtAgentData.atr = ExtractJSONDouble(json, "atr");
   ExtAgentData.sma_20 = ExtractJSONDouble(json, "sma_20");
   ExtAgentData.sma_50 = ExtractJSONDouble(json, "sma_50");
   ExtAgentData.bb_upper = ExtractJSONDouble(json, "bb_upper");
   ExtAgentData.bb_middle = ExtractJSONDouble(json, "bb_middle");
   ExtAgentData.bb_lower = ExtractJSONDouble(json, "bb_lower");

   Print("✅ Dados atualizados: ", ExtAgentData.agent_name,
         " | Estado: ", ExtAgentData.state,
         " | Operações: ", ExtAgentData.daily_trades, "/", ExtAgentData.max_daily_trades,
         " | Lucro: $", DoubleToString(ExtAgentData.total_profit, 2));
}

//+------------------------------------------------------------------+
//| Extrai string do JSON                                            |
//+------------------------------------------------------------------+
string ExtractJSONString(string json, string key)
{
   string pattern = "\"" + key + "\":\"";
   int start = StringFind(json, pattern);
   if(start == -1) pattern = "\"" + key + "\": \"";
   start = StringFind(json, pattern);
   if(start == -1) return "";

   start += StringLen(pattern);
   int end = StringFind(json, "\"", start);
   if(end == -1) return "";

   return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| Extrai double do JSON                                            |
//+------------------------------------------------------------------+
double ExtractJSONDouble(string json, string key)
{
   string pattern = "\"" + key + "\":";
   int start = StringFind(json, pattern);
   if(start == -1) pattern = "\"" + key + "\": ";
   start = StringFind(json, pattern);
   if(start == -1) return 0.0;

   start += StringLen(pattern);
   int end = StringFind(json, ",", start);
   if(end == -1) end = StringFind(json, "}", start);
   if(end == -1) return 0.0;

   string value = StringSubstr(json, start, end - start);
   StringTrimLeft(value);
   StringTrimRight(value);

   return StringToDouble(value);
}

//+------------------------------------------------------------------+
//| Extrai bool do JSON                                              |
//+------------------------------------------------------------------+
bool ExtractJSONBool(string json, string key)
{
   string pattern = "\"" + key + "\":";
   int start = StringFind(json, pattern);
   if(start == -1) return false;

   start += StringLen(pattern);

   return (StringFind(json, "true", start) == start);
}

//+------------------------------------------------------------------+
//| Desenha painel de informações                                    |
//+------------------------------------------------------------------+
void DrawPanel()
{
   int x = InpPanelX;
   int y = InpPanelY;
   int line_height = 20;
   int panel_width = 350;

   // Background do painel
   CreateLabel("PANEL_BG", x, y, "", InpPanelColor, 14, "Consolas", panel_width, 400);

   // Título
   y += 10;
   CreateLabel("PANEL_TITLE", x + 10, y, "🤖 " + ExtAgentData.agent_name, clrWhite, 12, "Arial Bold");

   // Separador
   y += line_height + 5;
   CreateLine("PANEL_SEP1", x, y, x + panel_width, y, clrGray, 1);

   // Estado do Agente
   y += 15;
   color state_color = GetStateColor(ExtAgentData.state);
   CreateLabel("PANEL_STATE", x + 10, y, "Estado: " + ExtAgentData.state, state_color, 10, "Arial Bold");

   // Operações
   y += line_height;
   string trades_text = StringFormat("Operações: %d/%d", ExtAgentData.daily_trades, ExtAgentData.max_daily_trades);
   CreateLabel("PANEL_TRADES", x + 10, y, trades_text, clrWhite, 9, "Consolas");

   // Lucro Total
   y += line_height;
   color profit_color = ExtAgentData.total_profit >= 0 ? clrLime : clrRed;
   string profit_text = StringFormat("Lucro Total: $%+.2f", ExtAgentData.total_profit);
   CreateLabel("PANEL_PROFIT", x + 10, y, profit_text, profit_color, 10, "Arial Bold");

   // Winning Streak
   y += line_height;
   CreateLabel("PANEL_STREAK", x + 10, y, "Winning Streak: " + IntegerToString(ExtAgentData.winning_streak), clrYellow, 9, "Consolas");

   // Hedge
   y += line_height;
   string hedge_text = "Hedge: " + (ExtAgentData.hedge_active ? "✅ ATIVO" : "❌ Inativo");
   color hedge_color = ExtAgentData.hedge_active ? clrOrange : clrGray;
   CreateLabel("PANEL_HEDGE", x + 10, y, hedge_text, hedge_color, 9, "Arial Bold");

   // Separador Mercado
   y += line_height + 5;
   CreateLine("PANEL_SEP2", x, y, x + panel_width, y, clrGray, 1);

   // Mercado
   y += 15;
   CreateLabel("PANEL_MARKET_TITLE", x + 10, y, "📈 MERCADO - " + ExtAgentData.symbol, clrCyan, 10, "Arial Bold");

   // Preço
   y += line_height;
   CreateLabel("PANEL_PRICE", x + 10, y, StringFormat("Preço: $%,.2f", ExtAgentData.current_price), clrWhite, 9, "Consolas");

   // Tendência
   y += line_height;
   color trend_color = ExtAgentData.trend == "UP" ? clrLime : clrRed;
   CreateLabel("PANEL_TREND", x + 10, y, "Tendência: " + ExtAgentData.trend, trend_color, 9, "Arial Bold");

   // RSI
   y += line_height;
   color rsi_color = GetRSIColor(ExtAgentData.rsi);
   CreateLabel("PANEL_RSI", x + 10, y, StringFormat("RSI: %.1f", ExtAgentData.rsi), rsi_color, 9, "Consolas");

   // MACD
   y += line_height;
   color macd_color = ExtAgentData.macd > 0 ? clrLime : clrRed;
   CreateLabel("PANEL_MACD", x + 10, y, StringFormat("MACD: %+.2f", ExtAgentData.macd), macd_color, 9, "Consolas");

   // ATR
   y += line_height;
   CreateLabel("PANEL_ATR", x + 10, y, StringFormat("ATR: %.2f", ExtAgentData.atr), clrWhite, 9, "Consolas");

   // Separador Posições
   y += line_height + 5;
   CreateLine("PANEL_SEP3", x, y, x + panel_width, y, clrGray, 1);

   // Posições
   y += 15;
   CreateLabel("PANEL_POS_TITLE", x + 10, y, StringFormat("💼 POSIÇÕES ABERTAS: %d", ExtAgentData.positions_count), clrYellow, 10, "Arial Bold");

   // Última atualização
   y += panel_width - 50;
   string update_text = "Atualizado: " + TimeToString(ExtLastUpdate, TIME_SECONDS);
   CreateLabel("PANEL_UPDATE", x + 10, y, update_text, clrGray, 8, "Arial");
}

//+------------------------------------------------------------------+
//| Desenha indicadores no gráfico                                   |
//+------------------------------------------------------------------+
void DrawIndicators()
{
   datetime current_time = iTime(Symbol(), PERIOD_CURRENT, 0);

   // Bollinger Bands
   if(ExtAgentData.bb_upper > 0)
   {
      CreateHLine("IND_BB_UPPER", ExtAgentData.bb_upper, clrDodgerBlue, STYLE_DOT, 1);
      CreateHLine("IND_BB_MIDDLE", ExtAgentData.bb_middle, clrGray, STYLE_DOT, 1);
      CreateHLine("IND_BB_LOWER", ExtAgentData.bb_lower, clrDodgerBlue, STYLE_DOT, 1);
   }

   // SMAs
   if(ExtAgentData.sma_20 > 0)
   {
      CreateHLine("IND_SMA20", ExtAgentData.sma_20, clrYellow, STYLE_SOLID, 2);
      CreateHLine("IND_SMA50", ExtAgentData.sma_50, clrOrange, STYLE_SOLID, 2);
   }
}

//+------------------------------------------------------------------+
//| Desenha sinais de compra/venda                                   |
//+------------------------------------------------------------------+
void DrawSignals()
{
   // Baseado em RSI e MACD
   datetime signal_time = iTime(Symbol(), PERIOD_CURRENT, 0);
   double signal_price = ExtAgentData.current_price;

   // Sinal de COMPRA
   if(ExtAgentData.rsi < 45 && ExtAgentData.macd > 0)
   {
      CreateArrow("SIGNAL_BUY", signal_time, signal_price, 233, clrLime, 3);
      CreateText("SIGNAL_BUY_TEXT", signal_time, signal_price - 100, "BUY", clrLime, 10);
   }
   else
   {
      ObjectDelete(0, "SIGNAL_BUY");
      ObjectDelete(0, "SIGNAL_BUY_TEXT");
   }

   // Sinal de VENDA
   if(ExtAgentData.rsi > 55 && ExtAgentData.macd < 0)
   {
      CreateArrow("SIGNAL_SELL", signal_time, signal_price, 234, clrRed, 3);
      CreateText("SIGNAL_SELL_TEXT", signal_time, signal_price + 100, "SELL", clrRed, 10);
   }
   else
   {
      ObjectDelete(0, "SIGNAL_SELL");
      ObjectDelete(0, "SIGNAL_SELL_TEXT");
   }
}

//+------------------------------------------------------------------+
//| Funções auxiliares de criação de objetos                         |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, color clr, int size, string font, int width=0, int height=0)
{
   if(ObjectFind(0, name) < 0)
      ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);

   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
   ObjectSetString(0, name, OBJPROP_FONT, font);
   ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);

   if(width > 0)
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
   if(height > 0)
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
}

void CreateLine(string name, int x1, int y1, int x2, int y2, color clr, int width)
{
   if(ObjectFind(0, name) >= 0)
      ObjectDelete(0, name);

   ObjectCreate(0, name, OBJ_TREND, 0, 0, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, width);
}

void CreateHLine(string name, double price, color clr, int style, int width)
{
   if(ObjectFind(0, name) >= 0)
      ObjectDelete(0, name);

   ObjectCreate(0, name, OBJ_HLINE, 0, 0, price);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE, style);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, width);
}

void CreateArrow(string name, datetime time, double price, int code, color clr, int width)
{
   if(ObjectFind(0, name) >= 0)
      ObjectDelete(0, name);

   ObjectCreate(0, name, OBJ_ARROW, 0, time, price);
   ObjectSetInteger(0, name, OBJPROP_ARROWCODE, code);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, width);
}

void CreateText(string name, datetime time, double price, string text, color clr, int size)
{
   if(ObjectFind(0, name) >= 0)
      ObjectDelete(0, name);

   ObjectCreate(0, name, OBJ_TEXT, 0, time, price);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
}

void DeleteAllObjects()
{
   ObjectsDeleteAll(0, "PANEL_");
   ObjectsDeleteAll(0, "IND_");
   ObjectsDeleteAll(0, "SIGNAL_");
}

//+------------------------------------------------------------------+
//| Funções auxiliares de cores                                      |
//+------------------------------------------------------------------+
color GetStateColor(string state)
{
   if(state == "TRADING") return clrLime;
   if(state == "HEDGING") return clrOrange;
   if(state == "ANALYZING") return clrYellow;
   if(state == "PAUSED") return clrGray;
   return clrWhite;
}

color GetRSIColor(double rsi)
{
   if(rsi < 30) return clrLime;       // Sobrevendido - BUY
   if(rsi > 70) return clrRed;        // Sobrecomprado - SELL
   if(rsi < 45) return clrYellow;
   if(rsi > 55) return clrOrange;
   return clrWhite;
}
//+------------------------------------------------------------------+
