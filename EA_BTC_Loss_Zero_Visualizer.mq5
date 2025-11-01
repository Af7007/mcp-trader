//+------------------------------------------------------------------+
//|                                EA_BTC_Loss_Zero_Visualizer.mq5    |
//|                           Visualizador para BTC Loss Zero Agent   |
//|                        https://github.com/Af7007/mcp-trader       |
//+------------------------------------------------------------------+
#property copyright "Trading System Agent - BTC Loss Zero"
#property link      "https://github.com/Af7007/mcp-trader"
#property version   "1.00"
#property strict
#property indicator_chart_window

//--- Input parameters
input string DataFilePath = "C:\\mcp-trader\\btc_loss_zero_data.json";  // Caminho do arquivo JSON
input int    UpdateIntervalSeconds = 5;  // Intervalo de atualização (segundos)
input bool   ShowEntryLine = true;       // Mostrar linha de entrada
input bool   ShowSLLine = true;          // Mostrar linha de SL
input bool   ShowTPLine = true;          // Mostrar linha de TP
input bool   ShowTrailingLine = true;    // Mostrar linha de trailing stop
input bool   ShowInfoPanel = true;       // Mostrar painel de informações

//--- Colors
input color  EntryLineColor = clrDodgerBlue;      // Cor da linha de entrada
input color  SLLineColor = clrRed;                // Cor da linha de SL
input color  TPLineColor = clrLime;               // Cor da linha de TP
input color  TrailingLineColor = clrYellow;       // Cor da linha de trailing

//--- Global variables
datetime last_update_time = 0;
int file_handle = INVALID_HANDLE;

// Data structure
struct AgentData
{
    string timestamp;
    string symbol;
    double current_price;
    bool has_position;
    bool trailing_active;
    double trailing_amount_dollars;
    double entry_price;
    long entry_ticket;
    string position_type;
    double sl;
    double tp;
    double profit;
    double trailing_stop_level;
};

AgentData agent_data;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("BTC Loss Zero Visualizer iniciado para ", Symbol());
    Print("Arquivo de dados: ", DataFilePath);

    // Criar timer para atualização
    EventSetTimer(UpdateIntervalSeconds);

    // Primeira leitura
    ReadAgentData();
    UpdateChartLines();

    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Remover timer
    EventKillTimer();

    // Limpar objetos do gráfico
    DeleteAllObjects();

    Print("BTC Loss Zero Visualizer finalizado");
}

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
{
    // Ler dados do arquivo JSON
    if(ReadAgentData())
    {
        // Atualizar linhas no gráfico
        UpdateChartLines();

        // Atualizar painel de informações
        if(ShowInfoPanel)
            UpdateInfoPanel();
    }
}

//+------------------------------------------------------------------+
//| Read agent data from JSON file                                   |
//+------------------------------------------------------------------+
bool ReadAgentData()
{
    // Abrir arquivo JSON
    int handle = FileOpen(DataFilePath, FILE_READ|FILE_TXT|FILE_ANSI);

    if(handle == INVALID_HANDLE)
    {
        if(TimeCurrent() - last_update_time > 60)  // Log apenas a cada 60s
        {
            Print("Erro ao abrir arquivo: ", DataFilePath, " - Error: ", GetLastError());
            last_update_time = TimeCurrent();
        }
        return false;
    }

    // Ler todo o conteúdo
    string json_content = "";
    while(!FileIsEnding(handle))
    {
        json_content += FileReadString(handle);
    }

    FileClose(handle);

    // Parse JSON manualmente (MQL5 não tem parser JSON nativo)
    if(!ParseJSON(json_content))
    {
        Print("Erro ao fazer parse do JSON");
        return false;
    }

    return true;
}

//+------------------------------------------------------------------+
//| Parse JSON content (simple parser for our specific structure)   |
//+------------------------------------------------------------------+
bool ParseJSON(string json)
{
    // Remover espaços e quebras de linha
    StringReplace(json, "\n", "");
    StringReplace(json, "\r", "");
    StringReplace(json, " ", "");

    // Extrair valores (parser simples para nosso formato específico)
    agent_data.symbol = ExtractStringValue(json, "symbol");
    agent_data.current_price = ExtractDoubleValue(json, "current_price");
    agent_data.has_position = ExtractBoolValue(json, "has_position");
    agent_data.trailing_active = ExtractBoolValue(json, "trailing_active");
    agent_data.trailing_amount_dollars = ExtractDoubleValue(json, "trailing_amount_dollars");
    agent_data.entry_price = ExtractDoubleValue(json, "entry_price");
    agent_data.entry_ticket = (long)ExtractDoubleValue(json, "entry_ticket");
    agent_data.position_type = ExtractStringValue(json, "position_type");
    agent_data.sl = ExtractDoubleValue(json, "sl");
    agent_data.tp = ExtractDoubleValue(json, "tp");
    agent_data.profit = ExtractDoubleValue(json, "profit");
    agent_data.trailing_stop_level = ExtractDoubleValue(json, "trailing_stop_level");

    return true;
}

