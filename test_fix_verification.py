"""
Test to verify the fix is working by calling the corrected function directly
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import MT5 and MCP server
import MetaTrader5 as mt5
from mcp_mt5.main import history_deals_get, history_orders_get

# Initialize MT5
if not mt5.initialize():
    print("Failed to initialize MT5")
    exit(1)

print("Testing FIXED history functions\n")
print("=" * 80)

# Calculate date range
now = datetime.now()
from_date = now - timedelta(days=1)

print(f"Date range: {from_date} to {now}\n")

# Test history_deals_get (from our fixed MCP server code)
print("Test 1: history_deals_get with date range")
try:
    deals = history_deals_get(from_date=from_date, to_date=now)
    print(f"✓ Deals found: {len(deals)}")
    if deals:
        print(f"  First deal: ticket={deals[0].ticket}, time={deals[0].time}")
        print(f"  Last deal: ticket={deals[-1].ticket}, time={deals[-1].time}")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test history_orders_get (from our fixed MCP server code)
print("Test 2: history_orders_get with date range")
try:
    orders = history_orders_get(from_date=from_date, to_date=now)
    print(f"✓ Orders found: {len(orders)}")
    if orders:
        print(f"  First order: ticket={orders[0].ticket}")
        print(f"  Last order: ticket={orders[-1].ticket}")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test without date range
print("Test 3: history_deals_get without date range")
try:
    deals = history_deals_get()
    print(f"✓ Total deals found: {len(deals)}")
except Exception as e:
    print(f"✗ Error: {e}")

mt5.shutdown()
print("\n" + "=" * 80)
print("Fix verification complete!")
