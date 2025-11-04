#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importar dados históricos do MT5 para o banco do game
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client
import sqlite3

def import_mt5_history():
    """Importar histórico de trades do MT5 para o banco do game"""
    
    # Conectar ao banco
    db_path = Path('trading.db')
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Garantir que a tabela existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket INTEGER NOT NULL UNIQUE,
            magic_number INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            type TEXT NOT NULL,
            volume REAL NOT NULL,
            open_price REAL,
            close_price REAL,
            sl REAL,
            tp REAL,
            profit REAL NOT NULL,
            open_time TEXT,
            close_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Conectar ao MT5
    mt5 = get_mt5_client()
    if not mt5:
        print("Erro: Não foi possível conectar ao MT5")
        return
    
    print("Conectado ao MT5, buscando histórico...")
    
    # Buscar deals dos últimos 7 dias
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    deals = mt5.history_deals_get(
        date_from=week_ago,
        date_to=now,
        symbol="XAUUSDc"
    )
    
    if not deals:
        print("Nenhum deal encontrado nos últimos 7 dias")
        return
    
    print(f"Encontrados {len(deals)} deals")
    
    # Organizar deals por position
    positions = {}
    
    for deal in deals:
        magic = deal.get('magic', 0)
        pos_id = deal.get('position_id')
        entry_type = deal.get('entry')
        
        # Apenas processar deals com magic number 777777 ou sem magic (para testes)
        if magic != 777777 and magic != 0:
            continue
            
        if not pos_id:
            continue
            
        if pos_id not in positions:
            positions[pos_id] = {
                'ticket': pos_id,
                'magic': magic,
                'symbol': deal.get('symbol', 'XAUUSDc'),
                'volume': 0,
                'open_time': None,
                'close_time': None,
                'open_price': 0,
                'close_price': 0,
                'profit': 0,
                'type': 'UNKNOWN'
            }
        
        # Entry = 0 (IN), 1 (OUT), 2 (INOUT)
        if entry_type == 0:  # IN
            positions[pos_id]['volume'] = deal.get('volume', 0)
            positions[pos_id]['open_time'] = deal.get('time')
            positions[pos_id]['open_price'] = deal.get('price', 0)
            positions[pos_id]['type'] = 'BUY' if deal.get('type') == 0 else 'SELL'
            
        elif entry_type == 1:  # OUT
            positions[pos_id]['close_time'] = deal.get('time')
            positions[pos_id]['close_price'] = deal.get('price', 0)
            positions[pos_id]['profit'] += deal.get('profit', 0)
    
    print(f"Processadas {len(positions)} posições")
    
    # Salvar no banco
    imported_count = 0
    for pos_id, pos_data in positions.items():
        # Se não tem magic number, usar 777777 como padrão
        magic_number = pos_data['magic'] if pos_data['magic'] != 0 else 777777
        
        # Verificar se já existe
        cursor.execute(
            "SELECT id FROM game_history WHERE ticket = ? AND magic_number = ?", 
            (pos_data['ticket'], magic_number)
        )
        if cursor.fetchone():
            continue  # Já existe
        
        # Formatar datas - converter timestamp Unix para datetime se necessário
        def format_time(time_obj):
            if not time_obj:
                return datetime.now().isoformat()
            
            # Se for timestamp Unix (número grande)
            if isinstance(time_obj, (int, float)) and time_obj > 1000000000:
                try:
                    return datetime.fromtimestamp(time_obj).isoformat()
                except:
                    return str(time_obj)
            
            # Se for datetime
            if hasattr(time_obj, 'isoformat'):
                return time_obj.isoformat()
            
            # Se for string, tentar converter
            if isinstance(time_obj, str):
                try:
                    # Tentar converter de timestamp Unix
                    if time_obj.isdigit():
                        return datetime.fromtimestamp(int(time_obj)).isoformat()
                except:
                    pass
            
            return str(time_obj)
        
        open_time_str = format_time(pos_data['open_time'])
        close_time_str = format_time(pos_data['close_time'])
        
        # Inserir ou atualizar no banco
        cursor.execute("""
            INSERT OR REPLACE INTO game_history 
            (ticket, magic_number, symbol, type, volume, open_price, close_price, sl, tp, profit, open_time, close_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pos_data['ticket'],
            magic_number,
            pos_data['symbol'],
            pos_data['type'],
            pos_data['volume'],
            pos_data['open_price'],
            pos_data['close_price'],
            None,  # sl
            None,  # tp
            pos_data['profit'],
            open_time_str,
            close_time_str
        ))
        
        imported_count += 1
        print(f"Importado: Ticket {pos_data['ticket']}, Profit: ${pos_data['profit']:.2f}, Type: {pos_data['type']}")
    
    # Commit e fechar
    conn.commit()
    conn.close()
    
    print(f"\nImportação concluída!")
    print(f"Total importado: {imported_count} trades")
    
    # Verificar resultado
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM game_history WHERE magic_number = 777777")
    count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT SUM(profit), COUNT(CASE WHEN profit > 0 THEN 1 END), COUNT(CASE WHEN profit < 0 THEN 1 END)
        FROM game_history WHERE magic_number = 777777
    """)
    stats = cursor.fetchone()
    
    total_profit = stats[0] or 0
    wins = stats[1] or 0
    losses = stats[2] or 0
    
    print(f"\nEstatísticas atualizadas:")
    print(f"Total de trades: {count}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Profit Total: ${total_profit:.2f}")
    
    conn.close()

if __name__ == "__main__":
    import_mt5_history()
