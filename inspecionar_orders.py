#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar ORDERS do MT5 (não deals).
Orders podem ter SL/TP, deals não têm.
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta

print('=' * 120)
print('  INSPECIONANDO ESTRUTURA DAS ORDERS DO MT5')
print('=' * 120)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Obter orders recentes
from_date = datetime.now() - timedelta(days=7)
orders = mt5.history_orders_get(from_date, datetime.now())

if not orders or len(orders) == 0:
    print('[ERRO] Nenhuma order encontrada nos ultimos 7 dias')
    mt5.shutdown()
    exit(1)

print(f'Total de orders encontradas: {len(orders)}')
print()

# Inspecionar a primeira order
first_order = orders[0]

print('ESTRUTURA DA PRIMEIRA ORDER:')
print('-' * 120)
print(f'Tipo: {type(first_order)}')
print()

print('ATRIBUTOS DA ORDER:')
print()

# Listar todos os atributos
if hasattr(first_order, '__dict__'):
    for attr, value in sorted(first_order.__dict__.items()):
        print(f'  {attr:25s}: {value}')
else:
    # Tentar acessar via getattr
    common_fields = [
        'ticket', 'order', 'state', 'time_setup', 'time_setup_msc', 'time_done', 'time_done_msc',
        'type', 'magic', 'reason', 'symbol', 'volume', 'volume_current', 'price_open',
        'sl', 'tp', 'price_current', 'commission', 'swap', 'profit', 'comment', 'external_id',
        'position_id', 'position_by_id'
    ]

    for field in common_fields:
        try:
            value = getattr(first_order, field, 'N/A')
            print(f'  {field:25s}: {value}')
        except Exception as e:
            print(f'  {field:25s}: ERRO - {e}')

print()
print('=' * 120)
print('ANALISANDO ORDERS COM SL/TP:')
print('=' * 120)
print()

# Procurar por orders que tenham SL/TP
orders_with_sl = 0
orders_with_tp = 0
sl_values = []
tp_values = []

for order in orders:
    sl = getattr(order, 'sl', None)
    tp = getattr(order, 'tp', None)

    if sl is not None and sl != 0:
        orders_with_sl += 1
        sl_values.append((order.ticket, sl))

    if tp is not None and tp != 0:
        orders_with_tp += 1
        tp_values.append((order.ticket, tp))

print(f'Orders com SL != 0: {orders_with_sl}/{len(orders)}')
print(f'Orders com TP != 0: {orders_with_tp}/{len(orders)}')

if sl_values:
    print()
    print('Exemplos de SL encontrados:')
    for ticket, sl in sl_values[:5]:
        print(f'  Ticket {ticket}: SL=${sl:.2f}')

if tp_values:
    print()
    print('Exemplos de TP encontrados:')
    for ticket, tp in tp_values[:5]:
        print(f'  Ticket {ticket}: TP=${tp:.2f}')

print()
print('=' * 120)
print('EXEMPLO COMPLETO DE ORDER:')
print('=' * 120)
print()

if orders:
    order = orders[0]
    print(f'Ticket: {getattr(order, "ticket", "N/A")}')
    print(f'Order: {getattr(order, "order", "N/A")}')
    print(f'State: {getattr(order, "state", "N/A")}')
    print(f'Type: {getattr(order, "type", "N/A")}')
    print(f'Symbol: {getattr(order, "symbol", "N/A")}')
    print(f'Volume: {getattr(order, "volume", "N/A")}')
    print(f'Volume Current: {getattr(order, "volume_current", "N/A")}')
    print(f'Price Open: {getattr(order, "price_open", "N/A")}')
    print(f'SL: {getattr(order, "sl", "N/A")}')
    print(f'TP: {getattr(order, "tp", "N/A")}')
    print(f'Price Current: {getattr(order, "price_current", "N/A")}')
    print(f'Position ID: {getattr(order, "position_id", "N/A")}')

print()
print('=' * 120)
print('PROCURANDO RELATIONSHIP ENTRE ORDERS E DEALS:')
print('=' * 120)
print()

# Obter deals também
deals = mt5.history_deals_get(from_date, datetime.now())
print(f'Total de orders: {len(orders)}')
print(f'Total de deals: {len(deals)}')
print()

# Ver se conseguimos encontrar padrão
if orders and deals:
    print('Primeiras 5 orders:')
    for order in orders[:5]:
        order_ticket = getattr(order, 'ticket', None)
        order_pos = getattr(order, 'position_id', None)
        order_sl = getattr(order, 'sl', 0)
        order_tp = getattr(order, 'tp', 0)

        print(f'  Order #{order_ticket} | Posição #{order_pos} | SL=${order_sl:.2f} | TP=${order_tp:.2f}')

mt5.shutdown()

print()
print('=' * 120)
print('FIM DA INSPECAO')
print('=' * 120)