//+------------------------------------------------------------------+
//| Extract string value from JSON                                   |
//+------------------------------------------------------------------+
string ExtractStringValue(string json, string key)
{
    string search = "\"" + key + "\":\"";
    int start = StringFind(json, search);
    if(start < 0) return "";

    start += StringLen(search);
    int end = StringFind(json, "\"", start);
    if(end < 0) return "";

    return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| Extract double value from JSON                                   |
//+------------------------------------------------------------------+
double ExtractDoubleValue(string json, string key)
{
    string search = "\"" + key + "\":";
    int start = StringFind(json, search);
    if(start < 0) return 0;

    start += StringLen(search);
    int end = StringFind(json, ",", start);
    if(end < 0) end = StringFind(json, "}", start);
    if(end < 0) return 0;

    string value = StringSubstr(json, start, end - start);
    return StringToDouble(value);
}

//+------------------------------------------------------------------+
//| Extract bool value from JSON                                     |
//+------------------------------------------------------------------+
bool ExtractBoolValue(string json, string key)
{
    string search = "\"" + key + "\":";
    int start = StringFind(json, search);
    if(start < 0) return false;

    start += StringLen(search);
    string value = StringSubstr(json, start, 4);  // "true" or "fals"

    return (StringFind(value, "true") >= 0);
}

//+------------------------------------------------------------------+
//| Update chart lines                                               |
//+------------------------------------------------------------------+
void UpdateChartLines()
{
    // Se não tem posição, limpar linhas
    if(!agent_data.has_position)
    {
        DeleteAllObjects();
        return;
    }

    // Linha de Entrada (azul)
    if(ShowEntryLine && agent_data.entry_price > 0)
    {
        DrawHLine("Entry_Line", agent_data.entry_price, EntryLineColor, STYLE_SOLID, 2,
                  "ENTRY: " + DoubleToString(agent_data.entry_price, _Digits) +
                  " | " + agent_data.position_type + " #" + IntegerToString(agent_data.entry_ticket));
    }

    // Linha de SL (vermelha)
    if(ShowSLLine && agent_data.sl > 0)
    {
        DrawHLine("SL_Line", agent_data.sl, SLLineColor, STYLE_SOLID, 2,
                  "SL: " + DoubleToString(agent_data.sl, _Digits) + " (Max Loss: $4.00)");
    }

    // Linha de TP (verde)
    if(ShowTPLine && agent_data.tp > 0)
    {
        DrawHLine("TP_Line", agent_data.tp, TPLineColor, STYLE_SOLID, 2,
                  "TP: " + DoubleToString(agent_data.tp, _Digits) + " (Target: ~$20.00)");
    }

    // Linha de Trailing Stop (amarela tracejada) - dinâmica
    if(ShowTrailingLine && agent_data.trailing_active && agent_data.trailing_stop_level > 0)
    {
        DrawHLine("Trailing_Line", agent_data.trailing_stop_level, TrailingLineColor, STYLE_DASH, 3,
                  "TRAILING STOP: " + DoubleToString(agent_data.trailing_stop_level, _Digits) +
                  " | Defending: $" + DoubleToString(agent_data.trailing_amount_dollars, 2));
    }
    else
    {
        // Remover linha de trailing se não está ativa
        ObjectDelete(0, "Trailing_Line");
    }
}

//+------------------------------------------------------------------+
//| Draw horizontal line                                             |
//+------------------------------------------------------------------+
void DrawHLine(string name, double price, color line_color, ENUM_LINE_STYLE style, int width, string description)
{
    // Deletar se já existe
    if(ObjectFind(0, name) >= 0)
        ObjectDelete(0, name);

    // Criar linha horizontal
    if(ObjectCreate(0, name, OBJ_HLINE, 0, 0, price))
    {
        ObjectSetInteger(0, name, OBJPROP_COLOR, line_color);
        ObjectSetInteger(0, name, OBJPROP_STYLE, style);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, width);
        ObjectSetInteger(0, name, OBJPROP_BACK, false);
        ObjectSetInteger(0, name, OBJPROP_SELECTABLE, true);
        ObjectSetInteger(0, name, OBJPROP_SELECTED, false);
        ObjectSetString(0, name, OBJPROP_TEXT, description);
        ObjectSetString(0, name, OBJPROP_TOOLTIP, description);
    }
}

