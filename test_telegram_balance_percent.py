#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Telegram com Balance e Profit Percentage
Verifica se as mensagens WIN/LOSS incluem corretamente:
- Wins/Losses count
- Account balance
- Profit percentage
"""

import sys
import os

# Carregar .env
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print("\n" + "="*80)
print("TESTE TELEGRAM - BALANCE + PROFIT PERCENTAGE")
print("="*80)

if not bot_token or not chat_id:
    print("ERRO: Telegram nao configurado no .env")
    sys.exit(1)

print("OK: Variaveis de ambiente carregadas\n")

sys.path.insert(0, os.path.dirname(__file__))

from src.core.telegram_notifier import TelegramNotifier
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

notifier = TelegramNotifier()

if not notifier.enabled:
    print("ERRO: Telegram nao habilitado")
    sys.exit(1)

print("OK: Telegram inicializado\n")

# TESTE 1: WIN com balance e profit percentage positivo
print("="*80)
print("TESTE 1: WIN com Profit Percentage POSITIVO")
print("="*80)

result1 = notifier.send_trade_closed(
    ticket=125967293,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4070.00,
    close_price=4065.00,
    profit=5.00,
    duration_seconds=525,
    daily_stats={
        'total_profit': 27.50,
        'win_rate': 71.4,
        'winning_streak': 2,
        'trades_count': 7,
        'wins': 5,
        'losses': 2
    },
    total_wins=5,
    total_losses=2,
    account_balance=1250.00,
    profit_percentage=2.20  # +2.20% (27.50 / 1250 * 100)
)

if result1:
    print("[OK] WIN enviado com sucesso!\n")
else:
    print("[ERRO] Falha ao enviar WIN\n")

time.sleep(2)

# TESTE 2: LOSS com balance e profit percentage reduzido
print("="*80)
print("TESTE 2: LOSS com Profit Percentage REDUZIDO")
print("="*80)

result2 = notifier.send_trade_closed(
    ticket=125967294,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4068.00,
    close_price=4073.00,
    profit=-5.00,
    duration_seconds=312,
    daily_stats={
        'total_profit': 22.50,
        'win_rate': 62.5,
        'winning_streak': 0,
        'trades_count': 8,
        'wins': 5,
        'losses': 3
    },
    total_wins=5,
    total_losses=3,
    account_balance=1245.00,
    profit_percentage=1.81  # +1.81% (22.50 / 1245 * 100) - reduzido
)

if result2:
    print("[OK] LOSS enviado com sucesso!\n")
else:
    print("[ERRO] Falha ao enviar LOSS\n")

time.sleep(2)

# TESTE 3: WIN com profit percentage ALTO (🔥)
print("="*80)
print("TESTE 3: WIN com Profit Percentage ALTO (>=1.0%)")
print("="*80)

result3 = notifier.send_trade_closed(
    ticket=125967295,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4075.00,
    close_price=4070.00,
    profit=5.00,
    duration_seconds=180,
    daily_stats={
        'total_profit': 50.00,
        'win_rate': 75.0,
        'winning_streak': 5,
        'trades_count': 12,
        'wins': 9,
        'losses': 3
    },
    total_wins=9,
    total_losses=3,
    account_balance=1250.00,
    profit_percentage=4.0  # +4.0% (50 / 1250 * 100) - ALTO, mostra 🔥
)

if result3:
    print("[OK] WIN com HIGH % enviado com sucesso!\n")
else:
    print("[ERRO] Falha ao enviar WIN HIGH %\n")

time.sleep(2)

# TESTE 4: LOSS com profit percentage negativo
print("="*80)
print("TESTE 4: LOSS com Profit Percentage NEGATIVO")
print("="*80)

result4 = notifier.send_trade_closed(
    ticket=125967296,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=4060.00,
    close_price=4070.00,
    profit=-10.00,
    duration_seconds=240,
    daily_stats={
        'total_profit': 40.00,
        'win_rate': 66.7,
        'winning_streak': 0,
        'trades_count': 13,
        'wins': 9,
        'losses': 4
    },
    total_wins=9,
    total_losses=4,
    account_balance=1240.00,
    profit_percentage=3.22  # +3.22% (40 / 1240 * 100) - mas trade foi perda
)

if result4:
    print("[OK] LOSS enviado com sucesso!\n")
else:
    print("[ERRO] Falha ao enviar LOSS\n")

# RESUMO
print("="*80)
print("RESUMO DO TESTE")
print("="*80)

all_sent = result1 and result2 and result3 and result4

if all_sent:
    print("\n[SUCESSO] 4 mensagens enviadas com sucesso!\n")
    print("Voce deve ter recebido 4 mensagens no Telegram:\n")
    print("1. WIN com Balance=$1250.00 e Lucro Acumulado=+2.20%")
    print("2. LOSS com Balance=$1245.00 e Lucro Acumulado=+1.81%")
    print("3. WIN com Balance=$1250.00 e Lucro Acumulado=+4.0% (emoji fogo)")
    print("4. LOSS com Balance=$1240.00 e Lucro Acumulado=+3.22%\n")
    print("Verificar especialmente:")
    print("  [*] Campo 'Balance' presente em todas")
    print("  [*] Campo 'Lucro Acumulado' (%) presente em todas")
    print("  [*] Emoji fogo na mensagem 3 (percentual >= 1.0%)")
    print("  [*] Emoji seta nas mensagens com % positivo")
    print("  [*] Wins/Losses counters atualizados em cada mensagem")
    print("\n[COMPLETO] Implementacao COMPLETA!\n")
else:
    print("\n[ERRO] Uma ou mais mensagens falharam")
    print(f"Results: WIN1={result1}, LOSS1={result2}, WIN2={result3}, LOSS2={result4}\n")

print("="*80)
