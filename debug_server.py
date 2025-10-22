#!/usr/bin/env python3
"""Debug script for MCP MT5 server"""

import sys
import os
import subprocess
import time

def debug_server():
    """Debug the MCP server startup process"""

    print("=== MCP MT5 Server Debug ===")

    # Test 1: Check if Python path exists
    python_server_path = r'c:\mcp-trader\src\mcp_mt5\main.py'
    print(f"1. Checking Python server path: {python_server_path}")
    if os.path.exists(python_server_path):
        print("   [OK] Path exists")
    else:
        print("   [FAIL] Path does not exist")
        return False

    # Test 2: Check current directory
    print(f"2. Current working directory: {os.getcwd()}")

    # Test 3: Check Python environment
    print("3. Checking Python environment...")
    try:
        result = subprocess.run([r'uv', '--version'], capture_output=True, text=True)
        print(f"   UV version: {result.stdout.strip()}")
    except Exception as e:
        print(f"   [ERROR] UV error: {e}")
        return False

    # Test 4: Check if we can import the server module
    print("4. Testing Python imports...")
    try:
        # Change to correct directory
        os.chdir(r'c:\mcp-trader')

        # Try to run Python directly first
        result = subprocess.run(
            [r'uv', 'run', 'python', '-c', 'import sys; print(f"Python path: {sys.path}"); print("Basic imports work")'],
            capture_output=True,
            text=True,
            cwd=r'c:\mcp-trader'
        )

        print(f"   Basic Python test stdout: {result.stdout}")
        if result.stderr:
            print(f"   Basic Python test stderr: {result.stderr}")

        if result.returncode != 0:
            print("   [ERROR] Basic Python test failed")
            return False

    except Exception as e:
        print(f"   [ERROR] Python environment error: {e}")
        return False

    # Test 5: Try to start the actual server
    print("5. Starting MCP server...")
    try:
        process = subprocess.Popen(
            [r'uv', 'run', 'python', python_server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r'c:\mcp-trader'
        )

        print(f"   Process started with PID: {process.pid}")

        # Wait a few seconds and check output
        time.sleep(3)

        if process.poll() is None:
            print("   [OK] Server is still running")

            # Get some output
            stdout, stderr = process.communicate(timeout=5)
            print(f"   Server stdout: {stdout}")
            if stderr:
                print(f"   Server stderr: {stderr}")

            process.terminate()
            process.wait()

        else:
            print(f"   [ERROR] Server exited with code: {process.poll()}")
            stdout, stderr = process.communicate()
            print(f"   Server stdout: {stdout}")
            print(f"   Server stderr: {stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("   [OK] Server started successfully (timed out waiting for exit)")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"   [ERROR] Server startup error: {e}")
        return False

    print("=== Debug Complete ===")
    return True

if __name__ == "__main__":
    success = debug_server()
    print(f"\nDebug result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
