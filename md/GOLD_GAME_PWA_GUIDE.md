# 🎰 Gold Loss Zero Game - PWA Gamificado

## 📋 Visão Geral

PWA (Progressive Web App) gamificado estilo cassino para trading de ouro (XAUUSDc) com sistema de predição avançado e trailing stop automático.

## 🎮 Características do Jogo

### Visual & UX
- **Interface estilo cassino**: Colorida, neon, animações fluidas
- **Efeitos sonoros**: Vitória, perda, trade, alertas
- **Animações de partículas**: Canvas com efeitos de celebração
- **Responsivo**: Funciona em desktop e mobile
- **PWA**: Instalável como app nativo

### Sistema de Trading
- **Predições em tempo real**: Sistema de análise de 20 candles M1
- **Score de qualidade**: 0-100 (mínimo 70 para trading)
- **Jogador decide**: Escolhe BUY/SELL, lote e stop loss
- **Trailing automático**: Worker gerencia trailing stops

### Regras de Trailing Stop

```
Ativação: Lucro >= $0.50
Proteção Inicial: $0.40 (trailing de $0.10 atrás)
Incremento: A cada $0.20 de lucro adicional

Exemplos:
  Lucro $0.50 → Protege $0.40 (trailing ativa)
  Lucro $0.70 → Protege $0.60 (+$0.20)
  Lucro $0.90 → Protege $0.80 (+$0.20)
  Lucro $1.10 → Protege $1.00 (+$0.20)
  Lucro $1.30 → Protege $1.20 (+$0.20)
```

## 🚀 Como Usar

### 1. Iniciar o Jogo

```batch
RUN_GOLD_GAME.bat
```

Ou manualmente:

```bash
uv run python run_game_server.py
```

### 2. Acessar o Jogo

Abra no navegador: **http://localhost:3000/game**

### 3. Instalar como PWA (Opcional)

No navegador:
1. Chrome/Edge: Clique no ícone de instalação na barra de endereço
2. Mobile: "Adicionar à tela inicial"

### 4. Como Jogar

1. **Aguarde a predição**: Sistema analisa mercado a cada 5 segundos
2. **Veja o score**: Só opera com score >= 70/100
3. **Configure seus parâmetros**:
   - Lote (padrão: 0.02)
   - Stop Loss em dólares (padrão: $5.00)
4. **Clique em COMPRAR ou VENDER**: Botões só habilitam quando há sinal válido
5. **Acompanhe posição**: Trailing ativa automaticamente com $0.50 de lucro
6. **Acumule lucro**: Objetivo é maximizar profit com trailing inteligente

## 📊 Painel do Jogo

### Header (Score)
- 💰 **Lucro Total**: P&L acumulado
- 🎯 **Win Rate**: % de vitórias
- 🔥 **Streak**: Sequência de wins/losses

### Zona de Predição
- 🔮 **Direção**: BUY / SELL / AGUARDANDO
- 📊 **Score**: Barra visual 0-100
- 📈 **Confiança**: % de confiança da predição
- 📝 **Análise**: Detalhes técnicos (Up20:15/20, etc.)
- 💰 **Preço Atual**: Cotação em tempo real

### Controles
- 💼 **Lote**: Volume da operação (0.01-1.0)
- 🛡️ **Stop Loss**: Perda máxima em dólares ($1-$50)
- 📈 **Botão COMPRAR**: Verde, só ativa com sinal BUY
- 📉 **Botão VENDER**: Vermelho, só ativa com sinal SELL

### Posições Ativas
- Lista de posições abertas
- Lucro em tempo real
- Status do trailing (🟢 ativo / ⚪ inativo)

### Histórico
- Últimas 10 operações
- Resultado de cada trade
- Horário de fechamento

## 🎨 Arquitetura

