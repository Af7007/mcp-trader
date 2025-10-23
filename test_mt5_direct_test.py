#!/usr/bin/env python3
"""Direct MT5 Test - Testa funcionalidade por tentativa direta sem MCP"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_mt5():
    """Testa MT5 diretamente sem usar MCP"""
    try:
        print("Testing direct MT5 functionality...")

        # Import MetaTrader5
        import MetaTrader5 as mt5

        # Initialize MT5
        print("Initializing MT5...")
        mt5_init = mt5.initialize()
        if not mt5_init:
            print("[ERROR] MT5 initialization failed")
            print("Make sure MetaTrader 5 terminal is running")
            return False

        print("[OK] MT5 initialized successfully")

        # Check terminal info
        terminal = mt5.terminal_info()
        if terminal:
            print(f"[OK] Terminal connected: {terminal.company}")
            print("[OK] Terminal path: ...{os.path.basename(terminal.path)}")
        else:
            print("[WARN] Terminal info unavailable")

        # Check if account is logged in
        account_info = mt5.account_info()
        if account_info:
            print(f"[OK] Account logged in: {account_info.login}")
            print(f"[OK] Account balance: ${account_info.balance:.2f}")
            print(f"[OK] Account currency: {account_info.currency}")
        else:
            print("[WARN] No account logged in")
            print("Account may need to be logged in manually or through initialize+login")

        # Get available symbols
        symbols = mt5.symbols_get()
        if symbols:
            print(f"[OK] Found {len(symbols)} symbols")
            major_symbols = [s.name for s in symbols if s.name in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCHF']]
            print(f"[OK] Major symbols: {major_symbols}")
        else:
            print("[WARN] No symbols available")

        # Test symbol info for EURUSD if available
        if symbols and any(s.name == 'EURUSD' for s in symbols):
            print("\nTesting EURUSD...")
            symbol_info = mt5.symbol_info("EURUSD")
            if symbol_info:
                print(f"[OK] EURUSD symbol info available")
                print(f"[OK] EURUSD digits: {symbol_info.digits}")
                print(f"[OK] EURUSD point: {symbol_info.point}")

                # Get tick data
                tick = mt5.symbol_info_tick("EURUSD")
                if tick:
                    print(f"[OK] EURUSD current bid: {tick.bid}")
                    print(f"[OK] EURUSD current ask: {tick.ask}")
                    print(f"[OK] EURUSD spread: {tick.ask - tick.bid:.5f}")
                else:
                    print("[WARN] No EURUSD tick data available")
            else:
                print("[WARN] EURUSD symbol info unavailable")
        else:
            print("[WARN] EURUSD not available for testing")

        # Get positions if any
        positions = mt5.positions_get()
        if positions:
            print(f"\n[OK] Open positions: {len(positions)}")
            for pos in positions[:3]:  # Show first 3
                print(f"[OK] Position: {pos.symbol} {pos.type} {pos.volume} lots @ {pos.price_open} profit: ${pos.profit:.2f}")
        else:
            print("\n[INFO] No open positions")

        # Get orders if any
        orders = mt5.orders_get()
        if orders:
            print(f"[OK] Pending orders: {len(orders)}")
        else:
            print("[INFO] No pending orders")

        print("\n[INFO] Test completed - MT5 is responsive")
        return True

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    finally:
        # Clean up
        try:
            mt5.shutdown()
            print("[OK] MT5 shutdown clean")
        except:
            print("[WARN] MT5 shutdown may have failed")

if __name__ == "__main__":
    success = test_direct_mt5()
    if success:
        print("\n[SUCCESS] MT5 connectivity test PASSED")
        sys.exit(0)
    else:
        print("\n[FAILED] MT5 connectivity test FAILED")
        sys.exit(1)
