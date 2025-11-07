# 🚀 INICIAR TESTE DO AGENTE BTCUSD

## ⚡ Início Rápido (3 passos)

### 1️⃣ Certifique-se que o MT5 está aberto
- ✅ MetaTrader 5 rodando
- ✅ Conta logada (DEMO recomendado)
- ✅ BTCUSD disponível

### 2️⃣ Execute o script
```batch
RUN_BTC_AGENT.bat
```

### 3️⃣ Confirme e observe
- Digite `S` para confirmar
- Aguarde logs a cada 30s
- Pressione Ctrl+C para parar

---

## 📊 O Que Vai Acontecer

### Minuto 0-1
```
✅ MT5 inicializado
🤖 Agente BTCUSD inicializado
📊 Calculando indicadores...
```

### Minuto 1-2
```
================================================================================
🤖 AGENTE BTC HEDGE | Ciclo #1 | 18:00:30
================================================================================

📊 AGENTE:
   Estado: ANALYZING
   Operações Hoje: 0/20
   ...

📈 MERCADO (BTCUSD):
   Preço: $67,850.00
   Tendência: UP
   RSI: 58.3
   ...

💼 POSIÇÕES ABERTAS: 0
================================================================================
```

### Quando Sinal Aparecer
```
📈 Sinal detectado: BUY
✅ Posição aberta: BUY | Ticket: 123456 | SL: 67700.00 | TP: 67870.00
```

### Se Entrar em Prejuízo
```
⚠️ Posição em prejuízo: $-12.50
🔄 Ativando HEDGE para posição 123456
✅ Hedge ativado: Original=123456, Hedge=123457
```

---

## 🎯 Checklist Pré-Execução

Antes de rodar, verifique:

- [ ] MT5 está aberto
- [ ] MT5 está logado
- [ ] Usando conta DEMO (recomendado)
- [ ] BTCUSD está no Market Watch
- [ ] Tem saldo suficiente ($100+ recomendado)
- [ ] Horário de negociação está aberto
- [ ] Conexão internet estável

---

## 📝 Comandos

### Iniciar Agente
```powershell
# Opção 1: Script automático
RUN_BTC_AGENT.bat

# Opção 2: Manual
cd C:\mcp-trader
uv run python src\agents\btc_hedge_agent.py
```

### Parar Agente
Pressione **Ctrl+C** no terminal

### Ver Posições no MT5
No terminal MT5:
1. Aba "Trade"
2. Ver posições abertas
3. Monitorar P&L

---

## 🔍 Monitoramento

### Logs Automáticos (a cada 30s)
```
================================================================================
🤖 AGENTE BTC HEDGE | Ciclo #15 | 18:23:45
================================================================================

📊 AGENTE:
   Estado: TRADING              ← Status do agente
   Operações Hoje: 5/20         ← Contador diário
   Lucro Total: $+8.50          ← P&L acumulado
   Winning Streak: 3            ← Sequência de vitórias
   Hedge Ativo: NÃO             ← Se tem hedge

📈 MERCADO (BTCUSD):
   Preço: $67,850.00            ← Preço atual
   Tendência: UP                ← Direção da tendência
   RSI: 58.3                    ← Força relativa
   MACD: +15.20                 ← Momentum
   ATR: 125.50                  ← Volatilidade
   SMA20: $67,500.00            ← Média 20
   SMA50: $66,800.00            ← Média 50

💼 POSIÇÕES ABERTAS: 2         ← Total de posições
   1. Ticket 123456 | COMPRA | 0.02 lots | Lucro: $+3.20
   2. Ticket 123457 | COMPRA | 0.02 lots | Lucro: $+1.50
   💰 TOTAL: $+4.70             ← P&L total aberto

================================================================================
```

### O Que Observar

✅ **Bons Sinais:**
- Estado: TRADING
- Winning Streak aumentando
- Lucro Total positivo
- Posições com P&L positivo

⚠️ **Atenção:**
- Hedge Ativo: SIM (indica reversão)
- Operações Hoje: 18+/20 (perto do limite)
- Posições com P&L muito negativo

❌ **Problemas:**
- Estado: PAUSED/STOPPED
- Erros nos logs
- Sem posições abertas por muito tempo

---

## 🎲 Cenários de Teste

### Cenário 1: Mercado em Tendência Alta
- Espera: Múltiplas operações BUY
- Resultado: Lucros consecutivos
- Hedge: Não deve ativar

### Cenário 2: Mercado em Reversão
- Espera: Ativação de hedge
- Resultado: 2 posições opostas
- Lucro: Em ambas direções

### Cenário 3: Mercado Lateral
- Espera: Poucos sinais
- Resultado: Poucas operações
- Estado: ANALYZING mais tempo

---

## 📊 Exemplo de Execução Bem-Sucedida

```
Ciclo #1:  ANALYZING | 0 posições | Aguardando sinal
Ciclo #2:  ANALYZING | 0 posições | RSI=45, MACD=+5
Ciclo #3:  TRADING   | 1 posição  | BUY aberto @ 67850
Ciclo #4:  TRADING   | 1 posição  | P&L: $+1.20
Ciclo #5:  TRADING   | 1 posição  | P&L: $+2.10 ← TP atingido!
Ciclo #6:  TRADING   | 0 posições | Lucro: $+2.10
Ciclo #7:  TRADING   | 1 posição  | BUY aberto @ 67900
Ciclo #8:  TRADING   | 1 posição  | P&L: $-8.50
Ciclo #9:  HEDGING   | 2 posições | Hedge ativado!
Ciclo #10: HEDGING   | 2 posições | BUY: $-5, SELL: $+3
Ciclo #11: HEDGING   | 2 posições | BUY: $-2, SELL: $+6
Ciclo #12: TRADING   | 0 posições | Ambas fechadas, Lucro: $+4
```

---

## ⏱️ Duração Recomendada do Teste

### Teste Curto (30 min)
- Ver se agente inicia
- Ver 1-2 operações
- Validar logs

### Teste Médio (2 horas)
- Ver múltiplas operações
- Testar hedge
- Validar winning streak

### Teste Longo (1 dia)
- Teste completo
- Limite diário
- Reset à meia-noite

---

## 🛑 Quando Parar o Teste

Pare se:
- ❌ Erros constantes nos logs
- ❌ Posições não abrem corretamente
- ❌ SL/TP não são definidos
- ❌ Prejuízos consecutivos (>5)
- ❌ Comportamento estranho

Continue se:
- ✅ Logs aparecem corretamente
- ✅ Posições abrem/fecham normalmente
- ✅ Hedge funciona
- ✅ Lucros aparecem

---

## 📞 Próximos Passos Após Teste

### Se Funcionar Bem ✅
1. Ajustar parâmetros
2. Testar outros símbolos
3. Aumentar volume gradualmente
4. Adicionar notificações

### Se Tiver Problemas ❌
1. Revisar logs de erro
2. Verificar configuração MT5
3. Testar com volume menor
4. Ajustar indicadores

---

## 🎯 EXECUTE AGORA!

```batch
RUN_BTC_AGENT.bat
```

**BOA SORTE! 🚀📈**

*Monitore de perto nas primeiras horas!*
