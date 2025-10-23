#!/usr/bin/env python3
"""Test script for chatbot + MT5 integration"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_chatbot_mt5():
    """Test chatbot with MT5 direct integration"""
    try:
        print("Testing chatbot + MT5 integration...")

        # Import chatbot sync function
        from chatbot.client import send_message_sync

        print("\nTesting basic commands...")

        # Test basic status check
        result = send_message_sync("teste")
        print(f"[RESULT] Test command response: {result.get('response', 'No response')[:100]}...")

        # Test balance inquiry
        result = send_message_sync("saldo")
        print(f"[RESULT] Balance check: {result.get('response', 'No response')}")

        # Test positions inquiry
        result = send_message_sync("posicoes")
        print(f"[RESULT] Positions check: {result.get('response', 'No response')}")

        print("\n[OK] Chatbot tests completed")
        return True

    except Exception as e:
        print(f"[ERROR] Chatbot test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot_mt5()
    if success:
        print("\n[SUCCESS] Chatbot + MT5 integration test PASSED")
        sys.exit(0)
    else:
        print("\n[FAILED] Chatbot + MT5 integration test FAILED")
        sys.exit(1)
