#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Carregar .env
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print("\n" + "="*70)
print("TESTE TELEGRAM WIN/LOSS")
print("="*70)

if not bot_token or not chat_id:
    print("ERRO: Telegram nao configurado no .env")
    sys.exit(1)

print("OK: Variaveis de ambiente carregadas")
print(f"Bot Token: {bot_token[:20]}...")
print(f"Chat ID: {chat_id}\n")

sys.path.insert(0, os.path.dirname(__file__))

from src.core.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

if not notifier.enabled:
    print("ERRO: Telegram nao habilitado")
    sys.exit(1)

print("OK: Telegram inicializado\n")

# Teste WIN
print("Enviando mensagem WIN...")
result1 = notifier.send_trade_closed(
    ticket=125967293,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4070.00,
    close_price=4065.00,
    profit=5.00,
    duration_seconds=525,
    daily_stats={'total_profit': 27.50, 'win_rate': 71.4},
    total_wins=5,
    total_losses=2
)

if result1:
    print("OK: Mensagem WIN enviada\n")
else:
    print("ERRO: Falha ao enviar WIN\n")

# Teste LOSS
print("Enviando mensagem LOSS...")
import time
time.sleep(2)

result2 = notifier.send_trade_closed(
    ticket=125967294,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4068.00,
    close_price=4073.00,
    profit=-5.00,
    duration_seconds=312,
    daily_stats={'total_profit': 22.50, 'win_rate': 62.5},
    total_wins=5,
    total_losses=3
)

if result2:
    print("OK: Mensagem LOSS enviada\n")
else:
    print("ERRO: Falha ao enviar LOSS\n")

if result1 and result2:
    print("="*70)
    print("SUCESSO! Verifique seu Telegram por 2 mensagens:")
    print("  1. WIN com Wins: 5, Losses: 2")
    print("  2. LOSS com Wins: 5, Losses: 3")
    print("="*70)
else:
    print("ERRO: Uma ou mais mensagens falharam")
