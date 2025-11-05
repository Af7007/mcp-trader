#!/usr/bin/env python3
"""Lista todos os bancos de dados encontrados"""
import os

dbs = ['trading.db', 'btc_trading_logs.db', 'btc_trading.db', 'trading_bot.db']

print("="*60)
print("BANCOS DE DADOS ENCONTRADOS")
print("="*60)

for db in dbs:
    status = "EXISTE" if os.path.exists(db) else "NAO EXISTE"
    print(f"  {db}: {status}")
    if os.path.exists(db):
        size = os.path.getsize(db)
        print(f"    Tamanho: {size:,} bytes ({size/1024:.1f} KB)")

print("\n" + "="*60)
print("RECOMENDACAO: Usar apenas btc_trading_logs.db")
print("="*60)
