#!/usr/bin/env python3
"""Test script to debug main.py execution"""

import subprocess
import sys
import os
import time

def test_execution():
    """Test main.py execution and capture output"""
    print("Testing main.py execution...")

    # Change to project directory
    os.chdir("c:\\mcp-trader")

    # Start the process
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print("Process started, waiting for output...")

        # Read output line by line for 15 seconds
        start_time = time.time()
        while time.time() - start_time < 15:
            if process.poll() is not None:
                # Process finished
                break

            # Check for output
            output = process.stdout.readline()
            if output:
                print(f"STDOUT: {output.strip()}")

            error = process.stderr.readline()
            if error:
                print(f"STDERR: {error.strip()}")

            time.sleep(0.1)

        # Get remaining output
        stdout, stderr = process.communicate(timeout=5)

        if stdout:
            print(f"REMAINING STDOUT: {stdout}")
        if stderr:
            print(f"REMAINING STDERR: {stderr}")

        return_code = process.returncode
        print(f"Process finished with return code: {return_code}")

        if return_code != 0:
            print(f"ERROR: Process failed with return code {return_code}")
            return False
        else:
            print("SUCCESS: Process completed successfully")
            return True

    except subprocess.TimeoutExpired:
        print("Process timed out after 15 seconds")
        process.kill()
        return False
    except Exception as e:
        print(f"ERROR: Failed to execute process: {e}")
        return False

if __name__ == "__main__":
    test_execution()
