# Como Usar Gold Agent v2.0.0

## GUIA RAPIDO DE USO

### 1. VALIDAR INSTALACAO

Primeiro, valide que todas as melhorias foram aplicadas:

```bash
python test_gold_v2_improvements.py
```

Resultado esperado:
```
[OK] TODAS AS MELHORIAS FORAM APLICADAS COM SUCESSO!
```

Se aparecer `[FALHA]`, revise o arquivo [gold_loss_zero_simple.py](src/agents/gold_loss_zero_simple.py).

---

### 2. INICIAR AGENTE GOLD v2.0.0

#### Opcao 1: Usar script de inicializacao (RECOMENDADO)
```bash
RUN_GOLD_AGENT.bat
```

#### Opcao 2: Executar diretamente
```bash
python src/agents/gold_loss_zero_simple.py
```

#### Opcao 3: Codigo Python
```python
from src.agents.gold_loss_zero_simple import GoldLossZeroSimple

# Criar agente com parametros otimizados v2.0.0
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=0.03,  # Ajustar conforme margem disponivel
    fixed_sl_dollars=5.0,  # SL fixo $5.00
    use_buy=True,
    use_sell=True
)

# Iniciar
agent.run()
```

---

### 3. MONITORAR AGENTE EM TEMPO REAL

O agente vai mostrar logs detalhados:

```
[CICLO 1] 2025-11-07 20:00:00
================================================================================
[M5 BUY] Score: 4.5 | RSI: 45.2 | Momentum: 0.08%
[FILTRO ATR] M5 ATR = $1.20 (OK)
[FILTRO SPREAD] Spread = $0.30 (OK)
[M1 CONFIRM] BUY confirmado (2 velas up)
[SINAL CONFIRMADO] M5 BUY (score 4.5) + M1 timing OK

[ABRINDO POSICAO]
  Type: BUY
  Volume: 0.03
  Entry: $4005.50
  SL: $4000.50 ($5.00 abaixo)
  TP: SEM TP (trailing ilimitado)

[POSICAO ABERTA] Ticket #123456
```

---

### 4. ENTENDER OS LOGS

#### Analise M5 (Sinal Principal)
```
[M5 BUY] Score: 4.5 | RSI: 45.2 | Momentum: 0.08%
```
- Score >= 4.0: Sinal forte confirmado
- RSI: Indicador de sobre-compra/venda
- Momentum: Forca da tendencia

#### Filtros de Seguranca
```
[FILTRO ATR] M5 ATR muito alto ($2.50 > $2.00), aguardando
```
- ATR alto = mercado volatil = AGUARDAR

```
[FILTRO SPREAD] Spread muito alto ($0.70 > $0.50), aguardando
```
- Spread alto = custos altos = AGUARDAR

#### Confirmacao M1 (Timing)
```
[M1 WAIT] Aguardando confirmacao BUY em M1...
```
- M1 ainda nao confirmou, aguardando 2 velas consecutivas

```
[M1 CONFIRM] BUY confirmado (2 velas up)
```
- M1 confirmou com 2 velas subindo = ENTRAR AGORA

#### Trailing Stop
```
[TRAILING] Ativado! Lucro: $2.50 | Protegendo: $1.00
```
- Trailing ativou quando lucro atingiu $2.00
- Agora protege $1.00 de lucro minimo

```
[TRAILING] Subiu! Lucro: $4.00 | Protegendo: $2.50
```
- A cada $1.50 de lucro adicional, protege +$1.00

---

### 5. ANALISAR RESULTADOS

Apos 10-20 trades, analise os resultados:

```bash
python analyze_gold_quick_detailed.py
```

Metricas importantes:
- **Win Rate**: Deve estar entre 60-65% (antes: 52%)
- **Avg Win**: Deve estar entre $1.50-2.00 (antes: $1.02)
- **Avg Loss**: Deve ser ~$5.00 (fixo)
- **Net Result**: Deve ser POSITIVO (antes: -$29.20)

---

### 6. AJUSTES CONFORME NECESSARIO

#### Se Win Rate < 55%
```python
# Aumentar score minimo M5
agent.min_score_m5 = 4.5  # ao inves de 4.0
```

#### Se SL sendo atingido com frequencia
```python
# Aumentar SL fixo
agent.fixed_sl_dollars = 6.0  # ao inves de 5.0
```

#### Se poucos trades por dia
```python
# Reduzir score minimo M5 (com cuidado!)
agent.min_score_m5 = 3.5  # ao inves de 4.0
```

#### Se trailing fechando muito cedo
```python
# Aumentar ativacao do trailing
agent.trailing_activation_dollar = 3.0  # ao inves de 2.0
```

---

### 7. COMPARAR COM VERSAO ANTERIOR

