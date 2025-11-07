# 🤖 Teste do Agente BTCUSD com Hedge

## ⚠️ ATENÇÃO - OPERAÇÕES REAIS!

Este agente vai operar com **DINHEIRO REAL** (ou demo). Certifique-se que:
- ✅ Está usando conta DEMO para testes
- ✅ Entende os riscos envolvidos
- ✅ MT5 está conectado e operacional

---

## 📋 Configuração do Agente

| Parâmetro | Valor |
|-----------|-------|
| Símbolo | BTCUSD |
| Volume | 0.02 lots |
| Target Profit | $2 por operação |
| Max Operações/Dia | 20 |
| SL Dinâmico | 1.5x ATR |
| Intervalo Check | 30 segundos |

---

## 🎯 Estratégia

### Modo Normal (Tendência Lucrativa)
1. ✅ Analisa 5 indicadores (RSI, MACD, Bollinger, SMAs, Trend)
2. ✅ Abre posição quando 3+ indicadores concordam
3. ✅ Operações consecutivas em winning streak
4. ✅ TP fixo de $2, SL dinâmico baseado em ATR

### Modo Hedge (Reversão)
1. ⚠️ Detecta prejuízo > $10 em posição
2. 🔄 Abre posição oposta (hedge)
3. 📈 Aproveita movimento reverso
4. ✅ Lucros em ambas direções

---

## 🚀 Como Iniciar

### Opção 1: Script Automático (Recomendado)

```batch
RUN_BTC_AGENT.bat
```

O script vai:
1. Pedir confirmação (segurança)
2. Verificar MT5
3. Parar processos antigos
4. Iniciar agente
5. Mostrar logs a cada 30s

### Opção 2: Manual

```powershell
cd C:\mcp-trader
uv run python src\agents\btc_hedge_agent.py
```

---

## 📊 Logs em Tempo Real

A cada 30 segundos você verá:

```
================================================================================
🤖 AGENTE BTC HEDGE | Ciclo #15 | 18:23:45
================================================================================

📊 AGENTE:
   Estado: TRADING
   Operações Hoje: 5/20
   Lucro Total: $+8.50
   Winning Streak: 3
   Hedge Ativo: NÃO

📈 MERCADO (BTCUSD):
   Preço: $67,850.00
   Tendência: UP
   RSI: 58.3
   MACD: +15.20
   ATR: 125.50
   SMA20: $67,500.00
   SMA50: $66,800.00

💼 POSIÇÕES ABERTAS: 2
   1. Ticket 123456 | COMPRA | 0.02 lots | Lucro: $+3.20
   2. Ticket 123457 | COMPRA | 0.02 lots | Lucro: $+1.50
   💰 TOTAL: $+4.70

================================================================================
```

---

## 🛑 Como Parar

Pressione **Ctrl+C** no terminal

O agente vai:
- Parar de abrir novas posições
- Manter posições abertas
- Sair do loop

**IMPORTANTE**: Posições abertas NÃO são fechadas automaticamente!

---

## 📈 Indicadores Utilizados

1. **RSI (14)** - Força relativa
   - <30: Sobrevendido (BUY)
   - >70: Sobrecomprado (SELL)

2. **MACD** - Convergência/Divergência
   - >0: Momentum altista
   - <0: Momentum baixista

3. **Bollinger Bands (20, 2)** - Volatilidade
   - Preço < Lower Band: BUY
   - Preço > Upper Band: SELL

4. **SMA 20/50** - Tendência
   - SMA20 > SMA50: Tendência altista
   - SMA20 < SMA50: Tendência baixista

5. **ATR (14)** - Volatilidade para SL
   - SL = ATR × 1.5

---

## ⚡ Lógica de Decisão

### Sinal de COMPRA (mínimo 3 de 5):
- RSI < 45
- MACD > 0
- Preço < BB Lower
- SMA20 > SMA50
- Tendência UP

### Sinal de VENDA (mínimo 3 de 5):
- RSI > 55
- MACD < 0
- Preço > BB Upper
- SMA20 < SMA50
- Tendência DOWN

---

## 🔄 Sistema de Hedge

### Quando Ativa?
- Posição em prejuízo > $10
- Não tem hedge ativo
- Ainda dentro do limite diário

### Como Funciona?
1. Detecta prejuízo significativo
2. Abre posição oposta (mesmo volume)
3. Mantém ambas abertas
4. Lucra na reversão
5. Fecha quando ambas lucrativas

---

## 📝 Limites de Segurança

1. **Máximo 20 operações/dia**
   - Evita overtrading
   - Reset à meia-noite

2. **Máximo 5 posições simultâneas**
   - Previne exposição excessiva

3. **SL Dinâmico**
   - Adapta-se à volatilidade
   - Baseado em ATR atual

4. **Winning Streak**
   - 2+ lucros consecutivos = continue
   - Reset em prejuízo

---

## 🧪 Teste Inicial Recomendado

Para seu primeiro teste:

1. ✅ Use conta DEMO
2. ✅ Monitore por 1-2 horas
3. ✅ Observe os logs
4. ✅ Verifique se:
   - Posições estão abrindo corretamente
   - SL/TP estão sendo definidos
   - Hedge ativa quando necessário
   - Limite diário funciona

---

## 📊 Resultados Esperados

### Cenário Conservador
- 10-15 operações/dia
- 60% taxa de acerto
- $1.5-2.0 lucro médio/operação
- **~$15-20/dia**

### Cenário Otimista
- 18-20 operações/dia
- 70% taxa de acerto
- $2.0-2.5 lucro médio/operação
- **~$30-35/dia**

**NOTA**: Resultados variam com volatilidade e condições de mercado!

---

## ⚠️ Riscos e Considerações

### Riscos
- ❌ Slippage em mercado volátil
- ❌ Gaps em abertura/fechamento
- ❌ Notícias impactantes
- ❌ Problemas de conexão

### Mitigações
- ✅ SL em todas posições
- ✅ Limite diário
- ✅ Hedge automático
- ✅ Volume conservador (0.02)

---

## 📞 Suporte

**Se tiver problemas:**

1. **Agente não inicia**
   - Verifique se MT5 está aberto
   - Teste: `uv run python test_mt5_connection.py`

2. **Erro ao abrir posição**
   - Verifique saldo
   - Verifique se BTCUSD está disponível
   - Verifique horário de negociação

3. **Logs não aparecem**
   - Agente pode estar pausado (limite atingido)
   - Verifique mensagens de erro

---

## 🎯 Próximos Passos Após Teste

Se tudo funcionar bem:

1. ✅ Ajustar parâmetros (volume, TP, etc)
2. ✅ Testar outros símbolos
3. ✅ Adicionar mais indicadores
4. ✅ Melhorar estratégia de hedge
5. ✅ Implementar notificações

---

**BOA SORTE! 🚀📈**

*Lembre-se: Trading envolve riscos. Nunca opere com dinheiro que não pode perder.*
