#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug - Verificar posições abertas vs fechadas
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'trading.db'
GAME_MAGIC_NUMBER = 777777

def debug_positions():
    """Verificar diferença entre posições abertas e fechadas"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        print("=== ANÁLISE DETALHADA DO BANCO ===")
        
        # Ver todas as posições do game
        cursor.execute("""
            SELECT ticket, type, profit, close_time, open_price, close_price
            FROM game_history
            WHERE magic_number = ?
            ORDER BY ticket DESC
            LIMIT 20
        """, (GAME_MAGIC_NUMBER,))
        
        rows = cursor.fetchall()
        
        print(f"Total de posições no banco: {len(rows)}")
        print()
        
        # Categorizar por profit
        open_positions = []  # profit = 0
        closed_positions = []  # profit != 0
        
        for row in rows:
            ticket, trade_type, profit, close_time, open_price, close_price = row
            
            if profit == 0:
                open_positions.append(row)
                status = "ABERTA"
            else:
                closed_positions.append(row)
                status = "FECHADA"
            
            print(f"#{ticket}: {trade_type} ${profit:.2f} ({status}) - Close time: {close_time}")
        
        print(f"\n=== RESUMO ===")
        print(f"Posições ABERTA (profit = 0): {len(open_positions)}")
        print(f"Posições FECHADA (profit ≠ 0): {len(closed_positions)}")
        
        print(f"\n=== POSIÇÕES FECHADAS (devem aparecer no histórico) ===")
        for pos in closed_positions:
            ticket, trade_type, profit, close_time, open_price, close_price = pos
            print(f"#{ticket}: {trade_type} ${profit:.2f} em {close_time}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_positions()
