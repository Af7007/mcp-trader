# Quick Start - Sistema de Aprendizado Automático

**5 Minutos para começar a usar**

---

## 🚀 O Que Foi Implementado

Sistema de **análise e otimização automática** para o Gold Agent:

1. **PerformanceAnalyzer** - Analisa trades e calcula métricas avançadas
2. **OptimizationLogger** - Registra todas as mudanças e otimizações
3. **MarketRegimeDetector** - Detecta regime atual do mercado

**Status:** Fase 1 completa (Foundation)

---

## 📦 Instalação

Nenhuma instalação adicional necessária! Tudo já está no projeto.

**Arquivos criados:**
```
src/core/
├── performance_analyzer.py     ✓ Criado
├── optimization_logger.py      ✓ Criado
└── market_regime.py            ✓ Criado

demo_auto_learning.py           ✓ Criado
```

**Banco de dados:**
- 4 novas tabelas adicionadas a `btc_trading_logs.db`

---

## 🎯 Uso Rápido

### 1. Demo Completa (Ver tudo funcionando):

```bash
python demo_auto_learning.py
```

**Resultado:**
- Analisa performance de XAUUSDc
- Detecta regime de mercado atual
- Mostra métricas avançadas
- Registra exemplos no banco

---

### 2. Analisar Performance:

```python
from src.core.performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Analisar últimos 100 trades
metrics = analyzer.analyze_recent_performance(100, "XAUUSDc")

print(f"Win Rate: {metrics['win_rate']}%")
print(f"Profit Factor: {metrics['profit_factor']}")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")

# Gerar relatório completo
report = analyzer.generate_report("XAUUSDc", 100)
print(report)
```

---

### 3. Detectar Regime de Mercado:

```python
from src.core.market_regime import MarketRegimeDetector
from src.core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()
detector = MarketRegimeDetector(mt5, "XAUUSDc")

regime = detector.detect_current_regime()

print(f"Regime: {regime['regime']}")
print(f"Confidence: {regime['confidence']}")
print(f"Estratégia Recomendada: {regime['recommended_strategy']}")
```

---

### 4. Registrar Mudanças:

```python
from src.core.optimization_logger import OptimizationLogger

logger = OptimizationLogger()

# Registrar mudança de parâmetro
change_id = logger.log_parameter_change(
    symbol="XAUUSDc",
    parameter_name="stop_loss_atr_multiplier",
    old_value=5.0,
    new_value=4.5,
    reason="Reduzir stops prematuros",
    expected_improvement=5.0
)

print(f"Mudança registrada - ID: {change_id}")

# Ver histórico
history = logger.get_parameter_history("XAUUSDc")
for change in history:
    print(f"{change['parameter_name']}: {change['old_value']} -> {change['new_value']}")
```

---

## 📊 Métricas Disponíveis

### Básicas:
- **Win Rate** - % de trades lucrativos
- **Profit Factor** - Lucro total / Perda total
- **Net Profit** - Lucro líquido total

### Avançadas:
- **Sharpe Ratio** - Retorno ajustado ao risco
- **Sortino Ratio** - Downside risk ajustado
- **Calmar Ratio** - Annual return / Max drawdown
- **Max Drawdown** - Maior sequência de perdas
- **Recovery Factor** - Profit / Max drawdown

---

## 🔍 Consultar Banco de Dados

### Ver mudanças de parâmetros:

```sql
sqlite3 btc_trading_logs.db "
  SELECT timestamp, parameter_name, old_value, new_value, reason 
  FROM parameter_changes 
  ORDER BY timestamp DESC 
  LIMIT 10
"
```

### Ver otimizações:

```sql
sqlite3 btc_trading_logs.db "
  SELECT timestamp, optimization_type, improvement_percent, success 
  FROM optimization_history 
  ORDER BY timestamp DESC
"
```

### Ver regimes detectados:

```sql
sqlite3 btc_trading_logs.db "
  SELECT timestamp, regime_type, confidence, recommended_strategy 
  FROM regime_detection 
  ORDER BY timestamp DESC 
  LIMIT 10
"
```

---

## ⚠️ Limitações Atuais

1. **Sem otimização automática ainda** - Componentes prontos mas não integrados ao agente
2. **Precisa trades com profit_loss** - Para análise funcionar completamente
3. **Regime detection básico** - Pode precisar ajustes finos
4. **Sem interface web** - Apenas CLI por enquanto

---

## 🎯 Próximos Passos

### Para você usar AGORA:
1. ✅ Executar `demo_auto_learning.py` para ver funcionando
2. ✅ Usar `PerformanceAnalyzer` para analisar seus trades
3. ✅ Usar `MarketRegimeDetector` para detectar regime
4. ✅ Registrar mudanças manuais com `OptimizationLogger`

### Para implementação completa (Fase 2+):
- ⏳ ParameterOptimizer (Bayesian optimization)
- ⏳ GoldAdaptiveAgent (auto-tuning)
- ⏳ Dashboard web
- ⏳ A/B testing automatizado

---

## 📚 Documentação Completa

Ver `AUTO_LEARNING_PROGRESS.md` para:
- Detalhes técnicos de cada componente
- Plano completo de implementação
- Roadmap das próximas fases
- Exemplos avançados de uso

---

## 🆘 Troubleshooting

### "Dados insuficientes" no PerformanceAnalyzer:
**Causa:** Não há trades com `profit_loss` preenchido.
**Solução:** Aguardar trades fechados ou atualizar banco manualmente.

### Regime detection retorna UNKNOWN:
**Causa:** Lógica de classificação precisa ajuste ou dados insuficientes.
**Solução:** Normal - será refinado na Fase 2.

### Erro ao conectar MT5:
**Causa:** MT5 não está aberto ou não conectado.
**Solução:** Abrir e logar no MT5 antes de executar scripts.

---

## 💡 Dicas

1. **Execute demo primeiro** para entender o fluxo
2. **Monitore tabelas do banco** para ver registros
3. **Combine com Gold Agent** manualmente por enquanto
4. **Registre suas mudanças** para análise futura

---

## 🎉 Exemplo Prático

```bash
# 1. Ver demonstração
python demo_auto_learning.py

# 2. Analisar sua performance atual
python -c "
from src.core.performance_analyzer import PerformanceAnalyzer
a = PerformanceAnalyzer()
print(a.generate_report('XAUUSDc', 100))
"

# 3. Detectar regime atual
python src/core/market_regime.py

# 4. Ver histórico no banco
sqlite3 btc_trading_logs.db "SELECT * FROM parameter_changes"
```

---

**Pronto para usar!** 🚀

Execute `python demo_auto_learning.py` para começar.

**Dúvidas?** Ver `AUTO_LEARNING_PROGRESS.md` para detalhes completos.
