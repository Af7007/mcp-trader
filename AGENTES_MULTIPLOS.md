# Agentes Múltiplos - BTC + Gold

## 🎯 Estratégia Multi-Símbolo

Execute a mesma estratégia de hedge simultaneamente em diferentes símbolos para diversificar e maximizar oportunidades.

---

## 📊 Símbolos Disponíveis

### Crypto/Commodities

#### 1. Bitcoin (BTCUSDm)
- **Volume**: 0.02 lots
- **Características**: Alta volatilidade, movimentos grandes
- **ATR Médio**: ~150-300 pontos
- **Script**: `RUN_BTC_AGENT.bat`

#### 2. Ouro (XAUUSDm)
- **Volume**: 0.01 lots (menor devido ao valor do ouro)
- **Características**: Volatilidade moderada, safe haven
- **ATR Médio**: ~0.50-2.00 pontos
- **Script**: `RUN_GOLD_AGENT.bat`

### Forex (Pares de Moedas)

#### 3. Libra Esterlina (GBPUSDc)
- **Volume**: 0.10 lots
- **Características**: Alta liquidez, volátil entre pares forex
- **ATR Médio**: ~0.0010-0.0020
- **Script**: `RUN_GBP_AGENT.bat`

#### 4. Euro (EURUSDc)
- **Volume**: 0.10 lots
- **Características**: Maior liquidez do mundo, mais estável
- **ATR Médio**: ~0.0008-0.0015
- **Script**: `RUN_EUR_AGENT.bat`

#### 5. Yen Japonês (USDJPYc)
- **Volume**: 0.10 lots
- **Características**: Safe haven, correlação negativa com risco
- **ATR Médio**: ~0.08-0.15 (cotação em 3 dígitos)
- **Script**: `RUN_JPY_AGENT.bat`

---

## 🚀 Executando Agentes

### Opção 1: Um Agente por Vez

**Crypto/Commodities:**
```batch
RUN_BTC_AGENT.bat   # Bitcoin
RUN_GOLD_AGENT.bat  # Ouro
```

**Forex:**
```batch
RUN_GBP_AGENT.bat   # Libra
RUN_EUR_AGENT.bat   # Euro
RUN_JPY_AGENT.bat   # Yen
```

### Opção 2: Múltiplos Agentes por Categoria

**Crypto + Commodities (BTC + Gold):**
```batch
RUN_MULTI_AGENTS.bat
```

**Todos os Forex (GBP + EUR + JPY):**
```batch
RUN_ALL_FOREX_AGENTS.bat
```

### Opção 3: TODOS os Agentes (5 símbolos)

**BTC + Gold + GBP + EUR + JPY:**
```batch
RUN_ALL_AGENTS.bat
```

⚠️ **AVISO**: Requer margem livre de $5,000+

---

Cada janela representa um agente independente com:
- Contadores de operações (20 por dia cada)
- Métricas de lucro separadas
- Estratégias de hedge próprias
- Winning streaks individuais

---

## ⚙️ Configurações por Símbolo

### BTCUSDm (Bitcoin)
```
Symbol: BTCUSDm
Volume: 0.02 lots
Target Profit: $2
Daily Limit: 20 operações
SL: 1.5x ATR (~272 pontos)
TP: Calculado dinamicamente
```

### XAUUSDm (Ouro)
```
Symbol: XAUUSDm
Volume: 0.01 lots
Target Profit: $2
Daily Limit: 20 operações
SL: 1.5x ATR (~1.5-3.0 pontos)
TP: Calculado dinamicamente
```

### GBPUSDc (Libra)
```
Symbol: GBPUSDc
Volume: 0.10 lots
Target Profit: $2
Daily Limit: 20 operações
SL: 1.5x ATR (~0.0015-0.0030)
TP: Calculado dinamicamente
```

### EURUSDc (Euro)
```
Symbol: EURUSDc
Volume: 0.10 lots
Target Profit: $2
Daily Limit: 20 operações
SL: 1.5x ATR (~0.0012-0.0023)
TP: Calculado dinamicamente
```

### USDJPYc (Yen)
```
Symbol: USDJPYc
Volume: 0.10 lots
Target Profit: $2
Daily Limit: 20 operações
SL: 1.5x ATR (~0.12-0.23)
TP: Calculado dinamicamente
```

---

## 🧪 Testando Símbolos

Antes de operar, teste se os símbolos estão disponíveis:

**Testar Crypto/Commodities:**
```batch
uv run python test_btc_symbol.py    # Bitcoin
TESTAR_GOLD.bat                      # Ouro
```

**Testar Forex:**
```batch
TESTAR_FOREX.bat                     # GBP + EUR + JPY (todos de uma vez)
```

Ou use Python diretamente:
```bash
uv run python test_forex_symbols.py  # Testa os 3 pares forex
uv run python test_gold_symbol.py    # Testa ouro
uv run python test_btc_symbol.py     # Testa bitcoin
```

---

## 📈 Monitoramento

### Dashboard MT5 Visual

O mesmo dashboard funciona para **todos os símbolos**!

1. **Para BTC**: Adicione `BTC_Agent_Dashboard.mq5` ao gráfico BTCUSDm
2. **Para Gold**: Adicione o mesmo dashboard ao gráfico XAUUSDm

O dashboard detecta automaticamente qual símbolo está sendo negociado através do arquivo `agent_data.json`.

**Limitação**: O dashboard mostra dados do **último agente** que exportou JSON. Para monitorar múltiplos agentes, seria necessário:
- Criar dashboards separados (opcional)
- Ou modificar o agente para exportar arquivos JSON separados por símbolo

---

## 💾 Banco de Dados

Todos os trades de **todos os agentes** são salvos no mesmo banco de dados SQLite.