//+------------------------------------------------------------------+
//| Update info panel                                                |
//+------------------------------------------------------------------+
void UpdateInfoPanel()
{
    int x = 20;
    int y = 30;
    int line_height = 20;

    // Título
    CreateLabel("Info_Title", x, y, "=== BTC LOSS ZERO AGENT ===", clrWhite, 12, true);
    y += line_height + 5;

    // Status
    string status = agent_data.has_position ? "TRADING" : "ANALYZING";
    color status_color = agent_data.has_position ? clrLime : clrYellow;
    CreateLabel("Info_Status", x, y, "Status: " + status, status_color, 10, true);
    y += line_height;

    // Se tem posição, mostrar detalhes
    if(agent_data.has_position)
    {
        // Tipo de posição
        CreateLabel("Info_Type", x, y, "Position: " + agent_data.position_type + " #" + IntegerToString(agent_data.entry_ticket), clrWhite, 10, false);
        y += line_height;

        // Preço de entrada
        CreateLabel("Info_Entry", x, y, "Entry: " + DoubleToString(agent_data.entry_price, _Digits), clrDodgerBlue, 10, false);
        y += line_height;

        // Preço atual
        CreateLabel("Info_Current", x, y, "Current: " + DoubleToString(agent_data.current_price, _Digits), clrWhite, 10, false);
        y += line_height;

        // Lucro
        color profit_color = agent_data.profit >= 0 ? clrLime : clrRed;
        CreateLabel("Info_Profit", x, y, "Profit: $" + DoubleToString(agent_data.profit, 2), profit_color, 10, true);
        y += line_height;

        // Trailing
        if(agent_data.trailing_active)
        {
            CreateLabel("Info_Trailing", x, y,
                       "Trailing: ACTIVE ($" + DoubleToString(agent_data.trailing_amount_dollars, 2) + ")",
                       clrYellow, 10, true);
            y += line_height;

            CreateLabel("Info_TrailingLevel", x, y,
                       "Trail Level: " + DoubleToString(agent_data.trailing_stop_level, _Digits),
                       clrYellow, 10, false);
            y += line_height;
        }
        else
        {
            CreateLabel("Info_Trailing", x, y, "Trailing: WAITING ($1.00)", clrGray, 10, false);
            y += line_height;
        }

        // SL e TP
        CreateLabel("Info_SL", x, y, "SL: " + DoubleToString(agent_data.sl, _Digits) + " ($4 max)", clrRed, 10, false);
        y += line_height;

        CreateLabel("Info_TP", x, y, "TP: " + DoubleToString(agent_data.tp, _Digits) + " (~$20)", clrLime, 10, false);
        y += line_height;
    }
    else
    {
        CreateLabel("Info_NoPos", x, y, "No position - Scanning for signals...", clrGray, 10, false);
        y += line_height;

        CreateLabel("Info_Signals", x, y, "Using: RSI + MFI dual confirmation", clrGray, 9, false);
        y += line_height;
    }

    // Atualização
    y += 5;
    CreateLabel("Info_Update", x, y, "Last update: " + TimeToString(TimeCurrent(), TIME_SECONDS), clrGray, 8, false);
}

//+------------------------------------------------------------------+
//| Create label on chart                                            |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, color clr, int font_size, bool bold)
{
    if(ObjectFind(0, name) >= 0)
        ObjectDelete(0, name);

    if(ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0))
    {
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
        ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, font_size);
        ObjectSetString(0, name, OBJPROP_FONT, bold ? "Arial Bold" : "Arial");
        ObjectSetString(0, name, OBJPROP_TEXT, text);
        ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
        ObjectSetInteger(0, name, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
        ObjectSetInteger(0, name, OBJPROP_BACK, false);
    }
}

//+------------------------------------------------------------------+
//| Delete all objects created by this EA                            |
//+------------------------------------------------------------------+
void DeleteAllObjects()
{
    ObjectDelete(0, "Entry_Line");
    ObjectDelete(0, "SL_Line");
    ObjectDelete(0, "TP_Line");
    ObjectDelete(0, "Trailing_Line");

    ObjectDelete(0, "Info_Title");
    ObjectDelete(0, "Info_Status");
    ObjectDelete(0, "Info_Type");
    ObjectDelete(0, "Info_Entry");
    ObjectDelete(0, "Info_Current");
    ObjectDelete(0, "Info_Profit");
    ObjectDelete(0, "Info_Trailing");
    ObjectDelete(0, "Info_TrailingLevel");
    ObjectDelete(0, "Info_SL");
    ObjectDelete(0, "Info_TP");
    ObjectDelete(0, "Info_NoPos");
    ObjectDelete(0, "Info_Signals");
    ObjectDelete(0, "Info_Update");
}

//+------------------------------------------------------------------+
//| OnTick function (not used, but required)                         |
//+------------------------------------------------------------------+
void OnTick()
{
    // Não usado - atualização via timer
}
//+------------------------------------------------------------------+
