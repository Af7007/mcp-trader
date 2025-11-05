#!/usr/bin/env python3
"""Mostra trades recentes salvos no banco"""
import sqlite3
from datetime import datetime

print("="*70)
print("TRADES RECENTES - btc_trading_logs.db")
print("="*70)

conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

# Contar total
cursor.execute('SELECT COUNT(*) FROM trades')
total = cursor.fetchone()[0]
print(f"\nTotal de trades: {total}")

# Mostrar ultimos 10
print(f"\nUltimos 10 trades:")
print("-"*70)

cursor.execute('''
    SELECT id, timestamp, symbol, trade_type, entry_price, 
           sl_price, tp_price, volume, status, reason
    FROM trades 
    ORDER BY id DESC 
    LIMIT 10
''')

for row in cursor.fetchall():
    trade_id, timestamp, symbol, trade_type, entry, sl, tp, volume, status, reason = row
    print(f"\nID: {trade_id}")
    print(f"  Time: {timestamp}")
    print(f"  Symbol: {symbol}")
    print(f"  Type: {trade_type}")
    print(f"  Entry: ${entry:.3f}")
    print(f"  SL: ${sl:.3f}")
    print(f"  TP: ${tp if tp else 0:.1f}")
    print(f"  Volume: {volume}")
    print(f"  Status: {status}")
    print(f"  Reason: {reason}")

# Verificar trailing stops
print(f"\n" + "="*70)
print("TRAILING STOPS REGISTRADOS")
print("="*70)

cursor.execute('SELECT COUNT(*) FROM trailing_stops')
total_trailing = cursor.fetchone()[0]
print(f"\nTotal de trailing stops: {total_trailing}")

if total_trailing > 0:
    print(f"\nUltimos 5 trailing stops:")
    print("-"*70)
    
    cursor.execute('''
        SELECT id, timestamp, trade_id, symbol, action, 
               old_sl_price, new_sl_price, profit_dinheiro
        FROM trailing_stops 
        ORDER BY id DESC 
        LIMIT 5
    ''')
    
    for row in cursor.fetchall():
        ts_id, timestamp, trade_id, symbol, action, old_sl, new_sl, profit = row
        print(f"\nID: {ts_id} | Trade ID: {trade_id}")
        print(f"  Time: {timestamp}")
        print(f"  Symbol: {symbol}")
        print(f"  Action: {action}")
        print(f"  SL: ${old_sl:.3f} -> ${new_sl:.3f}")
        print(f"  Profit: ${profit if profit else 0:.2f}")

conn.close()

print("\n" + "="*70)
