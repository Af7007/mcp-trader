# ✅ TESTE A CONEXÃO DIRETA COM MT5

## 🎯 Nova Arquitetura Simplificada

O sistema agora usa **CONEXÃO DIRETA** com o MetaTrader 5!

- ✅ **Sem MCP Server HTTP** - Não precisa rodar `start_mt5_http.py`
- ✅ **Mais Simples** - Menos componentes para gerenciar
- ✅ **Mais Rápido** - Sem overhead de HTTP
- ✅ **Menos Erros** - Sem problemas de endpoint/protocolo

## 📋 Teste Agora (2 minutos)

### ✅ Pré-requisito
- MetaTrader 5 **ABERTO** e **LOGADO**

---

### Passo 1: Teste a Conexão

```powershell
cd C:\mcp-trader
uv run python test_mt5_connection.py
```

✅ **Você deve ver:**
```
============================================================
🧪 TESTANDO CONEXÃO DIRETA COM MT5
============================================================

[1/6] Verificando conexão direta com MT5...
    ✅ Cliente conectado ao MT5 Terminal

[2/6] Verificando versão do MT5...
    ✅ MT5 versão: (5, 0, 3930)

[3/6] Obtendo informações da conta...
    ✅ Conta: 12345678
    💰 Saldo: $10,000.00
    📊 Equity: $10,000.00
    📈 Margem Livre: $10,000.00

[4/6] Verificando posições abertas...
    ✅ Posições abertas: 0
       Nenhuma posição aberta no momento

[5/6] Listando símbolos disponíveis...
    ✅ 50 símbolos disponíveis
    Exemplos: EURUSD, GBPUSD, USDJPY, AUDUSD, XAUUSD

[6/6] Testando informações de símbolo (EURUSD)...
    ✅ EURUSD:
       Bid: 1.08500
       Ask: 1.08510
       Spread: 10 points
       Volume: 0.01 - 100.0

============================================================
✅ TESTE CONCLUÍDO COM SUCESSO!
============================================================
```

---

### Passo 2: Inicie o Web Dashboard

```powershell
# Em NOVA janela PowerShell
cd C:\mcp-trader
uv run python run_simple_web.py
```

---

### Passo 3: Inicie o Worker (Opcional)

```powershell
# Em NOVA janela PowerShell
cd C:\mcp-trader
uv run python src\core\main.py
```

✅ **Agora NÃO deve ter erro 406!**

Deve ver:
```
🚀 Iniciando Worker de Trading em segundo plano...
✅ MT5 inicializado com sucesso via conexão direta
Verificando trades abertos...
Nenhum trade aberto para monitorar.
Ciclo do worker concluído. Aguardando 60 segundos...
```

---

### Passo 4: Acesse o Dashboard

```
http://localhost:3000
```

---

## 🎉 Vantagens da Nova Arquitetura

### Antes (com MCP Server HTTP)
```
Web App ──→ HTTP ──→ MCP Server ──→ MT5 Terminal
Worker ───→ HTTP ──→ MCP Server ──→ MT5 Terminal
              ❌ Erro 404/406
```

### Agora (Conexão Direta)
```
Web App ──→ MT5Client ──→ MT5 Terminal  ✅
Worker ───→ MT5Client ──→ MT5 Terminal  ✅
                Singleton (mesma instância)
```

---

## 📊 Componentes Ativos

| Componente | Status | Porta | Necessário? |
|-----------|--------|-------|-------------|
| MT5 Terminal | ✅ Obrigatório | - | Sim |
| Web Dashboard | ✅ Rodando | 3000 | Sim |
| Worker | ✅ Rodando | - | Opcional |
| MCP HTTP Server | ❌ Não usado | 8000 | Não* |

**Nota**: MCP Server HTTP só é necessário para integração com Claude Desktop ou outros clientes MCP externos.

---

## 🔧 Se Algo Der Errado

### Erro: "MT5 initialization failed"
**Solução**: Abra o MetaTrader 5 e faça login

### Erro: "Module 'MetaTrader5' not found"
**Solução**:
```powershell
uv sync
```

### Worker ainda mostra erro
**Solução**: Certifique-se que parou o Worker antigo:
```powershell
taskkill /F /IM python.exe
```

E inicie novamente:
```powershell
uv run python src\core\main.py
```

---

## 🚀 Inicialização Rápida (Script Automático)

Criei um script que inicia tudo automaticamente:

```batch
START_SERVICES_DIRECT.bat
```

Este script:
1. Para todos os processos Python antigos
2. Inicia o Web Dashboard
3. Inicia o Worker
4. Abre o navegador

---

## 📝 Comandos para Testar no Dashboard

Após acessar http://localhost:3000:

```
saldo
posições
preço EURUSD
comprar EURUSD 0.01
vender GBPUSD 0.01
listar agentes
```

---

## ✅ Checklist de Sucesso

- [ ] MT5 Terminal aberto e logado
- [ ] Teste de conexão passou (6/6 testes)
- [ ] Web Dashboard rodando (porta 3000)
- [ ] Worker rodando SEM erro 406
- [ ] Dashboard acessível no navegador
- [ ] Comandos funcionando no chat

---

**Tudo pronto! Sistema funcionando com conexão direta!** 🎉
