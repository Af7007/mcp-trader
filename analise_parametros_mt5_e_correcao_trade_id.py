#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TABELA DE PARÂMETROS CORRETOS DO MT5
=====================================
Este script obtém TODOS os parâmetros corretos do MT5 para o símbolo XAUUSDc
e cria uma tabela completa de referência para cálculos precisos.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import sqlite3
import os

def obter_parametros_completos_mt5():
    """Obtém todos os parâmetros corretos do MT5 para XAUUSDc"""
    
    print("🔍 OBTENDO PARÂMETROS COMPLETOS DO MT5")
    print("=" * 60)
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"[ERRO] Falha ao inicializar MT5: {mt5.last_error()}")
        return None
        
    print("[✅] MT5 inicializado com sucesso")
    
    # Obter informações do símbolo XAUUSDc
    symbol_info = mt5.symbol_info("XAUUSDc")
    
    if symbol_info is None:
        print("[❌] Símbolo XAUUSDc não encontrado")
        mt5.shutdown()
        return None
        
    print(f"[✅] Símbolo XAUUSDc encontrado")
    
    # Obter informações detalhadas do símbolo
    symbol_info_tick = mt5.symbol_info_tick("XAUUSDc")
    
    print("\n" + "=" * 60)
    print("📊 TABELA DE PARÂMETROS CORRETOS DO MT5")
    print("=" * 60)
    
    # Tabela 1: Parâmetros Básicos do Símbolo
    print("\n🏷️  PARÂMETROS BÁSICOS DO SÍMBOLO")
    print("-" * 50)
    
    parametros_basicos = {
        'Parâmetro': [
            'Símbolo', 'Descrição', 'Moeda Base', 'Moeda Lucro', 
            'Moeda Margem', 'Dígitos', 'Spread Atual', 
            'Spread em Pontos', 'Nível de Stop', 'StopLevel',
            'FreezeLevel', 'Volume Mínimo', 'Volume Máximo',
            'Volume Step', 'Margem Inicial', 'Margem de Manutenção'
        ],
        'Valor': [
            symbol_info.name,
            symbol_info.description,
            symbol_info.currency_base,
            symbol_info.currency_profit,
            symbol_info.currency_margin,
            symbol_info.digits,
            symbol_info.spread,
            symbol_info.spread * 10,  # converter para pontos
            symbol_info.trade_mode,
            symbol_info.trade_stops_level,
            symbol_info.trade_freeze_level,
            symbol_info.volume_min,
            symbol_info.volume_max,
            symbol_info.volume_step,
            symbol_info.margin_initial,
            symbol_info.margin_maintenance
        ],
        'Unidade': [
            '-', '-', '-', '-', '-', 'decimais', 'pontos', 
            'pontos', '-', 'pontos', 'pontos', 'lotes', 
            'lotes', 'lotes', '-', '-'
        ],
        'Importante Para': [
            'Identificação', '-', 'Cálculos', 'Cálculos', 
            'Cálculos', 'Precisão', 'Custo', 'Custo',
            'Ordem', 'SL/TP', 'Execução', 'Volume', 
            'Volume', 'Volume', 'Margem', 'Margem'
        ]
    }
    
    df_basicos = pd.DataFrame(parametros_basicos)
    print(df_basicos.to_string(index=False))
    
    # Tabela 2: Cálculos de Precisão
    print("\n🎯 CÁLCULOS DE PRECISÃO")
    print("-" * 50)
    
    calculos = {
        'Cálculo': [
            'Preço ASK (atual)', 'Preço BID (atual)', 'Spread em USD',
            'Spread em pontos', 'Distância mínima SL/TP', 'Valor por ponto',
            'Custo do spread por lote', 'Margem requerida por lote'
        ],
        'Fórmula': [
            f'{symbol_info_tick.ask:.3f}',
            f'{symbol_info_tick.bid:.3f}',
            f'(Ask - Bid)',
            f'{symbol_info.spread} pts',
            f'{symbol_info.trade_stops_level} pts',
            f'{symbol_info.digits} casas decimais',
            f'{symbol_info.spread * 10} * $1',
            f'Margem atual calculada'
        ],
        'Resultado': [
            f'${symbol_info_tick.ask:.3f}',
            f'${symbol_info_tick.bid:.3f}',
            f'${(symbol_info_tick.ask - symbol_info_tick.bid):.3f}',
            f'{symbol_info.spread} pontos',
            f'{symbol_info.trade_stops_level / 10:.2f} USD',
            f'Precisão: 10^{-symbol_info.digits}',
            f'${symbol_info.spread * 10 * 0.01:.2f}',
            f'${symbol_info.margin_initial:.2f}'
        ],
        'Observação': [
            'Preço de compra', 'Preço de venda', 'Spread real atual',
            'Spread oficial do símbolo', 'Distância mínima obrigatória',
            'Precisão dos preços', 'Custo fixo por trade', 'Margem por lote'
        ]
    }
    
    df_calculos = pd.DataFrame(calculos)
    print(df_calculos.to_string(index=False))
    
    # Tabela 3: Parâmetros para Trailing Stop
    print("\n📈 PARÂMETROS PARA TRAILING STOP")
    print("-" * 50)
    
    trailing_params = {
        'Parâmetro': [
            'Distância Mínima SL', 'Precisão do Preço', 'Valor por Ponto',
            'Distância Mínima SL (USD)', 'Passo Mínimo SL', 
            'Atualização SL Permitida', 'Margem de Segurança'
        ],
        'Valor MT5': [
            f'{symbol_info.trade_stops_level} pts',
            f'{symbol_info.digits} casas',
            f'${symbol_info.spread * 0.01:.2f}',
            f'${symbol_info.trade_stops_level / 10:.2f}',
            '0.1 pts',
            'Sim',
            '2 pts'
        ],
        'Recomendação': [
            'Usar MÍNIMO este valor',
            'Arredondar para esta precisão',
            'Calcular P&L corretamente',
            'SL deve ser >= este valor',
            'Incrementos de 0.1 pts',
            'Verificar antes de modificar',
            'Adicionar ao StopLevel'
        ],
        'Uso no Código': [
            'sl_distance = max(calculated_sl, stop_level)',
            'round(price, digits)',
            'point_value * points',
            'validation_check',
            'trailing_step',
            'before modify position',
            'safety_margin'
        ]
    }
    
    df_trailing = pd.DataFrame(trailing_params)
    print(df_trailing.to_string(index=False))
    
    # Tabela 4: Fórmulas de Conversão
    print("\n🧮 FÓRMULAS DE CONVERSÃO")
    print("-" * 50)
    
    formulas = {
        'Conversão': [
            'Pontos → USD', 'USD → Pontos', 'Spread USD → Pontos',
            'Volume → Lotes', 'P&L USD → Pontos', 'Margem % → USD'
        ],
        'Fórmula': [
            'points / 10',
            'usd * 10',
            'spread_usd * 10 / 0.01',
            'volume / symbol_info.volume_step',
            'pnl_usd / (volume * 0.01)',
            'balance * margin_percent / 100'
        ],
        'Exemplo com XAUUSDc': [
            f'{symbol_info.spread} pts = ${symbol_info.spread / 10:.2f}',
            f'$1.00 = 10 pts',
            f'${(symbol_info_tick.ask - symbol_info_tick.bid):.3f} = {symbol_info.spread} pts',
            '0.01 / 0.01 = 1 lote',
            f'$1.00 = 100 pts (para 0.01 lotes)',
            'Com $1000 e 1% = $10'
        ]
    }
    
    df_formulas = pd.DataFrame(formulas)
    print(df_formulas.to_string(index=False))
    
    # Salvar em arquivo CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'tabela_parametros_mt5_xauusdc_{timestamp}.csv'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("TABELA DE PARÂMETROS CORRETOS DO MT5 - XAUUSDc\n")
        f.write(f"Gerado em: {datetime.now()}\n\n")
        
        f.write("PARÂMETROS BÁSICOS:\n")
        f.write(df_basicos.to_csv(index=False))
        f.write("\nCÁLCULOS DE PRECISÃO:\n")
        f.write(df_calculos.to_csv(index=False))
        f.write("\nPARÂMETROS PARA TRAILING STOP:\n")
        f.write(df_trailing.to_csv(index=False))
        f.write("\nFÓRMULAS DE CONVERSÃO:\n")
        f.write(df_formulas.to_csv(index=False))
    
    print(f"\n💾 Tabelas salvas em: {filename}")
    
    # Retornar parâmetros importantes para uso
    parametros_importantes = {
        'symbol': symbol_info.name,
        'digits': symbol_info.digits,
        'spread': symbol_info.spread,
        'stop_level': symbol_info.trade_stops_level,
        'volume_min': symbol_info.volume_min,
        'volume_step': symbol_info.volume_step,
        'point': symbol_info.point,
        'trade_tick_value': symbol_info.trade_tick_value,
        'ask': symbol_info_tick.ask,
        'bid': symbol_info_tick.bid,
        'timestamp': datetime.now()
    }
    
    mt5.shutdown()
    print("\n✅ Análise completa finalizada!")
    
    return parametros_importantes

