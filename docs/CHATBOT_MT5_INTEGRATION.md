# Integração Chatbot ↔ MT5

## 📋 Visão Geral

Este documento descreve a arquitetura e fluxo de comunicação entre o **Trading Chatbot** e o **MetaTrader 5 (MT5)** através do **MCP Server**.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADING CHATBOT SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │   Web Interface  │         │  Chatbot Client  │              │
│  │   (Flask 3000)   │         │  (Ollama + MT5)  │              │
│  └────────┬─────────┘         └────────┬─────────┘              │
│           │                            │                         │
│           └────────────────┬───────────┘                         │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  MT5 Integration │                          │
│                   │  (mt5_integration)                          │
│                   └────────┬────────┘                           │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  MT5 Connector  │                           │
│                   │ (mt5_connector) │                           │
│                   │  + Retry Logic  │                           │
│                   └────────┬────────┘                           │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  MT5 MCP Server │                           │
│                   │   (port 8000)   │                           │
│                   └────────┬────────┘                           │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  MetaTrader 5   │                           │
│                   │   Terminal      │                           │
│                   └─────────────────┘                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Arquitetura

### Componentes Principais

#### 1. **MT5Connector** (`src/core/mt5_connector.py`)
Camada de abstração para comunicação com o servidor MT5 MCP.

**Responsabilidades:**
- Comunicação HTTP com MT5 MCP Server
- Retry logic com backoff exponencial
- Tratamento de erros e timeouts
- Operações de trading (buy, sell, close)
- Consulta de dados (account, positions, orders, candles)

**Características:**
- ✅ Retry automático em caso de falha
- ✅ Timeout configurável
- ✅ Logging detalhado
- ✅ Exceções customizadas

#### 2. **ChatbotMT5Integration** (`src/chatbot/mt5_integration.py`)
Camada de integração de alto nível para o chatbot.

**Responsabilidades:**
- Interface simplificada para operações MT5
- Formatação de respostas para o chatbot
- Validação de símbolos
- Resumos de conta e posições

**Métodos Principais:**
```python
await integration.verify_connection()           # Verifica conexão
await integration.get_account_summary()         # Resumo da conta
await integration.get_open_positions_summary()  # Posições abertas
await integration.execute_buy_order(...)        # Executa compra
await integration.execute_sell_order(...)       # Executa venda
await integration.close_position(ticket)        # Fecha posição
await integration.get_symbol_price(symbol)      # Preço atual
await integration.validate_symbol(symbol)       # Valida símbolo
await integration.get_market_data(...)          # Dados de mercado
```

## 🔄 Fluxo de Comunicação

### Exemplo: Executar uma Ordem de Compra

```
1. Usuário → Chatbot
   "Comprar 0.1 EURUSD com TP $100 e SL $50"

2. Chatbot → Intent Parser (Ollama)
   Parse: symbol=EURUSD, volume=0.1, tp=$100, sl=$50

3. Chatbot → ChatbotMT5Integration
   execute_buy_order(symbol="EURUSD", volume=0.1, tp=100, sl=50)

4. ChatbotMT5Integration → MT5Connector
   buy_market(symbol="EURUSD", volume=0.1, tp=100, sl=50)

5. MT5Connector → MT5 MCP Server (HTTP POST)
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "order_send",
       "arguments": {
         "action": TRADE_ACTION_DEAL,
         "symbol": "EURUSD",
         "volume": 0.1,
         "type": ORDER_TYPE_BUY,
         "price": 1.0850,
         "sl": 1.0800,
         "tp": 1.0950,
         ...
       }
     }
   }

6. MT5 MCP Server → MetaTrader 5
   Executa ordem no terminal

7. MetaTrader 5 → MT5 MCP Server
   Retorna resultado da ordem

8. MT5 MCP Server → MT5Connector
   {
     "result": {
       "retcode": TRADE_RETCODE_DONE,
       "order": 123456,
       "price": 1.0850,
       ...
     }
   }

9. MT5Connector → ChatbotMT5Integration
   Formata resposta

10. ChatbotMT5Integration → Chatbot
    {
      "status": "success",
      "action": "BUY",
      "symbol": "EURUSD",
      "volume": 0.1,
      "price": 1.0850,
      "order": 123456,
      "tp": 100,
      "sl": 50
    }

11. Chatbot → Usuário
    "✅ Ordem executada! BUY 0.1 EURUSD @ 1.0850"
```

## 🛡️ Tratamento de Erros

### Retry Logic

O `MT5Connector` implementa retry automático com backoff:

```python
# Configuração padrão
MT5Connector(
    server_url="http://localhost:8000",
    timeout=30,           # 30 segundos
    max_retries=3,        # 3 tentativas
    retry_delay=1.0       # 1 segundo entre tentativas
)
```

**Cenários de Retry:**
- ❌ Timeout na conexão → Retry automático
- ❌ Erro de conexão → Retry automático
- ❌ Erro HTTP 5xx → Retry automático
- ✅ Erro HTTP 4xx → Sem retry (erro do cliente)
- ✅ Erro MCP → Sem retry (erro da operação)

### Exceções Customizadas

```python
# MT5ConnectorError (base)
├── MT5ConnectionError     # Erro de conexão
└── MT5OperationError      # Erro na operação
```

