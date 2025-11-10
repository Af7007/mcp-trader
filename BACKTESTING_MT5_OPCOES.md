# Backtesting MT5 - Opções Disponíveis

## OPÇÃO 1: Strategy Tester Nativo (MQL5)

### Como Funciona
- Usar o Strategy Tester do MT5
- Criar EA (Expert Advisor) em MQL5
- Testar com dados históricos do MT5

### Vantagens
✅ Visual (gráficos, relatórios completos)
✅ Dados reais do broker
✅ Testa slippage, spread histórico
✅ Relatórios profissionais (PDF, HTML)
✅ Otimização de parâmetros

### Desvantagens
❌ Precisa converter Python → MQL5
❌ Linguagem diferente (curva aprendizado)
❌ Manutenção duplicada (2 códigos)

---

## OPÇÃO 2: Backtesting em Python (RECOMENDADO)

### Como Funciona
- Buscar dados históricos via MT5 Python
- Simular trades em Python
- Usar mesma lógica do agente real

### Vantagens
✅ Mesmo código do agente (zero retrabalho)
✅ Fácil de debugar
✅ Resultados rápidos
✅ Customizável (qualquer métrica)
✅ Pode rodar milhares de cenários

### Desvantagens
❌ Sem interface visual automática
❌ Precisa criar relatórios manualmente

---

## IMPLEMENTAÇÃO RECOMENDADA

### Backtesting Python com Dados MT5

```python
class BTCBacktester:
    """
    Backtester para BTC v2.1.0
    Usa dados históricos do MT5
    """

    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

        # Usar mesma lógica do agente
        self.agent = BTCLossZeroV2(
            symbol=symbol,
            volume=0.30,
            use_buy=True,
            use_sell=True
        )

    def get_historical_data(self):
        """Busca dados históricos do MT5"""
        import MetaTrader5 as mt5
        mt5.initialize()

        rates = mt5.copy_rates_range(
            self.symbol,
            mt5.TIMEFRAME_M5,
            self.start_date,
            self.end_date
        )
        return rates

    def simulate_trades(self, rates):
        """Simula trades usando lógica do agente"""
        trades = []

        for i in range(50, len(rates)):
            # Pegar janela de dados
            rates_m5 = rates[i-50:i]
            rates_m1 = self._get_m1_window(rates, i)

            # Usar método do agente
            signal = self.agent._get_simple_signal()

            if signal:
                # Simular abertura
                trade = self._open_virtual_trade(signal, rates[i])

                # Simular gerenciamento
                for j in range(i+1, len(rates)):
                    result = self._manage_virtual_trade(trade, rates[j])
                    if result:  # Trade fechou
                        trades.append(result)
                        break

        return trades

    def run_backtest(self):
        """Executa backteste completo"""
        rates = self.get_historical_data()
        trades = self.simulate_trades(rates)
        metrics = self.calculate_metrics(trades)

        return {
            'trades': trades,
            'metrics': metrics,
            'report': self.generate_report(metrics)
        }
```

---

## EXEMPLO DE USO

### Testar Última Semana

```python
from datetime import datetime, timedelta

# Configurar período
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Executar backtest
backtester = BTCBacktester(
    symbol="BTCUSDc",
    start_date=start_date,
    end_date=end_date
)

results = backtester.run_backtest()

# Ver resultados
print(f"Total Trades: {len(results['trades'])}")
print(f"Win Rate: {results['metrics']['win_rate']:.1f}%")
print(f"Net Profit: ${results['metrics']['net_profit']:.2f}")
```

---

## MÉTRICAS CALCULADAS

### Básicas
- Total de trades
- Wins / Losses
- Win rate (%)
- Profit factor
- Net profit/loss

### Avançadas
- Avg win / Avg loss
- Maior sequência de wins
- Maior sequência de losses
- Drawdown máximo
- Sharpe ratio
- Recovery factor

### Por Período
- Trades por dia
- Profit por dia/semana/mês
- Win rate por horário
- Performance por dia da semana

---

## VALIDAÇÃO

### Comparar com MT5 Real

```python
# 1. Backtest do último mês
backtest_result = backtester.run_backtest()

# 2. Buscar trades reais do DB
real_trades = get_trades_from_db(last_month=True)

# 3. Comparar
comparison = compare_results(backtest_result, real_trades)

# Ver diferenças
print(f"Backtest WR: {backtest_result['win_rate']}")
print(f"Real WR: {real_trades['win_rate']}")
print(f"Diferença: {comparison['difference']}")
```

---

## OTIMIZAÇÃO DE PARÂMETROS

### Testar Múltiplos Cenários

```python
# Testar diferentes scores
scores_to_test = [3.0, 3.5, 4.0, 4.5]
results = {}

for score in scores_to_test:
    backtester = BTCBacktester(...)
    backtester.agent.min_score_m5 = score

    result = backtester.run_backtest()
    results[score] = result

# Ver melhor score
best_score = max(results, key=lambda s: results[s]['net_profit'])
print(f"Melhor score: {best_score}")
```

---

## VISUALIZAÇÃO

### Gráficos em Python

```python
import matplotlib.pyplot as plt

# Curva de equity
plt.plot(equity_curve)
plt.title('Equity Curve - BTC Backtest')
plt.xlabel('Trades')
plt.ylabel('Balance ($)')
plt.show()

# Win rate por hora
plt.bar(hours, win_rates)
plt.title('Win Rate por Hora (UTC)')
plt.show()
```

---

## CRIAR AGORA?

Posso criar para você:

### Opção A: Backtester Completo
- Classe completa de backtesting
- Todas as métricas
- Relatórios HTML
- Gráficos
- Tempo: ~2h

### Opção B: Backtester Simples
- Teste rápido de win rate
- Métricas básicas
- Relatório texto
- Tempo: ~30 min

### Opção C: Converter para MQL5
- EA em MQL5
- Testar no Strategy Tester
- Relatórios visuais do MT5
- Tempo: ~3h

Qual prefere?