def verificar_banco_trailing():
    """Verifica o problema do trade_id no banco trailing_stops"""
    
    print("\n🔍 VERIFICANDO BANCO DE TRAILING STOPS")
    print("=" * 60)
    
    # Procurar arquivos de banco
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'trailing' in file.lower() and file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    
    print(f"📁 Bancos de dados encontrados: {len(db_files)}")
    for db_file in db_files:
        print(f"   - {db_file}")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   📋 Tabelas: {[t[0] for t in tables]}")
            
            # Verificar estrutura da tabela trailing_stops
            if any('trailing' in str(t).lower() for t in tables):
                for table in tables:
                    table_name = table[0]
                    if 'trailing' in table_name.lower():
                        print(f"   🔍 Estrutura da tabela '{table_name}':")
                        cursor.execute(f"PRAGMA table_info({table_name});")
                        columns = cursor.fetchall()
                        for col in columns:
                            print(f"      - {col[1]} ({col[2]})")
                        
                        # Verificar se existe trade_id
                        column_names = [col[1] for col in columns]
                        if 'trade_id' not in column_names:
                            print(f"      ⚠️  PROBLEMA: Coluna 'trade_id' NÃO existe!")
                        else:
                            print(f"      ✅ Coluna 'trade_id' existe")
                        
                        # Verificar registros
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                        count = cursor.fetchone()[0]
                        print(f"   📊 Total de registros: {count}")
                        
                        if count > 0:
                            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                            sample = cursor.fetchall()
                            print(f"   📝 Amostra de dados:")
                            for i, row in enumerate(sample, 1):
                                print(f"      Registro {i}: {row}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar {db_file}: {e}")

