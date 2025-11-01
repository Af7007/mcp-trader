#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise detalhada de trades abertos/fechados hoje
"""

import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path(__file__).parent / "trading_bot.db"

print("\n" + "="*80)
print(" ANALISE DETALHADA - TRADES DE HOJE")
print("="*80)

if not db_path.exists():
    print(f"[ERRO] Banco de dados nao encontrado: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Verificar trades fechados hoje
    print("\n" + "="*80)
    print(" TRADES FECHADOS HOJE")
    print("="*80)

    cursor.execute("""
        SELECT
            ticket,
            symbol,
            type,
            volume,
            open_price,
            close_price,
            profit,
            open_time,
            close_time
        FROM trades
        WHERE close_time IS NOT NULL
        AND DATE(close_time) = DATE('now')
        ORDER BY close_time DESC
    """)

    today_trades = cursor.fetchall()

    print(f"\nTotal de trades fechados HOJE: {len(today_trades)}")

    if today_trades:
        total_profit_today = sum(t[6] for t in today_trades)
        wins_today = sum(1 for t in today_trades if t[6] > 0)
        losses_today = sum(1 for t in today_trades if t[6] <= 0)

        print(f"  Wins: {wins_today}")
        print(f"  Losses: {losses_today}")
        print(f"  Lucro/Prejuizo total: ${total_profit_today:+.2f}")

        print("\nDetalhes (ultimos 20 trades):\n")
        for i, (ticket, symbol, trade_type, volume, open_price, close_price, profit, open_time, close_time) in enumerate(today_trades[:20], 1):
            status = "WIN" if profit > 0 else "LOSS"
            print(f"{i}. Ticket #{ticket} - {symbol}")
            print(f"   Type: {trade_type} | Volume: {volume}")
            print(f"   Entrada: ${open_price:.2f} -> Saida: ${close_price:.2f}")
            print(f"   {status}: ${profit:+.2f}")
            print(f"   Hora: {close_time}")
            print()

    # Verificar trades ainda abertos (sem close_time)
    print("\n" + "="*80)
    print(" TRADES AINDA ABERTOS")
    print("="*80)

    cursor.execute("SELECT COUNT(*) FROM trades WHERE close_time IS NULL")
    open_trades_count = cursor.fetchone()[0]

    print(f"\nTotal de trades ABERTOS (sem close_time): {open_trades_count}")

    if open_trades_count > 0:
        cursor.execute("""
            SELECT
                ticket,
                symbol,
                type,
                volume,
                open_price,
                open_time
            FROM trades
            WHERE close_time IS NULL
            ORDER BY open_time DESC
        """)
        active = cursor.fetchall()

        print("\nDetalhes dos trades abertos:\n")
        for ticket, symbol, trade_type, volume, open_price, open_time in active:
            print(f"Ticket #{ticket} ({symbol})")
            print(f"  Type: {trade_type} | Volume: {volume}")
            print(f"  Preco entrada: ${open_price:.2f}")
            print(f"  Aberto em: {open_time}")
            print()

    # Resumo por hora (ultimas 24h)
    print("\n" + "="*80)
    print(" RESUMO POR HORA - ULTIMAS 24H")
    print("="*80)

    cursor.execute("""
        SELECT
            SUBSTR(close_time, 1, 13) as hora,
            COUNT(*) as total,
            SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
            SUM(profit) as total_profit
        FROM trades
        WHERE close_time IS NOT NULL
        AND datetime(close_time) > datetime('now', '-24 hours')
        GROUP BY hora
        ORDER BY hora DESC
    """)

    hourly = cursor.fetchall()

    if hourly:
        print("\nUltimas 12 horas:\n")
        for hora, total, wins, total_profit in hourly[:12]:
            loss_rate = 100 - (wins/total*100) if total > 0 else 0
            print(f"{hora}: {total} trades | {wins} wins ({wins/total*100:.0f}%) | ${total_profit:+.2f}")

    conn.close()

except Exception as e:
    print(f"[ERRO] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
