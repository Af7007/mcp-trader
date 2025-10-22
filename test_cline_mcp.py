#!/usr/bin/env python3
"""Test script to simulate exact Cline MCP connection"""

import subprocess
import sys
import os
import time
import json

def test_cline_mcp_connection():
    """Test the exact MCP connection that Cline uses"""

    print("=== Testing Cline MCP Connection ===")

    # Set up the exact environment that Cline uses
    os.chdir(r'c:\mcp-trader')

    # Load the configuration that Cline uses
    config_path = r'../Users/adan/AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json'

    try:
        with open(config_path, 'r') as f:
            cline_config = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load Cline config: {e}")
        return False

    print(f"[OK] Loaded Cline configuration for server: {list(cline_config.get('mcpServers', {}).keys())}")

    # Get the MT5 server configuration
    mt5_config = cline_config.get('mcpServers', {}).get('mt5-mcp-server', {})
    if not mt5_config:
        print("[ERROR] MT5 server not found in Cline configuration")
        return False

    print(f"[OK] MT5 server configuration: {mt5_config.get('command')} {mt5_config.get('args', [])}")

    # Test the exact command that Cline executes
    cmd = [
        mt5_config['command'],
        *mt5_config.get('args', [])
    ]

    print(f"[TEST] Executing command: {' '.join(cmd)}")
    print(f"[TEST] Working directory: {mt5_config.get('cwd', os.getcwd())}")
    print(f"[TEST] Environment variables: {mt5_config.get('env', {})}")

    try:
        # Execute exactly as Cline does
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=mt5_config.get('cwd', os.getcwd()),
            env={
                **os.environ,
                **mt5_config.get('env', {})
            }
        )

        print(f"[OK] Process started with PID: {process.pid}")

        # Wait a moment for initialization
        time.sleep(3)

        if process.poll() is None:
            print("[OK] Server is running successfully")

            # Test MCP protocol handshake
            print("[TEST] Testing MCP protocol...")

            # Send initialize message (standard MCP protocol)
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "cline",
                        "version": "1.0.0"
                    }
                }
            }

            try:
                print("[TEST] Testing basic communication...")

                # Send a simple test message
                test_message = "test\n"
                process.stdin.write(test_message)
                process.stdin.flush()

                print("[TEST] Sent test message")

                # Wait for response with timeout
                start_time = time.time()
                timeout = 3  # 3 seconds timeout

                output = ""
                while time.time() - start_time < timeout:
                    line = process.stdout.readline()
                    if line:
                        output += line.strip() + "\n"
                        break
                    time.sleep(0.1)

                if output:
                    print(f"[OK] Received response: {output}")
                else:
                    print("[WARN] No response received within timeout")
                    print("[DEBUG] Checking stderr...")
                    # Check stderr for any error messages
                    error_output = ""
                    while True:
                        error_line = process.stderr.readline()
                        if not error_line:
                            break
                        error_output += error_line.strip() + "\n"
                    if error_output:
                        print(f"[DEBUG] stderr: {error_output}")

            except Exception as e:
                print(f"[ERROR] Communication test failed: {e}")

            # Clean shutdown
            process.terminate()
            process.wait(timeout=5)

            print("[OK] Test completed successfully")
            return True

        else:
            print(f"[ERROR] Server exited with code: {process.poll()}")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

if __name__ == "__main__":
    success = test_cline_mcp_connection()
    print(f"\n=== Result: {'SUCCESS' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)
