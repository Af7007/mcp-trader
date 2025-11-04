#!/usr/bin/env python3
"""
VERIFICAÇÃO DE DADOS NO BANCO DE DADOS
Verifica se os agentes estão armazenando dados de trades
"""

import sqlite3
import os
from pathlib import Path

def verificar_banco(db_path):
    """Verifica dados no banco de dados"""
    if not os.path.exists(db_path):
        print(f"ERRO: Banco {db_path} não encontrado")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()

        print(f"\nBANCO: {db_path}")
        print(f"Tabelas encontradas: {[t[0] for t in tabelas]}")

        # Verificar dados em cada tabela
        for tabela in tabelas:
            nome_tabela = tabela[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
                count = cursor.fetchone()[0]
                print(f"   {nome_tabela}: {count} registros")

                # Mostrar estrutura da tabela
                cursor.execute(f"PRAGMA table_info({nome_tabela})")
                colunas = cursor.fetchall()
                print(f"   Colunas: {[col[1] for col in colunas]}")

                # Mostrar alguns registros se houver
                if count > 0:
                    cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
                    registros = cursor.fetchall()
                    print(f"   Amostra: {registros[:1]}")

            except Exception as e:
                print(f"   ERRO na tabela {nome_tabela}: {e}")

        conn.close()

    except Exception as e:
        print(f"ERRO ao acessar {db_path}: {e}")

def main():
    """Verifica todos os bancos de dados"""
    print("VERIFICACAO DE DADOS NOS BANCOS DE DADOS")
    print("=" * 60)

    bancos = [
        'trading.db',
        'btc_trading_logs.db',
        'trading_bot.db'
    ]

    for banco in bancos:
        verificar_banco(banco)

    print("\n" + "=" * 60)
    print("VERIFICACAO CONCLUIDA")

if __name__ == "__main__":
    main()
