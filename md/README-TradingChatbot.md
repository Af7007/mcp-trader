# 🤖 Trading Chatbot - IA Conversacional para Trading

Um sistema avançado de chatbot que integra modelos de IA locais (Ollama) com operações reais de trading no MetaTrader 5 através do protocolo MCP (Model Context Protocol).

## 📋 Visão Geral

O Trading Chatbot permite que usuários façam operações de trading através de linguagem natural, usando inteligência artificial para interpretar comandos e executar trades de forma segura e automatizada.

### 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Chatbot Client │    │     MCP Servers │
│   (Flask)       │◄──►│  (AI Logic)     │◄──►│  - MT5 Server   │
│   Port: 3000    │    │                 │    │  - Ollama Server│
└─────────────────┘    └─────────────────┘    │  Ports: 8000/8001│
                                              └─────────────────┘
                                                           ▲
                                                           │
                                              ┌─────────────────┐
                                              │   External APIs  │
                                              │  - MT5 Terminal  │
                                              │  - Ollama AI     │
                                              │  - Models Local  │
                                              └─────────────────┘
```

## 🚀 Recursos Principais

### 💬 Comandos de Trading Natural
- **Compra/Venda**: "comprar 100 EURUSD" ou "vender 0.01 BTCUSD com stop loss 44000"
- **Informações**: "qual meu saldo?" ou "mostrar posições abertas"
- **Análises**: "analisar tendência EURUSD" ou "melhores oportunidades agora"

### 🛡️ Segurança Integrada
- Validação automática de comandos de trading
- Confirmação para operações de alto risco
- Limites de volume e verificações de conta
- Logs detalhados de todas as operações

### 🔧 MCP - Model Context Protocol
- Protocolo padrão para integração com LLMs
- Servidor MT5 completo com 20+ ferramentas
- Servidor Ollama para modelos locais
- Comunicação HTTP eficiente

### 🌐 Interface Web Moderna
- Interface responsiva com design moderno
- Comandos rápidos predefinidos
- Status em tempo real dos sistemas
- Suporte a confirmações visuais

## 📦 Instalação

### Pré-requisitos

1. **Python 3.8+**
2. **MetaTrader 5 Terminal** rodando e logado
3. **Ollama** instalado: https://ollama.ai

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/Af7007/mcp-trader.git
cd mcp-trader

# 2. Instale dependências
pip install -r requirements.txt

# 3. Instale modelos Ollama (opcional)
ollama pull qwen2.5-coder    # Para análise de comandos
ollama pull llama3.1:8b      # Para conversação geral
ollama pull deepseek-r1     # Para análise avançada

# 4. Execute o sistema completo
python main.py
```

### Configuração Avançada

#### Arquivo .env
```env
# MT5 Configuration
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server

# System Configuration
OLLAMA_HOST=http://localhost:11434
MT5_HOST=127.0.0.1
WEB_HOST=0.0.0.0
WEB_PORT=3000
```

## 🖥️ Como Usar

### 1. Iniciar o Sistema
```bash
python main.py
```

### 2. Acessar Interface Web
Abra: http://localhost:3000

### 3. Exemplos de Comandos

```bash
# Ordens de compra/venda
"comprar 100 EURUSD"
"vender 0.01 BTCUSD com stop loss 45000 e take profit 47000"
"comprar EURUSD market 0.02 lots"

# Consultas de conta
"quanto dinheiro tenho na conta?"
"mostrar minhas posições abertas"
"qual o saldo atual?"

# Informações de mercado
"qual o preço atual de GBPUSD?"
"mostrar candles H1 de BTCUSD"
"listar símbolos disponíveis"

# Análises
"analisar tendência do mercado"
"qual a melhor oportunidade de trading agora?"
"prever direção do EURUSD para próxima hora"

# Gerenciamento de ordens
"cancelar ordem 12345"
"mostrar todas as ordens pendentes"
"modificar stop loss da posição EURUSD"
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
mcp-trader/
├── src/
│   ├── core/              # Configurações compartilhadas
│   ├── mcp_mt5/          # Servidor MCP MT5
│   ├── mcp_ollama/       # Servidor MCP Ollama
│   ├── chatbot/          # Lógica do chatbot
│   └── web/              # Interface web Flask
├── tests/                # Testes unitários
├── main.py               # Ponto de entrada principal
├── test_chatbot.py       # Teste do sistema completo
├── fastmcp.json          # Configuração MCP
└── pyproject.toml        # Dependências Python
```

### Servidores Individuais

```bash
# MT5 MCP Server (porta 8000)
python -m fastmcp run fastmcp.json

# Ollama MCP Server (porta 8001)
python -c "from src.mcp_ollama.main import mcp; mcp.run()"

# Web Interface (porta 3000)
python src/web/app.py
```

