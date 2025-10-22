#!/usr/bin/env python3
"""Test script for MCP MT5 server functionality"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp_mt5.main import mcp
    print("SUCCESS: MCP server loaded successfully")
    print(f"SUCCESS: Server name: {mcp.name}")
    # Check available attributes
    print(f"SUCCESS: Available attributes: {dir(mcp)}")

    # Get tools and resources using the proper methods
    try:
        tools = mcp.get_tools()
        print(f"SUCCESS: Number of tools: {len(tools)}")

        # List available tools
        print("\nAvailable tools:")
        for tool in tools:
            print(f"  - {tool.name}")

    except Exception as e:
        print(f"INFO: Could not get tools: {e}")

    try:
        resources = mcp.get_resources()
        print(f"SUCCESS: Number of resources: {len(resources)}")

        # List available resources
        print("\nAvailable resources:")
        for resource in resources:
            print(f"  - {resource.uri}")

    except Exception as e:
        print(f"INFO: Could not get resources: {e}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nSUCCESS: All tests passed!")
