#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir timestamps Unix restantes no banco de dados
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def fix_timestamps():
    """Converter timestamps Unix para formato ISO"""
    
    # Conectar ao banco
    db_path = Path('trading.db')
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Buscar todos os registros com close_time numérico
    cursor.execute("""
        SELECT id, ticket, close_time 
        FROM game_history 
        WHERE CAST(close_time AS INTEGER) > 1000000000
    """)
    
    records = cursor.fetchall()
    print(f"Encontrados {len(records)} registros com timestamps Unix")
    
    for record in records:
        record_id, ticket, timestamp = record
        
        try:
            # Converter timestamp Unix para datetime
            dt = datetime.fromtimestamp(int(timestamp))
            iso_time = dt.isoformat()
            
            # Atualizar registro
            cursor.execute("""
                UPDATE game_history 
                SET close_time = ? 
                WHERE id = ?
            """, (iso_time, record_id))
            
            print(f"Atualizado ticket {ticket}: {timestamp} -> {iso_time}")
            
        except Exception as e:
            print(f"Erro ao converter ticket {ticket}: {e}")
    
    # Commit e fechar
    conn.commit()
    conn.close()
    
    print(f"\nCorreção concluída! {len(records)} registros atualizados.")

if __name__ == "__main__":
    fix_timestamps()
