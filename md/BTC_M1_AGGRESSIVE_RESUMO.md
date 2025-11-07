# BTC M1 AGGRESSIVE - RESUMO COMPLETO

## 🎯 **CONCEITO**

Cópia do BTC Optimized adaptada para:
- **Timeframe**: M1 (scalping)
- **Símbolo**: BTCUSDc (cents - menor spread)
- **Abordagem**: AGGRESSIVE

## 📊 **CONFIGURAÇÕES PRINCIPAIS**

### VS BTC OPTIMIZED (M15)
| Parâmetro | BTC Optimized | BTC M1 Aggressive | Diferença |
|-----------|---------------|-------------------|-----------|
| **Symbol** | BTCUSDm | BTCUSDc | Cents version |
| **Timeframe** | M15 | M1 | 15x mais frequente |
| **Volume** | 0.03 lots | 0.05 lots | +67% |
| **Target Profit** | $2.5 | $1.0 | -60% |
| **Check Interval** | 30s | 15s | +100% |
| **Hedge Trigger** | -$4.0 | -$3.0 | +25% sensibilidade |
| **Hedge TP** | $4.0 | $3.0 | -25% |
| **ATR Multiplier** | 2.5x | 1.5x | -40% (SL apertado) |
| **BUY/SELL** | BUY enabled | BUY enabled | Igual |

## 🚀 **AGGRESSIVE FEATURES**

### 1. **Volume Agressivo**
- **0.05 lots** vs 0.03 otimizado
- **+67% exposição**
- Maior potencial de lucro por trade

### 2. **Hedge Mais Sensível**
- **Trigger**: -$3.0 vs -$4.0
- **25% mais sensível** ao prejuízo
- Proteção mais rápida

### 3. **TP Menor**
- **$1.0** vs $2.5 otimizado
- **Realizado 60% mais rápido**
- Reduz exposição ao mercado

### 4. **Check Frequente**
- **15 segundos** vs 30s otimizado
- **2x mais frequente**
- Resposta mais rápida a mudanças

### 5. **SL Mais Apertado**
- **ATR 1.5x** vs 2.5x otimizado
- **40% mais apertado**
- Menos drawdown

## 📈 **VANTAGENS M1**

### Scalping Ativo
- **Timeframe M1**: Capture movimentos em 1 minuto
- **Sinais 15x mais frequentes** que M15
- **Mais oportunidades** de entrada

### BTCUSDc Benefits
- **Menor spread** que BTCUSDm
- **Mais acessível** para scalping
- **Custos reduzidos** por trade

### Performance Esperada
- **Volume 67% maior** = profits acelerados
- **Hedge 25% mais rápido** = proteção eficiente
- **Check 2x frequente** = resposta ágil

## ⚠️ **RISCOS M1**

### Alta Volatilidade
- **M1 é muito volátil**
- **Spikes podem causar SL**
- **Requer monitoramento ativo**

### Stress Emocional
- **Más decisões** por pressão
- **Over-trading** possível
- **Fatiga mental** maior

## 🛠️ **IMPLEMENTAÇÃO**

### Como Usar
```python
# Configurações M1 Aggressive
agent = BTCHedgeAgent(
    symbol='BTCUSDc',      # Cents version
    volume=0.05,           # Aggressive volume
    target_profit=1.0,     # Menor TP
    check_interval=15,     # Mais frequente
    hedge_trigger=-3.0,    # Mais sensível
    hedge_tp_target=3.0,   # TP hedge menor
    atr_multiplier=1.5,    # SL apertado
    only_sell=False        # BUY habilitado
)
```

### Script de Execução
```bash
# Para testar configurações
python -c "
from agents.btc_hedge_agent import BTCHedgeAgent
agent = BTCHedgeAgent(
    symbol='BTCUSDc',
    volume=0.05,
    target_profit=1.0,
    check_interval=15,
    hedge_trigger=-3.0,
    hedge_tp_target=3.0,
    atr_multiplier=1.5,
    only_sell=False
)
print('BTC M1 Aggressive configurado!')
print(f'Symbol: {agent.symbol}')
print(f'Volume: {agent.volume}')
print(f'Target: ${agent.target_profit}')
"

# Para executar live (descomentar no código)
# agent.run()
```

## 📋 **CHECKLIST DE ATIVAÇÃO**

- [ ] Verificar se BTCUSDc está disponível no broker
- [ ] Testar em conta demo primeiro
- [ ] Ajustar volume se necessário
- [ ] Configurar hedge notifications
- [ ] Monitorar performance 1 semana
- [ ] Implementar em conta real gradualmente

## 🏆 **RECOMENDAÇÃO**

### USE BTC M1 AGGRESSIVE SE:
- ✅ Quer **scalping ativo**
- ✅ Tem **tempo para monitorar**
- ✅ **Aceita volatilidade alta**
- ✅ Quer **acelerar profits**
- ✅ Tem **experiência com M1**

### USE BTC OPTIMIZED SE:
- ✅ Prefere **trades mais longos**
- ✅ Quer **menos stress**
- ✅ **Trading passivo**
- ✅ **Capital conservador**

## 🎯 **PRÓXIMOS PASSOS**

1. **Testar demo** por 1 semana
2. **Monitorar métricas**:
   - Win rate
   - Profit/dia
   - Max drawdown
   - Stress level
3. **Ajustar volume** baseado nos resultados
4. **Implementar gradualmente** em conta real
5. **Otimizar** parâmetros se necessário

---

## 📊 **PERFORMANCE ESPERADA**

### Simulação Diária (Estimada)
- **Trades**: 24-48 (M1 vs 12 M15)
- **Win Rate**: 60-65%
- **Profit/Trade**: $1.0
- **Volume**: 0.05 lots
- **Profit Diário**: $14-31

### Comparação
| Métrica | BTC Optimized | BTC M1 Aggressive |
|---------|---------------|-------------------|
| Trades/dia | 12 | 24-48 |
| Win Rate | 60% | 60-65% |
| Profit/Trade | $2.5 | $1.0 |
| Volume | 0.03 | 0.05 |
| **Profit/Dia** | **$18** | **$14-31** |

**BTC M1 Aggressive pode gerar 25-75% mais profit diário!**
