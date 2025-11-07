# 🤖 Chatbot com Agent Manager - Guia Completo

## Como Usar

### Iniciar Chatbot

```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python run_chatbot_manager.py
```

---

## 📋 Comandos Disponíveis

### 1️⃣ Informações da Conta

```
💬 Você: saldo
   ✅ Saldo: $1120.17
   ✅ Equity: $1120.17
   ✅ Margem Livre: $1120.17

💬 Você: posições
   ✅ Nenhuma posição aberta
```

### 2️⃣ Dados de Mercado

```
💬 Você: preço EURUSD
   ✅ EURUSDc:
      Bid: 1.16100
      Ask: 1.16108
```

### 3️⃣ Criar Agentes

```
💬 Você: criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1
   ✅ Agente criado com sucesso!
      Nome: XAUUSDm_RSI_20251022_173435
      ID: 7e50f893
      Símbolo: XAUUSDm
      Volume: 0.1
      TP: $3.0, SL: $1.0
      Indicadores: ['RSI']

💬 Você: criar agente EURUSD com Bollinger Bands, TP $2, SL $0.5, volume 0.05
   ✅ Agente criado com sucesso!
      Nome: EURUSDc_BOLLINGER_20251022_173435
      ID: a1b2c3d4
      Símbolo: EURUSDc
      Volume: 0.05
      TP: $2.0, SL: $0.5
      Indicadores: ['BOLLINGER']
```

### 4️⃣ Listar Agentes

```
💬 Você: listar agentes
   ✅ 2 agente(s) criado(s):
      • XAUUSDm_RSI_20251022_173435 (7e50f893)
        Status: active
      • EURUSDc_BOLLINGER_20251022_173435 (a1b2c3d4)
        Status: active
```

### 5️⃣ Gerenciar Worker

```
💬 Você: iniciar worker
   ✅ Worker iniciado

💬 Você: parar worker
   ✅ Worker parado
```

### 6️⃣ Controlar Agentes

```
💬 Você: pausar agente 7e50f893
   ✅ Agente 7e50f893 pausado

💬 Você: retomar agente 7e50f893
   ✅ Agente 7e50f893 retomado

💬 Você: parar agente 7e50f893
   ✅ Agente 7e50f893 parado

💬 Você: deletar agente 7e50f893
   ✅ Agente 7e50f893 deletado
```

### 7️⃣ Ver Estatísticas

```
💬 Você: stats agente 7e50f893
   ✅ Estatísticas de 7e50f893:
      Status: active
      Trades abertos: 2
      Trades fechados: 1
      Lucro total: $3.50
      Uptime: 3600s

💬 Você: resumo
   ✅ Resumo do Sistema:
      Total de agentes: 2
      Ativos: 1
      Pausados: 1
      Parados: 0
      Total de trades: 3
      Lucro total: $5.50
      Worker: Rodando
```

---

## 🎯 Fluxo Completo de Exemplo

```
💬 Você: criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1
   ✅ Agente criado com sucesso!
      ID: 7e50f893

💬 Você: criar agente EURUSD com MA 50, TP $2, SL $0.5, volume 0.05
   ✅ Agente criado com sucesso!
      ID: a1b2c3d4

💬 Você: listar agentes
   ✅ 2 agente(s) criado(s):
      • XAUUSDm_RSI_20251022_173435 (7e50f893)
        Status: active
      • EURUSDc_MA_20251022_173435 (a1b2c3d4)
        Status: active

💬 Você: iniciar worker
   ✅ Worker iniciado

💬 Você: resumo
   ✅ Resumo do Sistema:
      Total de agentes: 2
      Ativos: 2
      Total de trades: 0
      Lucro total: $0.00
      Worker: Rodando

💬 Você: stats agente 7e50f893
   ✅ Estatísticas de 7e50f893:
      Status: active
      Trades abertos: 0
      Trades fechados: 0
      Lucro total: $0.00
      Uptime: 45s

💬 Você: pausar agente 7e50f893
   ✅ Agente 7e50f893 pausado

💬 Você: listar agentes
   ✅ 2 agente(s) criado(s):
      • XAUUSDm_RSI_20251022_173435 (7e50f893)
        Status: paused
      • EURUSDc_MA_20251022_173435 (a1b2c3d4)
        Status: active

💬 Você: retomar agente 7e50f893
   ✅ Agente 7e50f893 retomado

💬 Você: parar worker
   ✅ Worker parado

💬 Você: deletar agente 7e50f893
   ✅ Agente 7e50f893 deletado

💬 Você: sair
   👋 Até logo!
```

---

## 📊 Estados do Agente

| Estado | Descrição |
|--------|-----------|
| **active** | Agente rodando, executando trades |
| **paused** | Agente pausado, não executa trades |
| **stopped** | Agente parado |
| **error** | Agente com erro |
| **completed** | Agente completou |

---

## 🚀 Recursos

✅ Criar agentes com linguagem natural
✅ Listar agentes com status
✅ Iniciar/Parar worker de monitoramento
✅ Pausar/Retomar agentes
✅ Parar/Deletar agentes
✅ Ver estatísticas em tempo real
✅ Ver resumo do sistema
✅ Suporte a múltiplos agentes simultâneos

---

## 💡 Dicas

- Use **IDs curtos** (primeiros 8 caracteres) para pausar/retomar/deletar
- O **worker** monitora agentes a cada 30 segundos
- **Pausar** agente mantém histórico, **deletar** remove tudo
- Ver **stats** para monitorar performance em tempo real
- Ver **resumo** para visão geral do sistema

---

**Chatbot com Agent Manager 100% Funcional!** ✅
