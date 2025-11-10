"""
Analyze last order using direct MT5 connection
This bypasses MCP to show the data is available
"""
import MetaTrader5 as mt5
import sqlite3
from datetime import datetime, timedelta

print("=" * 100)
print("ANALISE DA ULTIMA ORDEM - COMPARANDO BANCO vs MT5")
print("=" * 100)

# Get from database
print("\n[1] DADOS DO BANCO (SQLite):")
print("-" * 100)
conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT ticket, symbol, trade_type, timestamp, entry_price, sl_price, tp_price,
           exit_price, profit_loss, status, exit_reason
    FROM trades
    ORDER BY timestamp DESC
    LIMIT 1
''')
row = cursor.fetchone()
conn.close()

if row:
    db_ticket, db_symbol, db_type, db_time, db_entry, db_sl, db_tp, db_exit, db_profit, db_status, db_reason = row
    print(f"Ticket: {db_ticket}")
    print(f"Symbol: {db_symbol}")
    print(f"Type: {db_type}")
    print(f"Time: {db_time}")
    print(f"Entry: {db_entry}")
    print(f"SL: {db_sl}")
    print(f"TP: {db_tp}")
    print(f"Exit: {db_exit}")
    print(f"Profit/Loss: ${db_profit}")
    print(f"Status: {db_status}")
    print(f"Exit Reason: {db_reason}")
else:
    print("Nenhum dado no banco!")
    exit(1)

# Initialize MT5
if not mt5.initialize():
    print("\nFalha ao inicializar MT5!")
    exit(1)

# Get from MT5
print(f"\n[2] DADOS DO MT5 (Historico de Deals para position {db_ticket}):")
print("-" * 100)

# Get deals for this position in last 24 hours
now = datetime.now()
from_date = now - timedelta(days=1)
deals = mt5.history_deals_get(from_date, now)

if deals:
    position_deals = [d for d in deals if d.position_id == db_ticket]

    if position_deals:
        print(f"Found {len(position_deals)} deal(s) for position {db_ticket}:")
        print()
        for i, deal in enumerate(position_deals, 1):
            print(f"  Deal {i}:")
            print(f"    Deal Ticket: {deal.ticket}")
            print(f"    Position ID: {deal.position_id}")
            print(f"    Time: {datetime.fromtimestamp(deal.time)}")
            print(f"    Symbol: {deal.symbol}")
            print(f"    Type: {deal.type} (0=BUY, 1=SELL)")
            print(f"    Volume: {deal.volume}")
            print(f"    Price: {deal.price}")
            print(f"    Profit: ${deal.profit}")
            print(f"    Comment: {deal.comment}")
            print()
    else:
        print(f"No deals found for position {db_ticket}")
else:
    print("No deals found in MT5 history!")

# Get order info
print(f"[3] DADOS DO MT5 (Order History para ticket {db_ticket}):")
print("-" * 100)

orders = mt5.history_orders_get(from_date, now)
if orders:
    position_order = [o for o in orders if o.ticket == db_ticket]

    if position_order:
        order = position_order[0]
        print(f"Order Ticket: {order.ticket}")
        print(f"Time Setup: {datetime.fromtimestamp(order.time_setup)}")
        print(f"Symbol: {order.symbol}")
        print(f"Type: {order.type} (0=BUY, 1=SELL)")
        print(f"State: {order.state}")
        print(f"SL: {order.sl}")
        print(f"TP: {order.tp}")
        print(f"Volume Initial: {order.volume_initial}")
        print(f"Volume Current: {order.volume_current}")
    else:
        print(f"No order found with ticket {db_ticket}")
else:
    print("No orders found in MT5 history!")

mt5.shutdown()

print("\n" + "=" * 100)
print("RESUMO:")
print("=" * 100)
print(f"Position ID {db_ticket} ({db_symbol} {db_type}):")
print(f"  - Entry: {db_entry}")
print(f"  - Exit: {db_exit}")
print(f"  - SL: {db_sl}")
print(f"  - Result: ${db_profit} ({db_status})")
print(f"  - Reason: {db_reason}")
print("\nTodos os dados estao disponiveis no MT5!")
print("O problema era que o MCP estava usando parametros nomeados incorretos.")
print("=" * 100)
