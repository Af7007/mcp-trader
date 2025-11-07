# Worker Thread Debugging Guide

## Problema: Trailing Ativa Depois de 2.5s em vez de 0.02s

Se o trailing está ativando lentamente (após 2.5s+ em vez de 20ms), é sinal de que o **worker não está rodando**.

---

## Como Diagnosticar

### 1. Verificar Status do Worker no Output

Procure por estes prints no console ao executar `RUN_GOLD_AI.bat`:

**Esperado (Worker Ativo):**
```
[POSITIONS] Encontradas 1 posições abertas
[WORKER STATUS] Existe: True | Rodando: True
```

**Problema (Worker Não Rodando):**
```
[POSITIONS] Encontradas 1 posições abertas
[WORKER STATUS] Existe: True | Rodando: False
[WORKER] FALLBACK ATIVADO - Gerenciando trailing no loop principal

[TRAILING CALC] Protegendo $0.50
```

**Grave (Worker Nunca Criado):**
```
[POSITIONS] Encontradas 1 posições abertas
[WORKER STATUS] Existe: False
```

---

## Razões Comuns

### 1. **Worker Morreu Silenciosamente** (90% dos casos)

**Sintoma:** Worker Status mostra `Rodando: False` após ter sido criado

**Causa provável:** Exceção não-tratada no callback `_trailing_worker_callback`

**Verificação:**
```
Procure por "[WORKER] ERRO CRÍTICO" ou "[WORKER] Erro ao executar callback" no log
```

**Solução:**
- Verifique se há erros no console
- Certifique-se que os dicionários `positions_entry_price`, `positions_trailing_active`, `positions_trailing_stop`, `positions_trade_id` existem
- O worker agora é robusto e NÃO morre, mas logs mostram o problema

### 2. **Worker Nunca Foi Iniciado**

**Sintoma:** Worker Status mostra `Existe: False`

**Causa:** A ordem foi aberta com erro (retcode != 10009)

**Verificação:**
```
Procure por "[POSICAO ABERTA]" no console quando a ordem abre
Se não aparecer, a ordem não foi aberta com sucesso
```

**Solução:**
- Verifique se MT5 está conectado
- Verifique se há volume/margem suficiente
- Verifique conexão com servidor

### 3. **Condição de Corrida (Rare)**

**Sintoma:** Worker Status mostra `Rodando: True` MAS `[TRAILING CALC]` prints aparecem

**Causa:** Ambas (worker E _manage_position_trailing) estão rodando

**Solução:** Erro na lógica de verificação - reportar bug

---

## Output Esperado vs Real

### ✓ Comportamento Correto

```
[POSICAO ABERTA]: BUY $3988.46
   [DB] Trade registrado - ID: 1821 | Ticket: 114441279
   [WORKER] Monitoramento ULTRA-RÁPIDO INICIADO (check: 20ms = 50 checks/seg)

[POSICOES] Encontradas 1 posições abertas
[WORKER STATUS] Existe: True | Rodando: True
   ← Worker cuida do trailing silenciosamente ←

[WORKER] TRAILING ATIVADO! Lucro: $1.00 | Protege: $0.50
```

**Resultado:** Trailing ativa em ~20ms após atingir $1 de lucro


### ✗ Comportamento Problemático

```
[POSICAO ABERTA]: BUY $3988.46
   [DB] Trade registrado - ID: 1821 | Ticket: 114441279
   [WORKER] Monitoramento ULTRA-RÁPIDO INICIADO (check: 20ms = 50 checks/seg)

... 15 segundos depois ...

[POSICOES] Encontradas 1 posições abertas
[WORKER STATUS] Existe: True | Rodando: False
[WORKER] FALLBACK ATIVADO - Gerenciando trailing no loop principal

[TRAILING CALC] Protegendo $0.50
[TRAILING CALC] Pontos necessários: 250.0
[MT5] Tentando ATIVAR SL...
[MT5] ✅ SUCESSO! SL modificado
```

**Resultado:** Trailing ativa após 15s (lentíssimo!)


---

## Verificação de Logs

### 1. Procure por Erros do Worker

```bash
# No arquivo de log (se houver)
grep "\[WORKER\] ERRO" btc_trading_logs.log

# Ou no console, procure por:
[WORKER] ERRO CRÍTICO
[WORKER] Erro ao executar callback
```

### 2. Verifique Inicialização

```bash
# Procure por:
grep "\[WORKER\] Loop iniciado" output.log

# Se não encontrar, worker nunca iniciou
```

### 3. Verifique Checks

```bash
# Procure estatísticas:
[WORKER] Loop finalizado para XAUUSDc (total checks: 1500)

# Quer dizer: worker fez 1500 checks * 0.02s = 30 segundos de funcionamento
```

---

## Troubleshooting Passo a Passo

### Passo 1: Verificar Output
```
Ao abrir ordem, procure por:
[WORKER] Monitoramento ULTRA-RÁPIDO INICIADO (check: 20ms...)

Se NÃO aparecer → Ordem não foi aberta com sucesso
```

### Passo 2: Verificar Status
```
No próximo ciclo, procure por:
[WORKER STATUS] Existe: True | Rodando: True

Se Rodando: False → Worker morreu
```

### Passo 3: Procurar Erros
```
Se worker morreu, procure por erros:
[WORKER] ERRO CRÍTICO
[WORKER] Erro ao executar callback

Anote a mensagem de erro exata
```

### Passo 4: Relatar ou Debugar
```
Se encontrou erro do callback:
- Nota qual é a exceção (KeyError, AttributeError, etc)
- Reportar com o erro completo
- Código agora é robusto e continua mesmo com erro
```

---

## Melhorias Implementadas

1. **Worker nunca morre**
   - Callback errors não matam a thread
   - _run_loop errors não matam a thread
   - Tudo é logado para debugging

2. **Status visível**
   - Prints mostram se worker existe
   - Prints mostram se worker está rodando
   - Fácil de identificar problemas

3. **Fallback seguro**
   - Se worker falha, _manage_position_trailing ativa
   - Proteção é garantida mesmo sem worker
   - Mensagem clara quando fallback é usado

---

## Resumo Rápido

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Trailing ativa após 15s | Worker não está rodando | Verifique status do worker |
| [WORKER STATUS] Rodando: False | Worker morreu | Veja erros no console |
| [WORKER STATUS] Existe: False | Ordem não abriu | Verifique conexão MT5 |
| Sem [WORKER STATUS] | Ordem não foi aberta | Há erro na abertura |

---

## Esperado em Production

✓ Ordem abre → Worker inicia → Trailing ativa em 20ms quando lucro >= $1

Se isso não acontece, usar as dicas acima para debugar!
