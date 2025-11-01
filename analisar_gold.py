#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise detalhada dos ULTIMOS 30 TRADES DE GOLD (XAUUSDm)
Focar em padroes de loss.
"""

import sqlite3
from datetime import datetime

DB_FILE = "trading_bot.db"

print('=' * 140)
print('  ANALISE DOS ULTIMOS 30 TRADES DE GOLD (XAUUSDm)')
print('=' * 140)
print()

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Pegar últimos 30 trades de XAUUSDm
cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, sl, tp, profit, open_time
    FROM trades
    WHERE symbol = 'XAUUSDm'
    ORDER BY open_time DESC
    LIMIT 30
""")

trades = cursor.fetchall()

print(f'ANALISANDO OS ULTIMOS {len(trades)} TRADES DE GOLD:')
print()

wins = 0
losses = 0
win_profit = 0
loss_profit = 0
total_trades = 0
consecutive_wins = 0
consecutive_losses = 0
max_consecutive_losses = 0
current_consecutive_losses = 0

# Processar em ordem reversa (do mais antigo para o mais recente)
trades_reversed = list(reversed(trades))

print('DETALHES DE CADA TRADE (ORDEM CRONOLOGICA):')
print('-' * 140)
print(f'{"#":3s} | {"Ticket":11s} | {"Type":6s} | {"Volume":8s} | {"Entry":11s} | {"Exit":11s} | {"SL":11s} | {"TP":11s} | {"P&L":10s} | {"Status":8s}')
print('-' * 140)

for idx, row in enumerate(trades_reversed, 1):
    ticket, symbol, trade_type, volume, open_p, close_p, sl, tp, profit, open_time = row

    # Calcular movimento
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p
    pct = (distance / open_p) * 100 if open_p != 0 else 0

    # Status
    if profit > 0:
        status = "WIN"
        wins += 1
        win_profit += profit
        consecutive_wins += 1
        current_consecutive_losses = 0
    else:
        status = "LOSS"
        losses += 1
        loss_profit += profit
        consecutive_losses += 1
        current_consecutive_losses += 1
        max_consecutive_losses = max(max_consecutive_losses, current_consecutive_losses)
        consecutive_wins = 0

    total_trades += 1

    profit_str = f"+${profit:7.2f}" if profit >= 0 else f"-${abs(profit):7.2f}"
    distance_str = f"${distance:+7.2f}"

    print(f'{idx:3d} | {ticket:11d} | {trade_type:6s} | {volume:8.2f} | ${open_p:10.2f} | ${close_p:10.2f} | ${sl:10.2f} | ${tp:10.2f} | {profit_str} | {status:8s}')

print()
print('=' * 140)
print('RESUMO ESTATISTICO:')
print('=' * 140)
print()

total_trades = wins + losses
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
loss_rate = (losses / total_trades * 100) if total_trades > 0 else 0

print(f'Total de Trades: {total_trades}')
print(f'Vitórias: {wins} ({win_rate:.1f}%)')
print(f'Derrotas: {losses} ({loss_rate:.1f}%)')
print()

if wins > 0:
    avg_win = win_profit / wins
    print(f'Lucro Total (Winners): ${win_profit:.2f}')
    print(f'Lucro Médio (Winners): ${avg_win:.2f}')
    print()

if losses > 0:
    avg_loss = loss_profit / losses
    print(f'Prejuízo Total (Losers): ${loss_profit:.2f}')
    print(f'Prejuízo Médio (Losers): ${avg_loss:.2f}')
    print()

total_profit = win_profit + loss_profit
print(f'Lucro Total: ${total_profit:.2f}')
print(f'Max Consecutive Losses: {max_consecutive_losses}')
print()

# Análise de BUY vs SELL
print('=' * 140)
print('PERFORMANCE BUY vs SELL (30 ultimos trades de GOLD):')
print('=' * 140)
print()

cursor.execute("""
    SELECT
        type,
        COUNT(*) as total,
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit) as total_profit,
        AVG(profit) as avg_profit,
        MIN(profit) as min_profit,
        MAX(profit) as max_profit
    FROM (
        SELECT type, profit
        FROM trades
        WHERE symbol = 'XAUUSDm'
        ORDER BY open_time DESC
        LIMIT 30
    )
    GROUP BY type
""")

for row in cursor.fetchall():
    trade_type, total, sym_wins, sym_losses, sym_profit, sym_avg, min_p, max_p = row

    win_pct = (sym_wins / total * 100) if total > 0 else 0
    profit_str = f"+${sym_profit:.2f}" if sym_profit >= 0 else f"-${abs(sym_profit):.2f}"

    print(f'{trade_type:4s} | {total:2d} trades | {sym_wins:2d} wins ({win_pct:5.1f}%) | '
          f'{sym_losses:2d} losses | Lucro: {profit_str:9s} | Médio: ${sym_avg:+7.2f} | Min: ${min_p:+7.2f} | Max: ${max_p:+7.2f}')

