# 🚀 COMECE AQUI - Iniciar o Sistema

## ⚡ Solução Rápida (5 minutos)

Você recebeu o erro: **"Não foi possível conectar ao servidor MT5"**

Isso significa que o **servidor MT5 MCP não está rodando**. Siga estes passos:

### Passo 1: Abra 3 Terminais (PowerShell/CMD)

**Terminal 1 - MT5 MCP Server:**
```bash
cd c:\mcp-trader
python src/mcp_mt5/main.py
```

Você deve ver:
```
INFO - MT5 MCP Server iniciado
INFO - Listening on http://localhost:8000
```

**Terminal 2 - Ollama MCP Server:**
```bash
cd c:\mcp-trader
python src/mcp_ollama/main.py
```

Você deve ver:
```
INFO - Ollama MCP Server iniciado
INFO - Listening on http://localhost:8001
```

**Terminal 3 - Testes:**
```bash
cd c:\mcp-trader
python test_chatbot_mt5_integration.py
```

### Passo 2: Verificar Pré-requisitos

Antes de executar, certifique-se de:

- ✅ **MetaTrader 5 está rodando**
  - Abra o MT5
  - Faça login com suas credenciais
  - Aguarde carregar completamente

- ✅ **Ollama está instalado** (opcional para testes básicos)
  - Visite https://ollama.ai
  - Instale para seu SO
  - Execute: `ollama serve` em outro terminal

- ✅ **Python 3.8+** está instalado
  - Verifique: `python --version`

### Passo 3: Instalar Dependências (se necessário)

```bash
cd c:\mcp-trader
pip install -r requirements.txt
```

Se não houver `requirements.txt`, instale manualmente:

```bash
pip install MetaTrader5 requests aiohttp pydantic pandas fastmcp
```

---

## 🎯 Fluxo Completo (Recomendado)

### 1. Diagnóstico do Sistema
```bash
python diagnose_system.py
```

Isso verifica:
- ✅ MT5 Terminal
- ✅ Ollama Service
- ✅ Servidores MCP
- ✅ Banco de dados
- ✅ Pacotes Python

### 2. Iniciar Sistema Completo
```bash
python start_system.py
```

Isso inicia automaticamente:
- MT5 MCP Server (porta 8000)
- Ollama MCP Server (porta 8001)
- Web Interface (porta 3000)
- Worker em segundo plano

### 3. Testar Integração
```bash
python test_chatbot_mt5_integration.py
```

Esperado:
```
✅ PASSOU: Conexão
✅ PASSOU: Informações da Conta
✅ PASSOU: Posições Abertas
✅ PASSOU: Validação de Símbolos
✅ PASSOU: Preços de Símbolos
✅ PASSOU: Dados de Mercado
Resultado: 6/6 testes passaram
```

### 4. Executar Exemplos
```bash
python example_chatbot_mt5_usage.py
```

### 5. Acessar Interface Web
Abra seu navegador:
```
http://localhost:3000
```

---

## 🔧 Troubleshooting Rápido

### Erro: "Não foi possível conectar ao servidor MT5"

**Solução:**
1. Abra MT5 e faça login
2. Execute em um terminal: `python src/mcp_mt5/main.py`
3. Aguarde 2-3 segundos
4. Execute os testes novamente

### Erro: "Porta 8000 já está em uso"

**Solução:**
```bash
# Encontrar processo
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Tentar novamente
python src/mcp_mt5/main.py
```

### Erro: "MetaTrader5 não está instalado"

**Solução:**
```bash
pip install MetaTrader5
```

### Erro: "Ollama não está rodando"

**Solução:**
```bash
# Em outro terminal
ollama serve

# Se não tiver Ollama instalado
# Visite: https://ollama.ai
```

---

## 📋 Estrutura de Diretórios

```
c:\mcp-trader\
├── src/
│   ├── chatbot/
│   │   ├── client.py                    (Chatbot)
│   │   └── mt5_integration.py           ✨ NOVO
│   ├── core/
│   │   ├── mt5_connector.py             ✨ NOVO
│   │   ├── main.py                      (Worker)
│   │   └── database.py                  (DB)
│   └── mcp_mt5/
│       └── main.py                      (MT5 MCP Server)
│
├── test_chatbot_mt5_integration.py      ✨ NOVO
├── example_chatbot_mt5_usage.py         ✨ NOVO
├── start_system.py                      ✨ NOVO
├── diagnose_system.py                   ✨ NOVO
├── QUICK_START.md                       ✨ NOVO
├── TROUBLESHOOTING.md                   ✨ NOVO
└── START_HERE.md                        ✨ NOVO (este arquivo)
```

---

## 🎓 Próximos Passos

### Após Verificar Conexão

1. **Integrar com Chatbot Existente**
   - Editar: `src/chatbot/client.py`
   - Adicionar: `ChatbotMT5Integration`
   - Testar: `python test_chatbot.py`

2. **Implementar Agent System** (Fase 2)
   - Agent Generator
   - Strategy Engine
   - Agent Manager

3. **Adicionar Notificações** (Fase 3)
   - Email
   - Webhook
   - WebSocket

---

## 📊 Comandos Úteis

```bash
# Diagnóstico
python diagnose_system.py

# Iniciar sistema completo
python start_system.py

# Testar integração
python test_chatbot_mt5_integration.py

# Ver exemplos
python example_chatbot_mt5_usage.py

# Iniciar servidores individuais
python src/mcp_mt5/main.py
python src/mcp_ollama/main.py
python src/web/app.py
python src/core/main.py

# Iniciar Ollama
ollama serve

# Verificar portas
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :3000
```

---

## 🆘 Precisa de Ajuda?

1. **Consulte Troubleshooting**
   ```bash
   cat TROUBLESHOOTING.md
   ```

2. **Verifique Logs**
   ```bash
   type trading_bot.log
   ```

3. **Execute Diagnóstico**
   ```bash
   python diagnose_system.py
   ```

4. **Veja Exemplos**
   ```bash
   python example_chatbot_mt5_usage.py
   ```

---

## ✅ Checklist

- [ ] MT5 Terminal está rodando e logado
- [ ] Python 3.8+ está instalado
- [ ] Dependências estão instaladas (`pip install -r requirements.txt`)
- [ ] Executei `python diagnose_system.py` com sucesso
- [ ] Iniciei `python src/mcp_mt5/main.py`
- [ ] Executei `python test_chatbot_mt5_integration.py` com sucesso
- [ ] Todos os 6 testes passaram
- [ ] Acessei `http://localhost:3000` no navegador

---

## 🎉 Pronto!

Se chegou até aqui e todos os testes passaram, **parabéns!** 🎊

Você tem uma **integração funcional entre Chatbot e MT5**.

**Próximo passo**: Implementar o Agent System para criar agentes de trading automáticos!

---

**Última atualização**: 2024-01-15  
**Status**: ✅ Pronto para começar
