#!/usr/bin/env python3
"""Test script to simulate Cline MCP connection"""

import subprocess
import sys
import os
import time

def test_cline_connection():
    """Test the MCP server connection as Cline would do it"""

    # Change to the correct working directory (as configured in Cline)
    os.chdir(r'c:\mcp-trader')

    print("Testing MCP connection from Cline's perspective...")
    print(f"Working directory: {os.getcwd()}")
    print("Starting Node.js wrapper...")

    try:
        # Execute exactly as Cline would
        process = subprocess.Popen(
            ['node', 'build/index.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r'c:\mcp-trader'
        )

        # Wait a bit for startup
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print("SUCCESS: MCP server started successfully!")
            print("Server is running and ready for Cline connection")
            print(f"Process ID: {process.pid}")

            # Clean shutdown
            process.terminate()
            process.wait()
            return True
        else:
            print("FAILED: Server exited immediately")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

    except FileNotFoundError:
        print("ERROR: Could not find build/index.js")
        print(f"Current directory: {os.getcwd()}")
        print("Files in current directory:", os.listdir('.'))
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_cline_connection()
    sys.exit(0 if success else 1)
