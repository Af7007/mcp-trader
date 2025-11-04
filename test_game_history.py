#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gold Game History System
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

DB_PATH = Path(__file__).parent / 'trading.db'
GAME_MAGIC = 777777

def test_database():
    """Test database connection and data"""
    print("\n" + "="*60)
    print("GOLD GAME HISTORY TEST")
    print("="*60 + "\n")
    
    print(f"Database: {DB_PATH}")
    print(f"Magic Number: {GAME_MAGIC}\n")
    
    if not DB_PATH.exists():
        print("❌ Database file not found!")
        print(f"   Expected: {DB_PATH}")
        return
    
    print("✅ Database file exists\n")
    
    # Connect
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='game_history'
    """)
    
    if not cursor.fetchone():
        print("❌ Table 'game_history' not found!")
        print("   Run the game server first to create tables.")
        conn.close()
        return
    
    print("✅ Table 'game_history' exists\n")
    
    # Count all trades
    cursor.execute("SELECT COUNT(*) FROM game_history")
    total = cursor.fetchone()[0]
    print(f"Total trades in database: {total}")
    
    # Count trades with magic 777777
    cursor.execute("SELECT COUNT(*) FROM game_history WHERE magic_number = ?", (GAME_MAGIC,))
    game_trades = cursor.fetchone()[0]
    print(f"Gold Game trades (magic {GAME_MAGIC}): {game_trades}\n")
    
    if game_trades == 0:
        print("⚠️  No trades found with magic number 777777")
        print("   This is normal if you haven't closed any trades yet.")
        print("\n📋 How to test:")
        print("   1. Start game server: RUN_GOLD_GAME.bat")
        print("   2. Open http://localhost:3000/game")
        print("   3. Open a position")
        print("   4. Close it (use X button or let it hit SL)")
        print("   5. Run this test again\n")
        
        # Show other magic numbers
        cursor.execute("""
            SELECT magic_number, COUNT(*) as count
            FROM game_history
            GROUP BY magic_number
            ORDER BY count DESC
            LIMIT 5
        """)
        
        others = cursor.fetchall()
        if others:
            print("Other magic numbers found:")
            for magic, count in others:
                print(f"   Magic {magic}: {count} trades")
            print("\n   💡 These are from other bots/systems")
    
    else:
        print(f"✅ Found {game_trades} Gold Game trades!\n")
        
        # Show recent trades
        cursor.execute("""
            SELECT ticket, type, volume, profit, close_time
            FROM game_history
            WHERE magic_number = ?
            ORDER BY close_time DESC
            LIMIT 10
        """, (GAME_MAGIC,))
        
        trades = cursor.fetchall()
        
        print("Recent trades:")
        print("-" * 60)
        for ticket, type_, volume, profit, close_time in trades:
            profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
            print(f"#{ticket} | {type_:4} | {volume:.2f} lots | {profit_str:>10} | {close_time}")
        
        # Stats
        cursor.execute("""
            SELECT 
                SUM(profit) as total,
                COUNT(CASE WHEN profit > 0 THEN 1 END) as wins,
                COUNT(CASE WHEN profit < 0 THEN 1 END) as losses
            FROM game_history
            WHERE magic_number = ?
        """, (GAME_MAGIC,))
        
        total_profit, wins, losses = cursor.fetchone()
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        print("-" * 60)
        print(f"\n📊 Stats:")
        print(f"   Total Profit: ${total_profit:.2f}")
        print(f"   Wins: {wins} | Losses: {losses}")
        print(f"   Win Rate: {win_rate:.1f}%")
    
    conn.close()
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    test_database()
