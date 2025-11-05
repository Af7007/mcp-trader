#!/usr/bin/env python3
"""
Analisa erros de calculo de SL
"""

import sqlite3

conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

print("="*100)
print("ANALISE DE CALCULO DE SL - ULTIMOS 10 TRADES")
print("="*100)

# Buscar todos os trades
cursor.execute("""
    SELECT id, ticket, symbol, trade_type, entry_price, sl_price, volume, 
           CASE 
               WHEN trade_type = 'SELL' THEN (sl_price - entry_price) / 0.001
               ELSE (entry_price - sl_price) / 0.001
           END as sl_pontos,
           status, timestamp
    FROM trades 
    WHERE symbol = 'XAUUSDc'
    ORDER BY id DESC 
    LIMIT 10;
""")

print(f"\n{'ID':>5} {'Ticket':>8} {'Type':>5} {'Entry':>10} {'SL':>10} {'Vol':>6} {'SL Pontos':>12} {'Status':>12}")
print("-"*100)

erros = []
for row in cursor.fetchall():
    trade_id, ticket, symbol, trade_type, entry, sl, vol, sl_pontos, status, timestamp = row
    ticket_str = str(ticket) if ticket else "NULL"
    
    # Verificar se SL está errado (mais de 1000 pontos de diferença ao esperado)
    if sl_pontos > 1000:
        erros.append((trade_id, ticket_str, trade_type, entry, sl, vol, sl_pontos))
    
    print(f"{trade_id:>5} {ticket_str:>8} {trade_type:>5} ${entry:>9.2f} ${sl:>9.2f} {vol:>6.2f} {sl_pontos:>12.0f} {status:>12}")

conn.close()

print("\n" + "="*100)
if erros:
    print(f"[ERRO ENCONTRADO] {len(erros)} trade(s) com SL problematico:")
    for trade_id, ticket, trade_type, entry, sl, vol, sl_pontos in erros:
        print(f"\n  Trade ID: {trade_id}")
        print(f"  Ticket: {ticket}")
        print(f"  Type: {trade_type}")
        print(f"  Entry: ${entry:.2f}")
        print(f"  SL: ${sl:.2f}")
        print(f"  SL Distance: {sl_pontos:.0f} pontos (ERRO!)")
        
        # Calcular o que deveria ser
        if trade_type == "SELL":
            # Para SELL, SL deve estar ACIMA do entry (para proteção)
            # Se entry é $3950 e quer SL de 300 pontos:
            # SL = $3950 + (300 * 0.001) = $3950.30
            expected_sl = entry + (300 * 0.001)
        else:
            # Para BUY, SL deve estar ABAIXO do entry
            expected_sl = entry - (300 * 0.001)
        
        print(f"  SL Esperado (300 pts): ${expected_sl:.2f}")
        print(f"  Diferenca: ${sl - expected_sl:.2f}")
else:
    print("[OK] Nenhum erro de SL detectado")

print("\n" + "="*100)
