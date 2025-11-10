import MetaTrader5 as mt5
from datetime import datetime, timedelta

# Initialize MT5
if not mt5.initialize():
    print("Failed to initialize MT5")
    exit()

print("MT5 initialized successfully")

# Get history from last 24 hours
now = datetime.now()
from_date = now - timedelta(days=1)

print(f"\nBuscando historico de {from_date} ate {now}")

# Get deals
deals = mt5.history_deals_get(from_date, now)
print(f"\nDeals encontrados: {len(deals) if deals else 0}")

if deals:
    print("\nUltimos 3 deals:")
    for deal in deals[-3:]:
        print(f"  Ticket: {deal.ticket}")
        print(f"  Position ID: {deal.position_id}")
        print(f"  Time: {datetime.fromtimestamp(deal.time)}")
        print(f"  Symbol: {deal.symbol}")
        print(f"  Type: {deal.type}")
        print(f"  Volume: {deal.volume}")
        print(f"  Price: {deal.price}")
        print(f"  Profit: {deal.profit}")
        print(f"  Comment: {deal.comment}")
        print("-" * 50)

# Get orders
orders = mt5.history_orders_get(from_date, now)
print(f"\nOrders encontradas: {len(orders) if orders else 0}")

if orders:
    print("\nUltimas 3 orders:")
    for order in orders[-3:]:
        print(f"  Ticket: {order.ticket}")
        print(f"  Time: {datetime.fromtimestamp(order.time_setup)}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Type: {order.type}")
        print(f"  State: {order.state}")
        print(f"  Price: {order.price_open}")
        print(f"  SL: {order.sl}")
        print(f"  TP: {order.tp}")
        print("-" * 50)

mt5.shutdown()
print("\nMT5 shutdown")
