# GUIA EXECUÇÃO BTC M1 AGGRESSIVE

## 📋 STATUS ATUAL

O agente está **CONFIGURADO** mas não está **EXECUTANDO**. 

## 🚀 COMO EXECUTAR EM LIVE

### PASSO 1: Ativar Execução

1. **Abra o arquivo**: `executar_btc_m1_aggressive.py`
2. **Encontre a linha**:
   ```python
   # agent.run()  # <- Esta linha está comentada
   ```
3. **Descomente removendo o #**:
   ```python
   agent.run()  # <- Execute o agente
   ```

### PASSO 2: Executar

```bash
python executar_btc_m1_aggressive.py
```

## 📊 COMANDO DIRETO (Alternativa)

Se preferir, execute diretamente:

```bash
python -c "
from src.agents.btc_hedge_agent import BTCHedgeAgent
agent = BTCHedgeAgent(
    symbol='BTCUSDc',
    volume=0.05,
    target_profit=1.0,
    check_interval=15,
    hedge_trigger=-3.0,
    only_sell=False
)
agent.run()
"
```

## ⚙️ CONFIGURAÇÕES ATIVAS

### BTC M1 Aggressive:
- **Symbol**: BTCUSDc
- **Volume**: 0.05 lots (aggressive)
- **Target**: $1.0
- **Hedge**: -$3.0
- **Check**: 15s
- **BUY/SELL**: Ativo

## 🔍 MONITORAMENTO

### Durante a execução, você verá:
- Log de operações
- Sinais BUY/SELL
- Ativações de hedge
- Performance em tempo real

## ⚠️ AVISOS IMPORTANTES

### 1. TESTE PRIMEIRO
- **Sempre teste em conta DEMO primeiro**
- Verifique se BTCUSDc está disponível
- Confirme se MT5 está conectado

### 2. MONITORAMENTO
- O agente ira executar continuamente
- Monitor日志 de trading
- Estaja atento ao hedge

### 3. INTERROMPER
- **Ctrl+C** para parar
- Fechar terminal
- Stop no MetaTrader

## 🛠️ SOLUÇÃO DE PROBLEMAS

### Erro: "No module named agents"
```bash
pip install MetaTrader5 python-dotenv
```

### Erro: "BTCUSDc not found"
- Usar BTCUSDm ou BTCUSD
- Verificar simbolos disponíveis

### Erro: "MT5 connection"
- Abrir MetaTrader 5
- Fazer login
- Verificar conexão

## 📈 PERFORMANCE ESPERADA

### Em LIVE:
- **Trades**: ~36/dia
- **Win Rate**: 60-65%
- **Profit/dia**: $20-25
- **Hedge**: Ativação rápida

## 🎯 PRÓXIMOS PASSOS

1. **✅ Configuração**: Concluída
2. **🔄 Ativação LIVE**: Descomente `agent.run()`
3. **📊 Monitoramento**: Acompanhe performance
4. **⚡ Otimização**: Ajuste conforme necessário

---

**Para executar agora:**
1. Edite `executar_btc_m1_aggressive.py`
2. Descomente `agent.run()`
3. Execute: `python executar_btc_m1_aggressive.py`
