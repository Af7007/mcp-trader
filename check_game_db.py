#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar banco de dados do game
"""

import sqlite3
from pathlib import Path

def check_database():
    """Verificar conteúdo do banco de dados"""
    db_path = Path('trading.db')
    
    if not db_path.exists():
        print("[ERRO] Banco de dados nao encontrado!")
        return
    
    print(f"[OK] Banco encontrado: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"Tabelas: {table_names}")
        
        # Verificar game_history
        if any('game_history' in t for t in tables):
            cursor.execute("SELECT COUNT(*) FROM game_history WHERE magic_number = 777777")
            count = cursor.fetchone()[0]
            print(f"Trades no game_history (magic 777777): {count}")
            
            if count > 0:
                cursor.execute("""
                    SELECT ticket, profit, close_time, type, volume 
                    FROM game_history 
                    WHERE magic_number = 777777 
                    ORDER BY close_time DESC 
                    LIMIT 5
                """)
                recent = cursor.fetchall()
                print("Trades recentes:")
                for row in recent:
                    print(f"   Ticket: {row[0]}, Profit: ${row[1]:.2f}, Type: {row[3]}, Volume: {row[4]}")
                
                # Calcular estatísticas
                cursor.execute("""
                    SELECT 
                        SUM(profit) as total_profit,
                        COUNT(CASE WHEN profit > 0 THEN 1 END) as wins,
                        COUNT(CASE WHEN profit < 0 THEN 1 END) as losses,
                        COUNT(*) as total
                    FROM game_history
                    WHERE magic_number = 777777
                """)
                stats = cursor.fetchone()
                total_profit = stats[0] or 0
                wins = stats[1] or 0
                losses = stats[2] or 0
                total = stats[3] or 0
                
                print("Estatísticas:")
                print(f"   Total: {total} trades")
                print(f"   Wins: {wins}")
                print(f"   Losses: {losses}")
                print(f"   Profit Total: ${total_profit:.2f}")
                print(f"   Win Rate: {(wins/total*100):.1f}%" if total > 0 else "   Win Rate: 0%")
            else:
                print("Nenhum trade encontrado no game_history")
        
        # Verificar trades gerais
        if any('trades' in t for t in tables):
            cursor.execute("SELECT COUNT(*) FROM trades")
            trades_count = cursor.fetchone()[0]
            print(f"Trades totais na tabela 'trades': {trades_count}")
            
            if trades_count > 0:
                cursor.execute("""
                    SELECT ticket, symbol, type, volume, profit, status 
                    FROM trades 
                    ORDER BY id DESC 
                    LIMIT 5
                """)
                recent_trades = cursor.fetchall()
                print("Trades recentes na tabela 'trades':")
                for row in recent_trades:
                    print(f"   Ticket: {row[0]}, Symbol: {row[1]}, Type: {row[2]}, Profit: ${row[3]:.2f}, Status: {row[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database()
