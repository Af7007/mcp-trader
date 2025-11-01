#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recuperar SL/TP das ORDERS do MT5 e atualizar o banco de dados.
Orders têm SL/TP, deals não têm!
"""

import sqlite3
import MetaTrader5 as mt5
from datetime import datetime, timedelta

DB_FILE = "trading_bot.db"

print('=' * 120)
print('  RECUPERANDO SL/TP DAS ORDERS DO MT5 E ATUALIZANDO BANCO')
print('=' * 120)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Obter todas as orders
from_date = datetime.now() - timedelta(days=30)
orders = mt5.history_orders_get(from_date, datetime.now())

if not orders:
    print('[ERRO] Nenhuma order encontrada')
    mt5.shutdown()
    exit(1)

print(f'Total de orders encontradas: {len(orders)}')
print()

# Criar mapa de orders por position_id
orders_map = {}
for order in orders:
    pos_id = getattr(order, 'position_id', None)
    ticket = getattr(order, 'ticket', None)
    sl = getattr(order, 'sl', 0)
    tp = getattr(order, 'tp', 0)

    if pos_id and (sl != 0 or tp != 0):
        if pos_id not in orders_map:
            orders_map[pos_id] = {'sl': 0, 'tp': 0, 'ticket': ticket}

        # Pegar o maior SL e TP
        if sl != 0:
            orders_map[pos_id]['sl'] = sl
        if tp != 0:
            orders_map[pos_id]['tp'] = tp

print(f'Orders com SL/TP encontradas: {len(orders_map)}')
print()

# Conectar banco de dados
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Obter trades que têm SL=$0 ou TP=$0
cursor.execute("""
    SELECT ticket, sl, tp FROM trades WHERE sl = 0 OR tp = 0
""")

trades_to_update = cursor.fetchall()
print(f'Trades no banco com SL=$0 ou TP=$0: {len(trades_to_update)}')
print()

# Atualizar com dados das orders
updated = 0
not_found = 0

print('ATUALIZANDO TRADES:')
print('-' * 120)

for trade_ticket, old_sl, old_tp in trades_to_update:
    if trade_ticket in orders_map:
        order_data = orders_map[trade_ticket]
        new_sl = order_data['sl']
        new_tp = order_data['tp']

        if new_sl != 0 or new_tp != 0:
            cursor.execute("""
                UPDATE trades SET sl = ?, tp = ? WHERE ticket = ?
            """, (new_sl, new_tp, trade_ticket))

            print(f'Ticket {trade_ticket:10d} | SL: ${old_sl:8.2f} → ${new_sl:8.2f} | TP: ${old_tp:8.2f} → ${new_tp:8.2f}')
            updated += 1
    else:
        not_found += 1

conn.commit()
conn.close()

print()
print('-' * 120)
print(f'Trades atualizados: {updated}')
print(f'Trades não encontrados nas orders: {not_found}')
print()

# Verificar resultado
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM trades WHERE sl = 0 AND tp = 0")
still_zero = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM trades WHERE sl != 0 OR tp != 0")
with_sl_tp = cursor.fetchone()[0]

print('=' * 120)
print('RESULTADO APOS ATUALIZACAO:')
print('=' * 120)
print(f'Trades com SL=$0 E TP=$0: {still_zero}')
print(f'Trades com SL!=0 OU TP!=0: {with_sl_tp}')
print()

# Mostrar exemplos de trades atualizados
cursor.execute("""
    SELECT ticket, symbol, type, sl, tp, profit FROM trades
    WHERE sl != 0 OR tp != 0
    ORDER BY ticket DESC
    LIMIT 10
""")

print('EXEMPLOS DE TRADES ATUALIZADOS:')
print('-' * 120)

for row in cursor.fetchall():
    ticket, symbol, trade_type, sl, tp, profit = row
    profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
    print(f'Ticket {ticket:10d} | {symbol:9s} | {trade_type:4s} | SL=${sl:10.2f} | TP=${tp:10.2f} | {profit_str}')

conn.close()
mt5.shutdown()

print()
print('=' * 120)
print('RECUPERACAO COMPLETA!')
print('=' * 120)
