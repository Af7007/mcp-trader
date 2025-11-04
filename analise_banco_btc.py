#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise do Banco de Dados BTC Logger
Verifica dados coletados e performance do agente
"""

import sys
from pathlib import Path
import sqlite3

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.btc_logger import BTCLogger


def analisar_banco_dados():
    """
    Analisa completo o banco de dados BTC
    """
    print('ANALISE COMPLETA DO BANCO DE DADOS BTC')
    print('=' * 60)
    
    # Conectar ao banco
    logger = BTCLogger()
    conn = sqlite3.connect(logger.db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar tabelas
        print('\nTABELAS DO BANCO:')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f'   - {table[0]}')
        
        # 2. Analisar ciclos
        print('\nANALISE DE CICLOS:')
        try:
            cursor.execute('SELECT COUNT(*) FROM cycles')
            total_cycles = cursor.fetchone()[0]
            print(f'   Total de Ciclos: {total_cycles}')
            
            if total_cycles > 0:
                cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM cycles')
                min_time, max_time = cursor.fetchone()
                print(f'   Período: {min_time} até {max_time}')
                
                cursor.execute('SELECT symbol, COUNT(*) FROM cycles GROUP BY symbol')
                symbols = cursor.fetchall()
                print(f'   Símbolos: {symbols}')
                
                # Estatísticas de preços
                cursor.execute('SELECT MIN(price), MAX(price), AVG(price) FROM cycles WHERE price IS NOT NULL')
                price_stats = cursor.fetchone()
                if price_stats[0]:
                    print(f'   Preços - Min: ${price_stats[0]:.2f}, Max: ${price_stats[1]:.2f}, Média: ${price_stats[2]:.2f}')
                
                # Últimos ciclos com sinais
                cursor.execute('''
                    SELECT cycle_number, timestamp, symbol, price, signal_type, signal_strength, signal_reason 
                    FROM cycles 
                    WHERE signal_type IS NOT NULL 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''')
                recent_signals = cursor.fetchall()
                print(f'   Últimos 10 ciclos COM SINAIS:')
                for cycle in recent_signals:
                    print(f'      Ciclo #{cycle[0]}: {cycle[1]} - ${cycle[3]:.2f} - {cycle[4]} ({cycle[5]})')
                
                # Contagem de sinais por tipo
                cursor.execute('SELECT signal_type, COUNT(*) FROM cycles WHERE signal_type IS NOT NULL GROUP BY signal_type')
                signal_types = cursor.fetchall()
                print(f'   Sinais por tipo: {signal_types}')
                
                # Contagem por força
                cursor.execute('SELECT signal_strength, COUNT(*) FROM cycles WHERE signal_strength IS NOT NULL GROUP BY signal_strength')
                signal_strengths = cursor.fetchall()
                print(f'   Sinais por força: {signal_strengths}')
                
        except Exception as e:
            print(f'   Erro ao analisar ciclos: {e}')
        
        # 3. Analisar trades
        print('\nANALISE DE TRADES:')
        try:
            cursor.execute('SELECT COUNT(*) FROM trades')
            total_trades = cursor.fetchone()[0]
            print(f'   Total de Trades: {total_trades}')
            
            if total_trades > 0:
                cursor.execute('SELECT trade_type, COUNT(*) FROM trades GROUP BY trade_type')
                trade_types = cursor.fetchall()
                print(f'   Trades por tipo: {trade_types}')
                
                cursor.execute('SELECT status, COUNT(*) FROM trades GROUP BY status')
                status = cursor.fetchall()
                print(f'   Status dos trades: {status}')
                
                cursor.execute('SELECT agent_version, COUNT(*) FROM trades GROUP BY agent_version')
                versions = cursor.fetchall()
                print(f'   Trades por versão: {versions}')
                
                # Trades recentes
                cursor.execute('''
                    SELECT timestamp, trade_type, entry_price, sl_price, tp_price, status, reason, agent_version
                    FROM trades 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ''')
                recent_trades = cursor.fetchall()
                print(f'   Últimos 5 trades:')
                for trade in recent_trades:
                    print(f'      {trade[0]}: {trade[1]} ${trade[2]:.2f} - {trade[5]} ({trade[6]})')
                
                # Estatísticas de preços de trades
                cursor.execute('SELECT AVG(entry_price), MIN(entry_price), MAX(entry_price) FROM trades WHERE entry_price IS NOT NULL')
                trade_price_stats = cursor.fetchone()
                if trade_price_stats[0]:
                    print(f'   Preços de Entrada - Média: ${trade_price_stats[0]:.2f}, Min: ${trade_price_stats[1]:.2f}, Max: ${trade_price_stats[2]:.2f}')
                
        except Exception as e:
            print(f'   Erro ao analisar trades: {e}')
        
        # 4. Analisar performance de estratégias
        print('\nANALISE DE PERFORMANCE DE ESTRATEGIAS:')
        try:
            cursor.execute('SELECT COUNT(*) FROM strategy_performance')
            total_perf = cursor.fetchone()[0]
            print(f'   Total de Registros: {total_perf}')
            
            if total_perf > 0:
                # Top estratégias por número de sinais
                cursor.execute('''
                    SELECT strategy_name, SUM(total_signals) as total_sinais, SUM(successful_trades) as total_sucessos
                    FROM strategy_performance 
                    GROUP BY strategy_name 
                    ORDER BY total_sinais DESC 
                    LIMIT 10
                ''')
                top_strategies = cursor.fetchall()
                print(f'   Top 10 estratégias por sinais:')
                for strategy in top_strategies:
                    success_rate = (strategy[2] / strategy[1] * 100) if strategy[1] > 0 else 0
                    print(f'      {strategy[0]}: {strategy[1]} sinais, {strategy[2]} sucessos ({success_rate:.1f}%)')
                
                # Performance por tipo de sinal
                cursor.execute('''
                    SELECT signal_type, SUM(total_signals) as total_sinais, SUM(successful_trades) as total_sucessos
                    FROM strategy_performance 
                    GROUP BY signal_type 
                    ORDER BY total_sinais DESC
                ''')
                perf_by_type = cursor.fetchall()
                print(f'   Performance por tipo de sinal:')
                for perf in perf_by_type:
                    success_rate = (perf[2] / perf[1] * 100) if perf[1] > 0 else 0
                    print(f'      {perf[0]}: {perf[1]} sinais, {perf[2]} sucessos ({success_rate:.1f}%)')
                
                # Performance por força
                cursor.execute('''
                    SELECT signal_strength, SUM(total_signals) as total_sinais, SUM(successful_trades) as total_sucessos
                    FROM strategy_performance 
                    GROUP BY signal_strength 
                    ORDER BY total_sinais DESC
                ''')
                perf_by_strength = cursor.fetchall()
                print(f'   Performance por força:')
                for perf in perf_by_strength:
                    success_rate = (perf[2] / perf[1] * 100) if perf[1] > 0 else 0
                    print(f'      {perf[0]}: {perf[1]} sinais, {perf[2]} sucessos ({success_rate:.1f}%)')
                
        except Exception as e:
            print(f'   Erro ao analisar performance: {e}')
        
        # 5. Verificar erros recentes
        print('\nANALISE DE ERROS:')
        try:
            # Ciclos com erros
            cursor.execute('SELECT COUNT(*) FROM cycles WHERE order_result IS NOT NULL AND order_result != "10009"')
            error_cycles = cursor.fetchone()[0]
            print(f'   Ciclos com erros: {error_cycles}')
            
            if error_cycles > 0:
                cursor.execute('''
                    SELECT cycle_number, timestamp, order_result, order_error 
                    FROM cycles 
                    WHERE order_result IS NOT NULL AND order_result != "10009" 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ''')
                recent_errors = cursor.fetchall()
                print(f'   Erros recentes:')
                for error in recent_errors:
                    print(f'      Ciclo #{error[0]}: {error[1]} - {error[2]} ({error[3]})')
            
            # Trades com falha
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status != "OPEN" AND status != "CLOSED"')
            failed_trades = cursor.fetchone()[0]
            print(f'   Trades com falha: {failed_trades}')
            
        except Exception as e:
            print(f'   Erro ao analisar falhas: {e}')
        
        # 6. Resumo geral
        print('\nRESUMO GERAL:')
        try:
            cursor.execute('SELECT COUNT(*) FROM cycles')
            cycles = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL')
            signals = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trades')
            trades = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "OPEN"')
            open_trades = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM strategy_performance')
            perf_records = cursor.fetchone()[0]
            
            print(f'   Total de Ciclos: {cycles}')
            print(f'   Ciclos com Sinais: {signals} ({(signals/cycles*100):.1f}% dos ciclos)')
            print(f'   Total de Trades: {trades}')
            print(f'   Trades Abertos: {open_trades}')
            print(f'   Registros de Performance: {perf_records}')
            
            if signals > 0:
                signal_rate = (trades / signals * 100) if signals > 0 else 0
                print(f'   Taxa de Conversão (Sinais→Trades): {signal_rate:.1f}%')
            
        except Exception as e:
            print(f'   Erro no resumo: {e}')
        
    except Exception as e:
        print(f'Erro geral na análise: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print('\nAnalise concluida!')


if __name__ == "__main__":
    analisar_banco_dados()
