# 📱 Configuração de Notificações Telegram

Guia completo para configurar notificações do agente de trading no Telegram. Toda a equipe pode visualizar operações, análises e alertas em tempo real.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Criação do Bot Telegram](#criação-do-bot-telegram)
3. [Configuração do Canal/Grupo](#configuração-do-canalgrupo)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Testando a Integração](#testando-a-integração)
6. [Tipos de Notificações](#tipos-de-notificações)
7. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

- ✅ Conta Telegram ativa
- ✅ Acesso ao @BotFather (bot oficial do Telegram para criar bots)
- ✅ Um canal ou grupo Telegram para receber as notificações
- ✅ Python 3.11+
- ✅ Arquivo `.env` configurado

---

## Criação do Bot Telegram

### Passo 1: Abrir o @BotFather

1. Abra o Telegram
2. Procure por `@BotFather` (é um bot oficial do Telegram)
3. Clique em **"Start"** ou digite `/start`

### Passo 2: Criar um Novo Bot

1. Envie a mensagem: `/newbot`
2. O BotFather pedirá um **nome** para o bot:
   - Exemplo: `Meu Agente Trading`
3. Depois pedirá um **username** (deve terminar com `bot`):
   - Exemplo: `meu_agente_trading_bot`
4. **Copie o token** que será fornecido:
   - Formato: `123456789:ABCDEFGhijklmnoPQRstuvwXYZ123456789`
   - **Guarde este token com segurança!**

### Passo 3: Configurar Permissões (Opcional)

Se quiser adicionar mais segurança, você pode:

```
/setprivacy
- Escolha o bot
- Selecione "Disable" para ativar o bot em grupos

/setcommands
- Configure comandos customizados (opcional)
```

**Salve o token em um local seguro.** Você precisará dele na próxima etapa.

---

## Configuração do Canal/Grupo

### Opção A: Usar um Canal (Recomendado para Broadcasting)

Um canal permite enviar mensagens de forma broadcast para toda a equipe sem que todos precisem de permissões especiais.

#### Criar um Canal

1. No Telegram, toque no ícone de lápis (novo chat)
2. Selecione "Novo canal"
3. Digite um nome: `trading_agent_alerts`
4. Escolha privado ou público:
   - **Privado**: Apenas membros convidados veem
   - **Público**: Qualquer um pode procurar e entrar
5. Adicione uma descrição: "Notificações do agente de trading em tempo real"
6. Defina permissões se necessário

#### Adicionar o Bot ao Canal

1. Entre no canal criado
2. Toque no nome do canal (no topo)
3. Role para baixo até "Membros" ou "Administradores"
4. Toque em "Adicionar membro"
5. Procure por seu bot (ex: `@meu_agente_trading_bot`)
6. Selecione e clique para adicionar

#### Obter o Chat ID do Canal

O **Chat ID** é o identificador único do canal.

**Opção 1: Via Bot (Mais Fácil)**

1. Crie um bot temporário para testes ou use o seu
2. Envie qualquer mensagem no canal
3. Acesse: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Substitua `<YOUR_BOT_TOKEN>` pelo token do seu bot
4. Procure por `"chat"` na resposta JSON
5. O `id` será algo como: `-1001234567890` (números com hífen)

**Opção 2: Via Username (Se Canal Público)**

Para canais públicos, você pode usar o username diretamente:
- Exemplo: `@trading_agent_alerts`

**Dica**: Prefira usar o Chat ID numérico para canais privados.

### Opção B: Usar um Grupo

Se preferir usar um grupo (permite conversas entre membros):

1. Crie um novo grupo normalmente
2. Adicione o bot ao grupo com permissões de **enviar mensagens**
3. Para obter o Chat ID, envie `/start` ao seu bot dentro do grupo
4. Acesse `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` e procure pelo Chat ID

---

## Variáveis de Ambiente

Após obter o token e o Chat ID, configure seu arquivo `.env`:

### Abra `.env` na raiz do projeto:

```bash
# Telegram Notification Configuration
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGhijklmnoPQRstuvwXYZ123456789
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_SUMMARY_INTERVAL=30
```

### Explicação das Variáveis

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `TELEGRAM_ENABLED` | Ativar/desativar notificações | `true` ou `false` |
| `TELEGRAM_BOT_TOKEN` | Token do bot criado no BotFather | `123456789:ABCDEFGhijklmnoPQRstuvwXYZ123456789` |
| `TELEGRAM_CHAT_ID` | ID do canal ou grupo (números com `-` para privados) | `-1001234567890` ou `@seu_canal` |
| `TELEGRAM_SUMMARY_INTERVAL` | Intervalo de resumos periódicos em minutos | `30` (a cada 30 ciclos de 30s = ~15 min) |

---

## Testando a Integração

### Teste Rápido com Script

Execute o script de teste incluído para verificar se tudo está funcionando:

```bash
# Windows
TESTAR_TELEGRAM.bat

# Linux/Mac
bash test_telegram.sh
```

Ou via Python diretamente:

```bash
uv run python test_telegram.py
```

### Teste Manual

1. Configure as variáveis no `.env` como acima
2. Execute o agente normalmente:

```bash
uv run python src/agents/btc_hedge_agent.py
```

3. Você deve receber mensagens no Telegram quando:
   - Posição aberta
   - Posição fechada
   - Hedge ativado
   - Erros críticos
   - Resumos periódicos

### Checklist de Teste

- [ ] Bot foi criado no @BotFather
- [ ] Token foi copiado corretamente
- [ ] Canal/Grupo foi criado
- [ ] Bot foi adicionado ao canal/grupo com permissões
- [ ] Chat ID foi obtido
- [ ] `.env` foi atualizado com token e Chat ID
- [ ] Script de teste passou com sucesso
- [ ] Agente está enviando mensagens ao Telegram

---

## Tipos de Notificações

Seu agente enviará os seguintes tipos de notificações:

### 1️⃣ Posição Aberta

Enviada quando uma nova posição é aberta:

```
🟢 POSIÇÃO ABERTA - BTCUSDm

📊 Tipo: BUY
💰 Volume: 0.03 lots
📈 Entrada: $109,545.50
🎯 TP: $109,645.50
🛑 SL: $109,245.50

📉 Indicadores:
• RSI: 65.3
• MACD: +12.45
• Tendência: UP
• ATR: 181.44

⏰ [timestamp]
🎫 Ticket: #999999
```

### 2️⃣ Posição Fechada

Enviada quando uma posição é fechada com resultado:

```
✅ POSIÇÃO FECHADA

🎫 Ticket: #999999
💚 Resultado: +$2.15
📊 Tipo: BUY
⏱️ Duração: 3m 45s

📊 Preços:
• Entrada: $109,545.50
• Saída: $109,650.00
• Diferença: +$104.50

📈 Hoje (BTCUSDm):
• Lucro: +$18.50
• Win Rate: 75.0%
• Streak: 3 🔥
• Operações: 8/999

⏰ [timestamp]
```

### 3️⃣ Alerta de Hedge

Enviada quando o hedge é ativado automaticamente:

```
🛡️ ALERTA CRÍTICO

Tipo: HEDGE
Título: Hedge Ativado
Descrição: Posição em prejuízo. Hedge ativado para defender a posição.

Detalhes:
• Ticket Original: 123456
• Ticket Hedge: 654321
• Prejuízo Atual: -$12.50
• Sinal Contrário: SELL
• Símbolo: BTCUSDm

⏰ [timestamp]
```

### 4️⃣ Resumo Periódico

Enviado a cada 30 ciclos (~15 minutos):

```
📊 RESUMO DO AGENTE - BTCUSDm

⏰ últimos 15 minutos

🟢 Estado: TRADING
💼 Posições abertas: 2
💰 Lucro da sessão: +$18.50

📈 Estatísticas:
• Total: 8 operações
• ✅ Vencedoras: 6 (75.0%)
• ❌ Perdedoras: 2
• 🔥 Streak: 3

📉 Mercado:
• Preço: $109,650.00
• Tendência: UP
• RSI: 58.2
• MACD: +15.3

⏰ [timestamp]
```

### 5️⃣ Alerta de Erro

Enviado quando ocorrem erros críticos:

```
🚨 ALERTA CRÍTICO

Tipo: ERROR
Título: Erro no Agente
Descrição: Erro ao obter rates para BTCUSDm

Detalhes:
• Contexto: copy_rates_from_pos retornou None

⏰ [timestamp]
```

---

## Troubleshooting

### Problema: "Telegram não disponível"

**Mensagem de Erro:**
```
⚠️ Telegram não disponível. Instale: pip install python-telegram-bot
```

**Solução:**
```bash
uv pip install python-telegram-bot
# ou
pip install python-telegram-bot
```

### Problema: "Token ou Chat ID não configurados"

**Mensagem de Erro:**
```
⚠️ TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados no .env
```

**Solução:**
1. Verifique se `.env` existe na raiz do projeto
2. Confirme que o token foi copiado corretamente do @BotFather
3. Confirme que o Chat ID foi obtido corretamente
4. Certifique-se de não ter espaços extras nas variáveis

**Exemplo Correto:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGhijklmnoPQRstuvwXYZ123456789
TELEGRAM_CHAT_ID=-1001234567890
```

### Problema: "Erro ao enviar mensagem Telegram"

**Possíveis Causas:**

1. **Bot não foi adicionado ao canal/grupo**
   - Solução: Adicione o bot manualmente ao canal/grupo

2. **Bot não tem permissões para enviar mensagens**
   - Solução: Verifique as permissões do bot no canal/grupo

3. **Token inválido ou expirado**
   - Solução: Crie um novo token no @BotFather

4. **Chat ID incorreto**
   - Solução: Verifique o Chat ID com `getUpdates` novamente

5. **Problemas de conexão**
   - Solução: Verifique sua conexão com a internet

### Problema: Mensagens em Branco ou Mal Formatadas

**Causa:** Problemas com encoding ou HTML mal formatado

**Solução:**
```bash
# Atualize a biblioteca python-telegram-bot
uv pip install --upgrade python-telegram-bot
```

### Problema: Bot Funciona mas Não Envia Mensagens

1. Verifique se `TELEGRAM_ENABLED=true` no `.env`
2. Teste com `test_telegram.py`
3. Verifique os logs do agente para erros de envio

---

## Exemplos de Uso

### Exemplo 1: Canal Público para Equipe

```bash
# .env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=987654321:XYZabcdefghijklmnoPQRstuvWxyz987654
TELEGRAM_CHAT_ID=@trading_alerts_team
TELEGRAM_SUMMARY_INTERVAL=30
```

### Exemplo 2: Grupo Privado para Gerenciamento

```bash
# .env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=987654321:XYZabcdefghijklmnoPQRstuvWxyz987654
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_SUMMARY_INTERVAL=15
```

### Exemplo 3: Desabilitar Notificações

Se precisar pausar notificações sem remover a configuração:

```bash
# .env
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=987654321:XYZabcdefghijklmnoPQRstuvWxyz987654
TELEGRAM_CHAT_ID=-1001234567890
```

---

## Segurança

⚠️ **IMPORTANTE**: Nunca compartilhe seu `TELEGRAM_BOT_TOKEN`

1. **Não commite o `.env`** em repositórios públicos
2. **Use `.env.example`** para documentar variáveis sem valores
3. Se o token vazar, crie um novo bot no @BotFather imediatamente
4. Para múltiplos ambientes (dev, prod), use tokens diferentes

### .gitignore

Certifique-se de que seu `.gitignore` inclua:

```
.env
.env.local
*.log
__pycache__/
```

---

## Próximas Etapas

1. ✅ Criar bot no @BotFather
2. ✅ Configurar canal/grupo
3. ✅ Obter Chat ID
4. ✅ Adicionar ao `.env`
5. ✅ Testar com `test_telegram.py`
6. ✅ Executar agente e receber notificações

---

## Suporte

Se encontrar problemas:

1. Consulte a seção [Troubleshooting](#troubleshooting)
2. Verifique os logs do agente
3. Execute `test_telegram.py` para diagnóstico
4. Verifique se o bot foi adicionado corretamente ao canal/grupo

---

**Última atualização:** Outubro 2025
**Versão:** 1.0
**Compatibilidade:** Python 3.11+ | Telegram Bot API 7.0+
