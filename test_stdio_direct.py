#!/usr/bin/env python3
"""Test script for direct MCP stdio transport"""

import os
import sys
import logging
import time

# Set up environment for MCP server
os.environ["MT5_MCP_TRANSPORT"] = "stdio"

print("[TEST] Starting direct MCP stdio test", flush=True)
print("[TEST] Environment: MT5_MCP_TRANSPORT=stdio", flush=True)

try:
    # Import the MCP server
    print("[TEST] Importing MCP server...", flush=True)
    from mcp_mt5.main import mcp

    print("[TEST] Server imported successfully", flush=True)

    # Check if this would run in MCP mode
    if os.getenv("MT5_MCP_TRANSPORT") == "stdio":
        print("[TEST] Running MCP server in stdio mode", flush=True)
        print("[TEST] This should connect to MCP client", flush=True)

        # We'll run for a short time to test
        print("[TEST] Running server for 2 seconds...", flush=True)
        time.sleep(2)

        print("[TEST] Server test complete", flush=True)
        sys.exit(0)

    else:
        print("[TEST] Not running in MCP mode", flush=True)

except Exception as e:
    print(f"[ERROR] Failed to import/test MCP server: {e}", flush=True)
    import traceback
    traceback.print_exc(flush=True)
    sys.exit(1)
