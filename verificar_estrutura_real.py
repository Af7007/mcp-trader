#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura real do banco de dados
"""

import sqlite3

def verificar_estrutura_real():
    """Verifica a estrutura real do banco"""
    
    print("VERIFICANDO ESTRUTURA REAL DO BANCO")
    print("=" * 50)
    
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    
    try:
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"\n=== TABELA: {nome_tabela} ===")
            
            # Estrutura da tabela
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = cursor.fetchall()
            print("Colunas:")
            for col in colunas:
                print(f"  - {col[1]} ({col[2]})")
            
            # Alguns dados de exemplo
            cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
            dados = cursor.fetchall()
            
            if dados:
                print(f"\nPrimeiros {len(dados)} registros:")
                for i, linha in enumerate(dados):
                    print(f"  {i+1}: {linha}")
            
            # Contar registros por status
            if nome_tabela == 'trades':
                cursor.execute("SELECT status, COUNT(*) FROM trades GROUP BY status")
                status_counts = cursor.fetchall()
                print("\nContagem por status:")
                for status, count in status_counts:
                    print(f"  {status}: {count}")
                
                # Verificar símbolos únicos
                cursor.execute("SELECT DISTINCT symbol FROM trades")
                simbolos = cursor.fetchall()
                print(f"\nSímbolos encontrados: {[s[0] for s in simbolos]}")
                
                # Verificar se há dados de XAU
                cursor.execute("SELECT COUNT(*) FROM trades WHERE symbol LIKE '%XAU%'")
                count_xau = cursor.fetchone()[0]
                print(f"Trades XAU encontrados: {count_xau}")
    
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_estrutura_real()
