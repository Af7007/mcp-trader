#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise detalhada dos ÚLTIMOS TRADES para identificar padrões de loss.
"""

import sqlite3
from datetime import datetime

DB_FILE = "trading_bot.db"

print('=' * 120)
print('  ANALISE DOS ULTIMOS TRADES - IDENTIFICANDO PADROES DE LOSS')
print('=' * 120)
print()

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Pegar últimos 50 trades
cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, sl, tp, profit, open_time, close_time
    FROM trades
    ORDER BY open_time DESC
    LIMIT 50
""")

trades = cursor.fetchall()

print(f'ANALISANDO OS ULTIMOS {len(trades)} TRADES:')
print()

wins = 0
losses = 0
win_profit = 0
loss_profit = 0
win_distance = 0
loss_distance = 0

print('DETALHES DE CADA TRADE:')
print('-' * 120)

for row in trades:
    ticket, symbol, trade_type, volume, open_p, close_p, sl, tp, profit, open_time, close_time = row

    # Calcular distância do preço de abertura
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p

    # Calcular percentual
    pct = (distance / open_p) * 100

    # Contar wins e losses
    if profit > 0:
        wins += 1
        win_profit += profit
        win_distance += distance
    else:
        losses += 1
        loss_profit += profit
        loss_distance += distance

    profit_str = f"+${profit:7.2f}" if profit >= 0 else f"-${abs(profit):7.2f}"
    distance_str = f"+${distance:7.2f}" if distance >= 0 else f"-${abs(distance):7.2f}"

    print(f'Ticket {ticket:10d} | {symbol:9s} | {trade_type:4s} | '
          f'${open_p:10.2f} > ${close_p:10.2f} | {distance_str} ({pct:+6.2f}%) | '
          f'Lucro: {profit_str} | SL: ${sl:10.2f} | TP: ${tp:10.2f}')

print()
print('=' * 120)
print('RESUMO ESTATISTICO:')
print('=' * 120)
print()

total_trades = wins + losses
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
loss_rate = (losses / total_trades * 100) if total_trades > 0 else 0

print(f'Vitórias: {wins} ({win_rate:.1f}%)')
print(f'Derrotas: {losses} ({loss_rate:.1f}%)')
print()

if wins > 0:
    avg_win = win_profit / wins
    avg_distance_win = win_distance / wins
    print(f'Lucro Médio (Winners): ${avg_win:.2f}')
    print(f'Distância Média (Winners): ${avg_distance_win:.2f}')
    print()

if losses > 0:
    avg_loss = loss_profit / losses
    avg_distance_loss = loss_distance / losses
    print(f'Prejuízo Médio (Losers): ${avg_loss:.2f}')
    print(f'Distância Média (Losers): ${avg_distance_loss:.2f}')
    print()

print(f'Lucro Total (50 últimos): ${win_profit + loss_profit:.2f}')
print()

# Análise por símbolo
print('=' * 120)
print('PERFORMANCE DOS ULTIMOS TRADES POR SIMBOLO:')
print('=' * 120)
print()

cursor.execute("""
    SELECT
        symbol,
        COUNT(*) as total,
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit) as total_profit,
        AVG(profit) as avg_profit
    FROM (
        SELECT ticket, symbol, profit
        FROM trades
        ORDER BY open_time DESC
        LIMIT 50
    )
    GROUP BY symbol
    ORDER BY total_profit DESC
""")

for row in cursor.fetchall():
    symbol, total, sym_wins, sym_losses, sym_profit, sym_avg = row
    if symbol == '':
        symbol = 'UNKNOWN'

    win_pct = (sym_wins / total * 100) if total > 0 else 0
    profit_str = f"+${sym_profit:.2f}" if sym_profit >= 0 else f"-${abs(sym_profit):.2f}"

    print(f'{symbol:9s} | {total:2d} trades | {sym_wins:2d} wins ({win_pct:5.1f}%) | '
          f'{sym_losses:2d} losses | Lucro: {profit_str:9s} | Médio: ${sym_avg:+7.2f}')

print()

# Análise de BUY vs SELL
print('=' * 120)
print('PERFORMANCE BUY vs SELL (ULTIMOS 50 TRADES):')
print('=' * 120)
print()

cursor.execute("""
    SELECT
        type,
        COUNT(*) as total,
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit) as total_profit,
        AVG(profit) as avg_profit
    FROM (
        SELECT type, profit
        FROM trades
        ORDER BY open_time DESC
        LIMIT 50
    )
    GROUP BY type
""")

for row in cursor.fetchall():
    trade_type, total, sym_wins, sym_losses, sym_profit, sym_avg = row

    win_pct = (sym_wins / total * 100) if total > 0 else 0
    profit_str = f"+${sym_profit:.2f}" if sym_profit >= 0 else f"-${abs(sym_profit):.2f}"

    print(f'{trade_type:4s} | {total:2d} trades | {sym_wins:2d} wins ({win_pct:5.1f}%) | '
          f'{sym_losses:2d} losses | Lucro: {profit_str:9s} | Médio: ${sym_avg:+7.2f}')

print()

# Análise de maiores losses
print('=' * 120)
print('TOP 10 MAIORES LOSSES:')
print('=' * 120)
print()

cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, profit, open_time
    FROM trades
    WHERE profit < 0
    ORDER BY profit ASC
    LIMIT 10
""")

for row in cursor.fetchall():
    ticket, symbol, trade_type, volume, open_p, close_p, profit, open_time = row
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p
    pct = (distance / open_p) * 100 if open_p != 0 else 0

    print(f'Ticket {ticket:10d} | {symbol:9s} | {trade_type:4s} | '
          f'${open_p:10.2f} > ${close_p:10.2f} | '
          f'Distancia: ${distance:+7.2f} ({pct:+6.2f}%) | '
          f'Prejuizo: ${profit:.2f}')

print()

# Análise de maiores wins
print('=' * 120)
print('TOP 10 MAIORES WINS:')
print('=' * 120)
print()

cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, profit, open_time
    FROM trades
    WHERE profit > 0
    ORDER BY profit DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    ticket, symbol, trade_type, volume, open_p, close_p, profit, open_time = row
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p
    pct = (distance / open_p) * 100 if open_p != 0 else 0

    print(f'Ticket {ticket:10d} | {symbol:9s} | {trade_type:4s} | '
          f'${open_p:10.2f} > ${close_p:10.2f} | '
          f'Distancia: ${distance:+7.2f} ({pct:+6.2f}%) | '
          f'Lucro: ${profit:.2f}')

conn.close()

print()
print('=' * 120)
print('FIM DA ANALISE')
print('=' * 120)
