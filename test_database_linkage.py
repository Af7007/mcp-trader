#!/usr/bin/env python3
"""
Teste de linkagem completa: Orders -> Trailing Stops no banco de dados
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def test_database_structure():
    """Verifica se as tabelas existem e estão linkadas corretamente"""

    db_path = Path("btc_trading_logs.db")

    if not db_path.exists():
        print("[AVISO] Banco de dados nao existe. Sera criado na proxima execucao do agente.")
        return False

    print("=" * 70)
    print("TESTE DE LINKAGEM: ORDERS -> TRAILING STOPS")
    print("=" * 70)
    print()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Verificar tabelas
    print("1. Verificando estrutura do banco...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   Tabelas encontradas: {[t[0] for t in tables]}")
    print()

    # Verificar se trades existe
    cursor.execute("SELECT COUNT(*) FROM trades")
    total_trades = cursor.fetchone()[0]
    print(f"2. Total de trades: {total_trades}")

    if total_trades == 0:
        print("   [AVISO] Nenhum trade no banco ainda.")
        conn.close()
        return False

    print()

    # Verificar se trailing_stops existe
    cursor.execute("SELECT COUNT(*) FROM trailing_stops")
    total_trailing = cursor.fetchone()[0]
    print(f"3. Total de trailing updates: {total_trailing}")
    print()

    # Listar trades recentes
    print("4. Trades recentes:")
    cursor.execute('''
        SELECT id, ticket, symbol, trade_type, entry_price, status, profit_loss
        FROM trades
        ORDER BY timestamp DESC
        LIMIT 5
    ''')

    trades = cursor.fetchall()
    if trades:
        print(f"   {'ID':<5} {'Ticket':<12} {'Symbol':<10} {'Type':<6} {'Entry':<10} {'Status':<8} {'P/L':<8}")
        print("   " + "-" * 65)
        for trade in trades:
            trade_id, ticket, symbol, trade_type, entry, status, pl = trade
            ticket_str = str(ticket) if ticket else "N/A"
            entry_str = f"${entry:.2f}" if entry else "N/A"
            pl_str = f"${pl:.2f}" if pl else "OPEN"
            print(f"   {trade_id:<5} {ticket_str:<12} {symbol:<10} {trade_type:<6} {entry_str:<10} {status:<8} {pl_str:<8}")
    print()

    # Mostrar linkagem
    print("5. Linkagem Orders -> Trailing Stops:")
    cursor.execute('''
        SELECT
            t.id as trade_id,
            t.ticket,
            COUNT(ts.id) as trailing_actions,
            SUM(CASE WHEN ts.action = 'ACTIVATED' THEN 1 ELSE 0 END) as activations
        FROM trades t
        LEFT JOIN trailing_stops ts ON t.id = ts.trade_id
        GROUP BY t.id
        ORDER BY t.timestamp DESC
        LIMIT 5
    ''')

    linkages = cursor.fetchall()
    if linkages:
        print(f"   {'Trade_ID':<10} {'Ticket':<12} {'Trailing_Actions':<18} {'Activations':<12}")
        print("   " + "-" * 52)
        for link in linkages:
            trade_id, ticket, actions, activations = link
            ticket_str = str(ticket) if ticket else "N/A"
            actions_str = str(actions or 0)
            activations_str = str(activations or 0)
            print(f"   {trade_id:<10} {ticket_str:<12} {actions_str:<18} {activations_str:<12}")
    print()

    # Exemplo detalhado de uma ordem
    print("6. Exemplo detalhado - Ordem com Trailing:")
    cursor.execute('''
        SELECT
            t.id,
            t.ticket,
            t.entry_price,
            COUNT(ts.id) as total_updates
        FROM trades t
        LEFT JOIN trailing_stops ts ON t.id = ts.trade_id
        GROUP BY t.id
        HAVING total_updates > 0
        LIMIT 1
    ''')

    example = cursor.fetchone()
    if example:
        trade_id, ticket, entry_price, total_updates = example
        print(f"   Trade ID: {trade_id}, Ticket: {ticket}, Entry: ${entry_price:.2f}")
        print(f"   Total de updates: {total_updates}")
        print()

        # Mostrar todos os updates dessa ordem
        cursor.execute('''
            SELECT
                action,
                old_sl_price,
                new_sl_price,
                profit_dinheiro,
                timestamp
            FROM trailing_stops
            WHERE trade_id = ?
            ORDER BY timestamp
        ''', (trade_id,))

        print(f"   {'Action':<12} {'Old SL':<12} {'New SL':<12} {'Profit':<12} {'Timestamp':<20}")
        print("   " + "-" * 70)

        for row in cursor.fetchall():
            action, old_sl, new_sl, profit, ts = row
            old_sl_str = f"${old_sl:.2f}" if old_sl else "None"
            new_sl_str = f"${new_sl:.2f}" if new_sl else "None"
            profit_str = f"${profit:.2f}" if profit else "-"
            print(f"   {action:<12} {old_sl_str:<12} {new_sl_str:<12} {profit_str:<12} {ts:<20}")
    else:
        print("   [AVISO] Nenhuma ordem com trailing stops ainda.")

    print()

    # Verificar integridade referencial
    print("7. Verificando integridade referencial...")
    cursor.execute('''
        SELECT COUNT(*) as orphaned_trailing
        FROM trailing_stops ts
        WHERE NOT EXISTS (SELECT 1 FROM trades t WHERE t.id = ts.trade_id)
    ''')
    orphaned = cursor.fetchone()[0]

    if orphaned == 0:
        print("   [OK] Nenhum trailing stop orfao (integridade OK)")
    else:
        print(f"   [AVISO] {orphaned} trailing stops sem trade correspondente!")

    print()
    print("=" * 70)
    print("[OK] DATABASE LINKAGE TEST COMPLETO")
    print("=" * 70)

    conn.close()
    return True

if __name__ == "__main__":
    import sys

    try:
        success = test_database_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
