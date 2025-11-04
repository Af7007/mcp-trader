# 🎰 Gold Loss Zero Game

## 🎮 Um Jogo de Trading Gamificado

Interface estilo cassino para operar ouro (XAU/USD) com predições inteligentes e trailing stop automático.

---

## ✨ Recursos

🎨 **Visual Cassino** - Neon, animações, partículas  
🔮 **Predições IA** - Análise de 20 candles M1  
📊 **Score 0-100** - Qualidade do sinal em tempo real  
🎯 **Você Decide** - Escolhe direção, lote e stop loss  
🤖 **Trailing Auto** - Worker gerencia SL automaticamente  
🏆 **Ranking** - Lucro total, win rate, streak  
📱 **PWA** - Instalável como app nativo  
🎵 **Sons** - Efeitos de vitória, perda, trade, alerta  

---

## 🚀 Start

```batch
# 1. Teste
TESTAR_GOLD_GAME.bat

# 2. Execute
RUN_GOLD_GAME.bat

# 3. Acesse
http://localhost:3000/game
```

---

## 🎯 Como Jogar

1. 🔮 **Aguarde predição** (verde = bom sinal)
2. ⚙️ **Configure**: Lote + Stop Loss
3. 📈 **Clique**: BUY ou SELL
4. 👀 **Acompanhe**: Trailing ativa automaticamente
5. 💰 **Lucre**: Acumule profit!

---

## 📊 Trailing Stop

```
Lucro      →  Proteção
────────────────────────
$0.50      →  $0.40
$0.70      →  $0.60
$0.90      →  $0.80
$1.10      →  $1.00
...        →  +$0.20
```

Sobe a cada **$0.20** de lucro adicional!

---

## 🎨 Screenshots

### Tela Principal
```
┌────────────────────────────────────┐
│  💰 Lucro: $25.80  🎯 Win: 80%  🔥 3│
├────────────────────────────────────┤
│                                    │
│        🔮 PREDIÇÃO DO OURO         │
│                                    │
│            📈 COMPRAR              │
│                                    │
│   Score: ████████░░  85/100        │
│   Confiança: 78.5%                 │
│                                    │
│   Preço: $2658.45                  │
│                                    │
├────────────────────────────────────┤
│   💼 Lote: 0.02                    │
│   🛡️ Stop Loss: $5.00              │
├────────────────────────────────────┤
│   [   📈 COMPRAR   ]               │
│   [   📉 VENDER    ]               │
├────────────────────────────────────┤
│   📊 Posições Ativas               │
│   🟢 Ticket 123456  +$1.20         │
└────────────────────────────────────┘
```

---

## 🔧 Personalização

### 🎨 Cores
Edite `css/game.css`:
```css
--gold: #ffd700
--red: #ff3333
--green: #00ff88
```

### 🎵 Sons
Substitua em `sounds/`:
- `win.mp3` - Vitória 🎉
- `lose.mp3` - Perda 😢
- `trade.mp3` - Abertura 📈
- `alert.mp3` - Alerta ⚠️

### 🖼️ Ícones
Substitua em `icons/`:
- `icon-192.png`
- `icon-512.png`

---

## 📚 Guias

📖 **Completo**: `GOLD_GAME_PWA_GUIDE.md`  
⚡ **Quick Start**: `QUICK_START_GOLD_GAME.md`  
📝 **Resumo**: `GOLD_GAME_RESUMO.md`  

---

## 🆘 Ajuda Rápida

### ❓ Predição não aparece
✅ MT5 aberto?  
✅ XAUUSDc disponível?  

### ❓ Botões desabilitados
✅ Score >= 70?  
✅ Menos de 3 posições?  

### ❓ Trailing não ativa
✅ Lucro >= $0.50?  
✅ Worker rodando?  

### ❓ Sons não tocam
✅ Clicou na página?  
✅ Arquivos MP3 existem?  

---

## 🎯 Dicas

✅ Aguarde score **80+** para melhores sinais  
✅ Use **lotes menores** para operar mais  
✅ **Não mexa** no SL manualmente  
✅ Defina **meta diária** e pare ao atingir  
✅ Evite alta **volatilidade**  

---

## 🏆 Metas

### 🥉 Bronze
- 10 trades
- Win rate 60%
- $10 lucro

### 🥈 Prata
- 50 trades
- Win rate 70%
- $50 lucro

### 🥇 Ouro
- 100 trades
- Win rate 80%
- $100 lucro

---

## 🎓 O Que Aprende

1. 📊 **Análise Técnica** - Médias, tendências
2. 🛡️ **Gestão de Risco** - SL, trailing, lotes
3. 🧠 **Psicologia** - Disciplina, paciência
4. 🤖 **Automação** - Workers, triggers
5. 💻 **Web Dev** - PWA, APIs, Canvas

---

## 🎉 Divirta-se!

**Gold Loss Zero Game** é educacional e divertido!

Aprenda trading enquanto se diverte 🚀

**Bons trades!** 💰✨

---

## 📞 Suporte

- 📖 Documentação: `GOLD_GAME_PWA_GUIDE.md`
- 🐛 Issues: Veja logs do servidor
- 💬 Dúvidas: Consulte troubleshooting

---

**Desenvolvido com ❤️ para traders gamers**

v1.0.0 - 2025-11-03
