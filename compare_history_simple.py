"""
Comparacao simples: MT5 direto vs Banco de dados
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import sqlite3
import MetaTrader5 as mt5
from datetime import datetime, timedelta

def init_mt5():
    """Inicializa MT5"""
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        return False
    print("[OK] MT5 inicializado")
    return True

def get_db_trades():
    """Busca trades do banco"""
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket, symbol, trade_type, volume, entry_price, exit_price,
               sl_price, tp_price, profit_loss, timestamp, status
        FROM trades
        WHERE (symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%')
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    trades = []
    for row in cursor.fetchall():
        trades.append({
            'ticket': row[0],
            'symbol': row[1],
            'type': row[2],
            'volume': row[3],
            'entry': row[4],
            'exit': row[5],
            'sl': row[6],
            'tp': row[7],
            'profit': row[8],
            'time': row[9],
            'status': row[10]
        })

    conn.close()
    return trades

def get_mt5_deals():
    """Busca deals do MT5"""
    date_from = datetime.now() - timedelta(hours=48)
    date_to = datetime.now()

    deals = mt5.history_deals_get(date_from, date_to, group="*XAU*")
    return deals if deals else []

def main():
    print("=" * 100)
    print("COMPARACAO: MT5 vs BANCO DE DADOS")
    print("=" * 100)
    print()

    # Inicializar MT5
    if not init_mt5():
        return

    # Banco de dados
    print("[1] BANCO DE DADOS")
    print("-" * 100)

    db_trades = get_db_trades()
    print(f"Total: {len(db_trades)} trades")
    print()

    for trade in db_trades[:10]:
        sl_dist = abs(trade['entry'] - trade['sl']) if trade['sl'] and trade['entry'] else 0
        profit_str = f"${trade['profit']:.2f}" if trade['profit'] is not None else "N/A"
        print(f"Ticket {trade['ticket']}: {trade['type']} {trade['symbol']}")
        print(f"  Entry: {trade['entry']:.3f} | SL: {trade['sl']:.3f} ({sl_dist:.2f})")
        print(f"  Profit: {profit_str} | Status: {trade['status']}")
        print()

    # MT5
    print("[2] MT5 DEALS")
    print("-" * 100)

    mt5_deals = get_mt5_deals()
    print(f"Total: {len(mt5_deals)} deals")
    print()

    # Agrupar por order
    deal_groups = {}
    for deal in mt5_deals:
        order_id = deal.order
        if order_id not in deal_groups:
            deal_groups[order_id] = []
        deal_groups[order_id].append(deal)

    print(f"Orders unicas: {len(deal_groups)}")
    print()

    for order_id, deals in list(deal_groups.items())[:10]:
        # Separar deals IN e OUT
        in_deals = [d for d in deals if d.entry == 0]
        out_deals = [d for d in deals if d.entry == 1]
        total_profit = sum(d.profit for d in deals)

        print(f"Order {order_id}: {len(deals)} deals ({len(in_deals)} IN, {len(out_deals)} OUT)")

        # Mostrar entrada
        if in_deals:
            deal = in_deals[0]
            print(f"  IN:  Deal {deal.ticket} @ {deal.price:.3f} | Vol: {deal.volume:.2f}")

        # Mostrar saida com profit
        for deal in out_deals:
            print(f"  OUT: Deal {deal.ticket} @ {deal.price:.3f} | Profit: ${deal.profit:.2f}")

        print(f"  Total Profit: ${total_profit:.2f}")
        print()

    # Comparacao
    print("[3] COMPARACAO")
    print("-" * 100)

    db_tickets = {t['ticket'] for t in db_trades if t['ticket']}
    mt5_tickets = set(deal_groups.keys())

    common = db_tickets & mt5_tickets
    only_db = db_tickets - mt5_tickets
    only_mt5 = mt5_tickets - db_tickets

    print(f"Tickets em comum: {len(common)}")
    print(f"Apenas DB: {len(only_db)}")
    print(f"Apenas MT5: {len(only_mt5)}")
    print()

    if common:
        print("ANALISE DETALHADA:")
        print()

        for ticket in sorted(common, reverse=True)[:5]:
            db_trade = next((t for t in db_trades if t['ticket'] == ticket), None)
            mt5_order_deals = deal_groups.get(ticket, [])

            if db_trade and mt5_order_deals:
                # Separar IN e OUT
                in_deals = [d for d in mt5_order_deals if d.entry == 0]
                out_deals = [d for d in mt5_order_deals if d.entry == 1]
                mt5_total_profit = sum(d.profit for d in mt5_order_deals)

                # Mostrar precos de entrada/saida
                entry_price = in_deals[0].price if in_deals else 0
                exit_price = out_deals[0].price if out_deals else 0

                # Format exit price
                db_exit_str = f"{db_trade['exit']:.3f}" if db_trade['exit'] else "N/A"
                mt5_exit_str = f"{exit_price:.3f}" if exit_price else "N/A"

                print(f"Ticket {ticket}:")
                print(f"  [DB]  Entry: {db_trade['entry']:.3f} | Exit: {db_exit_str} | SL: {db_trade['sl']:.3f} | Profit: ${db_trade['profit']:.2f}")
                print(f"  [MT5] Entry: {entry_price:.3f} | Exit: {mt5_exit_str} | {len(in_deals)}IN/{len(out_deals)}OUT | Profit: ${mt5_total_profit:.2f}")

                # Comparar profit
                if db_trade['profit'] is not None:
                    diff = abs(db_trade['profit'] - mt5_total_profit)
                    if diff > 0.5:
                        print(f"  [ALERTA] Discrepancia de ${diff:.2f}")
                    else:
                        print(f"  [OK] Consistente (diff: ${diff:.2f})")
                print()

    print("=" * 100)
    mt5.shutdown()

if __name__ == "__main__":
    main()