#### Versao 1.3.0 (Antiga)
- M15 + M5 + M1 (conflitos)
- Score M5 minimo: 2.5-3.0
- TS activation: $1.50
- Win Rate: 52.2%
- Net Result: -$29.20

#### Versao 2.0.0 (Nova)
- M5 + M1 (sem conflitos)
- Score M5 minimo: 4.0
- TS activation: $2.00
- Filtros: ATR + Spread
- Win Rate esperado: 60-65%
- Net Result esperado: POSITIVO

---

### 8. DICAS DE USO

#### Horarios Recomendados
- **MELHOR**: London Session (08:00-16:00 UTC)
- **BOM**: NY Session (13:00-22:00 UTC)
- **EVITAR**: Asian Session (00:00-08:00 UTC) - baixa volatilidade

#### Volume Recomendado
- **Conta Cents**: 0.02-0.03 lotes
- **Conta Standard**: 0.01 lotes
- **Margem necessaria**: ~$100 por 0.01 lotes

#### Gestao de Risco
- **Max Drawdown**: $50 (10 trades com SL)
- **Circuit Breaker**: 5 perdas consecutivas = pausa 1h
- **Daily Limit**: Sem limite (agente monitora automaticamente)

---

### 9. TROUBLESHOOTING

#### Problema: Agente nao abre trades
**Solucao**:
1. Verificar se score M5 >= 4.0 (pode estar muito alto)
2. Verificar filtro ATR (ATR pode estar > $2.00)
3. Verificar filtro Spread (spread pode estar > $0.50)
4. Verificar confirmacao M1 (pode estar aguardando 2 velas)

#### Problema: Muitas perdas por SL
**Solucao**:
1. Aumentar `fixed_sl_dollars` de $5.00 para $6.00
2. Verificar se entrada esta ocorrendo em momento volatil
3. Revisar logs de ATR (pode estar alto demais)

#### Problema: Trailing fechando muito rapido
**Solucao**:
1. Aumentar `trailing_activation_dollar` de $2.00 para $3.00
2. Aumentar `trailing_distance_dollar` de $1.00 para $1.50

#### Problema: Poucos trades
**Solucao**:
1. Reduzir `min_score_m5` de 4.0 para 3.5 (com cuidado!)
2. Aumentar `max_atr_m5_dollars` de $2.00 para $2.50
3. Verificar horario (evitar Asian session)

---

### 10. LOGS E DEBUGGING

#### Ver trades no banco de dados
```bash
VER_TRADES.bat
```

#### Analisar ultima perda
```bash
python analyze_last_loss.py
```

#### Debug detalhado
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

### 11. BACKUPS E SEGURANCA

#### Backup do agente v1.3.0
```
src/agents/gold_loss_zero_simple_BACKUP.py
```

#### Backup do banco de dados
```bash
copy btc_trading_logs.db btc_trading_logs_backup.db
```

#### Reverter para v1.3.0 (se necessario)
```bash
copy src\agents\gold_loss_zero_simple_BACKUP.py src\agents\gold_loss_zero_simple.py
```

---

### 12. SUPORTE E DOCUMENTACAO

- **Changelog**: [GOLD_V2_CHANGELOG.md](GOLD_V2_CHANGELOG.md)
- **Analise Completa**: [MELHORIAS_GOLD_SCALPING.md](MELHORIAS_GOLD_SCALPING.md)
- **Validacao**: [test_gold_v2_improvements.py](test_gold_v2_improvements.py)
- **Analise de Trades**: [analyze_gold_quick_detailed.py](analyze_gold_quick_detailed.py)

---

### 13. CHECKLIST ANTES DE USAR

- [ ] MT5 aberto e logado
- [ ] Simbolo XAUUSDc disponivel
- [ ] Margem suficiente (minimo $100)
- [ ] Validacao executada (`test_gold_v2_improvements.py`)
- [ ] Backup do banco de dados feito
- [ ] Internet estavel
- [ ] Horario adequado (London/NY session)

---

### 14. EXPECTATIVAS REALISTAS

#### Primeira Semana (10-20 trades)
- Win Rate: 55-60% (adaptacao)
- Net Result: Breakeven ou pequeno lucro
- Objetivo: Validar melhorias

#### Segunda Semana (30-50 trades)
- Win Rate: 60-65% (estabilizacao)
- Net Result: POSITIVO (+$20-50)
- Objetivo: Confirmar efetividade

#### Terceiro Mes (100+ trades)
- Win Rate: 60-65% (consolidado)
- Net Result: POSITIVO (+$100-200)
- Objetivo: Operacao estavel

---

BOA SORTE COM O GOLD AGENT v2.0.0!

Qualquer duvida, revise os documentos de suporte ou ajuste os parametros conforme necessario.
