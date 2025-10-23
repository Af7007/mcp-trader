#!/usr/bin/env python3
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flask import Flask, render_template

    # Test template loading
    app = Flask(__name__, template_folder='src/web/templates')

    with app.app_context():
        result = render_template('index.html')
        print("SUCCESS: Template loaded successfully!")
        print(f"Length: {len(result)} characters")
        print("Web interface should be working!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
