# Configurar Telegram para Notificações (OPCIONAL)

O agente BTC Loss Zero funciona **com ou sem Telegram**. Se quiser receber notificações de trades no Telegram, siga este guia.

## ⚠️ Importante

Se o Telegram não estiver configurado, o agente funciona normalmente, apenas SEM notificações no celular/web.

## 🚀 Passo a Passo

### 1. Instalar a Biblioteca Python

```bash
pip install python-telegram-bot
```

### 2. Criar Bot no Telegram

1. Abra Telegram e procure por: `@BotFather`
2. Envie: `/newbot`
3. Escolha um nome (ex: `MeuBotBTC`)
4. Escolha um username (ex: `meu_bot_btc_trading`)
5. BotFather retorna um **TOKEN** (ex: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

**Copie e guarde este TOKEN!**

### 3. Obter seu Chat ID

Opção A - Via Bot Direto:
1. Abra o chat com seu bot no Telegram
2. Envie qualquer mensagem
3. Visite: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure por `"chat":{"id":XXXX}`
5. Copie o número (ex: `987654321`)

Opção B - Via Bot Helper:
1. Procure por: `@userinfobot`
2. Envie qualquer mensagem
3. Ele retorna seu ID (ex: `987654321`)

**Copie e guarde este ID!**

### 4. Configurar no .env

Abra o arquivo `.env` na raiz do projeto e adicione:

```env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
```

**Substitua pelos valores que você copiou!**

### 5. Testar Conexão

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('TELEGRAM_ENABLED:', os.getenv('TELEGRAM_ENABLED'))
print('TELEGRAM_BOT_TOKEN:', os.getenv('TELEGRAM_BOT_TOKEN')[:20] + '...')
print('TELEGRAM_CHAT_ID:', os.getenv('TELEGRAM_CHAT_ID'))
"
```

Se mostrar os valores, está configurado! ✅

### 6. Reiniciar Agente

Agora execute normalmente:
```bash
python EXECUTAR_LOSS_ZERO.py
```

Você receberá notificações como:

```
🟢 POSIÇÃO ABERTA - Loss Zero
==================================================
Tipo: BUY
Ticket: 12345678
Preço: $100,000.00
Volume: 0.05
Motivo: RSI oversold (28.50)
Estratégia: Trailing Stop Ilimitado
==================================================

🟢 POSIÇÃO FECHADA COM LUCRO - Trailing Stop
==================================================
Ticket: 12345678
Tipo: BUY
Lucro: 2.85%
Trailing Ativo: 2.75%
==================================================
```

## 🔧 Troubleshooting Telegram

### "Telegram não disponível"

Solução:
```bash
pip install python-telegram-bot
```

### "TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados"

Solução:
1. Verifique o arquivo `.env`
2. Confirme que o TOKEN e CHAT_ID estão corretos
3. Sem espaços extras
4. Salve o arquivo

### "Erro ao enviar mensagem"

Possíveis causas:
- Token inválido
- Chat ID inválido
- Bot foi deletado
- Conexão de internet fraca

Solução:
- Recrie o bot no @BotFather
- Obtenha novo TOKEN
- Atualize no `.env`

## 📱 Usando com Grupos

Se quiser notificações em um **grupo**:

1. Crie um grupo no Telegram
2. Adicione seu bot ao grupo
3. Envie uma mensagem no grupo
4. Abra: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
5. Procure por `"chat":{"id":-XXXXX}` (note o `-`)
6. Use esse ID no `.env`

## 🔔 Personalizando Mensagens

Para modificar as mensagens, edite `src/agents/btc_loss_zero_otimizado.py` e procure por:

```python
self._notify(msg)
```

Customize o conteúdo conforme desejado.

## ✅ Checklist

- [ ] Instalou `python-telegram-bot`?
- [ ] Criou bot no @BotFather?
- [ ] Copiou o TOKEN?
- [ ] Obteve seu CHAT_ID?
- [ ] Atualizou o `.env`?
- [ ] Testou a conexão?
- [ ] Reiniciou o agente?

## 📞 Dicas Finais

- **Backup**: Guarde o TOKEN e CHAT_ID em local seguro
- **Privado**: Não compartilhe o TOKEN com ninguém
- **Grupos**: Funciona melhor em chats privados (1-to-1)
- **Testes**: Mande teste antes de rodar o agente

---

**Pronto!** Agora você receberá notificações de todos os trades em tempo real no Telegram! 📱

Se não quiser Telegram, basta deixar sem configurar - o agente funciona perfeitamente sem!
