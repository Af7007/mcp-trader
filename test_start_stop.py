#!/usr/bin/env python3
"""Test script for MCP server start/stop only"""

import subprocess
import sys
import time
import signal
import os

def test_server_start_stop():
    """Test if the Node.js wrapper can start and stop the MCP server"""

    print("=== Testing Node.js Wrapper Start/Stop ===")

    # Change to correct directory
    os.chdir(r'c:\mcp-trader')

    try:
        # Start the server using Node.js wrapper
        print("[TEST] Starting Node.js wrapper...")
        process = subprocess.Popen(
            ['node', 'build/index.js'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r'c:\mcp-trader'
        )

        print(f"[TEST] Process started with PID: {process.pid}")

        # Wait a moment
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print("[SUCCESS] Server is running")

            # Try to kill it gracefully
            print("[TEST] Sending SIGTERM...")
            process.terminate()

            # Wait for it to exit
            try:
                stdout, stderr = process.communicate(timeout=5)
                print(f"[TEST] Process terminated successfully")
                print(f"[TEST] STDOUT: {stdout}")
                print(f"[TEST] STDERR: {stderr}")
                return True
            except subprocess.TimeoutExpired:
                print("[TEST] Process didn't terminate gracefully, killing...")
                process.kill()
                process.wait()
                print("[SUCCESS] Process killed successfully")
                return True

        else:
            stdout, stderr = process.communicate()
            print(f"[ERROR] Server exited early with code: {process.poll()}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server_start_stop()
    print(f"\n=== Result: {'SUCCESS' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)
