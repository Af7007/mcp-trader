# GOLD LOSS ZERO - CONFIGURAÇÃO COM 0.02 LOTE

**Data:** 2025-11-03
**Volume Fixo:** 0.02 lote
**Worker:** 0.5s

---

## ✅ CONFIGURAÇÃO COM 0.02 LOTE

### Parâmetros:
- **Volume:** 0.02 lote (FIXO)
- **Worker:** 0.5s (muito rápido!)
- **Multiplicadores:** Padrão otimizado

---

## 📊 VALORES REAIS EM DÓLARES

### Cálculo Base:
```
Point Value Gold: $0.10 por lote por ponto
Com 0.02 lote: 1 ponto = 0.02 × $0.10 = $0.002
```

### Stop Loss (SL):
```
90 pontos (1.5 × ATR 60)
90 pts × $0.002 = $0.18
```
**Risco:** $0.18 por operação

### Trailing Activation:
```
24 pontos (0.4 × ATR 60)
24 pts × $0.002 = $0.048 ≈ $0.05
```
**Ativa em:** $0.05 de lucro

### Trailing Distance:
```
18 pontos (0.3 × ATR 60)
18 pts × $0.002 = $0.036 ≈ $0.04
```
**Distância:** $0.04 do preço atual

---

## 📈 RESUMO

| Item | Pontos | Dólares |
|------|--------|---------|
| **Volume** | - | 0.02 lote |
| **SL** | 90 pts | $0.18 |
| **Trailing Ativa** | 24 pts | $0.05 |
| **Trailing Dist** | 18 pts | $0.04 |
| **Worker** | - | 0.5s |
| **Point Value** | 1 pt | $0.002 |

---

## 💰 EXEMPLO DE OPERAÇÃO

### Abertura:
```
Entry:  $4016.00
SL:     $3926.00 (90 pts abaixo)
Risco:  $0.18
Status: AGUARDANDO +24 pts ($0.05)
```

### Trailing Ativa (após +24pts):
```
Entry:  $4016.00
Preço:  $4040.00 (+24 pts)
SL:     $4022.00 (18 pts abaixo)
Lucro Protegido: $0.01
Status: TRAILING ATIVO!
```

### Trailing Subindo:
```
Preço $4045 → SL $4027 (protege $0.02)
Preço $4050 → SL $4032 (protege $0.03)
Preço $4060 → SL $4042 (protege $0.05)
```

**A cada 5 pontos de movimento, o SL sobe e protege mais $0.01**

---

## ⚡ WORKER 0.5s

### Monitoramento Rápido:
- Atualiza a cada **0.5 segundos**
- **4× mais rápido** que o padrão (2.0s)
- Trailing reage **instantaneamente**
- Maximiza proteção de lucros

### Comparação:
| Worker | Atualizações/min | Reação |
|--------|------------------|--------|
| 2.0s | 30× | Lenta |
| **0.5s** | **120×** | **Instantânea** ✓ |

---

## 🚀 EXECUTAR

```batch
EXECUTAR_GOLD_0.02.bat
```

**Ou manualmente:**
```bash
python gold_loss_zero_0.02.py
```

---

## 📊 COMPARAÇÃO COM OUTRAS CONFIGURAÇÕES

### Configuração Antiga (0.01 lote):
| Item | Valor |
|------|-------|
| Volume | 0.01 lote |
| SL | 90 pts = $0.09 |
| Trailing ativa | 24 pts = $0.024 |
| Trailing dist | 18 pts = $0.018 |
| Worker | 2.0s |

### Configuração Nova (0.02 lote):
| Item | Valor |
|------|-------|
| Volume | **0.02 lote** |
| SL | 90 pts = **$0.18** |
| Trailing ativa | 24 pts = **$0.05** |
| Trailing dist | 18 pts = **$0.04** |
| Worker | **0.5s** |

**Diferenças:**
- **2× mais volume** (0.01 → 0.02)
- **2× mais risco/lucro** ($0.09 → $0.18)
- **4× mais rápido** (2.0s → 0.5s)

---

## ⚠️ IMPORTANTE

### Margem Necessária:
```
0.02 lote de Gold (XAUUSDc)
Preço: ~$4,016
Margem aprox: ~$80 USD
```

### Risco por Trade:
```
SL: $0.18 (muito conservador)
100 trades: $18 de risco máximo
```

### Lucro Potencial:
```
Se trailing proteger 50 pts:
50 pts × $0.002 = $0.10 lucro
```

---

## 🎯 QUANDO USAR

### Use 0.02 lote quando:
- ✅ Quer 2× mais movimento que 0.01
- ✅ Conta permite risco de $0.18/trade
- ✅ Quer lucros potenciais maiores
- ✅ Tem margem disponível (~$80)

### Use 0.01 lote quando:
- ✅ Quer ser muito conservador
- ✅ Conta pequena
- ✅ Testando estratégia
- ✅ Risco de $0.09/trade é suficiente

---

## ✅ CHECKLIST

Antes de executar:

- [ ] MT5 aberto e conectado
- [ ] XAUUSDc disponível
- [ ] Margem disponível (~$80)
- [ ] Entendeu risco de $0.18/trade
- [ ] Worker 0.5s está OK (rápido)

---

## 🧪 LOGS ESPERADOS

### Ao Iniciar:
```
Volume: 0.02 lote (FIXO)
SL: 90 pts = $0.18
Trailing Ativa: 24 pts = $0.05
Worker: 0.5s
```

### Durante Operação:
```
[WORKER] Monitoramento continuo INICIADO (check: 0.5s)
[AGUARDANDO] Lucro: X pts ($Y) | Ativa em: 24pts ($0.05)
```

### Quando Trailing Ativar:
```
[WORKER] TRAILING ATIVADO! Lucro: 24.0pts ($0.05)
[WORKER] Trailing subiu: $4022.00 -> $4025.00 (+3.00)
```

---

## 📝 RESUMO FINAL

**Você configurou:**
- ✅ Volume: 0.02 lote (fixo)
- ✅ Worker: 0.5s (4× mais rápido)
- ✅ SL: $0.18 (risco controlado)
- ✅ Trailing: Ativa em $0.05

**Para executar:**
```batch
EXECUTAR_GOLD_0.02.bat
```

**Valores reais em $ calculados automaticamente!** ✓

---

**Arquivos:**
- `gold_loss_zero_0.02.py` - Script configurado
- `EXECUTAR_GOLD_0.02.bat` - Executável
- `GOLD_0.02_LOTE_CONFIG.md` - Esta documentação

**Status:** ✅ PRONTO PARA USO!
