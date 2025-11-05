#!/usr/bin/env python3
"""
Verifica se os novos campos estão sendo salvos
"""

import sqlite3

db_path = "btc_trading_logs.db"

print("="*70)
print("VERIFICACAO DE NOVOS CAMPOS - ticket, magic_number, strength")
print("="*70)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar estrutura
print("\n[1] ESTRUTURA DA TABELA:")
print("-"*70)
cursor.execute("PRAGMA table_info(trades);")
columns = cursor.fetchall()

has_ticket = False
has_magic = False  
has_strength = False

for col in columns:
    col_id, name, col_type, notnull, default, pk = col
    if name == 'ticket':
        has_ticket = True
        print(f"  [OK] ticket existe: {col_type}")
    elif name == 'magic_number':
        has_magic = True
        print(f"  [OK] magic_number existe: {col_type}")
    elif name == 'strength':
        has_strength = True
        print(f"  [OK] strength existe: {col_type}")

if not has_ticket:
    print(f"  [ERRO] Coluna 'ticket' NAO encontrada!")
if not has_magic:
    print(f"  [ERRO] Coluna 'magic_number' NAO encontrada!")
if not has_strength:
    print(f"  [ERRO] Coluna 'strength' NAO encontrada!")

# Verificar dados
print("\n[2] ULTIMOS 5 TRADES:")
print("-"*70)
cursor.execute("""
    SELECT id, ticket, magic_number, strength, status, 
           substr(timestamp, 1, 19) as time
    FROM trades 
    ORDER BY id DESC 
    LIMIT 5;
""")

trades = cursor.fetchall()
if trades:
    print(f"{'ID':>6} | {'Ticket':>10} | {'Magic':>6} | {'Strength':>10} | Status")
    print("-"*70)
    for trade in trades:
        trade_id, ticket, magic, strength, status, time = trade
        ticket_str = str(ticket) if ticket else "NULL"
        magic_str = str(magic) if magic else "NULL"
        strength_str = strength if strength else "NULL"
        print(f"{trade_id:>6} | {ticket_str:>10} | {magic_str:>6} | {strength_str:>10} | {status}")
else:
    print("  Nenhum trade encontrado")

# Verificar se novos trades terão dados
print("\n[3] ESTATISTICAS:")
print("-"*70)

cursor.execute("SELECT COUNT(*) FROM trades WHERE ticket IS NOT NULL;")
with_ticket = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM trades WHERE magic_number IS NOT NULL;")
with_magic = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM trades WHERE strength IS NOT NULL;")
with_strength = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM trades;")
total = cursor.fetchone()[0]

print(f"  Total de trades: {total}")
print(f"  Com ticket: {with_ticket} ({with_ticket/total*100:.1f}%)")
print(f"  Com magic_number: {with_magic} ({with_magic/total*100:.1f}%)")
print(f"  Com strength: {with_strength} ({with_strength/total*100:.1f}%)")

conn.close()

print("\n" + "="*70)
print("RESULTADO:")
print("="*70)

if has_ticket and has_magic and has_strength:
    print("[OK] Todas as colunas existem!")
    if with_ticket > 0 and with_magic > 0 and with_strength > 0:
        print("[OK] Dados estao sendo preenchidos!")
    else:
        print("[AVISO] Colunas existem mas trades antigos nao tem dados")
        print("        Novos trades terao os dados preenchidos")
else:
    print("[ERRO] Algumas colunas faltando - executar migracao")

print("\n" + "="*70)
