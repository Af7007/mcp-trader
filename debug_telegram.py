#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para Telegram
Ajuda a identificar problemas com a configuração
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Configurar encoding UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Carregar variáveis do .env
load_dotenv()

print("="*70)
print("🔍 DIAGNÓSTICO TELEGRAM")
print("="*70)
print()

# 1. Verificar variáveis de ambiente
print("[1] VARIÁVEIS DE AMBIENTE")
print("-" * 70)

enabled = os.getenv("TELEGRAM_ENABLED", "").lower()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print(f"✓ TELEGRAM_ENABLED: {enabled}")
print(f"✓ TELEGRAM_BOT_TOKEN: {bot_token[:20]}..." if bot_token else "✗ TELEGRAM_BOT_TOKEN: NÃO CONFIGURADO")
print(f"✓ TELEGRAM_CHAT_ID: {chat_id}")
print()

if not enabled or enabled != "true":
    print("❌ TELEGRAM_ENABLED não está 'true'")
    sys.exit(1)

if not bot_token:
    print("❌ TELEGRAM_BOT_TOKEN não está configurado")
    sys.exit(1)

if not chat_id:
    print("❌ TELEGRAM_CHAT_ID não está configurado")
    sys.exit(1)

print("✅ Todas as variáveis configuradas")
print()

# 2. Testar importação do telegram
print("[2] VERIFICANDO BIBLIOTECA python-telegram-bot")
print("-" * 70)

try:
    from telegram import Bot
    from telegram.error import TelegramError
    print("✅ Biblioteca python-telegram-bot importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    print("   Execute: pip install python-telegram-bot")
    sys.exit(1)

print()

# 3. Testar conexão com bot
print("[3] TESTANDO CONEXÃO COM BOT")
print("-" * 70)

try:
    bot = Bot(token=bot_token)
    print("✅ Bot criado com sucesso")
except Exception as e:
    print(f"❌ Erro ao criar bot: {e}")
    sys.exit(1)

print()

# 4. Testar obtenção de informações do bot
print("[4] OBTENDO INFORMAÇÕES DO BOT")
print("-" * 70)

async def get_bot_info():
    try:
        me = await bot.get_me()
        print(f"✅ Bot Username: @{me.username}")
        print(f"✅ Bot ID: {me.id}")
        print(f"✅ Bot Nome: {me.first_name}")
        return True
    except TelegramError as e:
        print(f"❌ Erro ao obter informações do bot: {e}")
        print("   Verifique se o token está correto")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

async def send_test_message():
    try:
        msg = await bot.send_message(
            chat_id=chat_id,
            text="🧪 Mensagem de teste do diagnóstico"
        )
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   Chat ID: {msg.chat_id}")
        print(f"   Message ID: {msg.message_id}")
        return True
    except TelegramError as e:
        print(f"❌ Erro do Telegram: {e}")
        print()
        print("SOLUÇÕES POSSÍVEIS:")
        if "Chat not found" in str(e):
            print("   • Chat ID está incorreto")
            print("   • Bot não foi adicionado ao canal/grupo")
            print("   • Canal/grupo foi deletado")
            print()
            print("COMO CORRIGIR:")
            print("   1. Verifique o nome do canal em Telegram")
            print("   2. Adicione o bot ao canal (procure por @hedgebtcbot)")
            print("   3. Se usar números, execute este comando no seu navegador:")
            print("      https://api.telegram.org/bot" + bot_token + "/getUpdates")
            print("      Procure por 'chat' no resultado JSON")
        elif "Unauthorized" in str(e):
            print("   • Token do bot está inválido ou expirado")
            print("   • Crie um novo bot em @BotFather")
        elif "Too Many Requests" in str(e):
            print("   • Muitas requisições ao Telegram")
            print("   • Aguarde alguns segundos e tente novamente")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"   Tipo: {type(e).__name__}")
        return False

async def main():
    try:
        result = await get_bot_info()
        if not result:
            sys.exit(1)
        print()
        print("[5] TESTANDO ENVIO DE MENSAGEM")
        print("-" * 70)
        result = await send_test_message()
        if result:
            print()
            print("="*70)
            print("✅ TUDO OK! Procure a mensagem em: " + chat_id)
            print("="*70)
        else:
            print()
            print("="*70)
            print("❌ FALHA AO ENVIAR MENSAGEM")
            print("="*70)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        sys.exit(1)

print()

try:
    # Usar asyncio.run com tratamento de event loop no Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
except Exception as e:
    print(f"❌ Erro crítico: {e}")
    sys.exit(1)
