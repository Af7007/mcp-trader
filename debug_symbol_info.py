#!/usr/bin/env python3
"""
Debug: Ver o que symbol_info retorna
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()

for symbol in ['XAUUSDc', 'BTCUSDc']:
    print(f"\n{'='*70}")
    print(f"Symbol: {symbol}")
    print(f"{'='*70}")

    info = mt5.get_symbol_info(symbol)

    if info:
        print(f"Type: {type(info)}")
        print(f"\nKeys available:")
        for key in sorted(info.keys()):
            value = info[key]
            if isinstance(value, (int, float, str)):
                print(f"  {key}: {value}")
    else:
        print("Nenhuma info retornada!")
