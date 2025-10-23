#!/usr/bin/env python3
"""
Visualiza trades salvos no banco de dados pelo BTC Hedge Agent.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.database import get_db_connection

def format_datetime(iso_str):
    """Formata datetime ISO para exibição."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return iso_str

def show_trades():
    """Mostra todos os trades do banco."""
    print("="*100)
    print("💾 TRADES SALVOS NO BANCO DE DADOS")
    print("="*100)
    print()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total de trades
        cursor.execute("SELECT COUNT(*) FROM trades")
        total = cursor.fetchone()[0]
        print(f"📊 Total de trades: {total}")

        if total == 0:
            print()
            print("   Nenhum trade encontrado no banco de dados.")
            print()
            print("💡 Dica: Os trades são salvos automaticamente quando as posições")
            print("   são fechadas (por TP, SL ou manual).")
            print()
            conn.close()
            return

        # Estatísticas
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(profit) as total_profit,
                AVG(profit) as avg_profit,
                MAX(profit) as max_profit,
                MIN(profit) as min_profit
            FROM trades
        """)
        stats = cursor.fetchone()

        print(f"✅ Trades com lucro: {stats[1]}")
        print(f"❌ Trades com prejuízo: {stats[2]}")
        print(f"💰 Lucro total: ${stats[3]:+.2f}")
        print(f"📊 Lucro médio: ${stats[4]:+.2f}")
        print(f"🎯 Maior lucro: ${stats[5]:+.2f}")
        print(f"💔 Maior prejuízo: ${stats[6]:+.2f}")

        win_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
        print(f"📈 Taxa de acerto: {win_rate:.1f}%")

        print()
        print("="*100)
        print("📋 HISTÓRICO DE TRADES")
        print("="*100)
        print()

        # Listar trades
        cursor.execute("""
            SELECT
                id, ticket, symbol, type, volume,
                open_price, close_price, open_time, close_time,
                sl, tp, profit, comment
            FROM trades
            ORDER BY id DESC
            LIMIT 50
        """)

        trades = cursor.fetchall()

        for trade in trades:
            (id, ticket, symbol, tipo, volume,
             open_price, close_price, open_time, close_time,
             sl, tp, profit, comment) = trade

            emoji = "✅" if profit > 0 else "❌"
            print(f"{emoji} Trade #{id} | Ticket: {ticket}")
            print(f"   Símbolo: {symbol}")
            print(f"   Tipo: {tipo} | Volume: {volume}")
            print(f"   Entrada: ${open_price:.2f} | Saída: ${close_price:.2f}")
            print(f"   SL: ${sl:.2f} | TP: ${tp:.2f}")
            print(f"   Abertura: {format_datetime(open_time)}")
            print(f"   Fechamento: {format_datetime(close_time)}")
            print(f"   💰 Lucro: ${profit:+.2f}")
            print(f"   Comentário: {comment}")
            print()

        if len(trades) == 50:
            print("(Mostrando apenas os 50 trades mais recentes)")
            print()

        conn.close()

    except Exception as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")
        import traceback
        traceback.print_exc()

    print("="*100)

if __name__ == "__main__":
    show_trades()
