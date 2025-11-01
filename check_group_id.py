#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para obter o Chat ID correto do seu grupo privado
"""

import sys
import os
from dotenv import load_dotenv
import asyncio

# Configurar encoding UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Carregar variáveis do .env
load_dotenv()

from telegram import Bot

print("="*70)
print("🔍 VERIFICADOR DE CHAT ID DO GRUPO PRIVADO")
print("="*70)
print()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print(f"Chat ID configurado no .env: {chat_id}")
print()

if not bot_token:
    print("❌ TELEGRAM_BOT_TOKEN não está configurado")
    sys.exit(1)

bot = Bot(token=bot_token)

async def get_chat_info():
    """Obtém informações do chat"""
    try:
        if chat_id.startswith('@'):
            print(f"ℹ️ Chat ID começa com @, tentando usar como username...")
            chat = await bot.get_chat(chat_id)
        else:
            print(f"ℹ️ Chat ID é numérico, obtendo informações...")
            chat = await bot.get_chat(int(chat_id))

        print()
        print("✅ Chat encontrado!")
        print(f"   Nome: {chat.title}")
        print(f"   Tipo: {chat.type}")
        print(f"   Chat ID: {chat.id}")
        print(f"   Username: {chat.username if chat.username else 'N/A'}")
        print()

        # Tentar enviar mensagem de teste
        print("Tentando enviar mensagem de teste...")
        msg = await bot.send_message(
            chat_id=chat.id,
            text="✅ Teste de mensagem - Chat ID correto!"
        )
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   Message ID: {msg.message_id}")
        print(f"   Seu Chat ID correto é: {chat.id}")

        return chat.id

    except Exception as e:
        print(f"❌ Erro: {e}")
        print()
        print("POSSÍVEIS CAUSAS:")
        print("1. Bot não foi adicionado ao grupo")
        print("2. Chat ID está incorreto")
        print("3. Grupo foi deletado")
        print()
        print("SOLUÇÃO:")
        print("1. Abra o Telegram")
        print("2. Abra seu grupo privado")
        print("3. Adicione o bot @hedgebtcbot ao grupo")
        print("4. Certifique-se que o bot tem permissão de enviar mensagens")
        return None

print("Obtendo informações do chat...")
print()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    chat_id_result = asyncio.run(get_chat_info())
    if chat_id_result:
        print()
        print("="*70)
        print(f"📝 Atualize seu .env com:")
        print(f"TELEGRAM_CHAT_ID={chat_id_result}")
        print("="*70)
except Exception as e:
    print(f"❌ Erro crítico: {e}")
