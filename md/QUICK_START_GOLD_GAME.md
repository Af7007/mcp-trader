# 🚀 Quick Start - Gold Loss Zero Game

## ⚡ Início Rápido (3 passos)

### 1️⃣ Verifique os requisitos
```batch
TESTAR_GOLD_GAME.bat
```

### 2️⃣ Inicie o jogo
```batch
RUN_GOLD_GAME.bat
```

### 3️⃣ Acesse no navegador
```
http://localhost:3000/game
```

## 🎮 Como Jogar (Resumo)

1. **Aguarde predição** (atualiza a cada 5s)
2. **Veja o score** (verde = bom sinal)
3. **Escolha lote e SL** (padrão: 0.02 lotes, $5 SL)
4. **Clique BUY ou SELL** (botões só habilitam com sinal forte)
5. **Acompanhe posição** (trailing ativa automaticamente)
6. **Lucre!** 💰

## 📊 Indicadores na Tela

### Score da Predição
- **0-69**: ❌ Fraco (não opera)
- **70-79**: ⚠️ Moderado
- **80-89**: ✅ Bom
- **90-100**: 🌟 Excelente

### Status do Trailing
- **⚪ Inativo**: Aguardando $0.50 de lucro
- **🟢 Ativo**: Trailing funcionando

## ⚙️ Regras Automáticas

### Trailing Stop
```
Lucro $0.50 → Ativa trailing (protege $0.40)
Lucro $0.70 → Sobe para $0.60
Lucro $0.90 → Sobe para $0.80
... e assim por diante (+$0.20 por nível)
```

### Limites
- **Posições simultâneas**: Máximo 3
- **Cooldown**: 5 segundos entre trades
- **Score mínimo**: 70 para habilitar botões

## 🎯 Dicas Rápidas

✅ **Faça**
- Aguarde scores altos (80+)
- Respeite o stop loss
- Defina meta diária
- Opere em horários de liquidez

❌ **Evite**
- Operar com score baixo
- Mover SL manualmente
- Operar em alta volatilidade
- Ignorar o sistema de predição

## 🛠️ Problemas Comuns

### "Aguardando..." não sai
➡️ MT5 está aberto e conectado?

### Botões desabilitados
➡️ Score deve ser >= 70

### Trailing não ativa
➡️ Precisa lucro >= $0.50

### Sons não tocam
➡️ Clique na página primeiro

## 📚 Mais Informações

Para guia completo, veja: `GOLD_GAME_PWA_GUIDE.md`

---

**Divirta-se e bons trades!** 🎰💎
