# 🚀 Como Usar o Trading Chatbot

## 📋 Pré-requisitos

1. ✅ MetaTrader 5 instalado e **ABERTO**
2. ✅ Conta MT5 logada (demo ou real)
3. ✅ Ambiente virtual Python ativado

---

## ⚡ Início Rápido (Mais Fácil)

### Opção 1: Usar o Script Automático

**Simplesmente execute este arquivo:**

```
START_ALL_SERVICES.bat
```

Isso vai:
- ✅ Iniciar MT5 MCP Server (porta 8000)
- ✅ Iniciar Web Dashboard (porta 3000)
- ✅ Iniciar Worker Service (background)
- ✅ Abrir o navegador automaticamente

### Opção 2: Iniciar Manualmente

#### Passo 1: Parar Processos Antigos
```batch
STOP_ALL_SERVICES.bat
```

#### Passo 2: Abrir 3 Janelas PowerShell

**Janela 1 - MT5 MCP Server:**
```powershell
cd C:\mcp-trader
.\.venv\Scripts\Activate.ps1
python start_mt5_http.py
```

**Janela 2 - Web Dashboard:**
```powershell
cd C:\mcp-trader
.\.venv\Scripts\Activate.ps1
python run_simple_web.py
```

**Janela 3 - Worker (Opcional):**
```powershell
cd C:\mcp-trader
.\.venv\Scripts\Activate.ps1
python src\core\main.py
```

#### Passo 3: Acessar o Dashboard
Abra seu navegador em: **http://localhost:3000**

---

## 🌐 URLs dos Serviços

| Serviço | URL | Status |
|---------|-----|--------|
| Web Dashboard | http://localhost:3000 | Principal |
| Admin Panel | http://localhost:3000/admin | Gerenciar agentes |
| Test Page | http://localhost:3000/test | Testar conexão |
| MT5 MCP Server | http://localhost:8000 | API MT5 |
| Health Check | http://localhost:3000/api/health | Status sistema |
| Ollama Service | http://localhost:11434 | IA/LLM |

---

## 🛑 Parar Todos os Serviços

**Opção 1: Usar Script**
```
STOP_ALL_SERVICES.bat
```

**Opção 2: Manual**
```powershell
taskkill /F /IM python.exe
```

---

## ✅ Verificar se Está Funcionando

### 1. Verificar Portas Ativas
```powershell
netstat -an | findstr "LISTENING" | findstr ":3000 :8000 :11434"
```

Você deve ver:
```
TCP    0.0.0.0:3000           LISTENING    # Web Dashboard
TCP    127.0.0.1:8000         LISTENING    # MT5 MCP
TCP    127.0.0.1:11434        LISTENING    # Ollama
```

### 2. Testar Conexões

**Test Web Server:**
```powershell
curl http://localhost:3000/test
```

**Test MT5 MCP Server:**
```powershell
curl http://localhost:8000
```

**Test Ollama:**
```powershell
curl http://localhost:11434/api/version
```

---

## 🔧 Troubleshooting

### Problema: "Porta 3000 já está em uso"
**Solução:**
```powershell
# Encontrar processo na porta 3000
netstat -ano | findstr :3000

# Matar processo (substitua PID)
taskkill /F /PID <PID>
```

### Problema: "MT5 não conecta"
**Verificações:**
1. ✅ MT5 Terminal está aberto?
2. ✅ Está logado em uma conta?
3. ✅ Servidor MT5 está respondendo?

**Teste direto:**
```powershell
python test_mt5_direct.py
```

### Problema: "Dashboard fica carregando"
**Solução:**
1. Pare tudo: `STOP_ALL_SERVICES.bat`
2. Aguarde 5 segundos
3. Inicie novamente: `START_ALL_SERVICES.bat`

### Problema: "Ollama não responde"
**Verificar se está rodando:**
```powershell
curl http://localhost:11434/api/version
```

**Iniciar Ollama:**
```powershell
ollama serve
```

---

## 💡 Dicas

1. **Sempre** abra o MT5 Terminal **ANTES** de iniciar os serviços
2. Use `START_ALL_SERVICES.bat` para facilitar
3. Acesse `/admin` para gerenciar agentes de trading
4. Use `/test` para verificar se tudo está funcionando
5. Mantenha as janelas abertas para ver os logs

---

## 📊 Comandos do Chatbot

Após abrir o dashboard em http://localhost:3000, você pode usar:

### Consultas
- `saldo` - Ver saldo da conta
- `posições` - Ver posições abertas
- `preço EURUSD` - Ver preço de um símbolo

### Operações
- `comprar EURUSD 0.01` - Comprar
- `vender XAUUSD 0.01` - Vender
- `fechar 123456` - Fechar posição por ticket

### Agentes
- `criar agente EURUSD com RSI` - Criar agente
- `listar agentes` - Ver agentes ativos

---

## 🎯 Estrutura dos Serviços

```
┌─────────────────────────────────────────┐
│         Browser (localhost:3000)        │
│           Trading Dashboard             │
└──────────────┬──────────────────────────┘
               │
               ├─────> MT5 MCP Server (8000)
               │         ↓
               │      MetaTrader 5 Terminal
               │
               ├─────> Ollama Service (11434)
               │         ↓
               │      AI Models (LLaMA, etc)
               │
               └─────> Worker Service
                        ↓
                     Database (SQLite)
```

---

## 📝 Próximos Passos

Depois que tudo estiver rodando:

1. ✅ Testar comandos básicos no chat
2. ✅ Criar seu primeiro agente
3. ✅ Configurar stop loss e take profit
4. ✅ Monitorar posições no dashboard
5. ✅ Explorar o admin panel

---

**Precisa de ajuda?** Veja os logs nas janelas do terminal!