def corrigir_banco_trailing_stops():
    """Corrige o banco de trailing stops adicionando trade_id"""
    
    print("\n🔧 CORRIGINDO BANCO TRAILING_STOPS")
    print("=" * 50)
    
    # Procurar arquivo do banco
    db_file = None
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'trailing' in file.lower() and file.endswith('.db'):
                db_file = os.path.join(root, file)
                break
        if db_file:
            break
    
    if not db_file:
        print("❌ Arquivo de banco trailing_stops não encontrado")
        return False
    
    print(f"📁 Banco encontrado: {db_file}")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verificar estrutura atual
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_name = None
        for table in tables:
            if 'trailing' in table[0].lower():
                table_name = table[0]
                break
        
        if not table_name:
            print("❌ Tabela de trailing não encontrada")
            return False
        
        print(f"📋 Tabela encontrada: {table_name}")
        
        # Verificar se trade_id já existe
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'trade_id' not in column_names:
            print("➕ Adicionando coluna trade_id...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN trade_id TEXT;")
            print("✅ Coluna trade_id adicionada")
            
            # Atualizar registros existentes
            cursor.execute(f"""
                UPDATE {table_name} 
                SET trade_id = 'RECONSTRUIDO_' || datetime('now') || '_' || rowid
                WHERE trade_id IS NULL OR trade_id = '';
            """)
            
            print(f"✅ {cursor.rowcount} registros atualizados")
            
        else:
            print("✅ Coluna trade_id já existe")
        
        # Verificar registros sem trade_id válido
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name} 
            WHERE trade_id IS NULL OR trade_id = '' OR trade_id LIKE 'RECONSTRUIDO_%'
        """)
        sem_trade_id = cursor.fetchone()[0]
        
        if sem_trade_id > 0:
            print(f"🔄 Corrigindo {sem_trade_id} registros sem trade_id válido...")
            
            cursor.execute(f"""
                UPDATE {table_name} 
                SET trade_id = 'AUTO_' || datetime('now') || '_' || rowid
                WHERE trade_id IS NULL OR trade_id = '' OR trade_id LIKE 'RECONSTRUIDO_%'
            """)
            
            print(f"✅ {cursor.rowcount} registros corrigidos")
        
        # Criar índices para performance
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_trade_id ON {table_name}(trade_id);")
            print("✅ Índice trade_id criado")
        except:
            print("⚠️  Índice trade_id já existe")
        
        # Salvar alterações
        conn.commit()
        
        # Verificar resultado final
        cursor.execute(f"SELECT COUNT(*), COUNT(trade_id) FROM {table_name};")
        total, com_trade_id = cursor.fetchone()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Total de registros: {total}")
        print(f"   Com trade_id: {com_trade_id}")
        print(f"   Taxa de sucesso: {(com_trade_id/total*100):.1f}%")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        return False

def criar_funcao_corrigida():
    """Cria função corrigida para salvar trade_id"""
    
    print("\n💻 CRIANDO FUNÇÃO CORRIGIDA PARA TRAILING STOP")
    print("=" * 50)
    
    codigo_corrigido = '''# FUNÇÃO CORRIGIDA PARA SALVAR TRAILING STOP
def salvar_trailing_stop_com_trade_id(ticket, sl_price, trail_distance, db_path="trailing_stops.db"):
    """
    Salva trailing stop com trade_id correto
    """
    import sqlite3
    from datetime import datetime
    
    # Gerar trade_id único
    trade_id = f"T{ticket}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Inserir com trade_id
        cursor.execute("""
            INSERT OR REPLACE INTO trailing_stops 
            (ticket, trade_id, sl_price, trail_distance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ticket, 
            trade_id,
            sl_price, 
            trail_distance, 
            datetime.now(), 
            datetime.now()
        ))
        
        conn.commit()
        
        print(f"✅ Trailing salvo - Ticket: {ticket}, TradeID: {trade_id}")
        return trade_id
        
    except sqlite3.IntegrityError as e:
        # Se já existe, atualizar
        cursor.execute("""
            UPDATE trailing_stops 
            SET sl_price = ?, trail_distance = ?, updated_at = ?
            WHERE ticket = ?
        """, (sl_price, trail_distance, datetime.now(), ticket))
        
        # Recuperar trade_id existente
        cursor.execute("SELECT trade_id FROM trailing_stops WHERE ticket = ?", (ticket,))
        result = cursor.fetchone()
        trade_id = result[0] if result else f"T{ticket}_FALLBACK"
        
        conn.commit()
        print(f"🔄 Trailing atualizado - Ticket: {ticket}, TradeID: {trade_id}")
        return trade_id
        
    except Exception as e:
        print(f"❌ Erro ao salvar trailing: {e}")
        return None
        
    finally:
        conn.close()