### Testes

```bash
# Teste completo
python test_chatbot.py

# Teste MCP MT5
python test_mcp.py

# Testes unitários
pytest tests/
```

## 🔧 API Endpoints

### Interface Web

- `GET /` - Interface principal do chatbot
- `POST /api/chatbot/initialize` - Inicializar chatbot
- `POST /api/chat` - Enviar mensagem
- `POST /api/chat/confirm` - Confirmar operação
- `GET /api/chatbot/status` - Status dos sistemas

### MCP Servers

#### MT5 Server (porta 8000)
- `initialize(path)` - Iniciar terminal MT5
- `login(login, password, server)` - Login conta
- `get_account_info()` - Informações da conta
- `buy_market(symbol, volume, sl, tp)` - Ordem market buy
- `sell_market(symbol, volume, sl, tp)` - Ordem market sell
- `positions_get()` - Posições abertas
- `orders_get()` - Ordens pendentes

#### Ollama Server (porta 8001)
- `chat_completion(model, messages)` - Chat com LLM
- `analyze_trading_intent(message)` - Analisar intenção
- `pull_model(model_name)` - Baixar modelo
- `get_available_models()` - Listar modelos

## 📊 Comandos Suportados

### 💰 Operações de Trading
| Comando | Exemplo | Descrição |
|---------|---------|-----------|
| `buy` | "comprar 100 EURUSD" | Ordem de compra |
| `sell` | "vender 0.01 BTCUSD sl 44000" | Ordem de venda |
| `long` | "ir long em EURUSD" | Posição comprada |
| `short` | "ir short em GBPUSD" | Posição vendida |

### 📈 Consultas de Informações
| Comando | Exemplo | Descrição |
|---------|---------|-----------|
| `balance` | "qual meu saldo?" | Saldo da conta |
| `positions` | "minhas posições" | Posições abertas |
| `orders` | "mostrar ordens" | Ordens pendentes |
| `price` | "preço de BTCUSD" | Preço atual |

### 🎯 Análises e Previsões
| Comando | Exemplo | Descrição |
|---------|---------|-----------|
| `analyze` | "analisar EURUSD" | Análise técnica |
| `predict` | "prever BTCUSD" | Previsão de preço |
| `trend` | "tendência do mercado" | Análise de tendência |
| `opportunity` | "melhores oportunidades" | Oportunidades de trade |

## 🛡️ Segurança e Validação

### Verificações Automáticas
- **Volume máximo** para prevenir perdas grandes
- **Stop Loss obrigatório** para todas as posições
- **Confirmação manual** para operações > 1 lote
- **Validação de símbolos** disponíveis
- **Verificação de saldo** suficiente

### Logs de Segurança
- Todas as operações são registradas
- Tentativas suspeitas são sinalizadas
- Histórico completo de conversação
- Alertas para padrões de risco

## 🔍 Monitoramento e Logs

### Arquivos de Log
- `trading_chatbot.log` - Logs principais do sistema
- `mt5_operations.log` - Operações de trading
- `ollama_requests.log` - Requisições à IA

### Monitoramento em Tempo Real
- Status dos servidores MCP
- Conectividade MT5 e Ollama
- Taxa de resposta do chatbot
- Contadores de operações

## 🚀 Deploy e Produção

### Configuração para Produção
```bash
# Usar Gunicorn para Flask
pip install gunicorn
gunicorn --bind 0.0.0.0:3000 --workers 4 src.web.app:create_app()

# Usar PM2 para gerenciar processos
npm install -g pm2
pm2 start ecosystem.config.js
```

### Docker (opcional)
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000 8000 8001

CMD ["python", "main.py"]
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/novo-comando`)
3. Commit suas mudanças (`git commit -am 'Adiciona novo comando'`)
4. Push para a branch (`git push origin feature/novo-comando`)
5. Abra um Pull Request

### Áreas de Contribuição
- Novos comandos de trading
- Melhorias na análise de intenção
- Interface web avançada
- Suporte a mais indicadores
- Documentação adicional

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

- **Issues**: https://github.com/Af7007/mcp-trader/issues
- **Documentação**: Consulte os arquivos em `docs/`
- **Exemplos**: Veja `test_chatbot.py` para exemplos de uso

## 🙏 Agradecimentos

- **FastMCP**: Framework MCP para Python
- **Ollama**: Plataforma de IA local
- **MetaTrader 5**: Plataforma de trading
- **Comunidade Open Source**: Por ferramentas e bibliotecas

---

**⚠️ Disclaimer**: Este software é para fins educacionais. Trading envolve riscos financeiros. Use por sua conta e risco. Sempre implemente suas próprias validações de segurança antes do uso em produção.
