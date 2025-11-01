#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consultar TODAS as ordens do MT5 (histórico completo).
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta

print('=' * 80)
print('  CONSULTANDO HISTORICO COMPLETO DO MT5')
print('=' * 80)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Posições abertas
print('POSICOES ABERTAS AGORA:')
print('-' * 80)
positions = mt5.positions_get()
if positions:
    print(f'Total de posicoes abertas: {len(positions)}')
    print()
    for pos in positions:
        deal_type = 'BUY' if pos.type == 0 else 'SELL'
        print(f'Ticket: {pos.ticket}')
        print(f'  Simbolo: {pos.symbol}')
        print(f'  Tipo: {deal_type}')
        print(f'  Volume: {pos.volume} lots')
        print(f'  Preco Entrada: ${pos.price_open:.2f}')
        print(f'  Preco Atual: ${pos.price_current:.2f}')
        print(f'  Lucro/Prejuizo: ${pos.profit:.2f}')
        print()
else:
    print('[INFO] Nenhuma posicao aberta')

print()
print('HISTORICO DE DEALS - ULTIMOS 7 DIAS:')
print('-' * 80)

# Obter deals dos últimos 7 dias
from_date = datetime.now() - timedelta(days=7)
deals = mt5.history_deals_get(from_date, datetime.now())

if deals:
    print(f'Total de deals nos ultimos 7 dias: {len(deals)}')
    print()

    for deal in deals:
        deal_type = 'BUY' if deal.type == 0 else 'SELL'
        deal_time = datetime.fromtimestamp(deal.time) if deal.time else datetime.now()

        print(f'Deal #{deal.ticket} | Posicao #{deal.position_id}')
        print(f'  Simbolo: {deal.symbol}')
        print(f'  Tipo: {deal_type}')
        print(f'  Volume: {deal.volume} lots')
        print(f'  Preco: ${deal.price:.2f}')
        print(f'  Lucro: ${deal.profit:.2f}')
        print(f'  Comissao: ${deal.commission:.2f}')
        print(f'  Hora: {deal_time.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
else:
    print('[INFO] Nenhum deal nos ultimos 7 dias')

print()
print('HISTORICO DE DEALS - TODOS OS TEMPOS:')
print('-' * 80)

# Obter TODOS os deals
all_deals = mt5.history_deals_get()

if all_deals:
    print(f'Total de deals de TODOS OS TEMPOS: {len(all_deals)}')
    print()

    # Agrupar por símbolo
    by_symbol = {}
    for deal in all_deals:
        symbol = deal.symbol
        if symbol not in by_symbol:
            by_symbol[symbol] = []
        by_symbol[symbol].append(deal)

    print('RESUMO POR SIMBOLO:')
    print('-' * 80)
    for symbol in sorted(by_symbol.keys()):
        deals_list = by_symbol[symbol]
        total_deals = len(deals_list)
        total_profit = sum(d.profit for d in deals_list)
        total_volume = sum(d.volume for d in deals_list)

        print(f'{symbol}: {total_deals} deals | Volume Total: {total_volume} lots | Lucro Total: ${total_profit:.2f}')

    print()
    print('ULTIMOS 50 DEALS:')
    print('-' * 80)

    for deal in all_deals[-50:]:
        deal_type = 'BUY' if deal.type == 0 else 'SELL'
        deal_time = datetime.fromtimestamp(deal.time) if deal.time else datetime.now()

        print(f'Deal #{deal.ticket} | Pos #{deal.position_id} | {deal.symbol}')
        print(f'  Tipo: {deal_type} | Volume: {deal.volume} | Preco: ${deal.price:.2f} | Lucro: ${deal.profit:.2f}')
        print(f'  Hora: {deal_time.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
else:
    print('[INFO] Nenhum deal encontrado')

print()
print('INFORMACOES DA CONTA:')
print('-' * 80)
account = mt5.account_info()
if account:
    print(f'Conta: {account.login}')
    print(f'Servidor: {account.server}')
    print(f'Saldo: ${account.balance:.2f}')
    print(f'Patrimonio: ${account.equity:.2f}')
    print(f'Margem Livre: ${account.margin_free:.2f}')
    print(f'Margem Usada: ${account.margin:.2f}')
    print(f'Nivel de Margem: {account.margin_level:.2f}%')

mt5.shutdown()
