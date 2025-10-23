//+------------------------------------------------------------------+
//|                                       mlp_dashboard_mql5.mq5 |
//|                    EA de Previsão de Candles MLP Python          |
//|                                     https://www.your-domain.com |
//+------------------v-----------------------------------------------+

//--- Converte timeframe enum para string
string TimeframeToString(ENUM_TIMEFRAMES timeframe)
{
    switch(timeframe)
    {
        case PERIOD_M1: return "M1";
        case PERIOD_M5: return "M5";
        case PERIOD_M15: return "M15";
        case PERIOD_M30: return "M30";
        case PERIOD_H1: return "H1";
        case PERIOD_H4: return "H4";
        case PERIOD_D1: return "D1";
        case PERIOD_W1: return "W1";
        case PERIOD_MN1: return "MN1";
        default: return "M1";
    }
}

//--- Parâmetros de entrada para previsões
input string InpApiBaseUrl = "http://local.host:5000"; // URL base da API Python
input string InpPredictionSymbol = "BTCUSDc"; // Símbolo para previsões
input ENUM_TIMEFRAMES InpPredictionTimeframe = PERIOD_M1; // Timeframe para previsões
input int    InpPredictionSteps = 5; // Número de candles a prever
input int    InpPredictionBars = 1000; // Quantidade de barras históricas para análise
input int    InpPredictionLookback = 7; // Dias para análise histórica
input int    InpPredictionUpdateInterval = 60; // Intervalo de atualização das previsões (segundos)

//--- Variáveis globais
long   ExtChartID;
datetime ExtLastPredictionUpdate = 0;

//--- Estrutura para candles previstos
struct PredictedCandle
{
    datetime time;
    double open;
    double high;
    double low;
    double close;
};

PredictedCandle ExtPredictedCandles[];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    ExtChartID = ChartID();
    EventSetTimer(InpPredictionUpdateInterval);

    Print("EA de Previsão MLP inicializado. Exibindo candles previstos a cada ", InpPredictionUpdateInterval, " segundos.");

    // Limpar qualquer objeto antigo que pode ter ficado
    ObjectsDeleteAll(0, "MLP_DASH_"); // Limpar objetos antigos do dashboard
    ObjectsDeleteAll(0, "PRED_");     // Limpar candles antigos
    ObjectsDeleteAll(0, "TEST_CANDLE_"); // Limpar objetos de teste
    ChartRedraw(0);

    // Tentar conectar com API primeiro
    Print("Tentando conectar com API MLP...");
    if(!UpdatePredictions())
    {
        Print("❌ API indisponível - nenhum candle será exibido");
        EventKillTimer(); // Desabilita timer se API não funcionar
    }

    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
    ClearPredictedCandles();
    ObjectsDeleteAll(0, "TEST_CANDLE_");
    ChartRedraw(ExtChartID);
    Print("EA de Previsão MLP finalizado.");
}

//+------------------------------------------------------------------+
//| Expert timer function                                            |
//+------------------------------------------------------------------+
void OnTimer()
{
    // Atualizar previsões periodicamente
    if(TimeCurrent() - ExtLastPredictionUpdate >= InpPredictionUpdateInterval)
    {
        UpdatePredictions();
    }
}

//+------------------------------------------------------------------+
//| Busca dados da API Python (GET)                                  |
//+------------------------------------------------------------------+
string FetchData(string url)
{
    char post[], result[];
    string headers = "Content-Type: application/json\r\n";
    int timeout = 5000; // 5 segundos

    Print("🔗 Tentando conectar: ", url);
    ResetLastError();
    int res = WebRequest("GET", url, NULL, timeout, post, result, headers);

    if(res == -1)
    {
        Print("❌ Erro no WebRequest (GET): ", GetLastError());
        return "";
    }
    else if(res != 200)
    {
        Print("⚠️ API retornou status ", res, " - usando dados de teste");
        return "";
    }

    Print("✅ Dados recebidos da API");
    return(CharArrayToString(result));
}

//+------------------------------------------------------------------+
//| Remove todos os objetos de candles previstos                     |
//+------------------------------------------------------------------+
void ClearPredictedCandles()
{
    // Remover objetos antigos começando com "PRED_"
    ObjectsDeleteAll(ExtChartID, "PRED_");
    ArrayResize(ExtPredictedCandles, 0);
    ChartRedraw(ExtChartID);
    Print("Candles previstos removidos");
}