print()

# Análise de padrões
print('=' * 140)
print('ANALISE DE PADROES:')
print('=' * 140)
print()

cursor.execute("""
    SELECT
        COUNT(*) as total,
        AVG(close_price - open_price) as avg_movement_buy,
        AVG(CASE WHEN type = 'BUY' THEN (close_price - open_price) * volume ELSE NULL END) as total_movement_buy,
        AVG(CASE WHEN type = 'SELL' THEN (open_price - close_price) * volume ELSE NULL END) as total_movement_sell
    FROM (
        SELECT type, volume, open_price, close_price
        FROM trades
        WHERE symbol = 'XAUUSDm'
        ORDER BY open_time DESC
        LIMIT 30
    )
""")

row = cursor.fetchone()
total, avg_mov_buy, total_mov_buy, total_mov_sell = row

if total > 0:
    print(f'Movimento médio por trade: ${avg_mov_buy:.2f}')
    print()

# Top losses e wins
print('=' * 140)
print('TOP 5 MAIORES LOSSES:')
print('=' * 140)
print()

cursor.execute("""
    SELECT ticket, type, volume, open_price, close_price, sl, tp, profit
    FROM trades
    WHERE symbol = 'XAUUSDm'
    ORDER BY profit ASC
    LIMIT 5
""")

for row in cursor.fetchall():
    ticket, trade_type, volume, open_p, close_p, sl, tp, profit = row
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p
    pct = (distance / open_p) * 100 if open_p != 0 else 0

    # Verificar se TP ou SL foram acionados
    if trade_type == 'BUY':
        hit_tp = close_p >= tp if tp > 0 else False
        hit_sl = close_p <= sl if sl > 0 else False
    else:
        hit_tp = close_p <= tp if tp > 0 else False
        hit_sl = close_p >= sl if sl > 0 else False

    trigger = ""
    if hit_sl:
        trigger = "SL HIT"
    elif hit_tp:
        trigger = "TP HIT"
    else:
        trigger = "TIMEOUT/OTHER"

    print(f'Ticket {ticket:10d} | {trade_type:4s} | ${open_p:10.2f} > ${close_p:10.2f} | '
          f'SL: ${sl:10.2f} | TP: ${tp:10.2f} | '
          f'Prejuizo: ${profit:+7.2f} | {trigger}')

print()
print('=' * 140)
print('TOP 5 MAIORES WINS:')
print('=' * 140)
print()

cursor.execute("""
    SELECT ticket, type, volume, open_price, close_price, sl, tp, profit
    FROM trades
    WHERE symbol = 'XAUUSDm'
    ORDER BY profit DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    ticket, trade_type, volume, open_p, close_p, sl, tp, profit = row
    distance = close_p - open_p if trade_type == 'BUY' else open_p - close_p
    pct = (distance / open_p) * 100 if open_p != 0 else 0

    # Verificar se TP ou SL foram acionados
    if trade_type == 'BUY':
        hit_tp = close_p >= tp if tp > 0 else False
        hit_sl = close_p <= sl if sl > 0 else False
    else:
        hit_tp = close_p <= tp if tp > 0 else False
        hit_sl = close_p >= sl if sl > 0 else False

    trigger = ""
    if hit_tp:
        trigger = "TP HIT"
    elif hit_sl:
        trigger = "SL HIT"
    else:
        trigger = "TIMEOUT/OTHER"

    print(f'Ticket {ticket:10d} | {trade_type:4s} | ${open_p:10.2f} > ${close_p:10.2f} | '
          f'SL: ${sl:10.2f} | TP: ${tp:10.2f} | '
          f'Lucro: ${profit:+7.2f} | {trigger}')

print()

# Análise de sequências
print('=' * 140)
print('SEQUENCIAS DE OPERACOES:')
print('=' * 140)
print()

cursor.execute("""
    SELECT ticket, type, profit
    FROM trades
    WHERE symbol = 'XAUUSDm'
    ORDER BY open_time DESC
    LIMIT 30
""")

trades_seq = list(reversed(cursor.fetchall()))

sequence = ""
for ticket, trade_type, profit in trades_seq:
    if profit > 0:
        sequence += "W"
    else:
        sequence += "L"

print(f'Sequência de Wins (W) e Losses (L):')
print(f'{sequence}')
print()

# Contar runs
runs = []
current_run = sequence[0]
run_length = 1

for i in range(1, len(sequence)):
    if sequence[i] == current_run:
        run_length += 1
    else:
        runs.append((current_run, run_length))
        current_run = sequence[i]
        run_length = 1

runs.append((current_run, run_length))

print('Sequências encontradas:')
for run_type, length in runs:
    status = "Wins" if run_type == "W" else "Losses"
    print(f'  {length} consecutive {status}')

conn.close()

print()
print('=' * 140)
print('FIM DA ANALISE DE GOLD')
print('=' * 140)
