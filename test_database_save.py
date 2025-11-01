#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the database save functionality.
Simulates the save_trade_to_db() logic to ensure it works correctly.
"""

import sqlite3
import sys
from datetime import datetime, timedelta

DB_FILE = "trading_bot.db"

def test_save_trade():
    """Test saving a trade with the same logic as the agent."""

    print("=" * 70)
    print("  TESTANDO SALVAMENTO DE TRADES NO BANCO DE DADOS")
    print("=" * 70)
    print()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Test data
        test_trades = [
            {
                'ticket': 1001,
                'symbol': 'BTCUSDm',
                'type': 'BUY',
                'volume': 0.02,
                'open_price': 45200.50,
                'close_price': 45240.00,
                'profit': 6.50,
                'sl': 45000.00,
                'tp': 45254.99,
            },
            {
                'ticket': 1002,
                'symbol': 'BTCUSDm',
                'type': 'SELL',
                'volume': 0.02,
                'open_price': 45240.00,
                'close_price': 45220.00,
                'profit': 2.50,
                'sl': 45400.00,
                'tp': 45000.00,
            },
            {
                'ticket': 1003,
                'symbol': 'BTCUSDm',
                'type': 'BUY',
                'volume': 0.02,
                'open_price': 45220.00,
                'close_price': 45100.00,
                'profit': -2.40,
                'sl': 45000.00,
                'tp': 45300.00,
            },
        ]

        print("[INFO] Inserindo trades de teste...")
        print()

        for trade in test_trades:
            open_time = (datetime.now() - timedelta(hours=2)).isoformat()
            close_time = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO trades (
                    ticket, symbol, type, volume,
                    open_price, close_price, open_time, close_time,
                    sl, tp, profit, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade['ticket'],
                trade['symbol'],
                trade['type'],
                trade['volume'],
                trade['open_price'],
                trade['close_price'],
                open_time,
                close_time,
                trade['sl'],
                trade['tp'],
                trade['profit'],
                "Test_Trade"
            ))

            profit_str = "+${:.2f}".format(trade['profit']) if trade['profit'] >= 0 else "-${:.2f}".format(abs(trade['profit']))
            print(f"  [OK] Ticket {trade['ticket']}: {trade['type']} {trade['volume']} lots, Lucro: {profit_str}")

        conn.commit()
        print()
        print("[INFO] Trades inseridos com sucesso!")
        print()

        # Verify saved trades
        cursor.execute("SELECT COUNT(*) FROM trades")
        total = cursor.fetchone()[0]

        print("=" * 70)
        print(f"  VERIFICANDO TRADES SALVOS: {total} trade(s)")
        print("=" * 70)
        print()

        cursor.execute("""
            SELECT ticket, symbol, type, volume, open_price, close_price, profit
            FROM trades
            ORDER BY ticket
        """)

        for row in cursor.fetchall():
            ticket, symbol, trade_type, volume, open_p, close_p, profit = row
            profit_str = "+${:.2f}".format(profit) if profit >= 0 else "-${:.2f}".format(abs(profit))
            print(f"  #{ticket:5d} | {symbol:9s} | {trade_type:4s} | {volume:5.2f} lots | "
                  f"${open_p:10.2f} → ${close_p:10.2f} | Lucro: {profit_str:9s}")

        print()

        # Calculate statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                ROUND(SUM(profit), 2) as total_profit,
                ROUND(AVG(profit), 2) as avg_profit
            FROM trades
        """)

        total, wins, losses, total_profit, avg_profit = cursor.fetchone()
        win_rate = (wins / total * 100) if total > 0 else 0

        print("=" * 70)
        print("  ESTATÍSTICAS")
        print("=" * 70)
        print(f"  Total Trades: {total}")
        print(f"  Vitórias: {wins} ({win_rate:.1f}%)")
        print(f"  Derrotas: {losses}")
        print(f"  Lucro Total: ${total_profit:.2f}")
        print(f"  Lucro Médio: ${avg_profit:.2f}")
        print()

        conn.close()

        print("=" * 70)
        print("  TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)

        return True

    except sqlite3.IntegrityError as e:
        print(f"[ERRO] Trade já existe (duplicado): {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao testar: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = test_save_trade()
    sys.exit(0 if success else 1)
