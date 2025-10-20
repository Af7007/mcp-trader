# MCP Trader Server

Servidor MCP (Model Context Protocol) que conecta MetaTrader 5, sistema MLP AI e banco de dados Django em uma interface integrada para chatbots e LLMs.

## 🏗️ Arquitetura

```
Chatbot (Claude/GPT-4) ↔ MCP Server ↔ MT5 + MLP + Database
                                      ^       ^       ^
                                      |       |       |
                              Dados Tempo Real    Predições Inteligentes
```

## 🚀 Instalação

### Requisitos
- Node.js >= 16.0.0
- Acesso aos APIs: MT5 (porta 5000), MLP (porta 5000), Django (porta 5001)

### Instalação
```bash
# Na pasta raíz do projeto
mkdir mcp-trader
cd mcp-trader

# Inicializar projeto
npm init -y

# Instalar dependências
npm install
```

### Arquivos Gerados

Após a instalação, a estrutura ficará:
```
mcp-trader/
├── server.js              ← Servidor MCP principal
├── mt5-connector.js       ← API MetaTrader 5
├── mlp-connector.js       ← Sistema de sinais MLP
├── db-connector.js        ← Banco de dados Django
├── test-client.js         ← Cliente para testes
├── prompts/
│   ├── trading.txt        ← Template para trading
│   └── analysis.txt       ← Template para análise
├── package.json           ← Configurações Node.js
└── README.md             ← Este arquivo
```

## 🛠️ Ferramentas MCP Disponíveis

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `get_market_data` | Dados em tempo real MT5 | `{symbol: 'BTCUSDc'}` |
| `get_mlp_signal` | Sinal atual MLP AI | `{symbol: 'BTCUSDc'}` |
| `get_trade_history` | Histórico de trades | `{limit: 10}` |
| `execute_trade` | Executar trade via MLP | `{signal, symbol, volume}` |
| `get_performance` | Métricas de performance | - |
| `train_mlp_model` | Re-treinar modelo | `{symbols, days}` |
| `get_portfolio` | Status do portfólio | - |
| `get_bot_status` | Status do sistema | - |

## 🎯 Uso com Claude/GPT

### Configuração Básica
```bash
# Executar o servidor MCP
cd mcp-trader
npm start
```

### Comandos de Exemplo no Chat
```
"Qual é o preço atual do BTC?"
"Mostre o sinal de trading do MLP"
"Quais meus últimos 5 trades?"
"Execute uma compra se confiança >80%"
"Como está performando o sistema?"
"Re-treine o modelo com dados dos últimos 15 dias"
```

## 📊 Funcionalidades

### 📈 Monitoramento em Tempo Real
- Preços, volumes e indicadores MT5
- Sinais MLP com análise de confiança
- Posições abertas e P&L

### 🤖 IA Conversacional
- Comandos naturais em português
- Interpretação contextual
- Análise automatizada de tendências

### 💼 Gestão de Portfolio
- Controle de posições ativas
- Métricas de performance
- Balance de conta e margem

### ⚙️ Controle Operacional
- Start/stop do bot MLP
- Ajuste de parâmetros
- Backup de dados

## 🔗 Conectores

### MT5 Connector (`mt5-connector.js`)
- 💰 **API**: `http://localhost:5000` (flask)
- 📊 Dados: Preços, volumes, spreads
- 🛡️ Orders: Buy/sell com TP/SL

### MLP Connector (`mlp-connector.js`)
- 🧠 **API**: `http://localhost:5000` (bot MT5)
- 📈 Sinais: BUY/SELL/HOLD com confiança
- 🔄 Train: Re-treinamento automático

### DB Connector (`db-connector.js`)
- 💾 **API**: `http://localhost:5001` (django)
- 📊 Histórico: Trades, análises, P&L
- 📋 Controle: Configurações do bot

## 📝 Scripts NPM

```json
{
  "start": "node server.js",
  "dev": "node server.js --dev"
}
```

## 🧪 Testes

### Testar Conexões
```bash
# Verificar se MT5 está rodando
curl http://localhost:5000/health

# Verificar MLP system
curl http://localhost:5000/api/mlp/health

# Verificar Django DB
curl http://localhost:5001/quant/dashboard/summary/
```

### Execução Manual
```bash
# Iniciar servidor MCP
npm start

# Testar com ferramentas manuais (opcional)
node -e "
import { MCPTraderServer } from './server.js';
const server = new MCPTraderServer();
server.testConnections();
"
```

## 🔐 Segurança

- ✅ **Thresholds de Confiança**: Trades só acima de 70%
- ✅ **Validação de Sinais**: Verificação múltipla MT5 + MLP
- ✅ **Limites Operacionais**: Máximo 7 posições simultâneas
- ✅ **Timeout de Conexão**: Proteção contra falhas

## 🎨 Prompts Inteligentes (pasta prompts/)

### trading.txt
```
Você é um assistente de trading profissional. Baseado nos dados MT5 e sinais MLP:

DADOS DISPONÍVEIS:
- Preços em tempo real
- Indicadores técnicos (RSI, BB, SMA)
- Sinais MLP com confiança %
- Histórico de performance
- Status do portfólio

DIRETRIZES:
- Seja conservador com recomendações
- Sempre mencione nível de confiança
- Sugira stop loss e take profit
- Considere risco de 1-2% por trade
- Analise tendência de curto a médio prazo
```

## 🚀 Próximas Etapas - Integração Completa

### 1. Chatbot Interface (Streamlit)
```bash
# Criar interface de chatbot
pip install streamlit openai anthropic

# Arquivo: chatbot.py
streamlit run chatbot.py
```

### 2. Claude Desktop Configuration
```json
// Arquivo: ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "mcp-trader": {
      "command": "cd",
      "args": ["/path/to/mcp-trader", "&&", "npm", "start"]
    }
  }
}
```

### 3. Comandos Avançados
```
"Monitore EURUSD com alertas RSI"
"Faca análise técnica completa do BTC"
"Mostre performance dos últimos 30 dias"
"Gere relatório de risco atual"
"Simule trade hipotético"
```

## 📞 Suporte

### Arquivos do Sistema Completo:
- `/mcp-trader/` ← **SERVIDOR MCP** (pasta isolada)
- `/bot_mt5_direct.py` ← Bot Python MT5
- `/django_server/` ← Dashboard e histórico
- `/mlp_dashboard_mql5.mq5` ← Expert Advisor colorido

### Verificação de Saúde:
```bash
# Testar MCP server
cd mcp-trader && npm test

# Verificar APIs
start_final.cmd status

# Monitorar logs
tail -f bot_mt5_direct.py.log
```

---

## 🎯 Resumo do Sistema

**MetaTrader MLP Trading System** é uma solução completa que combina:

### Backend:
- **MT5 + Python**: Execução e análise técnica
- **TensorFlow/SCIKIT**: Modelos de IA MLP treinados
- **Django Rest**: Gestão de dados e histórico
- **Flask API**: Conectividade com MT5

### Frontend:
- **MCP Server**: Protocolo para LLMs
- **Expert Advisor**: Interface MT5 colorizada
- **Dashboard Web**: Controle e visualização
- **Chatbot**: Interface conversacional

**🤖 Resultado**: Sistema de trading automatizado inteligente com controle total através de comandos naturais em português!

---

*"O futuro do trading: IA + Automação + Controle Conversacional"* ⚡📈
