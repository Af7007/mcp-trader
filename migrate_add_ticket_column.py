#!/usr/bin/env python3
"""
Adiciona coluna ticket na tabela trades existente
"""

import sqlite3

db_path = "btc_trading_logs.db"

print("="*70)
print("MIGRACAO: Adicionar coluna 'ticket' na tabela trades")
print("="*70)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar se coluna já existe
cursor.execute("PRAGMA table_info(trades);")
columns = [col[1] for col in cursor.fetchall()]

if 'ticket' in columns:
    print("\n[OK] Coluna 'ticket' já existe!")
else:
    print("\n[EXECUTANDO] Adicionando coluna 'ticket'...")
    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN ticket INTEGER;")
        conn.commit()
        print("[OK] Coluna 'ticket' adicionada com sucesso!")
    except Exception as e:
        print(f"[ERRO] Falha ao adicionar coluna: {e}")

# Verificar novamente
cursor.execute("PRAGMA table_info(trades);")
columns_after = {col[1]: col[2] for col in cursor.fetchall()}

print("\n" + "="*70)
print("COLUNAS NA TABELA TRADES:")
print("="*70)

for col_name in ['ticket', 'magic_number', 'strength']:
    if col_name in columns_after:
        print(f"  [OK] {col_name:20s} {columns_after[col_name]}")
    else:
        print(f"  [ERRO] {col_name:20s} NAO EXISTE")

conn.close()

print("\n" + "="*70)
print("MIGRACAO CONCLUIDA!")
print("="*70)
