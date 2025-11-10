#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica o schema do banco de dados e busca últimas ordens
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'btc_trading_logs.db'

if not db_path.exists():
    print(f"Banco nao encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Verificar schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='trades';")
schema = cursor.fetchone()

if schema:
    print("SCHEMA DA TABELA 'trades':")
    print("="*80)
    print(schema[0])
    print("\n")

# Listar colunas
cursor.execute("PRAGMA table_info(trades)")
columns = cursor.fetchall()

print("COLUNAS DISPONIVEIS:")
print("="*80)
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n")

# Buscar últimas 5 ordens
try:
    cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 5")
    trades = cursor.fetchall()

    col_names = [description[0] for description in cursor.description]

    print(f"ULTIMAS {len(trades)} ORDENS:")
    print("="*80)

    for trade in trades:
        print("\nOrdem:")
        for i, col_name in enumerate(col_names):
            if col_name in ['entry_price', 'sl_price', 'tp_price', 'profit_loss']:
                value = f"${trade[i]:.3f}" if trade[i] else "N/A"
            else:
                value = trade[i] if trade[i] else "N/A"
            print(f"  {col_name}: {value}")

        # Calcular SL distance se possível
        if 'entry_price' in col_names and 'sl_price' in col_names and 'type' in col_names:
            entry_idx = col_names.index('entry_price')
            sl_idx = col_names.index('sl_price')
            type_idx = col_names.index('type')

            entry = trade[entry_idx]
            sl = trade[sl_idx]
            trade_type = trade[type_idx]

            if entry and sl:
                if trade_type and 'BUY' in str(trade_type).upper():
                    sl_distance = entry - sl
                    print(f"  SL_DISTANCE (BUY): ${sl_distance:.3f}")
                elif trade_type and 'SELL' in str(trade_type).upper():
                    sl_distance = sl - entry
                    print(f"  SL_DISTANCE (SELL): ${sl_distance:.3f}")

except Exception as e:
    print(f"Erro ao buscar ordens: {e}")

conn.close()