### Frontend (PWA)
```
src/web/
├── templates/
│   └── game.html          # Interface principal
├── static/
│   ├── css/
│   │   └── game.css       # Estilos gamificados
│   ├── js/
│   │   └── game.js        # Lógica do jogo
│   ├── sounds/            # Efeitos sonoros
│   │   ├── win.mp3
│   │   ├── lose.mp3
│   │   ├── trade.mp3
│   │   └── alert.mp3
│   ├── icons/             # Ícones PWA
│   │   ├── icon-192.png
│   │   └── icon-512.png
│   ├── manifest.json      # PWA manifest
│   └── service-worker.js  # Service Worker
```

### Backend (Flask)
```
src/web/
├── game_api.py            # API endpoints do jogo
├── game_worker.py         # Worker de trailing stop
└── app.py                 # Integração com Flask
```

### API Endpoints

#### `GET /game`
Página principal do jogo

#### `GET /api/game/prediction`
Retorna predição atual
```json
{
  "prediction": {
    "type": "BUY",
    "score": 85,
    "confidence": 78.5,
    "reason": "Score:85 Up20:16/20 Up10:8/10 Up5:4/5"
  },
  "price": 2658.45
}
```

#### `GET /api/game/positions`
Lista posições ativas
```json
{
  "positions": [
    {
      "ticket": 123456,
      "type": "BUY",
      "volume": 0.02,
      "entry_price": 2658.45,
      "sl": 2653.45,
      "profit": 1.20,
      "trailing_active": true
    }
  ]
}
```

#### `GET /api/game/history`
Histórico e estatísticas
```json
{
  "history": [...],
  "stats": {
    "total_profit": 25.80,
    "wins": 12,
    "losses": 3,
    "streak": 2
  }
}
```

#### `POST /api/game/open`
Abre nova posição
```json
{
  "type": "BUY",
  "volume": 0.02,
  "sl": 5.0
}
```

## 🔧 Sistema de Predição

### Análise Multi-Timeframe
1. **M5 (Obrigatório)**: Confirma tendência forte (4 de 5 candles)
2. **M1 (Principal)**: Análise detalhada de 20 candles

### Scoring System (0-100 pontos)

**Consistência (0-25 pontos)**
- 15 de 20 candles na direção → +25
- 12 de 20 candles na direção → +15

**Tendência Recente (0-20 pontos)**
- 7 de 10 candles → +20
- 6 de 10 candles → +10

**Tendência Imediata (0-20 pontos)**
- 4 de 5 candles → +20
- 3 de 5 candles → +10

**Médias Móveis (0-15 pontos)**
- Preço > SMA5 > SMA10 > SMA20 → +15
- Preço > SMA5 e SMA10 → +10
- Preço > SMA5 → +5

**Momentum (0-10 pontos)**
- Acelerando na direção → +10
- Positivo/negativo → +5

**Volume (0-10 pontos)**
- 20% acima da média → +10
- Acima da média → +5

**Mínimo para operar**: 70 pontos

## 🎯 Estratégia de Jogo

### Iniciante
- Use lote mínimo (0.01)
- SL conservador ($5-10)
- Só opere com score >= 80

### Intermediário
- Lote moderado (0.02-0.03)
- SL balanceado ($5)
- Opere com score >= 75

### Avançado
- Lote variável conforme análise
- SL ajustado pela volatilidade
- Opere com score >= 70
- Múltiplas posições (máx 3)

## 📱 Instalação PWA

### Chrome Desktop
1. Acesse http://localhost:3000/game
2. Clique no ícone ⊕ na barra de endereço
3. "Instalar Gold Loss Zero Game"

### Chrome Mobile
1. Acesse http://localhost:3000/game
2. Menu (⋮) → "Adicionar à tela inicial"
3. Confirme instalação

### Recursos Offline
O PWA funciona offline com:
- Interface completa
- CSS e JavaScript cached
- Requer conexão para trading real

## 🎵 Efeitos Sonoros

### Adicionar Sons Personalizados

Substitua os arquivos em `src/web/static/sounds/`:

