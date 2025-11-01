#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se Telegram esta enviando com Balance e Profit Percentage
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print("\n" + "="*80)
print(" VERIFICACAO - TELEGRAM COM BALANCE E PROFIT PERCENTAGE")
print("="*80)

if not bot_token or not chat_id:
    print("ERRO: Telegram nao configurado no .env")
    sys.exit(1)

print("OK: Credenciais carregadas\n")

sys.path.insert(0, os.path.dirname(__file__))

from src.core.telegram_notifier import TelegramNotifier
import time

notifier = TelegramNotifier()

if not notifier.enabled:
    print("ERRO: Telegram nao habilitado")
    sys.exit(1)

print("OK: Telegram inicializado\n")

# Teste COM balance e profit_percentage
print("="*80)
print(" TESTE 1: Mensagem COM balance e profit_percentage")
print("="*80)

result = notifier.send_trade_closed(
    ticket=999888777,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=2050.00,
    close_price=2045.00,
    profit=50.00,
    duration_seconds=480,
    daily_stats={
        'total_profit': 125.00,
        'win_rate': 71.4,
        'wins': 5,
        'losses': 2,
        'trades_count': 7
    },
    total_wins=5,
    total_losses=2,
    account_balance=1500.00,
    profit_percentage=8.33
)

if result:
    print("[OK] Mensagem COM balance/percentage enviada com sucesso!")
    print("\nVerifique no Telegram por:")
    print("  - Campo 'Balance:' com valor $")
    print("  - Campo 'Lucro Acumulado:' com valor %")
    print("  - Emoji dinamico (fogo, seta ou queda)")
else:
    print("[ERRO] Falha ao enviar mensagem COM balance/percentage")

time.sleep(3)

# Teste SEM balance e profit_percentage (valores padroes)
print("\n" + "="*80)
print(" TESTE 2: Mensagem SEM balance e profit_percentage (valores padroes)")
print("="*80)

result2 = notifier.send_trade_closed(
    ticket=999888778,
    symbol="XAUUSDm",
    trade_type="SELL",
    entry_price=2048.00,
    close_price=2058.00,
    profit=-100.00,
    duration_seconds=240,
    daily_stats={
        'total_profit': 25.00,
        'win_rate': 60.0,
        'wins': 5,
        'losses': 3,
        'trades_count': 8
    },
    total_wins=5,
    total_losses=3
    # SEM account_balance e profit_percentage - serao 0
)

if result2:
    print("[OK] Mensagem SEM balance/percentage enviada com sucesso!")
    print("\nVerifique no Telegram por:")
    print("  - Campo 'Balance:' mostrando $0.00")
    print("  - Campo 'Lucro Acumulado:' mostrando 0.00%")
else:
    print("[ERRO] Falha ao enviar mensagem SEM balance/percentage")

# Resumo
print("\n" + "="*80)
print(" RESUMO DA VERIFICACAO")
print("="*80)

if result and result2:
    print("\n[OK] AMBAS as mensagens foram enviadas!")
    print("\nVerifique seu Telegram:")
    print("  1ª mensagem: COM valores de balance e percentage")
    print("  2ª mensagem: COM valores zerados (padroes)")
    print("\nISSO CONFIRMA QUE AS ALTERACOES ESTAO IMPLEMENTADAS!")
    print("\nPARA VER EM PRODUCAO:")
    print("  1. Reinicie o agent Gold:")
    print("     RUN_GOLD_AGENT.bat")
    print("  2. Aguarde primeiro trade fechar")
    print("  3. Verifique Telegram por:")
    print("     - Balance: valor real da sua conta")
    print("     - Lucro Acumulado: percentual do dia")
else:
    print("\n[AVISO] Possivel problema no envio de mensagens")
    print(f"  Resultado 1 (COM valores): {result}")
    print(f"  Resultado 2 (SEM valores): {result2}")

print("\n" + "="*80 + "\n")
