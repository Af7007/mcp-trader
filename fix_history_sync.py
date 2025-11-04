#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix History Synchronization
Limpa banco e testa sincronização correta do histórico
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

# Database path
DB_PATH = Path(__file__).parent / 'trading.db'
GAME_MAGIC_NUMBER = 777777

def clear_game_history():
    """Limpa histórico do jogo"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Delete all game history
        cursor.execute("DELETE FROM game_history WHERE magic_number = ?", (GAME_MAGIC_NUMBER,))
        
        conn.commit()
        conn.close()
        
        print(f"[CLEAN] Game history cleared for magic {GAME_MAGIC_NUMBER}")
        return True
    except Exception as e:
        print(f"[CLEAN] Error: {e}")
        return False

def test_sync_from_mt5():
    """Testa sincronização completa do MT5"""
    try:
        mt5 = get_mt5_client()
        
        # Get deals from last 24 hours
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        deals = mt5.history_deals_get(
            date_from=yesterday,
            date_to=now,
            symbol="XAUUSDc"
        )
        
        print(f"\n[SYNC] Found {len(deals) if deals else 0} total deals")
        
        if not deals:
            print("[SYNC] No deals found")
            return
        
        # Filter by magic number
        game_deals = []
        for deal in deals:
            magic = deal.get('magic', 0)
            if magic == GAME_MAGIC_NUMBER:
                game_deals.append(deal)
        
        print(f"[SYNC] Found {len(game_deals)} deals with magic {GAME_MAGIC_NUMBER}")
        
        # Group by position
        positions = {}
        
        for deal in game_deals:
            pos_id = deal.get('position_id')
            entry_type = deal.get('entry')
            deal_type = deal.get('type')  # 0=BUY, 1=SELL
            
            print(f"[SYNC] Deal #{deal.get('ticket')}: pos={pos_id}, entry={entry_type}, type={deal_type}, profit=${deal.get('profit', 0):.2f}")
            
            if not pos_id:
                continue
                
            if pos_id not in positions:
                positions[pos_id] = {
                    'ticket': pos_id,
                    'type': None,
                    'volume': 0,
                    'profit': 0,
                    'open_time': None,
                    'close_time': None,
                    'open_price': 0,
                    'close_price': 0
                }
            
            if entry_type == 0:  # IN deal
                positions[pos_id]['type'] = 'BUY' if deal_type == 0 else 'SELL'
                positions[pos_id]['volume'] = deal.get('volume', 0)
                positions[pos_id]['open_time'] = deal.get('time')
                positions[pos_id]['open_price'] = deal.get('price', 0)
                print(f"[SYNC]   -> OPEN: {positions[pos_id]['type']} at {positions[pos_id]['open_price']}")
                
            elif entry_type == 1:  # OUT deal
                positions[pos_id]['profit'] = deal.get('profit', 0)
                positions[pos_id]['close_time'] = deal.get('time')
                positions[pos_id]['close_price'] = deal.get('price', 0)
                print(f"[SYNC]   -> CLOSE: profit=${positions[pos_id]['profit']:.2f}")
        
        print(f"\n[SYNC] Processed {len(positions)} positions:")
        
        for pos_id, pos in positions.items():
            print(f"[SYNC] Position #{pos_id}: {pos['type']} ${pos['profit']:.2f}")
        
        return positions
        
    except Exception as e:
        print(f"[SYNC] Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

def save_corrected_history(positions):
    """Salva histórico corrigido"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        saved_count = 0
        for pos_id, pos in positions.items():
            if pos['close_time']:  # Only save closed positions
                cursor.execute("""
                    INSERT OR REPLACE INTO game_history 
                    (ticket, magic_number, symbol, type, volume, open_price, close_price, profit, open_time, close_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pos['ticket'],
                    GAME_MAGIC_NUMBER,
                    'XAUUSDc',
                    pos['type'],
                    pos['volume'],
                    pos['open_price'],
                    pos['close_price'],
                    pos['profit'],
                    str(pos['open_time']) if pos['open_time'] else datetime.now().isoformat(),
                    str(pos['close_time']) if pos['close_time'] else datetime.now().isoformat()
                ))
                saved_count += 1
                print(f"[SAVE] Position #{pos_id}: {pos['type']} ${pos['profit']:.2f}")
        
        conn.commit()
        conn.close()
        
        print(f"\n[SAVE] Saved {saved_count} positions to database")
        return saved_count
        
    except Exception as e:
        print(f"[SAVE] Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def verify_database():
    """Verifica dados no banco"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ticket, type, volume, profit, close_time
            FROM game_history
            WHERE magic_number = ?
            ORDER BY close_time DESC
            LIMIT 10
        """, (GAME_MAGIC_NUMBER,))
        
        rows = cursor.fetchall()
        conn.close()
        
        print(f"\n[VERIFY] Database contains {len(rows)} recent trades:")
        
        for row in rows:
            ticket, trade_type, volume, profit, close_time = row
            print(f"[VERIFY] #{ticket}: {trade_type} ${profit:.2f} at {close_time}")
        
        return rows
        
    except Exception as e:
        print(f"[VERIFY] Error: {e}")
        return []

def main():
    """Função principal"""
    print("=" * 60)
    print("FIX HISTORY SYNCHRONIZATION")
    print("=" * 60)
    
    # 1. Clear existing history
    print("\n1. Clearing existing game history...")
    if clear_game_history():
        print("History cleared")
    else:
        print("Failed to clear history")
        return
    
    # 2. Sync from MT5
    print("\n2. Syncing from MT5...")
    positions = test_sync_from_mt5()
    
    if not positions:
        print("No positions to sync")
        return
    
    # 3. Save corrected history
    print("\n3. Saving corrected history...")
    saved_count = save_corrected_history(positions)
    
    if saved_count > 0:
        print(f"Saved {saved_count} positions")
    else:
        print("Failed to save positions")
        return
    
    # 4. Verify database
    print("\n4. Verifying database...")
    verify_database()
    
    print("\n" + "=" * 60)
    print("HISTORY SYNCHRONIZATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
