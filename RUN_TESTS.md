# 🚀 Como Executar os Testes

## ⚡ Solução Rápida (Recomendada)

### Terminal 1: Iniciar MT5 MCP Server

```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
```

Você deve ver:
```
🚀 FastMCP server running on http://127.0.0.1:8000
```

### Terminal 2: Executar Testes

```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
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

---

## 📋 Passo a Passo Detalhado

### Passo 1: Abrir Terminal 1

```powershell
# Abrir PowerShell
# Navegar para o diretório
cd c:\mcp-trader

# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1
```

### Passo 2: Iniciar Servidor MT5 MCP

```powershell
# Iniciar servidor em modo HTTP
python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
```

**Deixe este terminal aberto!** O servidor precisa continuar rodando.

### Passo 3: Abrir Terminal 2

```powershell
# Abrir novo PowerShell
# Navegar para o diretório
cd c:\mcp-trader

# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1
```

### Passo 4: Executar Testes

```powershell
# Executar testes
python test_chatbot_mt5_integration.py
```

---

## 🔧 Troubleshooting

### Erro: "Porta 8000 já está em uso"

```powershell
# Encontrar processo usando porta 8000
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Tentar novamente
python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
```

### Erro: "fastmcp command not found"

```powershell
# Instalar fastmcp
pip install fastmcp

# Tentar novamente
python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
```

### Erro: "Conexão recusada"

1. Verifique se o Terminal 1 ainda está rodando
2. Verifique se a porta 8000 está aberta
3. Verifique se MT5 Terminal está logado
4. Reinicie o servidor

---

## 📊 Estrutura de Terminais

```
Terminal 1 (Servidor):
├─ python -m fastmcp run src.mcp_mt5.main:mcp --host 127.0.0.1 --port 8000
│  └─ Listening on http://127.0.0.1:8000
│     (deixe rodando)

Terminal 2 (Testes):
├─ python test_chatbot_mt5_integration.py
│  └─ Executar testes
│     (pode fechar após terminar)
```

---

## ✅ Checklist

- [ ] Terminal 1: Servidor MT5 MCP rodando na porta 8000
- [ ] Terminal 2: Testes executando
- [ ] Todos os 6 testes passando
- [ ] Mensagem: "Resultado: 6/6 testes passaram"

---

## 🎉 Sucesso!

Se todos os testes passarem, você tem uma **integração funcional entre Chatbot e MT5**!

**Próximos passos:**
1. Executar exemplos: `python example_chatbot_mt5_usage.py`
2. Integrar com chatbot: `src/chatbot/client.py`
3. Implementar Agent System (Fase 2)

---

**Dúvidas?** Consulte `TROUBLESHOOTING.md` ou `START_HERE.md`
