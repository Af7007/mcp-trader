# 🚀 Início Manual - Passo a Passo

Se o script automático não funcionar, siga estes passos:

## ✅ Pré-requisitos

1. MetaTrader 5 aberto e logado
2. Ollama rodando (deve estar rodando em segundo plano)

---

## 📋 Opção 1: Usando `uv run` (Recomendado)

Abra **3 janelas PowerShell** separadas:

### Janela 1 - MT5 MCP Server
```powershell
cd C:\mcp-trader
uv run python start_mt5_http.py
```

Aguarde ver:
```
🚀 Iniciando MT5 MCP Server em modo HTTP
📡 Transport: HTTP
🌐 Host: 127.0.0.1
🔌 Port: 8000
```

### Janela 2 - Web Dashboard
```powershell
cd C:\mcp-trader
uv run python run_simple_web.py
```

Aguarde ver:
```
🚀 SERVIDOR WEB SIMPLES INICIANDO...
🌐 Acesse: http://localhost:3000/test
```

### Janela 3 - Worker (Opcional)
```powershell
cd C:\mcp-trader
uv run python src\core\main.py
```

---

## 📋 Opção 2: Direto com Python

Se você já tem o Python no PATH:

### Janela 1
```powershell
cd C:\mcp-trader
python start_mt5_http.py
```

### Janela 2
```powershell
cd C:\mcp-trader
python run_simple_web.py
```

### Janela 3
```powershell
cd C:\mcp-trader
python src\core\main.py
```

---

## 🌐 Acessar o Dashboard

Depois que todos os serviços iniciarem, abra seu navegador em:

```
http://localhost:3000
```

Ou teste primeiro em:
```
http://localhost:3000/test
```

---

## ✅ Verificar se Está Funcionando

```powershell
# Ver portas ativas
netstat -an | findstr "LISTENING" | findstr ":3000 :8000 :11434"
```

Você deve ver:
- `:3000` - Web Dashboard
- `:8000` - MT5 MCP Server
- `:11434` - Ollama

---

## 🛑 Parar Tudo

Pressione `Ctrl+C` em cada janela PowerShell

Ou mate todos os processos:
```powershell
taskkill /F /IM python.exe
```

---

## 🔧 Troubleshooting

### Erro: "uv: command not found"

**Solução 1**: Instale o uv
```powershell
pip install uv
```

**Solução 2**: Use Python direto
```powershell
python start_mt5_http.py
```

### Erro: "No module named 'mcp_mt5'"

Execute:
```powershell
cd C:\mcp-trader
uv sync
```

### Porta já está em uso

Encontre e mate o processo:
```powershell
# Para porta 3000
netstat -ano | findstr :3000
taskkill /F /PID <numero_do_pid>

# Para porta 8000
netstat -ano | findstr :8000
taskkill /F /PID <numero_do_pid>
```

---

## 💡 Dica

Mantenha as 3 janelas abertas para ver os logs em tempo real!
