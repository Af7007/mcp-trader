#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura do banco de dados de trading
"""

import sqlite3
import pandas as pd

def verificar_banco():
    """Verifica a estrutura do banco de dados"""
    
    print("VERIFICANDO ESTRUTURA DO BANCO DE DADOS")
    print("=" * 50)
    
    conn = sqlite3.connect('trading.db')
    
    try:
        # Listar todas as tabelas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"[INFO] Tabelas encontradas: {len(tabelas)}")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        print()
        
        # Para cada tabela, mostrar estrutura e alguns dados
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"=== TABELA: {nome_tabela} ===")
            
            # Estrutura da tabela
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = cursor.fetchall()
            print("Colunas:")
            for col in colunas:
                print(f"  - {col[1]} ({col[2]})")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            total = cursor.fetchone()[0]
            print(f"Total de registros: {total}")
            
            # Mostrar alguns dados se existirem
            if total > 0:
                cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
                dados = cursor.fetchall()
                print("Primeiros registros:")
                for i, linha in enumerate(dados):
                    print(f"  {i+1}: {linha}")
            
            print()
    
    except Exception as e:
        print(f"[ERRO] Erro ao verificar banco: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_banco()
