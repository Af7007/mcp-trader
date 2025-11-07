# ⚡ Quick Start - Integração Chatbot ↔ MT5

## 🎯 Em 5 Minutos

### 1️⃣ Verificar Conexão
```bash
python test_chatbot_mt5_integration.py
```

Se tudo estiver funcionando, você verá:
```
✅ PASSOU: Conexão
✅ PASSOU: Informações da Conta
✅ PASSOU: Posições Abertas
✅ PASSOU: Validação de Símbolos
✅ PASSOU: Preços de Símbolos
✅ PASSOU: Dados de Mercado
Resultado: 6/6 testes passaram
```

### 2️⃣ Executar Exemplos
```bash
python example_chatbot_mt5_usage.py
```

Veja exemplos práticos de:
- Obter informações da conta
- Verificar posições abertas
- Obter preços de símbolos
- Obter dados de mercado
- E muito mais!

### 3️⃣ Usar no Seu Código

```python
import asyncio
from chatbot.mt5_integration import ChatbotMT5Integration

async def main():
    integration = ChatbotMT5Integration()
    
    # Verificar conexão
    connected = await integration.verify_connection()
    print(f"Conectado: {connected}")
    
    # Obter saldo
    account = await integration.get_account_summary()
    print(f"Saldo: ${account['balance']:.2f}")
    
    # Obter posições
    positions = await integration.get_open_positions_summary()
    print(f"Posições abertas: {positions['count']}")
    
    # Obter preço
    price = await integration.get_symbol_price("EURUSD")
    print(f"EURUSD: {price['bid']:.5f} / {price['ask']:.5f}")

asyncio.run(main())
```

## 📚 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `src/core/mt5_connector.py` | Camada de abstração MT5 (retry logic, error handling) |
| `src/chatbot/mt5_integration.py` | Interface para o chatbot |
| `test_chatbot_mt5_integration.py` | Testes automatizados |
| `example_chatbot_mt5_usage.py` | Exemplos de uso |
| `docs/CHATBOT_MT5_INTEGRATION.md` | Documentação completa |
| `INTEGRATION_SUMMARY.md` | Resumo executivo |

## 🔧 Configuração

### Padrão (Funciona na Maioria dos Casos)
```python
from chatbot.mt5_integration import ChatbotMT5Integration

integration = ChatbotMT5Integration()
```

### Customizado
```python
from core.mt5_connector import MT5Connector

connector = MT5Connector(
    server_url="http://localhost:8000",
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)
```

## 🚨 Troubleshooting

### Erro: "Não foi possível conectar ao servidor MT5"

**Solução:**
1. Certifique-se de que MT5 está rodando
2. Certifique-se de que está logado na conta
3. Inicie o servidor MCP MT5:
   ```bash
   python src/mcp_mt5/main.py
   ```
4. Verifique se a porta 8000 está acessível:
   ```bash
   curl http://localhost:8000/mcp
   ```

### Erro: "Símbolo não encontrado"

**Solução:**
1. Verifique a grafia exata do símbolo
2. Valide o símbolo:
   ```python
   is_valid = await integration.validate_symbol("EURUSD")
   ```
3. Consulte símbolos disponíveis no MT5

### Erro: "Ordem rejeitada"

**Solução:**
1. Verifique se há saldo suficiente
2. Verifique se o símbolo está em horário de negociação
3. Verifique se o volume está dentro dos limites
4. Verifique se há posições conflitantes

## 💡 Dicas

### 1. Sempre Verificar Conexão Primeiro
```python
connected = await integration.verify_connection()
if not connected:
    print("MT5 não está disponível")
    return
```

### 2. Validar Símbolos Antes de Usar
```python
if await integration.validate_symbol(symbol):
    # Prosseguir com a operação
    pass
else:
    print(f"Símbolo {symbol} não disponível")
```

