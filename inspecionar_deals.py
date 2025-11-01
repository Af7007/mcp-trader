#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar quais informacoes estao disponíveis nos deals do MT5.
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta

print('=' * 120)
print('  INSPECIONANDO ESTRUTURA DOS DEALS DO MT5')
print('=' * 120)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Obter deals recentes
from_date = datetime.now() - timedelta(days=1)
deals = mt5.history_deals_get(from_date, datetime.now())

if not deals or len(deals) == 0:
    print('[ERRO] Nenhum deal encontrado nos ultimos 1 dia')
    mt5.shutdown()
    exit(1)

print(f'Total de deals encontrados: {len(deals)}')
print()

# Inspecionar o primeiro deal
first_deal = deals[0]

print('ESTRUTURA DO PRIMEIRO DEAL:')
print('-' * 120)
print(f'Tipo: {type(first_deal)}')
print()

if hasattr(first_deal, '__dict__'):
    print('ATRIBUTOS DO DEAL:')
    for attr, value in first_deal.__dict__.items():
        print(f'  {attr:20s}: {value} (tipo: {type(value).__name__})')
else:
    print('CAMPOS DO DEAL (via atributos):')
    # Tentar acessar campos comuns
    common_fields = [
        'ticket', 'order', 'time', 'time_msc', 'type', 'entry', 'magic', 'symbol', 'volume',
        'price', 'commission', 'swap', 'profit', 'fee', 'sl', 'tp', 'position_id',
        'comment', 'external_id', 'reason'
    ]

    for field in common_fields:
        try:
            value = getattr(first_deal, field, 'N/A')
            print(f'  {field:20s}: {value}')
        except Exception as e:
            print(f'  {field:20s}: ERRO - {e}')

print()
print('=' * 120)
print('ANALISANDO DEALS COM SL/TP:')
print('=' * 120)
print()

# Procurar por deals que possam ter SL/TP
has_sl = 0
has_tp = 0
sl_values = []
tp_values = []

for deal in deals:
    sl = getattr(deal, 'sl', None)
    tp = getattr(deal, 'tp', None)

    if sl is not None and sl != 0:
        has_sl += 1
        sl_values.append(sl)

    if tp is not None and tp != 0:
        has_tp += 1
        tp_values.append(tp)

print(f'Deals com SL != 0: {has_sl}/{len(deals)}')
print(f'Deals com TP != 0: {has_tp}/{len(deals)}')

if sl_values:
    print(f'Exemplos de SL encontrados: {sl_values[:5]}')

if tp_values:
    print(f'Exemplos de TP encontrados: {tp_values[:5]}')

print()

# Verificar se há campo de position_id
print('VERIFICANDO RELACIONAMENTO COM POSICOES:')
print('-' * 120)

position_deals = {}
for deal in deals:
    pos_id = getattr(deal, 'position_id', None)
    if pos_id:
        if pos_id not in position_deals:
            position_deals[pos_id] = []
        position_deals[pos_id].append(deal)

print(f'Total de posicoes: {len(position_deals)}')
print()

# Mostrar exemplo de posição completa
if position_deals:
    first_pos = list(position_deals.items())[0]
    pos_id, pos_deals = first_pos

    print(f'EXEMPLO: Posicao #{pos_id} com {len(pos_deals)} deal(s):')
    print()

    for idx, deal in enumerate(pos_deals):
        print(f'  Deal {idx + 1}:')
        print(f'    Ticket: {getattr(deal, "ticket", "N/A")}')
        print(f'    Tipo: {"BUY" if getattr(deal, "type", 0) == 0 else "SELL"}')
        print(f'    Volume: {getattr(deal, "volume", "N/A")}')
        print(f'    Preco: ${getattr(deal, "price", "N/A"):.2f}')
        print(f'    SL: {getattr(deal, "sl", "N/A")}')
        print(f'    TP: {getattr(deal, "tp", "N/A")}')
        print(f'    Lucro: ${getattr(deal, "profit", "N/A")}')
        print()

mt5.shutdown()

print()
print('=' * 120)
print('FIM DA INSPECAO')
print('=' * 120)
