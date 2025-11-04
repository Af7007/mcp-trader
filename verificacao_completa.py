import sqlite3

def verificar_todos_bancos():
    """Verifica o status do magicnumber em todos os bancos"""
    
    databases = [
        ('btc_trading_logs.db', 'Banco BTC principal'),
        ('trading_bot.db', 'Banco trading_bot'),
        ('trading.db', 'Banco trading')
    ]
    
    for db_file, description in databases:
        if Path(db_file).exists():
            print(f"\n{'='*60}")
            print(f"VERIFICANDO: {description} - {db_file}")
            print('='*60)
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar todas as tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name in tables:
                    table = table_name[0]
                    
                    # Verificar estrutura da tabela
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'magic_number' in column_names:
                        print(f"  TABELA {table}:")
                        
                        # Contar registros
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        total_count = cursor.fetchone()[0]
                        
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE magic_number IS NOT NULL")
                        magic_count = cursor.fetchone()[0]
                        
                        print(f"    Total registros: {total_count}")
                        print(f"    Com magic_number: {magic_count}")
                        print(f"    Percentual: {(magic_count/total_count*100):.1f}%")
                        
                        # Verificar stop loss se existir
                        sl_columns = [col for col in column_names if 'sl' in col.lower()]
                        if sl_columns:
                            for sl_col in sl_columns:
                                cursor.execute(f"SELECT MIN({sl_col}), MAX({sl_col}), AVG({sl_col}) FROM {table} WHERE {sl_col} IS NOT NULL")
                                sl_stats = cursor.fetchone()
                                min_sl, max_sl, avg_sl = sl_stats
                                
                                print(f"    Stop Loss ({sl_col}):")
                                print(f"      Min: ${min_sl:.2f}, Max: ${max_sl:.2f}, Avg: ${avg_sl:.2f}")
                                
                                # Verificar valores baixos
                                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {sl_col} > 0 AND {sl_col} < 1")
                                low_sl_count = cursor.fetchone()[0]
                                
                                if low_sl_count > 0:
                                    print(f"      *** ATENCAO: {low_sl_count} registros com SL < $1.0 ***")
                    
                conn.close()
                
            except Exception as e:
                print(f"  Erro ao processar {db_file}: {e}")

if __name__ == "__main__":
    print("VERIFICACAO COMPLETA - MAGICNUMBER E STOP LOSS")
    print("="*60)
    verificar_todos_bancos()
    print(f"\n{'='*60}")
    print("VERIFICACAO CONCLUIDA")
    print('='*60)
