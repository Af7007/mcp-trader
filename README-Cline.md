# Configuração do MCP MetaTrader 5 com Cline

Este documento explica como configurar o servidor MCP MetaTrader 5 para funcionar com o Cline.

## 📋 Pré-requisitos

1. **MetaTrader 5** instalado e em execução
2. **Python 3.8+** com as dependências instaladas
3. **Node.js 16+** para o wrapper JavaScript
4. **Cline** configurado para usar MCP

## 🚀 Configuração Rápida

### 1. Instalar Dependências

```bash
# Instalar dependências Python
uv sync

# Ou instalar manualmente
pip install metatrader5 pandas pydantic python-dotenv
```

### 2. Configurar Arquivo de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais MT5:

```env
MT5_PATH="C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_LOGIN=123456
MT5_PASSWORD="your_password"
MT5_SERVER="YourBroker-Demo"
```

### 3. Configurar Cline

No Cline, adicione a seguinte configuração MCP:

```json
{
  "mcpServers": {
    "mt5": {
      "command": "node",
      "args": ["/caminho/para/mcp-trader/build/index.js"],
      "cwd": "/caminho/para/mcp-trader"
    }
  }
}
```

### 4. Executar o Servidor

```bash
# Método 1: Usando o wrapper Node.js
node build/index.js

# Método 2: Usando uv (recomendado)
uv run node build/index.js

# Método 3: Desenvolvimento direto
uv run python src/mcp_mt5/main.py
```

## 🛠️ Estrutura do Projeto

```
mcp-trader/
├── build/
│   └── index.js          # Wrapper Node.js para Cline
├── src/
│   ├── core/
│   │   ├── mt5_connection.py  # Conexão direta com MT5
│   │   ├── config.py          # Configurações
│   │   └── exceptions.py      # Exceções personalizadas
│   └── mcp_mt5/
│       └── main.py            # Servidor MCP principal
├── package.json           # Configuração Node.js
├── mcp-config.json        # Configuração MCP para Cline
└── README-Cline.md        # Este arquivo
```

## 🔧 Funcionalidades Disponíveis

### 🤖 **MLP Bot**
- `mlp/health` - Verificar status do bot
- `mlp/start` - Iniciar bot MLP
- `mlp/stop` - Parar bot MLP
- `mlp/execute` - Executar sinal de trading
- `mlp/analyze` - Análise automática de mercado
- `mlp/train` - Treinar modelo ML
- `mlp/performance` - Relatório de performance

### 💰 **Trading**
- `order_send` - Enviar ordens de trading
- `order_check` - Verificar ordens
- `positions_get` - Obter posições abertas
- `orders_get` - Obter ordens ativas
- `history_orders_get` - Histórico de ordens
- `history_deals_get` - Histórico de deals

### 📊 **Dados de Mercado**
- `get_symbols` - Lista de símbolos disponíveis
- `get_symbol_info` - Informações de símbolo
- `get_symbol_info_tick` - Dados de tick
- `copy_rates_*` - Dados de candles OHLC
- `copy_ticks_*` - Dados de ticks

### 🔧 **Sistema**
- `initialize` - Inicializar conexão MT5
- `login` - Login na conta MT5
- `shutdown` - Encerrar conexão
- `get_account_info` - Informações da conta
- `get_terminal_info` - Informações do terminal
- `get_version` - Versão do MT5

## 📝 Exemplo de Uso

```javascript
// No Cline, você pode usar:
await cline_mcp_mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe");
await cline_mcp_mt5.login(123456, "password", "broker-server");

// Obter dados de mercado
const symbols = await cline_mcp_mt5.get_symbols();
const account = await cline_mcp_mt5.get_account_info();

// Análise de dados
const rates = await cline_mcp_mt5.copy_rates_from_pos("EURUSD", 60, 0, 10);
```

## 🔍 Troubleshooting

### Erro: "Cannot find module fastmcp"
```bash
# Instalar dependências
uv sync
```

### Erro: "MT5 initialization failed"
- Verifique se o MetaTrader 5 está em execução
- Confirme se o caminho em MT5_PATH está correto
- Certifique-se que o terminal MT5 permite conexões via API

### Erro: "MT5 login failed"
- Verifique suas credenciais no arquivo .env
- Confirme se a conta está ativa e o servidor está correto

### Cline não conecta
- Verifique se o caminho para build/index.js está correto na configuração do Cline
- Certifique-se que o Node.js está instalado
- Reinicie o Cline após alterações na configuração

## 📚 Recursos Adicionais

- [Documentação MCP](https://modelcontextprotocol.io/)
- [Documentação MetaTrader 5 Python](https://www.mql5.com/en/docs/python_metatrader5)
- [Guia de Trading](docs/trading_guide.md)
- [Referência da API](docs/api_reference.md)

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs do servidor
2. Confirme se o MetaTrader 5 está rodando
3. Teste a conexão básica com `uv run python test_mcp.py`
4. Verifique as configurações no arquivo .env

---

**Nota**: Este servidor MCP fornece acesso direto ao MetaTrader 5 via Python, substituindo conexões via API por conexões diretas mais eficientes e confiáveis.
