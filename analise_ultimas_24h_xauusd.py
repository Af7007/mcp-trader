#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise de XAUUSD - ULTIMAS 24 HORAS
Foco na atividade mais recente para identificar problemas imediatos
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def analisar_ultimas_24h():
    """Analisa apenas as ultimas 24 horas de operacoes XAUUSD"""
    
    print("ANALISE XAUUSD - ULTIMAS 24 HORAS")
    print("=" * 50)
    
    conn = sqlite3.connect('trading_bot.db')
    
    try:
        # Calcular data limite (24h atras)
        data_24h = datetime.now() - timedelta(hours=24)
        
        print(f"[TEMPO] Analisando de {data_24h.strftime('%Y-%m-%d %H:%M')} ate agora")
        print()
        
        # 1. Analise geral das ultimas 24h
        print("[GERAL] TRADES XAUUSD ULTIMAS 24H")
        print("-" * 40)
        
        query_24h_geral = """
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
            AND open_time >= ?
            ORDER BY open_time DESC
        """
        
        df_24h = pd.read_sql_query(query_24h_geral, conn, params=[data_24h])
        
        print(f"Total de trades XAUUSD nas ultimas 24h: {len(df_24h)}")
        
        if not df_24h.empty:
            # Estatisticas basicas 24h
            print(f"Profit total 24h: ${df_24h['profit'].sum():.2f}")
            print(f"Maior loss 24h: ${df_24h['profit'].min():.2f}")
            print(f"Maior gain 24h: ${df_24h['profit'].max():.2f}")
            print(f"Profit medio 24h: ${df_24h['profit'].mean():.2f}")
            print()
            
            # Detalhar cada trade
            print("[DETALHES] TODOS OS TRADES 24H:")
            for idx, row in df_24h.iterrows():
                status_profit = f"LOSS: ${row['profit']:.2f}" if row['profit'] < 0 else f"GAIN: ${row['profit']:.2f}"
                print(f"  {idx+1:2d}. {row['type']} {row['volume']:.2f} | "
                      f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                      f"{row['open_time'][:16]} | {row['comment']} | {status_profit}")
            print()
            
            # Analise por comentario (sistema)
            print("[SISTEMA] POR TIPO DE OPERACAO 24H:")
            resumo_24h = df_24h.groupby('comment').agg({
                'profit': ['count', 'sum', 'min', 'max', 'mean']
            }).round(2)
            
            resumo_24h.columns = ['Trades', 'Total_Profit', 'Min_Loss', 'Max_Gain', 'Media']
            
            for comment, row in resumo_24h.iterrows():
                losses_comment = len(df_24h[(df_24h['comment'] == comment) & (df_24h['profit'] < 0)])
                gains_comment = len(df_24h[(df_24h['comment'] == comment) & (df_24h['profit'] > 0)])
                print(f"{comment}: {row['Trades']:2d} trades | "
                      f"Gains: {gains_comment:2d} | Losses: {losses_comment:2d} | "
                      f"Total: ${row['Total_Profit']:8.2f}")
            print()
            
            # Losses nas ultimas 24h
            losses_24h = df_24h[df_24h['profit'] < 0]
            if not losses_24h.empty:
                print("[CRITICO] LOSSES NAS ULTIMAS 24H:")
                for idx, row in losses_24h.iterrows():
                    print(f"  - {row['type']} {row['volume']:.2f} | "
                          f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                          f"{row['open_time'][:16]} | {row['comment']} | "
                          f"LOSS: ${row['profit']:.2f}")
                print(f"TOTAL LOSSES 24H: {len(losses_24h)} trades (${losses_24h['profit'].sum():.2f})")
            else:
                print("[OK] NENHUM LOSS NAS ULTIMAS 24H!")
            print()
            
            # Gains nas ultimas 24h
            gains_24h = df_24h[df_24h['profit'] > 0]
            if not gains_24h.empty:
                print("[POSITIVO] GAINS NAS ULTIMAS 24H:")
                for idx, row in gains_24h.iterrows():
                    print(f"  - {row['type']} {row['volume']:.2f} | "
                          f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                          f"{row['open_time'][:16]} | {row['comment']} | "
                          f"GAIN: ${row['profit']:.2f}")
                print(f"TOTAL GAINS 24H: {len(gains_24h)} trades (${gains_24h['profit'].sum():.2f})")
            else:
                print("[NEUTRO] NENHUM GAIN NAS ULTIMAS 24H")
            print()
            
            # Analise por hora
            print("[TEMPO] ATIVIDADE POR HORA 24H:")
            df_24h['hora'] = pd.to_datetime(df_24h['open_time'], format='mixed').dt.strftime('%H:00')
            
            resumo_hora = df_24h.groupby('hora').agg({
                'profit': ['count', 'sum']
            }).round(2)
            
            resumo_hora.columns = ['Trades', 'Profit_Total']
            
            for hora, row in resumo_hora.iterrows():
                status = "LOSS" if row['Profit_Total'] < 0 else "GAIN"
                print(f"{hora}: {row['Trades']:2d} trades | {status} ${row['Profit_Total']:7.2f}")
            print()
        
        else:
            print("[AVISO] NENHUM TRADE XAUUSD NAS ULTIMAS 24H")
            print()
        
        # 2. Comparacao com periodo anterior (24h-48h)
        print("[COMPARACAO] COMPARANDO COM 24H-48H ATRAS")
        print("-" * 45)
        
        data_48h = datetime.now() - timedelta(hours=48)
        data_24h_anterior = datetime.now() - timedelta(hours=24)
        
        query_24h_anterior = """
            SELECT COUNT(*) as count, SUM(profit) as total_profit
            FROM trades 
            WHERE symbol LIKE '%XAU%'
            AND open_time >= ?
            AND open_time < ?
        """
        
        df_anterior = pd.read_sql_query(query_24h_anterior, conn, 
                                      params=[data_48h, data_24h_anterior])
        
        if not df_anterior.empty:
            count_anterior = df_anterior.iloc[0]['count']
            profit_anterior = df_anterior.iloc[0]['total_profit'] or 0
            
            print(f"Periodo 24h-48h atras: {count_anterior} trades | Profit: ${profit_anterior:.2f}")
            
            if not df_24h.empty:
                count_atual = len(df_24h)
                profit_atual = df_24h['profit'].sum()
                
                print(f"Periodo atual 0-24h:  {count_atual} trades | Profit: ${profit_atual:.2f}")
                
                # Comparacao
                if count_anterior > 0:
                    variacao_trades = ((count_atual - count_anterior) / count_anterior) * 100
                    print(f"Variacao no volume de trades: {variacao_trades:+.1f}%")
                
                if profit_anterior != 0:
                    variacao_profit = ((profit_atual - profit_anterior) / abs(profit_anterior)) * 100
                    print(f"Variacao no profit: {variacao_profit:+.1f}%")
        
        # 3. Verificar tendencias preocupantes
        print("\n[TENDENCIAS] VERIFICANDO TENDENCIAS PREOCUPANTES")
        print("-" * 50)
        
        if not df_24h.empty:
            # Verificar se ha losses consecutivos
            df_24h_sorted = df_24h.sort_values('open_time')
            losses_consecutivos = 0
            max_consecutivos = 0
            
            for idx, row in df_24h_sorted.iterrows():
                if row['profit'] < 0:
                    losses_consecutivos += 1
                    max_consecutivos = max(max_consecutivos, losses_consecutivos)
                else:
                    losses_consecutivos = 0
            
            print(f"Maximo de losses consecutivos nas 24h: {max_consecutivos}")
            
            if max_consecutivos >= 3:
                print("[ALERTA] 3+ losses consecutivos - SISTEMA PRECISA PAUSAR!")
            elif max_consecutivos >= 2:
                print("[ATENCAO] 2 losses consecutivos - MONITORAR DE PERTO")
            else:
                print("[OK] Nao ha losses consecutivos preocupantes")
            
            # Verificar volume total
            volume_total = df_24h['volume'].sum()
            print(f"Volume total negociado nas 24h: {volume_total:.2f}")
            
            if volume_total > 1.0:  # Exemplo de threshold
                print("[ALERTA] Volume muito alto nas 24h - RISCO ELEVADO")
            else:
                print("[OK] Volume dentro dos limites normais")
            
            # Verificar se ha trades muito grandes
            volumes_grandes = df_24h[df_24h['volume'] > 0.25]
            if not volumes_grandes.empty:
                print(f"[ALERTA] {len(volumes_grandes)} trades com volume > 0.25 nas 24h:")
                for idx, row in volumes_grandes.iterrows():
                    print(f"  - {row['type']} {row['volume']:.2f} | {row['comment']}")
            else:
                print("[OK] Todos os volumes nas 24h dentro dos limites")
        
        print("\n" + "=" * 50)
        print("[FINAL] ANALISE 24H COMPLETADA")
        
    except Exception as e:
        print(f"[ERRO] Erro na analise 24h: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    analisar_ultimas_24h()
