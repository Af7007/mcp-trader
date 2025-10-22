#!/usr/bin/env python3
"""Trace script for MCP MT5 server startup"""

import sys
import os
import subprocess
import time

def trace_server():
    """Trace the MCP server startup in detail"""

    print("=== MCP MT5 Server Trace ===")

    # Change to correct directory first
    os.chdir(r'c:\mcp-trader')
    print(f"Working directory: {os.getcwd()}")

    # Test with verbose output
    python_server_path = r'c:\mcp-trader\src\mcp_mt5\main.py'

    print(f"Starting server: {python_server_path}")

    # Try with different approaches
    approaches = [
        ['uv', 'run', 'python', python_server_path],
        ['uv', 'run', 'python', '-v', python_server_path],
        ['uv', 'run', 'python', '-c', 'import sys; sys.path.insert(0, "src"); from mcp_mt5.main import mcp; print("Import successful")'],
    ]

    for i, cmd in enumerate(approaches, 1):
        print(f"\n--- Attempt {i}: {' '.join(cmd)} ---")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=r'c:\mcp-trader'
            )

            print(f"Process started with PID: {process.pid}")

            # Wait and capture output
            time.sleep(2)

            if process.poll() is None:
                print("[OK] Process is still running")

                # Try to get output with timeout
                try:
                    stdout, stderr = process.communicate(timeout=3)
                    print(f"STDOUT: {stdout}")
                    print(f"STDERR: {stderr}")
                except subprocess.TimeoutExpired:
                    print("[OK] Process running (timeout)")
                    process.terminate()
                    process.wait()
            else:
                stdout, stderr = process.communicate()
                print(f"[EXIT] Process exited with code: {process.poll()}")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")

        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n=== Testing individual imports ===")

    # Test imports one by one
    imports_to_test = [
        'import sys; print("sys imported")',
        'sys.path.insert(0, "src"); print("path updated")',
        'import fastmcp; print("fastmcp imported")',
        'import MetaTrader5 as mt5; print("MetaTrader5 imported")',
        'import pandas as pd; print("pandas imported")',
        'import pydantic; print("pydantic imported")',
        'from mcp_mt5.main import mcp; print("mcp imported")',
    ]

    for test_import in imports_to_test:
        print(f"\nTesting: {test_import}")
        try:
            result = subprocess.run(
                ['uv', 'run', 'python', '-c', test_import],
                capture_output=True,
                text=True,
                cwd=r'c:\mcp-trader',
                timeout=10
            )

            print(f"  [OK] {result.stdout.strip()}")
            if result.stderr:
                print(f"  [WARN] {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print("  [TIMEOUT] Import took too long")
        except Exception as e:
            print(f"  [ERROR] {e}")

    print("\n=== Trace Complete ===")

if __name__ == "__main__":
    trace_server()
