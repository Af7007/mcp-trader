#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recuperar SL/TP das ORDERS do MT5 usando position_id
como ligação entre orders e deals.
"""

import sqlite3
import MetaTrader5 as mt5
from datetime import datetime, timedelta

DB_FILE = "trading_bot.db"

print('=' * 120)
print('  RECUPERANDO SL/TP DAS ORDERS (COM CORRETO MATCHING POR POSITION_ID)')
print('=' * 120)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Obter deals
from_date = datetime.now() - timedelta(days=30)
deals = mt5.history_deals_get(from_date, datetime.now())

if not deals:
    print('[ERRO] Nenhum deal encontrado')
    mt5.shutdown()
    exit(1)

print(f'Total de deals encontrados: {len(deals)}')

# Criar mapa de position_id -> deal_tickets
position_to_deals = {}
for deal in deals:
    pos_id = getattr(deal, 'position_id', None)
    ticket = getattr(deal, 'ticket', None)

    if pos_id is not None and ticket is not None:
        if pos_id not in position_to_deals:
            position_to_deals[pos_id] = []
        position_to_deals[pos_id].append(ticket)

print(f'Posições com deals encontradas: {len(position_to_deals)}')
print()

# Obter orders
orders = mt5.history_orders_get(from_date, datetime.now())

if not orders:
    print('[ERRO] Nenhuma order encontrada')
    mt5.shutdown()
    exit(1)

print(f'Total de orders encontradas: {len(orders)}')

# Criar mapa de position_id -> SL/TP
position_to_sl_tp = {}
for order in orders:
    pos_id = getattr(order, 'position_id', None)
    sl = getattr(order, 'sl', 0)
    tp = getattr(order, 'tp', 0)

    if pos_id and (sl != 0 or tp != 0):
        if pos_id not in position_to_sl_tp:
            position_to_sl_tp[pos_id] = {'sl': sl, 'tp': tp}
        else:
            # Usar os valores se ainda nao foram setados
            if position_to_sl_tp[pos_id]['sl'] == 0 and sl != 0:
                position_to_sl_tp[pos_id]['sl'] = sl
            if position_to_sl_tp[pos_id]['tp'] == 0 and tp != 0:
                position_to_sl_tp[pos_id]['tp'] = tp

print(f'Posições com SL/TP encontradas: {len(position_to_sl_tp)}')
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

# Criar mapa inverso: ticket -> position_id
# Procurando nos deals synchronized
ticket_to_position = {}
for pos_id, tickets in position_to_deals.items():
    for ticket in tickets:
        if ticket not in ticket_to_position:
            ticket_to_position[ticket] = pos_id

# Atualizar com dados das orders
updated = 0
not_found = 0
matched = 0

print('ATUALIZANDO TRADES:')
print('-' * 120)

for trade_ticket, old_sl, old_tp in trades_to_update:
    # Procurar a position_id deste trade
    if trade_ticket in ticket_to_position:
        pos_id = ticket_to_position[trade_ticket]
        matched += 1

        if pos_id in position_to_sl_tp:
            sl_tp = position_to_sl_tp[pos_id]
            new_sl = sl_tp['sl']
            new_tp = sl_tp['tp']

            if new_sl != 0 or new_tp != 0:
                cursor.execute("""
                    UPDATE trades SET sl = ?, tp = ? WHERE ticket = ?
                """, (new_sl, new_tp, trade_ticket))

                print(f'Ticket {trade_ticket:10d} (Pos #{pos_id:10d}) | SL: ${old_sl:8.2f} > ${new_sl:10.2f} | TP: ${old_tp:8.2f} > ${new_tp:10.2f}')
                updated += 1

    if trade_ticket not in ticket_to_position:
        not_found += 1

conn.commit()
conn.close()

print()
print('-' * 120)
print(f'Trades matched com position_id: {matched}')
print(f'Trades com SL/TP encontrados: {updated}')
print(f'Trades sem position_id no mapping: {not_found}')
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
