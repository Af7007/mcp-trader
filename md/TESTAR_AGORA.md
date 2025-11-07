# 🚀 TESTE A NOVA ARQUITETURA MCP AGORA!

## ✅ O Que Foi Criado

1. **Cliente MCP Centralizado** - Uma única conexão com MT5
2. **Worker Atualizado** - Usa o novo cliente MCP
3. **Web App Atualizado** - Usa o novo cliente MCP
4. **Script de Teste** - Valida a conexão MCP

---

## 📋 Passo a Passo (5 minutos)

### ✅ Pré-requisito
- MetaTrader 5 **ABERTO** e **LOGADO**

---

### Passo 1: Parar Tudo que Está Rodando

```batch
STOP_ALL_SERVICES.bat
```

Ou manualmente:
```powershell
taskkill /F /IM python.exe
```

---

### Passo 2: Iniciar o MT5 MCP Server

Abra **PowerShell** e execute:

```powershell
cd C:\mcp-trader
uv run python start_mt5_http.py
```

✅ **Aguarde ver:**
```
🚀 Iniciando MT5 MCP Server em modo HTTP
📡 Transport: HTTP
🌐 Host: 127.0.0.1
🔌 Port: 8000
⚠️  IMPORTANTE: Certifique-se que o MT5 Terminal está aberto!
```

**Deixe esta janela ABERTA!**

---

### Passo 3: Testar a Conexão MCP

Abra **OUTRA janela PowerShell** e execute:

```powershell
cd C:\mcp-trader
uv run python test_mcp_connection.py
```

✅ **Você deve ver 6 testes passando:**
```
🧪 TESTANDO CONEXÃO COM MT5 MCP SERVER
[1/6] Testando Health Check...
    ✅ Health: {'status': 'ok', ...}
[2/6] Verificando conexão...
    ✅ Cliente conectado ao MCP server
[3/6] Obtendo informações da conta...
    ✅ Conta: 12345678
    💰 Saldo: $10,000.00
    📊 Equity: $10,000.00
[4/6] Verificando posições abertas...
    ✅ Posições abertas: 0
[5/6] Listando símbolos disponíveis...
    ✅ 50 símbolos disponíveis
[6/6] Testando informações de símbolo (EURUSD)...
    ✅ EURUSD:
       Bid: 1.08500
       Ask: 1.08510

✅ TESTE CONCLUÍDO COM SUCESSO!
```

---

### Passo 4: Iniciar o Web Dashboard

Abra **OUTRA janela PowerShell** e execute:

```powershell
cd C:\mcp-trader
uv run python run_simple_web.py
```

✅ **Aguarde ver:**
```
🚀 SERVIDOR WEB SIMPLES INICIANDO...
🌐 Acesse: http://localhost:3000/test
```

---

### Passo 5: Iniciar o Worker (Opcional)

Abra **OUTRA janela PowerShell** e execute:

```powershell
cd C:\mcp-trader
uv run python src\core\main.py
```

✅ **Agora você NÃO deve ver o erro 406!**

Deve ver algo como:
```
🚀 Iniciando Worker de Trading em segundo plano...
Verificando trades abertos...
Nenhum trade aberto para monitorar.
Analisando mercado por novas oportunidades...
Ciclo do worker concluído. Aguardando 60 segundos...
```

---

### Passo 6: Acessar o Dashboard

Abra seu navegador em:
```
http://localhost:3000
```

---

## 🎯 O Que Você Deve Ver Agora

### ✅ MT5 MCP Server (Janela 1)
- Rodando na porta 8000
- Recebendo requisições
- Sem erros

### ✅ Worker (Janela 3)
- **SEM erro 406!**
- Conectando via MCP
- Monitorando trades

### ✅ Web Dashboard (Janela 2)
- Rodando na porta 3000
- Respondendo
- Conectado ao MT5 via MCP

### ✅ Navegador
- Dashboard funcionando
- Comandos funcionando
- Conectado aos serviços

---

## 🔧 Se Algo Der Errado

### Erro no Passo 2: "MT5 initialization failed"
**Solução**: Abra o MetaTrader 5 e faça login

### Erro no Passo 3: "Connection refused"
**Solução**: Volte ao Passo 2 e verifique se o servidor está rodando

### Erro no Passo 5: Ainda aparece erro 406
**Possível causa**: Servidor MT5 não está em modo HTTP
**Solução**:
1. Pare o servidor (Ctrl+C na janela 1)
2. Execute novamente: `uv run python start_mt5_http.py`

---

## 📊 Resumo das Janelas

Você deve ter **3 ou 4 janelas PowerShell** abertas:

1. **MT5 MCP Server** - `start_mt5_http.py` - Porta 8000
2. **Web Dashboard** - `run_simple_web.py` - Porta 3000
3. **Worker** (opcional) - `src\core\main.py` - Background
4. **Testes** (quando rodar) - `test_mcp_connection.py`

---

## 🎉 Sucesso!

Se todos os passos funcionaram:
- ✅ Cliente MCP centralizado funcionando
- ✅ Worker sem erro 406
- ✅ Dashboard conectado ao MT5
- ✅ Tudo usando UMA ÚNICA conexão MT5

---

## 📝 Próximos Comandos para Testar

No dashboard (http://localhost:3000), teste:

```
saldo
posições
comprar EURUSD 0.01
listar agentes
```

---

**Agora você tem uma arquitetura MCP centralizada funcionando!** 🚀
