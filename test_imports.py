#!/usr/bin/env python3
"""Test script to check imports"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("Testing imports...")

    try:
        import MetaTrader5 as mt5
        print("SUCCESS: MetaTrader5 import successful")
    except ImportError as e:
        print(f"FAILED: MetaTrader5 import failed: {e}")
        return False

    try:
        import fastmcp
        print("SUCCESS: FastMCP import successful")
    except ImportError as e:
        print(f"FAILED: FastMCP import failed: {e}")
        return False

    try:
        import pandas as pd
        print("SUCCESS: Pandas import successful")
    except ImportError as e:
        print(f"FAILED: Pandas import failed: {e}")
        return False

    try:
        import pydantic
        print("SUCCESS: Pydantic import successful")
    except ImportError as e:
        print(f"FAILED: Pydantic import failed: {e}")
        return False

    try:
        import flask
        print("SUCCESS: Flask import successful")
    except ImportError as e:
        print(f"FAILED: Flask import failed: {e}")
        return False

    print("All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