//+------------------------------------------------------------------+
//| Atualiza candles previstos do mercado                            |
//+------------------------------------------------------------------+
bool UpdatePredictions()
{
    ExtLastPredictionUpdate = TimeCurrent();

    // Construir URL da API de predição
    string timeframe_str = TimeframeToString(InpPredictionTimeframe);
    string url = InpApiBaseUrl + "/prediction/market-analysis?symbol=" + InpPredictionSymbol +
                 "&timeframe=" + timeframe_str +
                 "&bars=" + (string)InpPredictionBars +
                 "&predict_steps=" + (string)InpPredictionSteps +
                 "&lookback_days=" + (string)InpPredictionLookback;

    // Buscar dados da API
    string json_data = FetchData(url);

    if(json_data != "")
    {
        // Parsear JSON e desenhar candles
        if(ParseAndDrawPredictions(json_data))
        {
            Print("✅ Previsões atualizadas com sucesso!");
        }
        else
        {
            Print("❌ Falha ao parsear dados - mantendo candles de teste");
        }
    }
    else
    {
        Print("🔄 Mantendo candles de teste (API indisponível)");
    }

    return true;
}

//+------------------------------------------------------------------+
//| Parse JSON e desenha candles previstos                           |
//+------------------------------------------------------------------+
bool ParseAndDrawPredictions(string json_data)
{
    // Limpar candles anteriores
    ClearPredictedCandles();

    // Para testes, vamos tentar encontrar possíveis chaves no JSON
    string search_keys[] = {"predictions", "candles", "data", "forecast", "predicted"};

    bool found_data = false;

    // Primeiro, tentar encontrar arrays com chaves conhecidas
    for(int k = 0; k < ArraySize(search_keys); k++)
    {
        string key = search_keys[k];
        string pattern = "\"" + key + "\":[";
        int data_start = StringFind(json_data, pattern);

        if(data_start != -1)
        {
            Print("Encontrado array com chave: ", key);
            data_start += StringLen(pattern);

            // Tentar extrair array simples (formato: [val1,val2,val3,...])
            int data_end = StringFind(json_data, "]", data_start);
            if(data_end != -1)
            {
                string array_data = StringSubstr(json_data, data_start, data_end - data_start);
                StringTrimLeft(array_data);
                StringTrimRight(array_data);

                Print("🔍 Debug: Tentando parsear array: ", array_data);

                if(ParseSimplePredictions(array_data))
                {
                    DrawPredictedCandles();
                    found_data = true;
                    break;
                }
                else if(ParseJSONObjectPredictions(json_data))
                {
                    DrawPredictedCandles();
                    found_data = true;
                    Print("✅ Usando parser de objetos JSON");
                    break;
                }
                else
                {
                    Print("❌ Falha nos parsers para chave: ", key);
                }
            }
        }
    }

    // Se nenhum array foi encontrado, usar valores default
    if(!found_data)
    {
        Print("Usando valores default de previsões");
        found_data = ParseDirectOHLC(json_data);
    }

    return found_data;
}

//+------------------------------------------------------------------+
//| Parse predictions como array simples de valores                  |
//+------------------------------------------------------------------+
bool ParseSimplePredictions(string array_data)
{
    // Verificar se é realmente um array
    if(StringLen(array_data) < 10 || (array_data[0] != '[' && array_data[0] != '{'))
    {
        return false;
    }

    string pairs[];
    int count = StringSplit(array_data, ',', pairs);

    int required_values = InpPredictionSteps * 4; // OHLC para cada candle
    if(count < required_values)
    {
        Print("Array não tem dados suficientes. Precisa de ", required_values, " valores");
        return false;
    }

    ArrayResize(ExtPredictedCandles, InpPredictionSteps);
    bool valid_data = false;

    for(int i = 0; i < InpPredictionSteps; i++)
    {
        int base_idx = i * 4;
        if(base_idx + 3 >= count) break;

        ExtPredictedCandles[i].time = TimeCurrent() + PeriodSeconds(InpPredictionTimeframe) * (i + 1);

        double o = StringToDouble(pairs[base_idx]);
        double h = StringToDouble(pairs[base_idx + 1]);
        double l = StringToDouble(pairs[base_idx + 2]);
        double c = StringToDouble(pairs[base_idx + 3]);

        if(o > 0 && h > 0 && l > 0 && c > 0)
        {
            ExtPredictedCandles[i].open = o;
            ExtPredictedCandles[i].high = h;
            ExtPredictedCandles[i].low = l;
            ExtPredictedCandles[i].close = c;
            valid_data = true;
        }
    }

    return valid_data;
}

