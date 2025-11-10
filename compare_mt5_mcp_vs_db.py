"""
Compara historico do MT5 (via MCP) com banco de dados SQLite
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import sqlite3
import requests
from datetime import datetime, timedelta

# URL do servidor MCP
MCP_URL = "http://127.0.0.1:8000"

def get_db_trades():
    """Busca trades do banco de dados"""
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket, symbol, trade_type, volume, entry_price, exit_price,
               sl_price, tp_price, profit_loss, timestamp, status
        FROM trades
        WHERE symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%'
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    trades = []
    for row in rows:
        trades.append({
            'ticket': row[0],
            'symbol': row[1],
            'type': row[2],
            'volume': row[3],
            'open_price': row[4],
            'close_price': row[5],
            'sl': row[6],
            'tp': row[7],
            'profit': row[8],
            'open_time': row[9],
            'status': row[10]
        })

    return trades

def get_mt5_history_mcp():
    """Busca historico do MT5 via MCP"""
    try:
        # Ultimas 48 horas
        date_from = datetime.now() - timedelta(hours=48)
        date_to = datetime.now()

        # Chamar tool history_deals_get via MCP
        response = requests.post(
            f"{MCP_URL}/mcp/tools/call",
            json={
                "name": "history_deals_get",
                "arguments": {
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                    "group": "*XAU*"
                }
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('content', [])
        else:
            print(f"Erro ao buscar do MCP: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"Erro ao conectar com MCP: {e}")
        return []

def main():
    print("=" * 100)
    print("COMPARACAO: MT5 (via MCP) vs BANCO DE DADOS")
    print("=" * 100)
    print()

    # 1. Banco de dados
    print("[1] BANCO DE DADOS (SQLite)")
    print("-" * 100)

    db_trades = get_db_trades()

    if db_trades:
        for trade in db_trades[:10]:
            sl_dist = abs(trade['open_price'] - trade['sl']) if trade['sl'] else 0
            print(f"Ticket: {trade['ticket']}")
            print(f"  Symbol: {trade['symbol']}")
            print(f"  Type: {trade['type']}")
            print(f"  Volume: {trade['volume']:.2f}")
            print(f"  Open: {trade['open_price']:.3f}")
            print(f"  SL: {trade['sl']:.3f}" if trade['sl'] else "  SL: N/A")
            print(f"  SL Distance: ${sl_dist:.2f}")
            print(f"  Profit: ${trade['profit']:.2f}" if trade['profit'] else "  Profit: N/A")
            print(f"  Status: {trade['status']}")
            print()

        print(f"Total no DB: {len(db_trades)} trades")
    else:
        print("  [VAZIO] Nenhum trade no banco de dados")

    print()
    print("[2] MT5 via MCP")
    print("-" * 100)

    # 2. MT5 via MCP
    mt5_deals = get_mt5_history_mcp()

    if mt5_deals:
        print(f"Total de deals encontrados: {len(mt5_deals)}")
        print()

        # Agrupar deals por order (ticket)
        deal_groups = {}
        for deal in mt5_deals:
            if isinstance(deal, dict):
                order_id = deal.get('order', 0)
                if order_id not in deal_groups:
                    deal_groups[order_id] = []
                deal_groups[order_id].append(deal)

        print(f"Orders unicas: {len(deal_groups)}")
        print()

        # Mostrar primeiros deals agrupados
        for order_id, deals in list(deal_groups.items())[:10]:
            print(f"Order: {order_id}")
            for deal in deals:
                entry_type = "IN" if deal.get('entry') == 0 else "OUT" if deal.get('entry') == 1 else "INOUT"
                deal_time = datetime.fromtimestamp(deal.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S') if deal.get('time') else 'N/A'
                print(f"  Deal: {deal.get('ticket', 'N/A')}")
                print(f"    Symbol: {deal.get('symbol', 'N/A')}")
                print(f"    Entry: {entry_type}")
                print(f"    Volume: {deal.get('volume', 0):.2f}")
                print(f"    Price: {deal.get('price', 0):.3f}")
                print(f"    Profit: ${deal.get('profit', 0):.2f}")
                print(f"    Time: {deal_time}")
            print()
    else:
        print("  [VAZIO] Nenhum deal encontrado via MCP")

    print()
    print("[3] COMPARACAO DE TICKETS")
    print("-" * 100)

    # Comparar tickets
    if db_trades and mt5_deals:
        db_tickets = {t['ticket'] for t in db_trades}

        # Extrair order tickets do MCP
        mcp_tickets = set()
        for deal in mt5_deals:
            if isinstance(deal, dict):
                mcp_tickets.add(deal.get('order', 0))

        common_tickets = db_tickets & mcp_tickets
        only_db = db_tickets - mcp_tickets
        only_mcp = mcp_tickets - db_tickets

        print(f"Tickets em comum: {len(common_tickets)}")
        print(f"Apenas no DB: {len(only_db)} - {list(only_db)[:5]}")
        print(f"Apenas no MCP: {len(only_mcp)} - {list(only_mcp)[:5]}")

        if common_tickets:
            print()
            print("Analise detalhada dos tickets em comum:")
            print()

            for ticket in sorted(common_tickets, reverse=True)[:5]:
                db_trade = next((t for t in db_trades if t['ticket'] == ticket), None)

                # Buscar deals deste ticket no MCP
                mcp_order_deals = [d for d in mt5_deals if isinstance(d, dict) and d.get('order') == ticket]

                if db_trade and mcp_order_deals:
                    print(f"Ticket: {ticket}")
                    print(f"  [DB] Open: {db_trade['open_price']:.3f} | SL: {db_trade['sl']:.3f} | Profit: ${db_trade['profit']:.2f}")

                    total_mcp_profit = sum(d.get('profit', 0) for d in mcp_order_deals)
                    print(f"  [MCP] {len(mcp_order_deals)} deals | Total Profit: ${total_mcp_profit:.2f}")

                    # Comparar lucro
                    if db_trade['profit'] is not None:
                        diff = abs(db_trade['profit'] - total_mcp_profit)
                        if diff > 0.1:
                            print(f"  [ALERTA] Discrepancia no profit: ${diff:.2f}")
                        else:
                            print(f"  [OK] Profit consistente")
                    print()

    print("=" * 100)

if __name__ == "__main__":
    main()
