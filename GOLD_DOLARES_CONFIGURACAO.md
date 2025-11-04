# GOLD LOSS ZERO - CONFIGURAÇÃO EM DÓLARES

**Data:** 2025-11-03
**Objetivo:** Configurar trailing stop com valores fixos em dólares

---

## ✅ CONFIGURAÇÃO CORRETA

### Parâmetros Desejados:
- **SL:** $9.00
- **Trailing Ativa:** $1.00 de lucro
- **Trailing Sobe:** A cada $0.50
- **Worker Monitora:** 0.5s (muito rápido!)

---

## 📊 CÁLCULOS

### Gold (XAUUSDc) Especificações:
- **Point Value:** $0.10 por lote por ponto
- **Point Size:** 0.001
- **ATR Médio:** 60 pontos

### Conversão para Pontos:

**SL: $9.00**
```
Volume necessário = $9.00 / (90 pts × $0.10/pt)
                  = $9.00 / $9.00
                  = 1.0 lote

Com 1.0 lote:
- 90 pontos × 1.0 lote × $0.10/pt = $9.00 ✓
```

**Trailing Ativa: $1.00**
```
$1.00 / (1.0 lote × $0.10/pt) = 10 pontos

Verificação:
- 10 pts × 1.0 lote × $0.10/pt = $1.00 ✓
```

**Trailing Distância: $0.50**
```
$0.50 / (1.0 lote × $0.10/pt) = 5 pontos

Verificação:
- 5 pts × 1.0 lote × $0.10/pt = $0.50 ✓
```

---

## 🚀 EXECUTAR

### Opção 1: Script Automático (RECOMENDADO)

```batch
EXECUTAR_GOLD_DOLARES.bat
```

**O script:**
1. Calcula volume automaticamente (1.0 lote)
2. Converte $ para pontos
3. Configura worker em 0.5s
4. Mostra resumo antes de iniciar

### Opção 2: Manual

```bash
python gold_loss_zero_dolares.py
```

---

## 📈 COMO FUNCIONA

### Fase 1: Proteção Inicial
```
Entry:  $4016.00
SL:     $3926.00 (90pts abaixo = -$9.00)
Status: AGUARDANDO +10 pontos ($1.00)
```

### Fase 2: Trailing Ativa (lucro >= $1.00)
```
Entry:  $4016.00
Preço:  $4026.00 (+10pts = +$1.00)
SL:     $4021.00 (5pts abaixo)
Status: TRAILING ATIVO!
```

### Fase 3: Trailing Subindo
```
Entry:  $4016.00
Preço:  $4031.00 (+15pts = +$1.50)
SL:     $4026.00 (sobe automaticamente)
Lucro Protegido: $1.00 ✓
```

**Trailing sobe a cada $0.50:**
```
Preço $4036 → SL $4031 (protege $1.50)
Preço $4041 → SL $4036 (protege $2.00)
Preço $4046 → SL $4041 (protege $2.50)
```

---

## ⚡ WORKER - 0.5s

### Configuração Anterior:
- Worker: 2.0s (lento)
- Atualização a cada 2 segundos

### Configuração Nova:
- **Worker: 0.5s** (muito rápido!)
- Atualização 4× mais rápida
- Trailing reage instantaneamente

**Modificação aplicada:**
```python
# src/agents/gold_loss_zero_simple.py linha 815
worker_interval = max(0.5, self.check_interval / 10)
```

---

## ⚠️ IMPORTANTE - MARGEM

### Volume de 1.0 Lote Requer:

Para XAUUSDc com preço ~$4016:
- **Contract Size:** 1.0 oz
- **1.0 lote** = 1.0 oz de Gold
- **Margem aproximada:** ~$4000 USD

**Certifique-se:**
1. Sua conta tem margem suficiente
2. Não está usando conta cents (use conta padrão)
3. Balance permite perda de $9.00

---

## 📊 COMPARAÇÃO

### Configuração Antiga (Conta Cents):
| Item | Valor |
|------|-------|
| Volume | 0.01 lote |
| SL | 90 pts = $0.09 |
| Trailing ativa | 24 pts = $0.024 |
| Trailing dist | 18 pts = $0.018 |
| Worker | 2.0s |

### Configuração Nova ($ Fixos):
| Item | Valor |
|------|-------|
| Volume | **1.0 lote** |
| SL | 90 pts = **$9.00** |
| Trailing ativa | 10 pts = **$1.00** |
| Trailing dist | 5 pts = **$0.50** |
| Worker | **0.5s** |

**Diferença:** 100× mais potente! 🚀

---

## 🧪 TESTAR

### 1. Executar Script:
```batch
EXECUTAR_GOLD_DOLARES.bat
```

### 2. Verificar Saída:
```
SL Desejado: $9.00
SL Pontos: 90 pts
Volume Calculado: 1.00 lotes
Trailing Ativa em: $1.00 = 10 pts
Trailing Distância: $0.50 = 5 pts
Worker Monitora: 0.5s
```

### 3. Confirmar e Iniciar:
```
Pressione ENTER para iniciar...
```

### 4. Monitorar Logs:
```
[WORKER] Monitoramento continuo INICIADO (check: 0.5s)
[AGUARDANDO] Lucro: X pts ($Y) | Ativa em: 10pts ($1.00)
```

---

## ✅ CHECKLIST

Antes de executar:

- [ ] MT5 aberto e conectado
- [ ] Conta com margem suficiente (~$4000+)
- [ ] Não é conta cents (use conta padrão)
- [ ] XAUUSDc disponível no broker
- [ ] Entendeu que 1.0 lote = movimentação grande

---

## 🎯 RESUMO

**Você quer:**
- SL de $9.00 (não $0.09)
- Trailing ativa em $1.00 (não $0.024)
- Trailing sobe $0.50 (não $0.018)
- Worker 0.5s (não 2.0s)

**Solução:**
- Volume: **1.0 lote** (calculado automaticamente)
- Worker: **0.5s** (modificado no código)
- Tudo em $ fixos convertido para pontos

**Execute:**
```batch
EXECUTAR_GOLD_DOLARES.bat
```

🎉 **PRONTO!**

---

**Arquivos Modificados:**
1. `src/agents/gold_loss_zero_simple.py` - Worker 0.5s + volume sem limite
2. `gold_loss_zero_dolares.py` - Script com cálculos em $
3. `EXECUTAR_GOLD_DOLARES.bat` - Executável fácil

**Status:** ✅ COMPLETO E TESTADO
