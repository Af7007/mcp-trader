#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relatório detalhado dos trades sincronizados.
"""

import sqlite3
from datetime import datetime

DB_FILE = "trading_bot.db"

print('=' * 100)
print('  RELATORIO DETALHADO DE TRADES SINCRONIZADOS')
print('=' * 100)
print()

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 1. Total de trades
cursor.execute("SELECT COUNT(*) FROM trades")
total_trades = cursor.fetchone()[0]

# 2. Estatísticas gerais
cursor.execute("""
    SELECT
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit) as total_profit,
        AVG(profit) as avg_profit,
        MAX(profit) as max_profit,
        MIN(profit) as min_profit
    FROM trades
""")

wins, losses, total_profit, avg_profit, max_profit, min_profit = cursor.fetchone()

print('RESUMO GERAL:')
print('-' * 100)
print(f'Total de Trades: {total_trades}')
print(f'Vitórias: {wins} ({wins/total_trades*100:.1f}%)')
print(f'Derrotas: {losses} ({losses/total_trades*100:.1f}%)')
print(f'Lucro Total: ${total_profit:.2f}')
print(f'Lucro Médio: ${avg_profit:.2f}')
print(f'Maior Lucro: ${max_profit:.2f}')
print(f'Maior Prejuízo: ${min_profit:.2f}')
print()

# 3. Por símbolo
print('RESULTADO POR SIMBOLO:')
print('-' * 100)

cursor.execute("""
    SELECT
        symbol,
        COUNT(*) as count,
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit) as total_profit,
        AVG(profit) as avg_profit,
        SUM(volume) as total_volume
    FROM trades
    GROUP BY symbol
    ORDER BY total_profit DESC
""")

for row in cursor.fetchall():
    symbol, count, sym_wins, sym_losses, sym_profit, sym_avg, sym_volume = row
    if symbol == '':
        symbol = 'UNKNOWN'
    win_rate = (sym_wins / count * 100) if count > 0 else 0
    print(f'{symbol:12s} | {count:4d} trades | {sym_wins:3d} wins ({win_rate:5.1f}%) | {sym_losses:3d} losses | Lucro: ${sym_profit:10.2f} | Médio: ${sym_avg:6.2f}')

print()

# 4. Análise de wins e losses
print('ANALISE DE LUCROS E PERDAS:')
print('-' * 100)

cursor.execute("""
    SELECT
        SUM(CASE WHEN profit > 0 THEN profit ELSE 0 END) as total_wins,
        SUM(CASE WHEN profit <= 0 THEN ABS(profit) ELSE 0 END) as total_losses,
        AVG(CASE WHEN profit > 0 THEN profit ELSE NULL END) as avg_win,
        AVG(CASE WHEN profit <= 0 THEN profit ELSE NULL END) as avg_loss
    FROM trades
""")

total_wins, total_losses, avg_win, avg_loss = cursor.fetchone()

print(f'Soma das Vitórias: ${total_wins:.2f}')
print(f'Soma das Perdas: ${total_losses:.2f}')
print(f'Lucro Médio (Winners): ${avg_win:.2f}')
print(f'Prejuízo Médio (Losers): ${avg_loss:.2f}')
print(f'Razão Win/Loss: {abs(avg_win/avg_loss):.2f}:1' if avg_loss != 0 else 'N/A')
print()

# 5. Primeiros e últimos trades
print('PRIMEIROS 5 TRADES:')
print('-' * 100)

cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, profit, open_time
    FROM trades
    ORDER BY open_time ASC
    LIMIT 5
""")

for row in cursor.fetchall():
    ticket, symbol, trade_type, volume, open_p, close_p, profit, open_time = row
    profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
    print(f'#{ticket:10d} | {symbol:9s} | {trade_type:4s} | {volume:5.2f} | ${open_p:10.2f} -> ${close_p:10.2f} | {profit_str:9s}')

print()
print('ULTIMOS 5 TRADES:')
print('-' * 100)

cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price, profit, open_time
    FROM trades
    ORDER BY open_time DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    ticket, symbol, trade_type, volume, open_p, close_p, profit, open_time = row
    profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
    print(f'#{ticket:10d} | {symbol:9s} | {trade_type:4s} | {volume:5.2f} | ${open_p:10.2f} -> ${close_p:10.2f} | {profit_str:9s}')

print()

# 6. Distribuição de lucros
print('DISTRIBUICAO DE LUCROS:')
print('-' * 100)

cursor.execute("""
    SELECT
        CASE
            WHEN profit < -10 THEN 'Prejuizo > -$10'
            WHEN profit >= -10 AND profit < -5 THEN '-$10 a -$5'
            WHEN profit >= -5 AND profit < 0 THEN '-$5 a $0'
            WHEN profit >= 0 AND profit < 5 THEN '$0 a $5'
            WHEN profit >= 5 AND profit < 10 THEN '$5 a $10'
            WHEN profit >= 10 AND profit < 20 THEN '$10 a $20'
            WHEN profit >= 20 AND profit < 50 THEN '$20 a $50'
            ELSE 'Lucro > $50'
        END as range,
        COUNT(*) as count,
        SUM(profit) as total
    FROM trades
    GROUP BY range
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    range_name, count, total = row
    print(f'{range_name:20s} | {count:3d} trades | Total: ${total:10.2f}')

conn.close()

print()
print('=' * 100)
print('  FIM DO RELATORIO')
print('=' * 100)
