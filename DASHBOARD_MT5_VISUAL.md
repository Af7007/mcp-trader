# Dashboard Visual MT5 para BTC Agent

## 📊 Integração Python ↔️ MT5

O agente Python agora exporta seus dados em tempo real para um dashboard visual no MT5.

---

## 🔧 Como Ativar

### 1. Iniciar o Agente Python

Execute o agente normalmente:

```bash
RUN_BTC_AGENT.bat
```

O agente vai:
- Operar normalmente com BTCUSDm
- Exportar dados a cada 30 segundos para: `C:\mcp-trader\agent_data.json`

### 2. Adicionar Dashboard no MT5

1. Abra o MetaTrader 5
2. Vá em: **Ferramentas → Editor MQL5** (ou pressione F4)
3. No MetaEditor, abra o arquivo: `BTC_Agent_Dashboard.mq5`
4. Compile o arquivo (F7) - deve compilar sem erros
5. Volte ao MT5
6. Abra um gráfico do **BTCUSDm** (qualquer timeframe)
7. Arraste o Expert Advisor **BTC_Agent_Dashboard** para o gráfico
8. Confirme "Permitir trading automatizado"

---

## 📈 O Que o Dashboard Mostra

### Painel de Informações (Canto Superior Esquerdo)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🤖 BTC HEDGE AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Estado: TRADING
  Trades: 5 / 20
  Lucro: $10.50
  Streak: 3
  Hedge: ATIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💹 MERCADO (BTCUSDm)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Preço: $45,234.50
  Trend: UP
  RSI: 65.3
  MACD: +12.45
  ATR: 85.32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 INDICADORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMA 20: $45,120
  SMA 50: $44,980
  BB Up: $45,450
  BB Low: $44,790
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💼 POSIÇÕES: 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Indicadores no Gráfico

- **Bollinger Bands**: Bandas superior, média e inferior (azul)
- **SMA 20**: Média móvel rápida (dourado)
- **SMA 50**: Média móvel lenta (laranja)

### Sinais de Trading

- **🟢 Setas VERDES**: Sinal de COMPRA (RSI < 40 e MACD > 0)
- **🔴 Setas VERMELHAS**: Sinal de VENDA (RSI > 60 e MACD < 0)

---

## ⚡ Frequência de Atualização

- **Agente Python**: Exporta dados a cada **30 segundos**
- **Dashboard MT5**: Lê e atualiza a cada **5 segundos**

---

## 🔍 Arquivo de Dados

**Localização**: `C:\mcp-trader\agent_data.json`

**Formato**:
```json
{
  "agent": "BTC_Hedge_Agent",
  "state": "trading",
  "symbol": "BTCUSDm",
  "daily_trades": 5,
  "max_daily_trades": 20,
  "total_profit": 10.50,
  "winning_streak": 3,
  "hedge_active": true,
  "positions_count": 2,
  "timestamp": "2025-01-15T14:30:45",
  "current_price": 45234.50,
  "trend": "UP",
  "rsi": 65.3,
  "macd": 12.45,
  "atr": 85.32,
  "sma_20": 45120.00,
  "sma_50": 44980.00,
  "bb_upper": 45450.00,
  "bb_middle": 45120.00,
  "bb_lower": 44790.00
}
```

---

## ⚙️ Configurações do Dashboard

No código MQL5 (`BTC_Agent_Dashboard.mq5`), você pode ajustar:

```mql5
#define DATA_FILE "C:\\mcp-trader\\agent_data.json"
#define REFRESH_SECONDS 5  // Intervalo de atualização
```

---

## ❓ Solução de Problemas

### Dashboard não mostra dados

1. **Verifique se o agente Python está rodando**
   ```bash
   # Deve estar executando RUN_BTC_AGENT.bat
   ```

2. **Verifique se o arquivo JSON existe**
   ```
   C:\mcp-trader\agent_data.json
   ```
   - O arquivo deve ser criado após o primeiro ciclo do agente (30s)

3. **Verifique o log do MT5**
   - Abra a aba "Experts" no MT5
   - Procure por mensagens do dashboard

### Erro de compilação no MT5

- Certifique-se que está usando **MetaTrader 5** (não MT4)
- Verifique se o arquivo está na pasta correta: `MQL5\Experts\`

---

## 🎯 Teste Completo

1. **Terminal 1**: Execute `RUN_BTC_AGENT.bat`
2. **MT5**: Adicione o dashboard ao gráfico BTCUSDm
3. Aguarde 30 segundos para o primeiro ciclo
4. O painel deve aparecer no canto superior esquerdo
5. Os indicadores devem ser desenhados no gráfico
6. Setas de sinal devem aparecer quando condições forem atendidas

---

## 📝 Notas

- O dashboard é **somente leitura** - não interfere nas operações
- Todas as operações são feitas pelo agente Python
- O dashboard apenas **visualiza** o estado do agente
- É possível ter múltiplos gráficos com o dashboard aberto

---

✅ **Integração completa Python + MT5 Dashboard funcionando!**
