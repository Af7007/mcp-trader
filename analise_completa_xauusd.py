#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise completa de losses XAUUSD - Todos os dados disponiveis
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def analise_completa_xauusd():
    """Analisa todos os trades XAUUSD no banco"""
    
    print("ANALISE COMPLETA XAUUSD - TODOS OS DADOS")
    print("=" * 60)
    
    conn = sqlite3.connect('trading_bot.db')
    
    try:
        # 1. Verificar todos os trades XAUUSD
        print("[INFO] ANALISANDO TODOS OS TRADES XAUUSD")
        print("-" * 40)
        
        query_todos = """
            SELECT 
                id,
                ticket,
                symbol,
                type,
                volume,
                open_price,
                close_price,
                open_time,
                close_time,
                profit,
                sl,
                tp,
                status,
                comment
            FROM trades 
            WHERE symbol LIKE '%XAU%'
            ORDER BY open_time DESC
        """
        
        df_todos = pd.read_sql_query(query_todos, conn)
        print(f"Total de trades XAUUSD: {len(df_todos)}")
        
        # Estatisticas basicas
        if not df_todos.empty:
            print(f"Profit total: ${df_todos['profit'].sum():.2f}")
            print(f"Maior loss: ${df_todos['profit'].min():.2f}")
            print(f"Maior gain: ${df_todos['profit'].max():.2f}")
            print(f"Profit medio: ${df_todos['profit'].mean():.2f}")
            print()
            
            # Losses mais expressivos
            losses = df_todos[df_todos['profit'] < 0].sort_values('profit')
            if not losses.empty:
                print(f"[CRITICO] TOP 10 LOSSES MAIS EXPRESSIVOS (TODOS OS TEMPOS):")
                for i, (idx, row) in enumerate(losses.head(10).iterrows()):
                    print(f"{i+1:2d}. {row['type']} {row['volume']:.2f} | "
                          f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                          f"{row['open_time'][:10]} | LOSS: ${row['profit']:.2f}")
                print()
                
                # Analise dos losses expressivos
                loss_100plus = losses[losses['profit'] < -100]
                loss_50plus = losses[losses['profit'] < -50]
                loss_20plus = losses[losses['profit'] < -20]
                
                print(f"[ANALISE] RESUMO DOS LOSSES:")
                print(f"Losses > $100: {len(loss_100plus)} trades (${loss_100plus['profit'].sum():.2f})")
                print(f"Losses > $50: {len(loss_50plus)} trades (${loss_50plus['profit'].sum():.2f})")
                print(f"Losses > $20: {len(loss_20plus)} trades (${loss_20plus['profit'].sum():.2f})")
                print(f"Total de losses: {len(losses)} trades (${losses['profit'].sum():.2f})")
                print()
            
            # Analise por data
            print("[TEMPO] ANALISE POR PERIODO")
            print("-" * 30)
            
            # Converter para datetime (corrigir formato)
            df_todos['open_date'] = pd.to_datetime(df_todos['open_time'], format='mixed').dt.date
            
            resumo_data = df_todos.groupby('open_date').agg({
                'profit': ['count', 'sum', 'min', 'max', 'mean']
            }).round(2)
            
            resumo_data.columns = ['Trades', 'Total_Profit', 'Min_Loss', 'Max_Gain', 'Media']
            resumo_data = resumo_data.sort_index(ascending=False)
            
            print("Por dia (mais recente primeiro):")
            for date, row in resumo_data.head(10).iterrows():
                print(f"{date}: {row['Trades']:2d} trades | Total: ${row['Total_Profit']:7.2f} | "
                      f"Min: ${row['Min_Loss']:7.2f} | Max: ${row['Max_Gain']:7.2f}")
            print()
            
            # Analise por tipo
            print("[TIPO] ANALISE POR TIPO DE OPERACAO")
            print("-" * 35)
            
            resumo_tipo = df_todos.groupby('type').agg({
                'profit': ['count', 'sum', 'min', 'max', 'mean']
            }).round(2)
            
            resumo_tipo.columns = ['Trades', 'Total_Profit', 'Min_Loss', 'Max_Gain', 'Media']
            
            for tipo, row in resumo_tipo.iterrows():
                losses_tipo = len(df_todos[(df_todos['type'] == tipo) & (df_todos['profit'] < 0)])
                gains_tipo = len(df_todos[(df_todos['type'] == tipo) & (df_todos['profit'] > 0)])
                zero_tipo = len(df_todos[(df_todos['type'] == tipo) & (df_todos['profit'] == 0)])
                
                print(f"{tipo}: {row['Trades']:3d} trades | "
                      f"Gains: {gains_tipo:2d} | Losses: {losses_tipo:2d} | Zero: {zero_tipo:2d} | "
                      f"Total: ${row['Total_Profit']:8.2f}")
            print()
            
            # Verificar trades com profit zerado
            zero_profit = df_todos[df_todos['profit'] == 0]
            if not zero_profit.empty:
                print(f"[ATENCAO] {len(zero_profit)} trades com profit = 0:")
                print("Estes trades podem estar abertos ou com problema no calculo:")
                
                for i, (idx, row) in enumerate(zero_profit.head(5).iterrows()):
                    print(f"  {i+1}. {row['ticket']} | {row['type']} {row['volume']:.2f} | "
                          f"{row['open_time'][:16]} | Status: {row['status']}")
                if len(zero_profit) > 5:
                    print(f"  ... e mais {len(zero_profit) - 5} trades")
                print()
        
        # 2. Buscar por perdas recentes (expansao do periodo)
        print("[BUSCA] BUSCANDO PERDAS NOS ULTIMOS 7 DIAS")
        print("-" * 45)
        
        data_7d = datetime.now() - timedelta(days=7)
        
        query_7d = """
            SELECT 
                symbol,
                type,
                volume,
                open_price,
                close_price,
                profit,
                open_time,
                close_time
            FROM trades 
            WHERE symbol LIKE '%XAU%'
            AND open_time >= ?
            AND profit < 0
            ORDER BY profit ASC
        """
        
        df_7d = pd.read_sql_query(query_7d, conn, params=[data_7d])
        
        if not df_7d.empty:
            print(f"Trades com loss nos ultimos 7 dias: {len(df_7d)}")
            for i, (idx, row) in enumerate(df_7d.iterrows()):
                print(f"{i+1:2d}. {row['type']} {row['volume']:.2f} | "
                      f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                      f"{row['open_time'][:16]} | LOSS: ${row['profit']:.2f}")
        else:
            print("Nenhum trade com loss encontrado nos ultimos 7 dias")
        
        print()
        
        # 3. Ultimos 30 dias
        print("[BUSCA] BUSCANDO PERDAS NOS ULTIMOS 30 DIAS")
        print("-" * 44)
        
        data_30d = datetime.now() - timedelta(days=30)
        
        query_30d = """
            SELECT 
                symbol,
                type,
                volume,
                open_price,
                close_price,
                profit,
                open_time,
                close_time
            FROM trades 
            WHERE symbol LIKE '%XAU%'
            AND open_time >= ?
            AND profit < 0
            ORDER BY profit ASC
        """
        
        df_30d = pd.read_sql_query(query_30d, conn, params=[data_30d])
        
        if not df_30d.empty:
            print(f"Trades com loss nos ultimos 30 dias: {len(df_30d)}")
            for i, (idx, row) in enumerate(df_30d.head(15).iterrows()):
                print(f"{i+1:2d}. {row['type']} {row['volume']:.2f} | "
                      f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                      f"{row['open_time'][:16]} | LOSS: ${row['profit']:.2f}")
        else:
            print("Nenhum trade com loss encontrado nos ultimos 30 dias")
        
        print("\n" + "=" * 60)
        print("[FINAL] ANALISE COMPLETA FINALIZADA")
        
    except Exception as e:
        print(f"[ERRO] Erro na analise: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    analise_completa_xauusd()
