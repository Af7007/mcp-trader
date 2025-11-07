# Como Rodar o Game - GOLD Loss Zero

**Data:** 2025-11-04  
**Status:** ✅ PRONTO

---

## 🎮 O que é o Game?

O GOLD Loss Zero Game é uma versão **gamificada** do agente de trading com:
- ✅ Dashboard visual em tempo real
- ✅ Simulação de trades (sem dinheiro real)
- ✅ Gráficos do mercado ao vivo
- ✅ Histórico de operações
- ✅ Estatísticas e performance
- ✅ Interface web (PWA)

---

## 🚀 Como Executar

### **Opção 1: Arquivo .bat (Mais Fácil)**

```batch
RUN_GOLD_GAME.bat
```

**O que faz:**
1. Inicia servidor web na porta 3000
2. Abre automaticamente o navegador
3. Acessa: `http://localhost:3000/game`

**Para parar:**
- Pressione `Ctrl+C` no terminal

---

### **Opção 2: Linha de Comando Manual**

```bash
cd C:\mcp-trader
uv run python run_game_server.py
```

**Depois acesse no navegador:**
```
http://localhost:3000/game
```

---

## 📋 Pré-requisitos

✅ MetaTrader 5 aberto (para dados ao vivo)  
✅ Banco de dados criado (btc_trading_logs.db)  
✅ Python/uv instalado  
✅ Porta 3000 disponível

---

## 🎯 O que Você Verá

### **Tela Principal:**
```
┌─────────────────────────────────────┐
│   GOLD Loss Zero Game               │
├─────────────────────────────────────┤
│                                     │
│  [Gráfico do Ouro ao vivo]         │
│                                     │
│  Preco: $3940.45                   │
│  Lucro: +$125.30                   │
│  Win Rate: 72%                     │
│                                     │
│  [Historico de Trades]             │
│                                     │
└─────────────────────────────────────┘
```

### **Funcionalidades:**
- 📊 Gráfico candlestick em tempo real
- 💰 Simulação de compra/venda
- 📈 Estatísticas de performance
- 🎯 Indicadores técnicos
- 📱 Responsivo (funciona em mobile)

---

## 🔧 Servidor Run Game

### **Arquivo:** `run_game_server.py`

**O que faz:**
1. Inicia servidor Flask (web framework)
2. Carrega dados do MT5
3. Oferece API REST para o frontend
4. Atualiza gráficos em tempo real

### **Logs:**
```
Running on http://127.0.0.1:3000
Press CTRL+C to quit
```

---

## 🌐 Acessando o Game

### **Local (seu PC):**
```
http://localhost:3000/game
http://127.0.0.1:3000/game
```

### **Outra Máquina na Rede:**
```
http://SEU_IP_LOCAL:3000/game
Exemplo: http://192.168.1.100:3000/game
```

---

## 📊 Dados do Game

### **Banco de Dados:**
- `btc_trading_logs.db` - Histórico de trades
- Tabela: `trades` - Operações simuladas/reais

### **Gráficos:**
- Carregam dados ao vivo do MT5
- Atualizam a cada tick
- Histórico dos últimos 100 candles

### **Performance:**
- Win rate calculado em tempo real
- Profit/loss atualizado instantaneamente
- Estatísticas por período

---

## 🎮 Como Jogar (Modo Simulado)

### **Básico:**
1. Abrir o jogo
2. Ver gráfico em tempo real
3. Ver sugestões de trades (opcionais)
4. Visualizar histórico

### **Avançado:**
- Ajustar parâmetros de estratégia
- Simular diferentes cenários
- Analisar performance histórica
- Exportar dados

---

## 🐛 Troubleshooting

### **Erro: "Porta 3000 em uso"**
```bash
# Liberar porta (parar outro servidor)
taskkill /F /IM python.exe

# Ou usar porta diferente
uv run python run_game_server.py --port 3001
```

### **Erro: "Banco de dados não encontrado"**
```bash
# Certifique-se que btc_trading_logs.db existe
ls C:\mcp-trader\btc_trading_logs.db

# Se não existir, criar:
python src/core/database.py
```

### **Gráfico não carrega**
```
1. Verificar se MT5 está aberto
2. Verificar conexão com MT5
3. Recarregar página (F5)
4. Limpar cache (Ctrl+Shift+Delete)
```

### **Dados não atualizam**
```
1. Pressionar F5 (refresh)
2. Verificar aba "Network" (F12)
3. Verificar logs do servidor
```

---

## 🔄 Parar o Game

### **Opção 1: Terminal**
```
Pressione: Ctrl+C
```

### **Opção 2: Fechar Janela**
```
Feche a janela do terminal
```

### **Opção 3: Matar Processo**
```bash
taskkill /F /IM python.exe
```

---

## 📱 Usar em Mobile

O game é **PWA (Progressive Web App)**:
1. Abrir no navegador mobile: `http://SEU_IP_LOCAL:3000/game`
2. Menu → Instalar app
3. Funciona offline (alguns recursos)

---

## 📚 Documentação Completa

Para mais detalhes, leia:
- `QUICK_START_GOLD_GAME.md` - Início rápido
- `GOLD_GAME_PWA_GUIDE.md` - Guia PWA
- `GOLD_GAME_V2_REDESIGN.md` - Design v2

---

## ✅ Checklist

- [ ] RUN_GOLD_GAME.bat pronto
- [ ] MT5 aberto
- [ ] Banco de dados existe
- [ ] Porta 3000 disponível
- [ ] Navegador atualizado

---

## 🚀 Resumo Rápido

```bash
# 1. Executar
RUN_GOLD_GAME.bat

# 2. Esperar: "Running on http://127.0.0.1:3000"

# 3. Acessar no navegador
http://localhost:3000/game

# 4. Visualizar gráfico, trades, estatísticas

# 5. Parar: Ctrl+C no terminal
```

**Pronto! Game rodando!** 🎮

---

**Data:** 2025-11-04  
**Status:** ✅ PRONTO PARA USAR
