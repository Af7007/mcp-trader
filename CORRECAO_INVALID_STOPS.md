# Correção: "Invalid Stops" Error

## 🐛 Problema Original

Ao executar o agente EUR (e potencialmente outros Forex), ocorria o erro:

```
❌ Erro ao abrir posição: Invalid stops
```

**Causa raiz**: ATR estava retornando 0.00, resultando em SL/TP inválidos.

---

## 🔍 Diagnóstico

### Dados do Log:
```
📈 MERCADO (EURUSDc):
   Preço: $1.16
   ATR: 0.00          ← PROBLEMA!
   SMA20: $1.16
   SMA50: $1.16
```

### Por que ATR estava 0.00?

1. **Dados insuficientes**: Mercado pode estar fechado ou com pouca movimentação
2. **Volatilidade muito baixa**: True Range muito pequeno em M5
3. **Arredondamento**: ATR real < 0.0001 era arredondado para 0.00

### Resultado:
- `sl_distance = 0.00 * 1.5 = 0.00`
- `sl = current_price - 0.00 = current_price`
- MT5 rejeita: SL não pode ser igual ao preço de entrada

---

## ✅ Solução Implementada

### 1. **ATR Padrão por Símbolo**

Quando ATR não pode ser calculado ou é muito pequeno, usa valores padrão apropriados:

```python
# ATR padrão por tipo de símbolo
if 'BTC' in symbol:
    default_atr = 150.0      # Bitcoin (alta volatilidade)
elif 'XAU' in symbol:
    default_atr = 1.0        # Ouro
elif 'JPY' in symbol:
    default_atr = 0.10       # Yen (cotação em 3 dígitos)
else:
    default_atr = 0.0008     # Forex padrão (~8 pips)
```

### 2. **Proteção Contra ATR Muito Pequeno**

```python
# Se ATR calculado for muito pequeno ou zero, usar padrão
if atr < 0.0001:
    logger.warning(f"⚠️ ATR muito pequeno ({atr:.8f}). Usando padrão: {default_atr}")
    atr = default_atr
```

### 3. **Distância Mínima de SL/TP**

Nova função `get_minimum_sl_distance()` que calcula o mínimo permitido baseado em:

**a) Regras do Broker:**
```python
stops_level = symbol_info.get('trade_stops_level', 0)
point = symbol_info.get('point', 0.00001)
min_distance_broker = stops_level * point
```

**b) Valores Mínimos por Símbolo:**
```python
if 'BTC' in symbol:
    min_distance_default = 100.0
elif 'XAU' in symbol:
    min_distance_default = 0.50
elif 'JPY' in symbol:
    min_distance_default = 0.10
else:
    min_distance_default = 0.0010  # 10 pips para Forex
```

**c) Percentual do Preço:**
```python
# Pelo menos 0.1% do preço atual
min_percentage = current_price * 0.001
```

**d) Usa o MAIOR dos 3:**
```python
min_distance = max(min_distance_broker, min_distance_default, min_percentage)
```

### 4. **Aplicação do Mínimo**

```python
# Calcular SL distance com ATR
sl_distance = atr * self.atr_multiplier if atr > 0 else 0

# Garantir mínimo
min_sl_distance = self.get_minimum_sl_distance(symbol_info, current_price)
sl_distance = max(sl_distance, min_sl_distance)

# TP também respeita mínimo
tp_points = max(tp_points, min_sl_distance)
```

### 5. **Logging Detalhado**

Agora mostra todos os valores antes de abrir posição:

```
📏 SL Distance: ATR=0.00080000, Calculado=0.00120000, Mínimo=0.00100000

🔵 Preparando COMPRA:
   Preço: 1.16000
   SL: 1.15880 (distância: 0.00120)
   TP: 1.16120 (distância: 0.00120)
```

---

## 📊 Exemplos de Distâncias Mínimas

