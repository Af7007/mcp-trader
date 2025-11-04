#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start Game Server
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

if __name__ == "__main__":
    from web.app import app
    print("🚀 Iniciando servidor na porta 3000...")
    app.run(host='0.0.0.0', port=3000, debug=False)
