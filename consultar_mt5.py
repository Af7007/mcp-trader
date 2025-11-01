#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consultar ordens direto do MT5.
"""

import MetaTrader5 as mt5
from datetime import datetime

print('=' * 80)
print('  CONSULTANDO ORDENS DIRETO DO MT5')
print('=' * 80)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    print()
    print('Certifique-se que:')
    print('1. Terminal MT5 esta aberto')
    print('2. Voce esta logado em uma conta de trading')
    print('3. Aguarde a conexao estabelecer (pode levar alguns segundos)')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Posições abertas
print('POSICOES ABERTAS:')
print('-' * 80)
positions = mt5.positions_get()
if positions:
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
print('HISTORICO DE DEALS (ULTIMOS 100):')
print('-' * 80)
deals = mt5.history_deals_get()
if deals:
    print(f'Total de deals no historico: {len(deals)}')
    print()

    # Mostrar apenas os últimos 100
    for deal in deals[-100:]:
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
    print('[INFO] Nenhum deal no historico')

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
