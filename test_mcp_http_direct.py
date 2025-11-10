import requests
from datetime import datetime, timedelta

# Test MT5 MCP HTTP server directly
base_url = "http://127.0.0.1:8000"

print("Testing MT5 MCP HTTP Server\n")
print("=" * 80)

# Test 1: Health check
print("\nTest 1: Health check")
try:
    response = requests.get(f"{base_url}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    print("MCP Server may not be running!")
    exit(1)

# Test 2: Get account info
print("\nTest 2: Get account info")
try:
    response = requests.post(
        f"{base_url}/call_tool",
        json={"name": "get_account_info", "arguments": {}},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if "result" in data:
        print(f"Account: {data['result'].get('login')}")
        print(f"Balance: {data['result'].get('balance')}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Get history deals (no date filter)
print("\nTest 3: Get history deals (no filter)")
try:
    response = requests.post(
        f"{base_url}/call_tool",
        json={"name": "history_deals_get", "arguments": {}},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if "result" in data:
        deals = data["result"]
        print(f"Deals found: {len(deals)}")
        if deals:
            print(f"First deal ticket: {deals[0].get('ticket')}")
            print(f"Last deal ticket: {deals[-1].get('ticket')}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Get history deals (with date range)
print("\nTest 4: Get history deals (with date range)")
now = datetime.now()
from_date = now - timedelta(days=1)
try:
    response = requests.post(
        f"{base_url}/call_tool",
        json={
            "name": "history_deals_get",
            "arguments": {
                "from_date": from_date.isoformat(),
                "to_date": now.isoformat()
            }
        },
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"From: {from_date}")
    print(f"To: {now}")
    data = response.json()
    if "result" in data:
        deals = data["result"]
        print(f"Deals found: {len(deals)}")
        if deals:
            print(f"First deal ticket: {deals[0].get('ticket')}")
            print(f"Last deal ticket: {deals[-1].get('ticket')}")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("Test complete!")
