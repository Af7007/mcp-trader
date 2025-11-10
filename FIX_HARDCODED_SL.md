# FIX: Hardcoded SL Parameter

**Data**: 2025-11-09
**Problema**: SL mostrando $20.00 mesmo com --fixed-sl-dollars 8.0
**Causa Raiz**: Valor hardcoded na classe pai ignorava parametro
**Solucao**: Usar parametro ao inves de hardcoded value

---

## PROBLEMA REPORTADO

Usuario rodou BTC AI Agent com `--fixed-sl-dollars 8.0` mas viu nos logs:
```
[AGENTE]:
   SL Fixo: $20.00
```

Mesmo apos multiplos restarts e correcoes anteriores, o SL continuava $20.

---

## CAUSA RAIZ

**Arquivo**: `src/agents/btc_loss_zero_v3.py`
**Linha 67**: Valor hardcoded ignorava parametro

**ANTES (ERRADO)**:
```python
def __init__(
    self,
    symbol: str = "BTCUSDc",
    volume: float = 0.30,
    check_interval: int = 1,
    stop_loss_atr_multiplier: float = 5.0,
    fixed_sl_dollars: float = 5.0,  # Parametro definido aqui
    use_buy: bool = True,
    use_sell: bool = True
):
    # ... outras inicializacoes ...
    self.fixed_sl_dollars = 20.0  # IGNORAVA O PARAMETRO!
```

O metodo `__init__` RECEBIA `fixed_sl_dollars` como parametro, mas IGNORAVA completamente e usava valor hardcoded.

---

## SOLUCAO APLICADA

**Arquivo**: `src/agents/btc_loss_zero_v3.py` (linha 67)

**ANTES**:
```python
self.fixed_sl_dollars = 20.0  # v3.2.0: $20 (maior espaco para timing de entrada)
```

**DEPOIS**:
```python
self.fixed_sl_dollars = fixed_sl_dollars  # v3.2.0: Usar parametro (default 5.0, ou 8.0 do btc_ai_agent)
```

---

## COMO FUNCIONA AGORA

### 1. Classe Pai (BTCLossZeroV3)
```python
def __init__(self, ..., fixed_sl_dollars: float = 5.0, ...):
    self.fixed_sl_dollars = fixed_sl_dollars  # Usa o parametro!
```

### 2. Classe Filha (BTCAIAgent)
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)  # Passa fixed_sl_dollars para pai
```

### 3. Linha de Comando
```bash
python src/agents/btc_ai_agent.py --fixed-sl-dollars 8.0
```

### 4. Argparse
```python
parser.add_argument('--fixed-sl-dollars', type=float, default=8.0)
agent = BTCAIAgent(
    symbol=args.symbol,
    volume=args.volume,
    fixed_sl_dollars=args.fixed_sl_dollars  # Passa para __init__
)
```

---

## VERIFICACAO

**Script de teste**: `test_sl_parameter.py`

**Resultado esperado**:
```
Test 1: Default (sem passar parametro)
   SL fixo: $5.00  (default da classe pai)

Test 2: fixed_sl_dollars=8.0 (via parametro)
   SL fixo: $8.00  (usa o valor passado!)

Test 3: Verificando codigo fonte...
   [OK] Parametro fixed_sl_dollars sendo usado corretamente
```

---

## TESTE FINAL

Execute o BTC AI Agent:
```bash
RUN_BTC_AI.bat
```

**Output esperado no console**:
```
============================================================
BTC AI AGENT - SEM INDICADORES TRADICIONAIS
============================================================
   CONFIGURACAO BTC AI:
   - SL fixo: $8.00  <- CORRIGIDO!
   - Volume: 0.05 lotes
   - Trailing: Ativa $4.00, protege $2.00
============================================================

Cycle #1:
[AGENTE]:
   Estado: BTC AI (IA + Trailing)
   SL Fixo: $8.00  <- CORRIGIDO!
```

---

## IMPACTO

### Antes do Fix
- Parametro `--fixed-sl-dollars` era IGNORADO
- SL sempre abria em $20.00 (hardcoded)
- Nao importava o valor passado na linha de comando

### Depois do Fix
- Parametro `--fixed-sl-dollars` e RESPEITADO
- SL abre com o valor solicitado ($8.00)
- Default e $5.00 (se nao passar parametro)
- BTC AI Agent usa $8.00 (definido no argparse default)

---

## ARQUIVOS MODIFICADOS

**src/agents/btc_loss_zero_v3.py**:
- Linha 67: `self.fixed_sl_dollars = fixed_sl_dollars` (ao inves de hardcoded 20.0)

**Nenhuma outra modificacao necessaria**:
- btc_ai_agent.py: JA passava parametro corretamente via `**kwargs`
- RUN_BTC_AI.bat: JA passava `--fixed-sl-dollars 8.0` corretamente

---

## CONCLUSAO

A causa raiz foi um valor **hardcoded esquecido** na classe pai que sobrescrevia o parametro recebido no `__init__`.

**Fix aplicado**: Uma linha mudada - usar o parametro ao inves do valor hardcoded.

**Resultado**: Agora o SL respeita o valor passado na linha de comando!
