#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa as últimas ordens do banco de dados
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Conectar ao banco de dados
db_path = Path(__file__).parent / 'btc_trading_logs.db'

if not db_path.exists():
    print(f"Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n" + "="*80)
print("ANÁLISE DAS ÚLTIMAS ORDENS")
print("="*80)

# Buscar últimas 10 ordens
cursor.execute("""
    SELECT
        id,
        symbol,
        action,
        volume,
        entry_price,
        sl_price,
        tp_price,
        profit_loss,
        open_time,
        close_time
    FROM trades
    ORDER BY open_time DESC
    LIMIT 10
""")

trades = cursor.fetchall()

if not trades:
    print("\nNenhuma ordem encontrada no banco de dados!")
else:
    print(f"\nÚltimas {len(trades)} ordens:")
    print("-" * 80)

    for trade in trades:
        trade_id, symbol, action, volume, entry, sl, tp, profit, open_time, close_time = trade

        # Calcular distância do SL
        if entry and sl:
            if action == "BUY":
                sl_distance = entry - sl
            else:
                sl_distance = sl - entry
        else:
            sl_distance = 0

        # Status
        status = "FECHADA" if close_time else "ABERTA"

        print(f"\nID: {trade_id} | {symbol} | {action} | {status}")
        print(f"  Volume: {volume} lotes")
        print(f"  Entrada: ${entry:.3f}" if entry else "  Entrada: N/A")
        print(f"  SL: ${sl:.3f}" if sl else "  SL: N/A")
        print(f"  TP: ${tp:.3f}" if tp and tp > 0 else "  TP: SEM TP")
        print(f"  SL Distance: ${sl_distance:.3f}" if sl_distance else "  SL Distance: N/A")
        print(f"  Lucro/Perda: ${profit:.2f}" if profit else "  Lucro/Perda: N/A")
        print(f"  Aberta: {open_time}")
        print(f"  Fechada: {close_time if close_time else 'AINDA ABERTA'}")

        # Verificar se SL está correto
        if sl_distance:
            if abs(sl_distance - 4.0) < 0.1:
                print(f"  ✓ SL CORRETO (${sl_distance:.2f})")
            elif abs(sl_distance - 11.80) < 0.1 or abs(sl_distance - 11.8) < 0.1:
                print(f"  ✗ SL ERRADO - ${sl_distance:.2f} (deveria ser $4.00)")
            elif abs(sl_distance - 12.0) < 0.1 or abs(sl_distance - 12.40) < 0.1:
                print(f"  ✗ SL ERRADO - ${sl_distance:.2f} (deveria ser $4.00)")
            else:
                print(f"  ? SL INESPERADO: ${sl_distance:.2f}")

conn.close()

print("\n" + "="*80)
