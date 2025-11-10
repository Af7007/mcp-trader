import MetaTrader5 as mt5
from datetime import datetime, timedelta

# Initialize MT5
if not mt5.initialize():
    print("Failed to initialize MT5")
    exit()

print("Testing MT5 history_deals_get with different date formats\n")

now = datetime.now()
from_date = now - timedelta(days=1)

print(f"Current time: {now}")
print(f"From date: {from_date}")
print("=" * 80)

# Test 1: Using datetime objects (Python way)
print("\nTest 1: Using datetime objects")
try:
    deals = mt5.history_deals_get(from_date, now)
    print(f"Result: {len(deals) if deals else 0} deals found")
    if deals:
        print(f"First deal ticket: {deals[0].ticket}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Using timestamp (Unix time)
print("\nTest 2: Using timestamp")
try:
    from_ts = int(from_date.timestamp())
    to_ts = int(now.timestamp())
    print(f"From timestamp: {from_ts}")
    print(f"To timestamp: {to_ts}")
    deals = mt5.history_deals_get(from_ts, to_ts)
    print(f"Result: {len(deals) if deals else 0} deals found")
    if deals:
        print(f"First deal ticket: {deals[0].ticket}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Using named parameters with datetime
print("\nTest 3: Using named parameters with datetime")
try:
    deals = mt5.history_deals_get(date_from=from_date, date_to=now)
    print(f"Result: {len(deals) if deals else 0} deals found")
    if deals:
        print(f"First deal ticket: {deals[0].ticket}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Check what MCP is passing
print("\nTest 4: Simulating MCP call")
try:
    # This is what MCP does
    request = {
        "from": from_date,
        "to": now
    }
    print(f"Request dict: {request}")
    deals = mt5.history_deals_get(**request)
    print(f"Result: {len(deals) if deals else 0} deals found")
    if deals:
        print(f"First deal ticket: {deals[0].ticket}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Check MT5 signature
print("\nTest 5: MT5 history_deals_get signature")
import inspect
sig = inspect.signature(mt5.history_deals_get)
print(f"Signature: {sig}")

mt5.shutdown()
print("\nDone!")
