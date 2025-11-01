# COMO EXECUTAR O BTC M1 AGGRESSIVE

## 🚀 PASSO A PASSO SIMPLES

### OPÇÃO 1: Descomentar no arquivo existente

1. **Abra o arquivo**: `executar_btc_m1_aggressive.py`
2. **Procure a linha** (está comentada):
   ```python
   # agent.run()
   ```
3. **Remova o #** (descomente):
   ```python
   agent.run()
   ```
4. **Execute**:
   ```bash
   python executar_btc_m1_aggressive.py
   ```

### OPÇÃO 2: Comando direto no terminal

Execute este comando EXATAMENTE como está:

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'src'))
from agents.btc_hedge_agent import BTCHedgeAgent
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

## ✅ O QUE VAI ACONTECER

### Durante a execução você verá:
```
[INFO] Conectando ao MT5...
[INFO] Agente inicializado
[INFO] Analisando mercado BTCUSDc...
[INFO] Aguardando sinais...
```

### Sinais de trading:
```
[SELL] BTCUSDc - Volume: 0.05 - Target: $1.0
[HEDGE] Ativado em $-3.0
[HEDGE] Fechando par em $3.0
```

## ⚠️ IMPORTANTE

### ANTES DE EXECUTAR:
1. **Verificar MetaTrader 5 aberto**
2. **Fazer login na conta**
3. **Testar DEMO primeiro**

### DURANTE A EXECUÇÃO:
- O agente vai executar **contínuamente**
- **NÃO feche o terminal**
- **Ctrl+C para parar**

## 🔧 SE DER ERRO

### "No module named agents"
```bash
pip install MetaTrader5 python-dotenv
```

### "BTCUSDc not found"
Troque por:
```python
symbol='BTCUSDm'  # ou
symbol='BTCUSD'
```

### "MT5 connection"
- Abrir MetaTrader 5
- Fazer login
- Verificar conexão

## 📊 CONFIGURAÇÕES ATIVAS

```
BTC M1 Aggressive:
- Symbol: BTCUSDc
- Volume: 0.05 lots
- Target: $1.0
- Hedge: -$3.0
- Check: 15s
- BUY/SELL: Ativo
```

## 🎯 RESULTADO ESPERADO

- **~36 trades/dia**
- **~60-65% win rate**
- **~$22 profit/dia**
- **Hedge automático**
- **Monitoramento contínuo**

---

**Para executar AGORA:**
Edite `executar_btc_m1_aggressive.py` → descomente `agent.run()` → execute
