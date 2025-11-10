import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

# Get order details
orders = mt5.history_orders_get(datetime.now() - timedelta(hours=2), datetime.now())

target_ticket = 115385205

for order in orders:
    if order.position_id == target_ticket:
        print(f"Order Ticket: {order.ticket}")
        print(f"Position ID: {order.position_id}")
        print(f"Time Setup: {datetime.fromtimestamp(order.time_setup)}")
        print(f"Symbol: {order.symbol}")
        print(f"Type: {'BUY' if order.type == 0 else 'SELL'}")
        print(f"State: {order.state}")
        print(f"SL: {order.sl}")
        print(f"TP: {order.tp}")
        print(f"Volume: {order.volume_initial}")
        print(f"Price Open: {order.price_open}")
        print(f"Price Current: {order.price_current}")
        print()

mt5.shutdown()