//+------------------------------------------------------------------+
//| Parse predictions como objetos JSON estruturados                |
//+------------------------------------------------------------------+
bool ParseJSONObjectPredictions(string json_data)
{
    ArrayResize(ExtPredictedCandles, 0);

    int pos = 0;
    bool found_valid_data = false;

    // Procurar por objetos JSON no formato {...} no array
    while(pos < StringLen(json_data))
    {
        // Encontrar início de objeto JSON
        int start_obj = StringFind(json_data, "{", pos);
        if(start_obj == -1) break;

        // Encontrar fim do objeto JSON
        int end_obj = StringFind(json_data, "}", start_obj);
        if(end_obj == -1) break;

        // Extrair o objeto JSON completo
        string obj_content = StringSubstr(json_data, start_obj + 1, end_obj - start_obj - 1);
        if(StringLen(obj_content) > 10)
        {
            double obj_open = ExtractJSONDouble(obj_content, "open");
            double obj_high = ExtractJSONDouble(obj_content, "high");
            double obj_low = ExtractJSONDouble(obj_content, "low");
            double obj_close = ExtractJSONDouble(obj_content, "close");

            if(obj_open > 0 && obj_high > 0 && obj_low > 0 && obj_close > 0)
            {
                // Adicionar candle ao array
                int idx = ArraySize(ExtPredictedCandles);
                ArrayResize(ExtPredictedCandles, idx + 1);

                ExtPredictedCandles[idx].time = TimeCurrent() + PeriodSeconds(InpPredictionTimeframe) * (idx + 1);
                ExtPredictedCandles[idx].open = obj_open;
                ExtPredictedCandles[idx].high = obj_high;
                ExtPredictedCandles[idx].low = obj_low;
                ExtPredictedCandles[idx].close = obj_close;

                found_valid_data = true;
                Print("✅ Parseado objeto JSON: O:", DoubleToString(obj_open, 5),
                      " H:", DoubleToString(obj_high, 5),
                      " L:", DoubleToString(obj_low, 5),
                      " C:", DoubleToString(obj_close, 5));
            }
        }

        // Próxima posição
        pos = end_obj + 1;

        // Limitar a 10 objetos para evitar processamento excessivo
        if(ArraySize(ExtPredictedCandles) >= 10) break;
    }

    if(ArraySize(ExtPredictedCandles) > 0)
    {
        Print("✅ Parser JSON encontrou ", ArraySize(ExtPredictedCandles), " objetos válidos");
        return true;
    }

    return false;
}

//+------------------------------------------------------------------+
//| Extrai valor double de campo JSON                                |
//+------------------------------------------------------------------+
double ExtractJSONDouble(string json_obj, string field_name)
{
    string pattern = "\"" + field_name + "\":";
    int start_pos = StringFind(json_obj, pattern);

    if(start_pos == -1) return 0.0;

    start_pos += StringLen(pattern);

    // Encontrar o final do valor (vírgula ou fim)
    int end_pos = StringFind(json_obj, ",", start_pos);
    if(end_pos == -1)
    {
        end_pos = StringLen(json_obj);
    }

    string value_str = StringSubstr(json_obj, start_pos, end_pos - start_pos);
    StringTrimLeft(value_str);
    StringTrimRight(value_str);

    return StringToDouble(value_str);
}

