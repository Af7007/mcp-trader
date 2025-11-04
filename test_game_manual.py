#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Manual - Abrir e Fechar Trade com Magic 777777
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

GAME_MAGIC = 777777

def test_trade():
    print("\n" + "="*60)
    print("TESTE MANUAL - GOLD GAME TRADE")
    print("="*60 + "\n")
    
    mt5 = get_mt5_client()
    
    # Check connection
    if not mt5._initialized:
        print("❌ MT5 not connected!")
        return
    
    print("✅ MT5 Connected\n")
    
    # Get account
    account = mt5.get_account_info()
    print(f"Account: {account['login']}")
    print(f"Balance: ${account['balance']:.2f}")
    print(f"Equity: ${account['equity']:.2f}\n")
    
    # Get current price
    tick = mt5.get_symbol_info_tick("XAUUSDc")
    print(f"Current Price:")
    print(f"  Bid: ${tick['bid']:.2f}")
    print(f"  Ask: ${tick['ask']:.2f}\n")
    
    # Check existing positions with magic 777777
    positions = mt5.positions_get(symbol="XAUUSDc", magic=GAME_MAGIC)
    
    if positions and len(positions) > 0:
        print(f"✅ Found {len(positions)} active positions with magic {GAME_MAGIC}:\n")
        
        for pos in positions:
            profit = ((pos['price_current'] - pos['price_open']) if pos['type'] == 0 else (pos['price_open'] - pos['price_current'])) * 100 * pos['volume']
            print(f"  #{pos['ticket']} | {'BUY' if pos['type'] == 0 else 'SELL'} | {pos['volume']} lots")
            print(f"    Entry: ${pos['price_open']:.2f} | Current: ${pos['price_current']:.2f}")
            print(f"    SL: ${pos['sl']:.2f} | Profit: ${profit:.2f}")
            print()
    else:
        print(f"⚠️  No active positions with magic {GAME_MAGIC}\n")
        print("To test, open a position in the game and run this script again.")
    
    # Check recent deals (using correct method signature)
    try:
        deals = mt5.get_deals_history(symbol="XAUUSDc", days=1)
    except:
        deals = None
    
    if deals:
        # Filter by magic
        game_deals = [d for d in deals if d.get('magic') == GAME_MAGIC]
        
        if game_deals:
            print(f"✅ Found {len(game_deals)} deals with magic {GAME_MAGIC} in last 24h:\n")
            
            for deal in game_deals[-5:]:  # Last 5
                print(f"  Deal #{deal['deal']}")
                print(f"    Position: #{deal['position_id']}")
                print(f"    Type: {deal['type']} | Entry: {deal['entry']} (0=IN, 1=OUT)")
                print(f"    Volume: {deal['volume']} | Profit: ${deal.get('profit', 0):.2f}")
                print(f"    Time: {deal['time']}")
                print()
        else:
            print(f"⚠️  No deals found with magic {GAME_MAGIC} in last 24h\n")
            print(f"Total deals for XAUUSDc: {len(deals)}")
            
            # Show other magics
            magics = {}
            for d in deals:
                m = d.get('magic', 0)
                magics[m] = magics.get(m, 0) + 1
            
            print("\nMagic numbers found:")
            for magic, count in sorted(magics.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  Magic {magic}: {count} deals")
    else:
        print("⚠️  No deals found for XAUUSDc in last 24h\n")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    test_trade()
