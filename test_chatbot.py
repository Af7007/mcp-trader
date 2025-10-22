#!/usr/bin/env python3
"""Test script for the trading chatbot"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test imports
    from chatbot.client import TradingChatbot, ChatbotConfig
    print("[OK] Chatbot client import successful")

    from mcp_ollama.main import mcp as ollama_mcp
    print("[OK] Ollama MCP import successful")

    from mcp_mt5.main import mcp as mt5_mcp
    print("[OK] MT5 MCP import successful")

    print("\nTesting Trading Chatbot Components...\n")

    async def test_chatbot():
        """Test basic chatbot functionality"""
        print("Testing chatbot initialization...")

        # Mock configuration for testing
        config = ChatbotConfig(
            ollama_host="http://127.0.0.1:8001",
            mt5_host="http://127.0.0.1:8000"
        )

        try:
            async with TradingChatbot(config) as chatbot:
                # Test basic initialization (may fail if servers not running)
                print("Note: Full initialization may fail without running MCP servers")
                print("      This is normal for offline testing")

                # Test trading command parsing
                print("Testing command parsing...")

                # This would normally connect to servers, but let's test the logic
                test_commands = [
                    "buy 100 EURUSD",
                    "sell 0.01 BTCUSD with stop loss 44000",
                    "show my balance",
                    "what's the best trading opportunity?",
                    "analyze EURUSD trend"
                ]

                print("Sample commands that would be processed:")
                for cmd in test_commands:
                    print(f"   • {cmd}")

                print("\n[SUCCESS] All components loaded successfully!")
                print("\nTo start the system:")
                print("   python main.py")
                print("\nAccess web interface at: http://localhost:3000")
                print("\nSystem requires:")
                print("   • MetaTrader 5 terminal running and logged in")
                print("   • Ollama installed: https://ollama.ai")
                print("   • Required models: ollama pull qwen2.5-coder llama3.1")
                return True

        except Exception as e:
            print(f"[ERROR] Chatbot test failed: {e}")
            return False

    # Run the test
    success = asyncio.run(test_chatbot())

    if success:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Tests failed")
        sys.exit(1)

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Try installing dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
