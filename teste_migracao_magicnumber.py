#!/usr/bin/env python3
"""
Script de teste para adicionar coluna magicnumber ao banco de dados
"""

import sqlite3
import sys
import os
from pathlib import Path

def test_migration():
    """Testa a migração do banco de dados para adicionar magicnumber"""
    
    databases = [
        ('btc_trading_logs.db', 'Banco BTC principal'),
        ('trading_bot.db', 'Banco trading_bot'),
        ('trading.db', 'Banco trading')
    ]
    
    for db_file, description in databases:
        if Path(db_file).exists():
            print(f"\n{'='*60}")
            print(f"TESTANDO MIGRAÇÃO: {description} - {db_file}")
            print('='*60)
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar todas as tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if not tables:
                    print(f"   Nenhuma tabela encontrada em {db_file}")
                    conn.close()
                    continue
                
                for table_name in tables:
                    table = table_name[0]
                    print(f"\n   PROCESSANDO TABELA: {table}")
                    print("   " + "-"*50)
                    
                    # Verificar estrutura atual
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    print(f"   Colunas atuais: {column_names}")
                    
                    # Verificar se a tabela tem trades ou posições que precisam de magicnumber
                    needs_magic = False
                    
                    # Para tabela trades
                    if table.lower() == 'trades':
                        needs_magic = True
                        print("   → Tabela 'trades' identificada - precisa de magicnumber")
                    
                    # Para tabelas que contêm ticket e símbolo
                    elif 'ticket' in column_names and 'symbol' in column_names:
                        needs_magic = True
                        print("   → Tabela com ticket/symbol - precisa de magicnumber")
                    
                    # Para tabela game_history (já tem magic_number)
                    elif 'magic_number' in column_names:
                        print("   → Já possui coluna magic_number")
                        continue
                    
                    if needs_magic:
                        # Verificar se magic_number já existe
                        if 'magic_number' not in column_names:
                            try:
                                # Adicionar coluna magic_number
                                cursor.execute(f"ALTER TABLE {table} ADD COLUMN magic_number INTEGER")
                                print(f"   ✓ Coluna magic_number adicionada à tabela {table}")
                                
                                # Se a tabela tem dados, definir valores padrão
                                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                                row_count = cursor.fetchone()[0]
                                
                                if row_count > 0:
                                    # Definir um magic number padrão baseado no tipo de operação
                                    if table.lower() == 'trades' or 'trade' in table.lower():
                                        cursor.execute(f"UPDATE {table} SET magic_number = 777777 WHERE magic_number IS NULL")
                                        print(f"   ✓ Magic number 777777 definido para {row_count} trades existentes")
                                    else:
                                        cursor.execute(f"UPDATE {table} SET magic_number = 888888 WHERE magic_number IS NULL")
                                        print(f"   ✓ Magic number 888888 definido para {row_count} registros existentes")
                                
                            except sqlite3.Error as e:
                                print(f"   ✗ Erro ao adicionar magic_number: {e}")
                        else:
                            print(f"   ✓ Coluna magic_number já existe na tabela {table}")
                    
                    # Verificar se a migração foi bem-sucedida
                    cursor.execute(f"PRAGMA table_info({table})")
                    new_columns = cursor.fetchall()
                    new_column_names = [col[1] for col in new_columns]
                    
                    if 'magic_number' in new_column_names:
                        print(f"   ✓ Migração concluída para tabela {table}")
                    else:
                        print(f"   ✗ Migração falhou para tabela {table}")
                
                conn.commit()
                conn.close()
                print(f"   Migração concluída para {db_file}")
                
            except Exception as e:
                print(f"   Erro ao processar {db_file}: {e}")
        else:
            print(f"\n{'='*60}")
            print(f"ARQUIVO NÃO ENCONTRADO: {description} - {db_file}")
            print('='*60)


def create_test_trade_with_magic():
    """Cria um trade de teste com magicnumber"""
    try:
        print(f"\n{'='*60}")
        print("TESTANDO CRIAÇÃO DE TRADE COM MAGICNUMBER")
        print('='*60)
        
        # Tentar usar o banco trading_bot.db para teste
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # Verificar se a coluna magic_number existe
        cursor.execute("PRAGMA table_info(trades)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'magic_number' not in column_names:
            print("   Adicionando coluna magic_number ao banco de teste...")
            cursor.execute("ALTER TABLE trades ADD COLUMN magic_number INTEGER")
        
        # Inserir um trade de teste
        test_trade_data = (
            99999,  # ticket
            123456,  # magic_number
            'BTCUSDc',  # symbol
            'BUY',  # type
            0.02,  # volume
            45000.0,  # open_price
            44900.0,  # sl
            45200.0,  # tp
            'Teste MagicNumber',  # comment
            'open'  # status
        )
        
        cursor.execute("""
            INSERT OR REPLACE INTO trades 
            (ticket, magic_number, symbol, type, volume, open_price, sl, tp, comment, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_trade_data)
        
        # Verificar se foi inserido
        cursor.execute("SELECT * FROM trades WHERE ticket = ?", (99999,))
        result = cursor.fetchone()
        
        if result:
            print("   ✓ Trade de teste criado com sucesso:")
            print(f"     Ticket: {result[1]}")
            print(f"     MagicNumber: {result[2]}")
            print(f"     Symbol: {result[3]}")
            print(f"     Type: {result[4]}")
        else:
            print("   ✗ Erro ao criar trade de teste")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"   Erro no teste: {e}")


def query_trades_by_magic():
    """Testa a consulta de trades por magicnumber"""
    try:
        print(f"\n{'='*60}")
        print("TESTANDO CONSULTA POR MAGICNUMBER")
        print('='*60)
        
        # Tentar diferentes bancos
        databases = ['trading_bot.db', 'btc_trading_logs.db', 'trading.db']
        
        for db_name in databases:
            if Path(db_name).exists():
                print(f"\n   Verificando {db_name}...")
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                
                # Verificar se a tabela tem a coluna magic_number
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_info in tables:
                    table_name = table_info[0]
                    if table_name.lower() in ['trades', 'game_history']:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                        
                        if 'magic_number' in column_names:
                            # Contar registros com magic_number
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE magic_number IS NOT NULL")
                            count = cursor.fetchone()[0]
                            print(f"     → Tabela {table_name}: {count} registros com magic_number")
                            
                            # Mostrar alguns exemplos
                            cursor.execute(f"SELECT ticket, magic_number, symbol, type FROM {table_name} WHERE magic_number IS NOT NULL LIMIT 3")
                            examples = cursor.fetchall()
                            
                            for example in examples:
                                ticket, magic, symbol, trade_type = example
                                print(f"       Ticket: {ticket}, Magic: {magic}, Symbol: {symbol}, Type: {trade_type}")
                
                conn.close()
    
    except Exception as e:
        print(f"   Erro na consulta: {e}")


if __name__ == "__main__":
    print("INICIANDO TESTE DE MIGRAÇÃO DO MAGICNUMBER")
    print("="*60)
    
    # Executar testes
    test_migration()
    create_test_trade_with_magic()
    query_trades_by_magic()
    
    print(f"\n{'='*60}")
    print("TESTES CONCLUÍDOS")
    print('='*60)