**Visualizar todos os trades:**
```batch
VER_TRADES.bat
```

Ou:
```bash
uv run python ver_trades_banco.py
```

O banco mostra:
- Símbolo de cada trade (BTCUSDm, XAUUSDm, etc.)
- Lucros separados
- Estatísticas consolidadas

**Filtrar por símbolo** (adicionar ao script se necessário):
```sql
SELECT * FROM trades WHERE symbol = 'XAUUSDm'
```

---

## 🛑 Parando Agentes

### Parar Um Agente Específico
- Feche a janela do agente (Ctrl+C ou X)

### Parar Todos os Agentes
```batch
STOP_ALL_AGENTS.bat
```

Ou manualmente:
```batch
taskkill /F /IM python.exe
```

---

## 📊 Estratégia de Diversificação

### Por que rodar múltiplos símbolos?

1. **Diversificação de Risco**
   - BTC e Ouro têm correlação baixa
   - Quando um está lateral, outro pode estar em tendência

2. **Mais Oportunidades**
   - 20 operações/dia no BTC
   - 20 operações/dia no Ouro
   - = 40 operações totais possíveis

3. **Hedge Natural**
   - Ouro tende a subir em momentos de risco (risk-off)
   - BTC pode ter movimentos independentes

4. **Mesmo Capital, Múltiplos Ativos**
   - Volumes ajustados para risco similar
   - Target profit igual ($2) para cada

---

## ⚠️ Requisitos de Margem

**IMPORTANTE**: Certifique-se de ter margem suficiente!

### Cálculo Aproximado por Símbolo

**Crypto/Commodities:**
- BTCUSDm 0.02 lots: ~$2,000 de margem
- XAUUSDm 0.01 lots: ~$300 de margem

**Forex:**
- GBPUSDc 0.10 lots: ~$130 de margem
- EURUSDc 0.10 lots: ~$110 de margem
- USDJPYc 0.10 lots: ~$100 de margem

### Total por Configuração

**Opção 1**: BTC + Gold (2 agentes)
- Margem necessária: ~$2,500
- Recomendado: $5,000+ livre

**Opção 2**: Todos Forex (3 agentes)
- Margem necessária: ~$400
- Recomendado: $1,000+ livre

**Opção 3**: TODOS (5 agentes)
- Margem necessária: ~$2,900
- **Recomendado: $6,000+ livre**

**Margem de segurança**: Recomendado ter pelo menos **2x** a margem necessária para suportar múltiplas posições simultâneas e hedges.

*Valores aproximados - varia conforme broker e alavancagem*

---

## 🔧 Customização

### Adicionar Novos Símbolos

Para adicionar EUR, Petróleo, etc:

1. **Teste o símbolo:**
```python
# Criar test_eur_symbol.py baseado em test_gold_symbol.py
```

2. **Crie o script de execução:**
```batch
# RUN_EUR_AGENT.bat
uv run python src\agents\btc_hedge_agent.py EURUSDc 0.10
```

3. **Ajuste os parâmetros:**
   - Volume apropriado para o símbolo
   - Target profit (opcional)
   - Timeframe (opcional, modificar código)

---

## 📝 Logs e Dados

### Arquivos Gerados

Cada agente gera:
- **JSON Export**: `agent_data.json` (sobrescrito - último agente)
- **Database**: `trades.db` (compartilhado - todos os agentes)
- **Logs**: Console de cada janela

### Melhorias Futuras

Para melhor separação de dados:
```python
# Modificar export_to_json para:
json_path = Path(f'C:/mcp-trader/agent_data_{self.symbol}.json')
```

Isso permite dashboards separados para cada símbolo.

---

## ✅ Checklist de Operação

Antes de iniciar múltiplos agentes:

- [ ] MT5 está aberto e logado
- [ ] Símbolos estão no Market Watch (BTCUSDm, XAUUSDm)
- [ ] Margem livre suficiente ($2,500+)
- [ ] Scripts de teste executados com sucesso
- [ ] Banco de dados inicializado (`setup_database()`)
- [ ] Confirmação de operar com dinheiro real

---

## 🎯 Exemplo de Sessão

### Sessão Forex (Recomendado para Iniciantes)

```batch
# 1. Testar símbolos Forex
TESTAR_FOREX.bat

# 2. Verificar margem no MT5
# Margem Livre > $1,000

# 3. Iniciar agentes Forex
RUN_ALL_FOREX_AGENTS.bat

# 4. Monitorar
# - 3 janelas de console (GBP + EUR + JPY)
# - Trades no MT5

# 5. Após algumas horas
VER_TRADES.bat  # Ver estatísticas

# 6. Finalizar
STOP_ALL_AGENTS.bat
```

### Sessão Completa (Avançado)

```batch
# 1. Testar TODOS os símbolos
uv run python test_btc_symbol.py
TESTAR_GOLD.bat
TESTAR_FOREX.bat

# 2. Verificar margem no MT5
# Margem Livre > $6,000

# 3. Iniciar TODOS os agentes
RUN_ALL_AGENTS.bat

# 4. Monitorar
# - 5 janelas de console
# - Dashboards no MT5 (opcional)
# - Trades no MT5

# 5. Após algumas horas
VER_TRADES.bat  # Ver estatísticas

# 6. Finalizar
STOP_ALL_AGENTS.bat
```

---

## 💡 Dicas

1. **Começar com um agente**: Teste primeiro com BTC ou Gold antes de rodar múltiplos

2. **Monitorar margem**: Use o MT5 para acompanhar margem livre em tempo real

3. **Limite diário**: 20 ops/símbolo previne over-trading

4. **Hedge automático**: Cada agente ativa hedge independentemente

5. **Logs separados**: Cada janela mostra logs do seu agente

---

✅ **Agentes múltiplos configurados e prontos para uso!**