## 📊 Exemplo de Uso

### Uso Direto do MT5Connector

```python
from core.mt5_connector import MT5Connector

connector = MT5Connector()

# Verificar conexão
if connector.check_connection():
    print("✅ Conectado ao MT5")

# Obter informações da conta
account = connector.get_account_info()
print(f"Balance: ${account['balance']}")

# Executar ordem
result = connector.buy_market(
    symbol="EURUSD",
    volume=0.1,
    sl=1.0800,
    tp=1.0950
)
print(f"Order: {result['order']} @ {result['price']}")

# Obter posições
positions = connector.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['volume']} lots")

# Fechar posição
connector.close_position(ticket=123456)
```

### Uso via ChatbotMT5Integration

```python
from chatbot.mt5_integration import ChatbotMT5Integration

integration = ChatbotMT5Integration()

# Verificar conexão
connected = await integration.verify_connection()

# Obter resumo da conta
account = await integration.get_account_summary()
print(f"Balance: ${account['balance']}")

# Executar compra
result = await integration.execute_buy_order(
    symbol="EURUSD",
    volume=0.1,
    sl=1.0800,
    tp=1.0950
)

# Obter posições abertas
positions = await integration.get_open_positions_summary()
print(f"Posições abertas: {positions['count']}")

# Fechar posição
result = await integration.close_position(ticket=123456)
```

## 🧪 Testes

### Executar Testes de Integração

```bash
python test_chatbot_mt5_integration.py
```

**Testes Inclusos:**
1. ✅ Verificar conexão com MT5
2. ✅ Obter informações da conta
3. ✅ Verificar posições abertas
4. ✅ Validar símbolos
5. ✅ Obter preços de símbolos
6. ✅ Obter dados de mercado (velas)

### Saída Esperada

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      TESTE DE INTEGRAÇÃO CHATBOT ↔ MT5                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

============================================================
🔍 TESTE 1: Verificando conexão com MT5
============================================================
✅ Conexão com MT5 estabelecida com sucesso!

============================================================
🔍 TESTE 2: Obtendo informações da conta
============================================================
✅ Informações da conta obtidas:
   Balance: $10000.00
   Equity: $10050.00
   Margem Livre: $9950.00
   Nível de Margem: 1005.00%
   Servidor: MetaQuotes-Demo

...

📊 RESUMO DOS TESTES
============================================================
✅ PASSOU: Conexão
✅ PASSOU: Informações da Conta
✅ PASSOU: Posições Abertas
✅ PASSOU: Validação de Símbolos
✅ PASSOU: Preços de Símbolos
✅ PASSOU: Dados de Mercado
============================================================
Resultado: 6/6 testes passaram
🎉 Todos os testes passaram! Integração funcionando!
```

## 🚀 Próximos Passos

### Fase 1: Integração Básica ✅
- [x] MT5Connector com retry logic
- [x] ChatbotMT5Integration
- [x] Testes de integração
- [x] Documentação

### Fase 2: Agent System (Próximo)
- [ ] Agent Generator (parse de linguagem natural)
- [ ] Strategy Engine (indicadores técnicos)
- [ ] Agent Manager (gerenciamento de múltiplos agentes)
- [ ] Database schema para agentes

### Fase 3: Notificações
- [ ] Sistema de notificações (email, webhook, WebSocket)
- [ ] Alertas em tempo real
- [ ] Dashboard de monitoramento

### Fase 4: Otimizações
- [ ] Cache de dados
- [ ] Rate limiting
- [ ] Logging estruturado
- [ ] Métricas de performance

## 📝 Configuração

### Variáveis de Ambiente

```bash
# .env
MT5_MCP_HOST=localhost
MT5_MCP_PORT=8000
MT5_MCP_TIMEOUT=30
MT5_MCP_RETRIES=3
```

### Configuração no Código

```python
from core.mt5_connector import MT5Connector

connector = MT5Connector(
    server_url="http://localhost:8000",
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)
```

## 🔧 Troubleshooting

### Problema: "Não foi possível conectar ao servidor MT5"

**Solução:**
1. Verifique se MT5 está rodando
2. Verifique se está logado na conta
3. Verifique se o servidor MCP MT5 está iniciado (porta 8000)
4. Verifique firewall/proxy

```bash
# Testar conexão
curl http://localhost:8000/mcp
```

### Problema: "Símbolo não encontrado"

**Solução:**
1. Verifique se o símbolo está disponível no broker
2. Verifique a grafia exata (case-sensitive)
3. Use `get_symbols()` para listar símbolos disponíveis

### Problema: "Ordem rejeitada"

**Solução:**
1. Verifique se há saldo suficiente
2. Verifique se o símbolo está em horário de negociação
3. Verifique se o volume está dentro dos limites
4. Verifique se há posições conflitantes

## 📚 Referências

- [MT5 MCP Server](../src/mcp_mt5/main.py)
- [Chatbot Client](../src/chatbot/client.py)
- [MetaTrader 5 Python API](https://www.mql5.com/en/docs/integration/python_metatrader5)
- [FastMCP Documentation](https://github.com/jlopp/fastmcp)

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `trading_bot.log`
2. Execute os testes de integração
3. Consulte a documentação do MT5 MCP Server
4. Abra uma issue no repositório