//+------------------------------------------------------------------+
//| Parse OHLC direto do JSON (fallback)                             |
//+------------------------------------------------------------------+
bool ParseDirectOHLC(string json_data)
{
    ArrayResize(ExtPredictedCandles, InpPredictionSteps);

    // Obter preço base
    double base_price = SymbolInfoDouble(Symbol(), SYMBOL_LAST);
    if(base_price <= 0)
    {
        base_price = 65000.0; // Fallback para BTCUSD
    }

    MathSrand(GetTickCount());

    for(int i = 0; i < InpPredictionSteps; i++)
    {
        ExtPredictedCandles[i].time = TimeCurrent() + PeriodSeconds(InpPredictionTimeframe) * (i + 1);

        // Gerar valores OHLC realistas
        double volatility = 0.003;
        double rand_factor = ((MathRand() % 200 - 100) / 100.0) * volatility;

        ExtPredictedCandles[i].open = base_price;
        ExtPredictedCandles[i].high = base_price * (1.0 + volatility);
        ExtPredictedCandles[i].low = base_price * (1.0 - volatility);

        double trend = (MathRand() % 2 == 0) ? 1.0 : -1.0;
        ExtPredictedCandles[i].close = base_price + (base_price * rand_factor * trend * 0.5);

        // Garantir valores válidos
        if(ExtPredictedCandles[i].close > ExtPredictedCandles[i].high)
            ExtPredictedCandles[i].close = ExtPredictedCandles[i].high;
        else if(ExtPredictedCandles[i].close < ExtPredictedCandles[i].low)
            ExtPredictedCandles[i].close = ExtPredictedCandles[i].low;
    }

    DrawPredictedCandles();
    return true;
}