### 3. Usar Try/Except para Operações
```python
try:
    result = await integration.execute_buy_order(
        symbol="EURUSD",
        volume=0.1,
        sl=1.0800,
        tp=1.0950
    )
    if result["status"] == "success":
        print(f"Ordem executada: {result['order']}")
    else:
        print(f"Erro: {result['message']}")
except Exception as e:
    print(f"Exceção: {e}")
```

### 4. Logging Detalhado
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Agora você verá logs detalhados
```

## 📊 Métodos Principais

### ChatbotMT5Integration

```python
# Verificação
await integration.verify_connection()

# Informações da Conta
await integration.get_account_summary()
await integration.get_open_positions_summary()

# Operações de Trading
await integration.execute_buy_order(symbol, volume, sl=None, tp=None)
await integration.execute_sell_order(symbol, volume, sl=None, tp=None)
await integration.close_position(ticket)

# Dados de Mercado
await integration.get_symbol_price(symbol)
await integration.validate_symbol(symbol)
await integration.get_market_data(symbol, timeframe=60, count=50)
```

### MT5Connector

```python
# Verificação
connector.check_connection()

# Informações
connector.get_account_info()
connector.get_symbol_info(symbol)
connector.get_symbol_tick(symbol)
connector.get_positions(symbol=None)
connector.get_orders(symbol=None)

# Operações
connector.buy_market(symbol, volume, sl=None, tp=None)
connector.sell_market(symbol, volume, sl=None, tp=None)
connector.close_position(ticket)

# Dados
connector.get_candles(symbol, timeframe=60, count=100)
```

## 🎓 Exemplos Rápidos

### Exemplo 1: Obter Saldo
```python
account = await integration.get_account_summary()
print(f"Saldo: ${account['balance']:.2f}")
```

### Exemplo 2: Listar Posições Abertas
```python
positions = await integration.get_open_positions_summary()
for pos in positions['positions']:
    print(f"{pos['symbol']}: {pos['volume']} lots @ {pos['price_open']:.5f}")
```

### Exemplo 3: Obter Preço Atual
```python
price = await integration.get_symbol_price("EURUSD")
print(f"Bid: {price['bid']:.5f}, Ask: {price['ask']:.5f}")
```

### Exemplo 4: Executar Compra
```python
result = await integration.execute_buy_order(
    symbol="EURUSD",
    volume=0.1,
    sl=1.0800,
    tp=1.0950
)
if result['status'] == 'success':
    print(f"✅ Ordem: {result['order']}")
else:
    print(f"❌ Erro: {result['message']}")
```

### Exemplo 5: Fechar Posição
```python
result = await integration.close_position(ticket=123456)
if result['status'] == 'success':
    print(f"✅ Posição fechada @ {result['price']:.5f}")
else:
    print(f"❌ Erro: {result['message']}")
```

## 🔗 Integração com Chatbot Existente

Para integrar com o chatbot existente (`src/chatbot/client.py`):

```python
from chatbot.mt5_integration import ChatbotMT5Integration

class TradingChatbot:
    def __init__(self, config):
        # ... código existente ...
        self.mt5_integration = ChatbotMT5Integration()
    
    async def _execute_trading_command(self, intent):
        # ... código existente ...
        
        if action.lower() == "buy":
            result = await self.mt5_integration.execute_buy_order(
                symbol=symbol,
                volume=volume,
                sl=sl,
                tp=tp
            )
            return result
```

## 📈 Próximos Passos

1. ✅ **Integração Básica** (Concluído)
2. 🔄 **Testar com Dados Reais** (Próximo)
3. 📊 **Implementar Agent System** (Fase 2)
4. 🔔 **Adicionar Notificações** (Fase 3)
5. 📈 **Otimizações** (Fase 4)

## 📞 Suporte

- **Documentação Completa**: `docs/CHATBOT_MT5_INTEGRATION.md`
- **Exemplos Práticos**: `example_chatbot_mt5_usage.py`
- **Testes Automatizados**: `test_chatbot_mt5_integration.py`
- **Logs**: Verifique `trading_bot.log`

---

**Pronto para começar?** Execute:
```bash
python test_chatbot_mt5_integration.py
```

**Sucesso!** 🎉
