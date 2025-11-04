#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir problemas da interface do game:
1. Valores incorretos de operação (trades com $0.00)
2. Interface esticada com scroll
3. Erro de encoding Unicode
"""

import sqlite3
from pathlib import Path

def fix_game_interface():
    """Corrigir problemas da interface do game"""
    
    # Conectar ao banco
    db_path = Path('trading.db')
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("🔧 CORRIGINDO PROBLEMAS DA INTERFACE DO GAME...")
    
    # 1. Corrigir valores de profit que estão como 0.0
    print("\n1️⃣ Verificando trades com profit = 0.0...")
    cursor.execute("""
        SELECT id, ticket, profit, close_time, type, volume
        FROM game_history 
        WHERE profit = 0.0 AND volume > 0
        ORDER BY close_time DESC
        LIMIT 10
    """)
    
    zero_profit_trades = cursor.fetchall()
    print(f"   Encontrados {len(zero_profit_trades)} trades com profit = 0.0")
    
    for trade in zero_profit_trades:
        trade_id, ticket, profit, close_time, trade_type, volume = trade
        print(f"   Trade #{ticket} - {trade_type} {volume} - Profit: ${profit}")
    
    # 2. Verificar trades com tipo UNKNOWN
    print("\n2️⃣ Verificando trades com tipo UNKNOWN...")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM game_history 
        WHERE type = 'UNKNOWN'
    """)
    
    unknown_count = cursor.fetchone()[0]
    print(f"   Encontrados {unknown_count} trades com tipo UNKNOWN")
    
    # 3. Verificar estrutura dos dados
    print("\n3️⃣ Analisando estrutura dos dados...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN profit > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit < 0 THEN 1 END) as losses,
            SUM(profit) as total_profit,
            AVG(CASE WHEN profit != 0 THEN ABS(profit) END) as avg_profit
        FROM game_history
        WHERE volume > 0
    """)
    
    stats = cursor.fetchone()
    total, wins, losses, total_profit, avg_profit = stats
    
    print(f"   Total de trades: {total}")
    print(f"   Wins: {wins}")
    print(f"   Losses: {losses}")
    print(f"   Profit total: ${total_profit:.2f}")
    print(f"   Profit médio: ${avg_profit:.2f}" if avg_profit else "   Profit médio: N/A")
    
    # 4. Verificar problemas de encoding
    print("\n4️⃣ Verificando problemas de encoding...")
    cursor.execute("""
        SELECT id, ticket, close_time
        FROM game_history 
        WHERE close_time LIKE '%%' OR close_time LIKE '%\\u%'
        LIMIT 5
    """)
    
    encoding_issues = cursor.fetchall()
    print(f"   Encontrados {len(encoding_issues)} registros com problemas de encoding")
    
    for issue in encoding_issues:
        issue_id, ticket, close_time = issue
        print(f"   Trade #{ticket} - Timestamp problemático: {close_time}")
    
    # 5. Sugerir correções
    print("\n5️⃣ CORREÇÕES SUGERIDAS:")
    print("   a) Atualizar game_api.py para tratar encoding Unicode")
    print("   b) Corrigir lógica de cálculo de profit")
    print("   c) Ajustar CSS para remover scroll desnecessário")
    print("   d) Validar dados antes de salvar no banco")
    
    conn.close()
    
    print("\n✅ ANÁLISE CONCLUÍDA!")
    print("📋 PRÓXIMOS PASSOS:")
    print("   1. Corrigir encoding no game_api.py")
    print("   2. Ajustar CSS game_v2.css")
    print("   3. Validar cálculo de profit")
    print("   4. Testar interface corrigida")

if __name__ == "__main__":
    fix_game_interface()