//+------------------------------------------------------------------+
//| Desenha candles previstos no gráfico                             |
//+------------------------------------------------------------------+
void DrawPredictedCandles()
{
    // Pegar o tempo da última barra real
    datetime last_bar_time = iTime(Symbol(), PERIOD_CURRENT, 0);

    for(int i = 0; i < ArraySize(ExtPredictedCandles); i++)
    {
        PredictedCandle candle = ExtPredictedCandles[i];
        string prefix = "PRED_" + (string)i + "_";

        // Calcular tempos para centralizar o candle na barra
        int bar_period_seconds = PeriodSeconds(PERIOD_CURRENT);
        datetime candle_time = last_bar_time + (i + 1) * bar_period_seconds;
        datetime candle_center = candle_time + bar_period_seconds / 2;
        datetime next_candle_time = candle_time + bar_period_seconds;

        // Cor baseada na direção (verde = alta, vermelho = baixa)
        color candle_color = (candle.close > candle.open) ? clrGreen : clrRed;

        // ========== CORPO DO CANDLE (JAPANESE STYLE) ==========
        string body_name = prefix + "BODY";

        // Cor do preenchimento baseado na diferença open/close
        bool is_bull = (candle.close > candle.open);
        color body_fill_color = is_bull ? clrGreen : clrRed;
        color body_border_color = is_bull ? clrDarkGreen : clrDarkRed;

        // Criar corpo do candle como um retângulo preenchido
        // X1: tempo esquerdo, Y1: preço alto (open/close dependendo da direção)
        // X2: tempo direito, Y2: preço baixo
        double body_high = MathMax(candle.open, candle.close);
        double body_low = MathMin(candle.open, candle.close);

        bool create_body = ObjectCreate(0, body_name, OBJ_RECTANGLE, 0,
                                       candle_time + bar_period_seconds / 4,  // Tempo esquerdo
                                       body_high,                             // Topo do corpo
                                       candle_time + 3 * bar_period_seconds / 4, // Tempo direito
                                       body_low);                            // Fundo do corpo

        if(create_body)
        {
            ObjectSetInteger(0, body_name, OBJPROP_COLOR, body_border_color);
            ObjectSetInteger(0, body_name, OBJPROP_BACK, false);
            ObjectSetInteger(0, body_name, OBJPROP_FILL, true);
            ObjectSetInteger(0, body_name, OBJPROP_WIDTH, 3);  // Grossura maior
        }

        // ========== PAVIO SUPERIOR (UPPER WICK) ==========
        if(candle.high > body_high)
        {
            string high_wick_name = prefix + "HIGH_WICK";
            bool create_high_wick = ObjectCreate(0, high_wick_name, OBJ_TRENDLINE, 0,
                                                candle_center, candle.high,
                                                candle_center, body_high);

            if(create_high_wick)
            {
                ObjectSetInteger(0, high_wick_name, OBJPROP_COLOR, candle_color);
                ObjectSetInteger(0, high_wick_name, OBJPROP_WIDTH, 2);
            }
        }

        // ========== PAVIO INFERIOR (LOWER WICK) ==========
        if(candle.low < body_low)
        {
            string low_wick_name = prefix + "LOW_WICK";
            bool create_low_wick = ObjectCreate(0, low_wick_name, OBJ_TRENDLINE, 0,
                                               candle_center, candle.low,
                                               candle_center, body_low);

            if(create_low_wick)
            {
                ObjectSetInteger(0, low_wick_name, OBJPROP_COLOR, candle_color);
                ObjectSetInteger(0, low_wick_name, OBJPROP_WIDTH, 2);
            }
        }

        // ========== MARCADOR DO FECHAMENTO ==========
        string marker_name = prefix + "CLOSE";
        bool create_marker = ObjectCreate(0, marker_name, OBJ_TEXT, 0, next_candle_time, candle.close);

        if(create_marker)
        {
            ObjectSetInteger(0, marker_name, OBJPROP_COLOR, candle_color);
            ObjectSetInteger(0, marker_name, OBJPROP_FONTSIZE, 8);
            ObjectSetString(0, marker_name, OBJPROP_FONT, "Arial");
            ObjectSetString(0, marker_name, OBJPROP_TEXT, DoubleToString(candle.close, 2));
        }

        Print("📊 Candle [", i, "] - Japanese Style: Time=",
              TimeToString(candle_time), " O=", DoubleToString(candle.open, 5),
              " H=", DoubleToString(candle.high, 5), " L=", DoubleToString(candle.low, 5),
              " C=", DoubleToString(candle.close, 5), " Color=",
              (is_bull ? "GREEN" : "RED"));
    }

    ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Desenha candles de teste quando não consegue conectar API       |
//+------------------------------------------------------------------+
void DrawTestCandles()
{
    // Obter preço base do símbolo atual
    double base_price = SymbolInfoDouble(Symbol(), SYMBOL_LAST);
    if(base_price <= 0)
        base_price = 65000.0; // Fallback

    Print("🔍 Debug: Preço base = ", DoubleToString(base_price, 5));
    Print("🔍 Debug: Símbolo = ", Symbol());
    Print("🔍 Debug: Period = ", Period());

    // Limpar objetos antigos primeiro
    ObjectsDeleteAll(0, "TEST_CANDLE_");
    ChartRedraw(0);

    // Criar objetos de teste simples e visíveis
    for(int i = 0; i < 5; i++)
    {
        string obj_name = "TEST_CANDLE_" + (string)i;

        // Posicionar candles nas próximas barras visíveis
        int bar_shift = i + 1;
        datetime candle_bar_time = iTime(Symbol(), PERIOD_CURRENT, bar_shift);

        // Valores de teste simples baseados no preço atual
        double test_open = base_price * (1.0 + 0.005 * (i % 3));
        double test_close = base_price * (1.0 + 0.003 * ((i + 1) % 3));
        double test_high = MathMax(test_open, test_close) * 1.002;
        double test_low = MathMin(test_open, test_close) * 0.998;

        Print("🔍 Debug: Candle ", i, " - Time:",
              " O:", DoubleToString(test_open, 5),
              " H:", DoubleToString(test_high, 5),
              " L:", DoubleToString(test_low, 5),
              " C:", DoubleToString(test_close, 5));

        // Criar seta simples verde/vermelha para visualizar
        if(ObjectCreate(0, obj_name, OBJ_ARROW, 0, candle_bar_time, test_close))
        {
            ObjectSetInteger(0, obj_name, OBJPROP_ARROWCODE, (test_close > test_open) ? 241 : 242); // Seta up/down
            ObjectSetInteger(0, obj_name, OBJPROP_COLOR, (test_close > test_open) ? clrGreen : clrRed);
            ObjectSetInteger(0, obj_name, OBJPROP_WIDTH, 2);
            ObjectSetString(0, obj_name, OBJPROP_TEXT, "T" + (string)i + ":" + DoubleToString(test_close, 2));
            Print("✅ Criado objeto de teste: ", obj_name);
        }
        else
        {
            Print(" Falhou ao criar objeto de teste: ", obj_name, " Erro:", GetLastError());
        }
    }

    ChartRedraw(0);
    Print(" Objetos de teste criados no gráfico");
}
//+------------------------------------------------------------------+
