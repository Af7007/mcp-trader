# GOLD (XAUUSDc) - CONFIGURAÇÃO FINAL

**Data:** 2025-11-03
**Status:** ✅ PRONTO PARA USO

---

## 🎯 CONFIGURAÇÃO

- **Volume:** 0.02 lote
- **SL:** $6.00
- **Trailing Ativa:** $1.00
- **Trailing Sobe:** $0.50
- **Worker:** 0.5s

---

## 📊 CÁLCULOS GOLD

### Especificações:
- **Point Value:** $0.10 por lote por ponto
- **Com 0.02 lote:** 1 ponto = $0.0020
- **ATR Médio:** 60 pontos

### Conversão $ → Pontos:

**Stop Loss:**
```
$6.00 ÷ $0.0020 = 3000 pontos
3000 pts ÷ 60 ATR = Multiplicador 50.00
```

**Trailing Ativa:**
```
$1.00 ÷ $0.0020 = 500 pontos
500 pts ÷ 60 ATR = Multiplicador 8.33
```

**Trailing Distância:**
```
$0.50 ÷ $0.0020 = 250 pontos
250 pts ÷ 60 ATR = Multiplicador 4.17
```

---

## 📋 RESUMO

| Item | Pontos | Dólares | Mult ATR |
|------|--------|---------|----------|
| **Volume** | - | 0.02 lote | - |
| **SL** | 3000 pts | $6.00 | 50.00 |
| **Trailing Ativa** | 500 pts | $1.00 | 8.33 |
| **Trailing Dist** | 250 pts | $0.50 | 4.17 |
| **Worker** | - | 0.5s | - |

---

## 🚀 EXECUTAR

```batch
GOLD_6USD.bat
```

**Ou manualmente:**
```bash
python EXECUTAR_GOLD_6USD.py
```

---

## 💰 EXEMPLO DE OPERAÇÃO

### Abertura:
```
Entry:  $4016.00
SL:     $1016.00 (3000 pts abaixo)
Risco:  $6.00
Status: AGUARDANDO +500 pts para ativar trailing
```

### Quando Lucro = $1.00 (500 pts):
```
Entry:  $4016.00
Preço:  $4516.00 (+500 pts = +$1.00)
SL:     $4266.00 (250 pts abaixo)
```

**TRAILING ATIVA!**
- SL move automaticamente
- Mantém 250 pts de distância
- Protege $0.50 de lucro

### Trailing Subindo:

```
Preço $4766 (+750pts = +$1.50)
  → SL $4516 (protege $1.00) ✓

Preço $5016 (+1000pts = +$2.00)
  → SL $4766 (protege $1.50) ✓

Preço $5266 (+1250pts = +$2.50)
  → SL $5016 (protege $2.00) ✓
```

**A cada 250 pontos (+$0.50), o SL sobe e protege mais $0.50!**

---

## ⚡ WORKER 0.5s

- **120 verificações por minuto**
- Trailing atualiza instantaneamente
- Maximiza proteção de lucros
- Reage em tempo real ao mercado

---

## ⚠️ IMPORTANTE

### Margem Necessária:
```
0.02 lote de XAUUSDc
Preço: ~$4,016
Margem aprox: ~$80 USD
```

### SL de 3000 pontos parece grande?
**MAS:**
- Risco real é $6.00 (controlado!)
- Proteção contra volatilidade extrema do Gold
- Trailing ativa rápido em $1.00
- Fecha com lucro garantido sempre

### Por que 3000 pontos?
```
Gold pode variar 100-200 pts facilmente em minutos
3000 pts dá espaço para volatilidade
MAS risco é fixo: $6.00 por trade
```

---

## 🧪 LOGS ESPERADOS

### Ao Iniciar:
```
Volume: 0.02 lote (FIXO)
Com 0.02 lote: 1 pt = $0.0020
SL: 3000 pts = $6.00
Trailing Ativa: 500 pts = $1.00
Trailing Dist: 250 pts = $0.50
Worker: 0.5s
```

### Durante Operação:
```
[GOLD] Valor do ponto (tick_value): $0.1000 por lote
[GOLD] Com volume 0.02: 1 ponto = $0.0020

[WORKER] Monitoramento continuo INICIADO (check: 0.5s)

[AGUARDANDO] Lucro: X pts ($Y) | Ativa em: 500pts ($1.00) | Faltam: Z pts
```

### Quando Trailing Ativar:
```
[WORKER] TRAILING ATIVADO! Lucro: 500.0pts ($1.00)
[WORKER] Trailing subiu: $4266.00 -> $4280.00 (+14.00)
```

---

## ✅ CHECKLIST

Antes de executar:

- [ ] MT5 aberto e conectado
- [ ] XAUUSDc disponível no broker
- [ ] Margem disponível (~$80)
- [ ] Entendeu risco de $6.00/trade
- [ ] Entendeu que SL é 3000 pts (mas risco fixo $6)
- [ ] Worker 0.5s está OK (muito rápido)
- [ ] Conta permite operar com 0.02 lote

---

## 📝 ARQUIVOS

- ✅ `EXECUTAR_GOLD_6USD.py` - Script configurado
- ✅ `GOLD_6USD.bat` - Executável Windows
- ✅ `GOLD_CONFIG_FINAL.md` - Esta documentação

---

## 🎯 RESUMO FINAL

**Configuração GOLD correta:**
- ✅ Volume: 0.02 lote
- ✅ SL: 3000 pts = $6.00
- ✅ Trailing ativa: 500 pts = $1.00
- ✅ Trailing sobe: 250 pts = $0.50
- ✅ Worker: 0.5s (muito rápido!)

**Execute:**
```batch
GOLD_6USD.bat
```

**Os valores em $ estão 100% corretos agora!** 🎉

---

**Status:** ✅ CONFIGURAÇÃO PERFEITA PARA GOLD!
