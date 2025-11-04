#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar o schema do banco de dados e adicionar coluna magicnumber
"""

import sqlite3
from pathlib import Path

def analyze_database_schema():
    """Analisa o schema completo dos bancos de dados existentes"""
    
    databases = [
        ('btc_trading_logs.db', 'Banco BTC principal'),
        ('trading_bot.db', 'Banco trading_bot'),
        ('trading.db', 'Banco trading'),
        ('src/trading_system.db', 'Banco sistema')
    ]
    
    for db_file, description in databases:
        if Path(db_file).exists():
            print(f"\n{'='*60}")
            print(f"ANALISE: {description} - {db_file}")
            print('='*60)
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar todas as tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if not tables:
                    print("   Nenhuma tabela encontrada")
                    continue
                
                for table_name in tables:
                    table = table_name[0]
                    print(f"\n   TABELA: {table}")
                    print("   " + "-"*50)
                    
                    # Obter schema da tabela
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    for col in columns:
                        cid, name, data_type, not_null, default, primary_key = col
                        pk_indicator = " (PK)" if primary_key else ""
                        null_indicator = " NOT NULL" if not_null else ""
                        default_indicator = f" DEFAULT {default}" if default else ""
                        print(f"      {name:15} {data_type:10}{null_indicator}{default_indicator}{pk_indicator}")
                    
                    # Mostrar algumas linhas de exemplo
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    sample_rows = cursor.fetchall()
                    
                    if sample_rows:
                        print("   DADOS DE EXEMPLO:")
                        for i, row in enumerate(sample_rows, 1):
                            print(f"      Linha {i}: {row}")
                
                conn.close()
                
            except Exception as e:
                print(f"   Erro ao analisar {db_file}: {e}")
        else:
            print(f"\n{'='*60}")
            print(f"NAO ENCONTRADO: {description} - {db_file}")
            print('='*60)

if __name__ == "__main__":
    analyze_database_schema()
