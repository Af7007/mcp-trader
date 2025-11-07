# ✅ Setup Final - Integração Chatbot ↔ MT5

## 🎯 Solução Definitiva

O problema era que `fastmcp` não pode ser executado como módulo (`-m`). Criei um script que funciona!

---

## ⚡ Passo 1: Instalar Uvicorn

```powershell
pip install uvicorn
```

Ou instale tudo de uma vez:

```powershell
pip install -r requirements.txt
```

---

## 🚀 Passo 2: Iniciar Servidor MT5 MCP

**Terminal 1:**

```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python run_server_http.py
```

Você deve ver:

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     Iniciando MT5 MCP Server em modo HTTP (porta 8000)    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

✅ Módulo MT5 MCP importado com sucesso

🚀 Iniciando servidor...
📍 Listening on http://127.0.0.1:8000

💡 Dica: Deixe este terminal aberto
   Abra outro terminal para executar os testes
```

**Deixe este terminal aberto!**

---

## 🧪 Passo 3: Executar Testes

**Terminal 2:**

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

## 📋 Resumo dos Comandos

### Terminal 1 (Servidor)
```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python run_server_http.py
```

### Terminal 2 (Testes)
```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python test_chatbot_mt5_integration.py
```

### Terminal 3 (Exemplos - Opcional)
```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python example_chatbot_mt5_usage.py
```

---

## ✅ Checklist

- [ ] Executei: `pip install uvicorn`
- [ ] Terminal 1: `python run_server_http.py` rodando
- [ ] Terminal 2: `python test_chatbot_mt5_integration.py` executando
- [ ] Todos os 6 testes passando
- [ ] Mensagem: "Resultado: 6/6 testes passaram"

---

## 🎉 Sucesso!

Se chegou aqui, você tem uma **integração funcional entre Chatbot e MT5**!

---

## 📚 Próximos Passos

1. **Explorar Exemplos**
   ```powershell
   python example_chatbot_mt5_usage.py
   ```

2. **Integrar com Chatbot**
   - Editar: `src/chatbot/client.py`
   - Adicionar: `ChatbotMT5Integration`

3. **Implementar Agent System** (Fase 2)
   - Agent Generator
   - Strategy Engine
   - Agent Manager

4. **Adicionar Notificações** (Fase 3)

---

## 🆘 Troubleshooting

### Erro: "No module named uvicorn"

```powershell
pip install uvicorn
```

### Erro: "Porta 8000 já está em uso"

```powershell
# Encontrar processo
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

### Erro: "Conexão recusada"

1. Verifique se Terminal 1 está rodando
2. Verifique se MT5 Terminal está logado
3. Reinicie o servidor

---

**Dúvidas?** Consulte:
- `START_HERE.md` - Guia para iniciantes
- `TROUBLESHOOTING.md` - Solução de problemas
- `RUN_TESTS.md` - Como executar testes