'''
    
    with open('funcao_corrigida_trailing_stop.py', 'w', encoding='utf-8') as f:
        f.write(codigo_corrigido)
    
    print("💾 Função corrigida salva em: funcao_corrigida_trailing_stop.py")
    
    return True

if __name__ == "__main__":
    print("🚀 ANÁLISE COMPLETA DE PARÂMETROS MT5 E CORREÇÃO TRADE_ID")
    print("=" * 70)
    
    # 1. Obter parâmetros corretos do MT5
    parametros = obter_parametros_completos_mt5()
    
    if parametros:
        print("\n✅ Parâmetros MT5 obtidos com sucesso!")
        print(f"🎯 Parâmetros principais:")
        print(f"   - Stop Level: {parametros['stop_level']} pts ({parametros['stop_level']/10:.1f} USD)")
        print(f"   - Spread: {parametros['spread']} pts")
        print(f"   - Precisão: {parametros['digits']} casas decimais")
        print(f"   - Volume Min: {parametros['volume_min']} lotes")
    
    # 2. Verificar banco de trailing
    verificar_banco_trailing()
    
    # 3. Corrigir banco de trailing
    if corrigir_banco_trailing_stops():
        print("✅ Banco corrigido com sucesso")
    else:
        print("❌ Falha na correção do banco")
    
    # 4. Criar função corrigida
    if criar_funcao_corrigida():
        print("✅ Função corrigida criada com sucesso")
    else:
        print("❌ Falha na criação da função corrigida")
    
    print("\n🎉 ANÁLISE E CORREÇÃO CONCLUÍDAS!")
    print("=" * 70)
