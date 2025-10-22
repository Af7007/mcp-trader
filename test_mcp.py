#!/usr/bin/env python3
"""Test script for MCP MT5 server"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp_mt5.main import mcp
    print("SUCCESS: MCP server loaded successfully")
    print(f"SUCCESS: Server name: {mcp.name}")
    print(f"SUCCESS: Server instructions: {mcp.instructions[:50]}...")
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("SUCCESS: All tests passed!")

# Test basic functionality
try:
    # Test if we can access the timeframe map
    from mcp_mt5.main import timeframe_map
    print(f"SUCCESS: Timeframe map loaded with {len(timeframe_map)} entries")

    # Test if we can access the connection manager
    from mcp_mt5.main import mt5_connection
    print(f"SUCCESS: MT5 connection manager loaded")

except Exception as e:
    print(f"ERROR: Functionality test failed: {e}")
    sys.exit(1)

print("SUCCESS: All functionality tests passed!")