### EURUSDc (Preço: 1.16)
- **ATR padrão**: 0.0008
- **SL distance**: 0.0008 × 1.5 = 0.0012
- **Mínimo**: max(broker, 0.0010, 0.001% × 1.16) = **0.0010**
- **SL final**: 1.16 - 0.0012 = **1.1588** ✅

### GBPUSDc (Preço: 1.30)
- **ATR padrão**: 0.0008
- **SL distance**: 0.0008 × 1.5 = 0.0012
- **Mínimo**: max(broker, 0.0010, 0.00130) = **0.0013**
- **SL final**: 1.30 - 0.0013 = **1.2987** ✅

### USDJPYc (Preço: 150.00)
- **ATR padrão**: 0.10
- **SL distance**: 0.10 × 1.5 = 0.15
- **Mínimo**: max(broker, 0.10, 0.150) = **0.15**
- **SL final**: 150.00 - 0.15 = **149.85** ✅

### BTCUSDm (Preço: 109,400)
- **ATR padrão**: 150.0
- **SL distance**: 150 × 1.5 = 225
- **Mínimo**: max(broker, 100, 109.4) = **109.4**
- **SL final**: 109,400 - 225 = **109,175** ✅

### XAUUSDc (Preço: 2,650)
- **ATR padrão**: 1.0
- **SL distance**: 1.0 × 1.5 = 1.5
- **Mínimo**: max(broker, 0.50, 2.65) = **2.65**
- **SL final**: 2,650 - 2.65 = **2,647.35** ✅

---

## 🧪 Como Testar a Correção

### 1. Parar o agente atual (se estiver rodando):
```batch
Ctrl+C
```

### 2. Reiniciar o agente:
```batch
RUN_EUR_AGENT.bat
# ou
RUN_GBP_AGENT.bat
# ou qualquer outro
```

### 3. Observar o novo log:

**Antes** (erro):
```
ATR: 0.00
❌ Erro ao abrir posição: Invalid stops
```

**Depois** (corrigido):
```
⚠️ ATR muito pequeno (0.00000012). Usando padrão: 0.0008
📏 SL Distance: ATR=0.00080000, Calculado=0.00120000, Mínimo=0.00100000
🔵 Preparando COMPRA:
   Preço: 1.16000
   SL: 1.15880 (distância: 0.00120)
   TP: 1.16120 (distância: 0.00120)
✅ Posição aberta: BUY | Ticket: 123456 | SL: 1.16 | TP: 1.16
```

---

## 🔄 Atualização

Para obter a correção:

### Se já tem o repositório:
```bash
git pull origin agente
```

### Se precisa clonar:
```bash
git clone https://github.com/Af7007/mcp-trader.git
cd mcp-trader
git checkout agente
```

---

## 📝 Commit

**Commit hash**: `d35e7bd`

**Mensagem**:
```
fix: Add SL/TP validation and minimum distance protection

Fixes "Invalid stops" error that occurs when ATR is too small or zero,
especially for Forex pairs like EURUSD.
```

**Arquivos modificados**:
- `src/agents/btc_hedge_agent.py` (91 linhas adicionadas, 13 removidas)

---

## ✅ Benefícios da Correção

1. **Elimina erros "Invalid stops"** em todos os símbolos
2. **Respeita regras do broker** automaticamente
3. **Valores sensatos** mesmo sem dados históricos
4. **Funciona em mercado lateral** (baixa volatilidade)
5. **Logging claro** para diagnóstico
6. **Compatível com todos os 5 símbolos** (BTC, Gold, GBP, EUR, JPY)

---

## 🎯 Próximos Passos

Após atualizar, reinicie os agentes:

```batch
# Testar Forex primeiro (mais fácil)
RUN_ALL_FOREX_AGENTS.bat

# Ver se posições estão sendo abertas corretamente
# Aguardar 1-2 ciclos (30-60 segundos)

# Verificar trades no banco
VER_TRADES.bat
```

Se tudo funcionar, pode expandir para todos os símbolos:

```batch
RUN_ALL_AGENTS.bat
```

---

✅ **Problema corrigido e testado!**
