import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()
deals = mt5.history_deals_get(datetime.now() - timedelta(hours=2), datetime.now())

print("ULTIMOS 10 DEALS:")
print("=" * 100)

for deal in sorted(deals, key=lambda x: x.time, reverse=True)[:10]:
    deal_type = "BUY" if deal.type == 0 else "SELL"
    entry_type = "IN" if deal.entry == 0 else "OUT"
    print(f"\nDeal: {deal.ticket} | Position: {deal.position_id}")
    print(f"  Time: {datetime.fromtimestamp(deal.time)}")
    print(f"  Symbol: {deal.symbol}")
    print(f"  Type: {deal_type} {entry_type}")
    print(f"  Volume: {deal.volume}")
    print(f"  Price: {deal.price}")
    print(f"  Profit: ${deal.profit:.2f}")
    print(f"  Comment: {deal.comment}")

mt5.shutdown()
