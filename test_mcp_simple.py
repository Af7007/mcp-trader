#!/usr/bin/env python3
"""Simple Test for MCP MT5 server"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing MCP imports...")

    # Test MetaTrader5 import
    import MetaTrader5 as mt5
    print("[OK] MetaTrader5 imported successfully")

    # Test MT5 initialization
    if mt5.initialize():
        print("[OK] MetaTrader5 initialized successfully")
    else:
        print("[WARN] MetaTrader5 initialization failed (terminal may not be running)")

    # Try to import our MT5 MCP module
    from mcp_mt5.main import mcp
    print("[OK] mcp_mt5.main imported successfully")

    print("\n[SUCCESS] ALL IMPORTS SUCCESSFUL!")
    print("Ready to test MCP connectivity with MT5.")

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Required packages may not be available.")
    sys.exit(1)

except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