- `win.mp3`: Tocado ao ganhar trade
- `lose.mp3`: Tocado ao perder trade
- `trade.mp3`: Tocado ao abrir posição
- `alert.mp3`: Tocado quando há sinal forte (score >= 70)

**Requisitos**:
- Formato: MP3 ou OGG
- Duração: 1-3 segundos
- Tamanho: < 100KB cada

### Desabilitar Sons

No JavaScript (`game.js`), linha 60-70, comente:

```javascript
// this.playSound('win');
// this.playSound('lose');
// etc.
```

## 🎨 Personalização

### Cores (CSS Variables)

Edite `src/web/static/css/game.css`:

```css
:root {
    --gold: #ffd700;        /* Dourado */
    --red: #ff3333;         /* Vermelho (SELL) */
    --green: #00ff88;       /* Verde (BUY) */
    --purple: #9966ff;      /* Roxo (Cards) */
    --blue: #00ccff;        /* Azul (Controles) */
    --bg-dark: #0f0f1e;     /* Background escuro */
}
```

### Animações

**Velocidade das partículas** (game.js linha 180):

```javascript
vx: (Math.random() - 0.5) * 4,  // Velocidade horizontal
vy: (Math.random() - 0.5) * 4,  // Velocidade vertical
```

**Quantidade de partículas** (game.js linha 195):

```javascript
for (let i = 0; i < 50; i++) {  // 50 partículas por celebração
```

## 🐛 Troubleshooting

### Predições não aparecem
- Verifique MT5 está aberto e conectado
- Confirme símbolo XAUUSDc está disponível
- Veja logs no console do servidor

### Trailing não ativa
- Confirme worker está rodando (veja logs)
- Verifique lucro atingiu >= $0.50
- Magic number correto nas posições

### Botões desabilitados
- Score deve ser >= 70
- Máximo 3 posições simultâneas
- Cooldown de 5 segundos entre trades

### Sons não tocam
- Clique na página primeiro (política de autoplay)
- Verifique arquivos MP3 existem em `static/sounds/`
- Veja console do navegador (F12) para erros

## 📚 Recursos Adicionais

### Logs do Servidor
```bash
# Veja logs em tempo real
tail -f nohup.out  # Linux/Mac
type nohup.out     # Windows
```

### Logs do Browser
Pressione **F12** → Console para ver:
- Requests API
- Erros JavaScript
- Estado do jogo

### Magic Number
Cada instância do jogo gera um magic number único (baseado em timestamp). Isso permite múltiplos jogadores simultâneos sem conflito.

## 🎓 Dicas de Jogo

1. **Paciência**: Aguarde scores altos (80+) para melhor taxa de acerto
2. **Disciplina**: Respeite o stop loss, não mova manualmente
3. **Trailing**: Deixe o sistema gerenciar, não interfira
4. **Diversificação**: Use lotes menores para operar mais vezes
5. **Análise**: Leia a "Análise" da predição para entender o sinal
6. **Volatilidade**: Evite operar em alta volatilidade (sistema bloqueia)
7. **Horários**: Melhores sinais durante sessões europeia e americana
8. **Sequência**: Após 2-3 losses, pause e reavalie
9. **Meta**: Defina meta diária ($10-20) e pare ao atingir
10. **Diversão**: É um jogo educacional, não aposta real dinheiro sem prática!

## 📝 Notas Importantes

- **Ambiente de Demonstração**: Teste primeiro em conta demo
- **Riscos**: Trading real envolve riscos de perda de capital
- **Responsabilidade**: Operações são de responsabilidade do jogador
- **Educacional**: Ferramenta para aprender sobre trading e análise técnica
- **Suporte**: Veja logs e documentação em caso de problemas

## 🎉 Divirta-se!

O Gold Loss Zero Game é uma forma divertida e educativa de aprender sobre:
- Análise técnica de mercados
- Gestão de risco com trailing stops
- Tomada de decisão baseada em dados
- Controle emocional no trading

**Boa sorte e bons trades!** 🚀💰
