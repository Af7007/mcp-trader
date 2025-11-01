#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise de losses XAUUSD - APENAS transacoes automatizadas
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def identificar_operacoes_automaticas():
    """Identifica e analisa apenas operacoes automaticas"""
    
    print("ANALISE XAUUSD - APENAS OPERACOES AUTOMATICAS")
    print("=" * 60)
    
    conn = sqlite3.connect('trading_bot.db')
    
    try:
        # Primeiro, examinar os comentarios para entender a identificacao
        print("[INFO] EXAMINANDO COMENTARIOS PARA IDENTIFICAR AUTOMATIZACAO")
        print("-" * 55)
        
        query_comentarios = """
            SELECT DISTINCT comment, COUNT(*) as count
            FROM trades 
            WHERE symbol LIKE '%XAU%'
            GROUP BY comment
            ORDER BY count DESC
        """
        
        df_comentarios = pd.read_sql_query(query_comentarios, conn)
        
        print("Comentarios encontrados:")
        for idx, row in df_comentarios.iterrows():
            print(f"  '{row['comment']}' - {row['count']} trades")
        print()
        
        # Identificar padroes de operacoes automaticas
        # Critérios baseados nos comentários
        operacoes_automaticas = []
        
        # Tratar cada comentario para identificar automacao
        for idx, row in df_comentarios.iterrows():
            comment = row['comment']
            count = row['count']
            
            # Operacoes automaticas sao identificadas por comentarios especificos
            if any(keyword in comment.lower() for keyword in ['sincronizado', 'mt5', 'bot', 'hedge', 'auto']):
                operacoes_automaticas.append(comment)
            elif comment == 'Test_Trade':  # Exemplo de operacao manual
                continue  # Pular operacoes de teste
            elif comment == 'UNKNOWN':  # Podem ser manuais ou automaticas
                # Vamos tratar como automaticas por padrao
                operacoes_automaticas.append(comment)
        
        print(f"[FILTRO] Operacoes automaticas identificadas: {operacoes_automaticas}")
        print()
        
        # Query principal para operacoes automaticas
        if operacoes_automaticas:
            placeholders = ','.join(['?' for _ in operacoes_automaticas])
            query_auto = f"""
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
                AND comment IN ({placeholders})
                ORDER BY open_time DESC
            """
            
            params = operacoes_automaticas
        else:
            # Fallback: usar range de tickets ou outros criterios
            query_auto = """
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
                AND ticket < 100000000  -- Tickets com numeração alta são automáticos
                ORDER BY open_time DESC
            """
            params = []
        
        print(f"[QUERY] Executando analise com {len(params)} criterios de filtro")
        
        # Executar analise
        df_auto = pd.read_sql_query(query_auto, conn, params=params)
        
        print(f"[RESULTADO] Total de trades XAUUSD automaticos: {len(df_auto)}")
        
        if not df_auto.empty:
            # Estatisticas basicas
            print(f"Profit total automatico: ${df_auto['profit'].sum():.2f}")
            print(f"Maior loss automatico: ${df_auto['profit'].min():.2f}")
            print(f"Maior gain automatico: ${df_auto['profit'].max():.2f}")
            print(f"Profit medio automatico: ${df_auto['profit'].mean():.2f}")
            print()
            
            # Losses automaticos
            losses_auto = df_auto[df_auto['profit'] < 0].sort_values('profit')
            if not losses_auto.empty:
                print(f"[CRITICO] TOP 10 LOSSES AUTOMATICOS:")
                for i, (idx, row) in enumerate(losses_auto.head(10).iterrows()):
                    print(f"{i+1:2d}. {row['type']} {row['volume']:.2f} | "
                          f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                          f"{row['open_time'][:10]} | {row['comment']} | "
                          f"LOSS: ${row['profit']:.2f}")
                print()
                
                # Resumo losses automaticos
                loss_100plus_auto = losses_auto[losses_auto['profit'] < -100]
                loss_50plus_auto = losses_auto[losses_auto['profit'] < -50]
                
                print(f"[ANALISE] RESUMO LOSSES AUTOMATICOS:")
                print(f"Losses > $100: {len(loss_100plus_auto)} trades (${loss_100plus_auto['profit'].sum():.2f})")
                print(f"Losses > $50: {len(loss_50plus_auto)} trades (${loss_50plus_auto['profit'].sum():.2f})")
                print(f"Total losses automaticos: {len(losses_auto)} trades (${losses_auto['profit'].sum():.2f})")
                print()
            
            # Analise por comentario (tipo de operacao automatica)
            print("[TIPO] LOSSES POR TIPO DE OPERACAO AUTOMATICA")
            print("-" * 50)
            
            resumo_auto = df_auto.groupby('comment').agg({
                'profit': ['count', 'sum', 'min', 'max', 'mean']
            }).round(2)
            
            resumo_auto.columns = ['Trades', 'Total_Profit', 'Min_Loss', 'Max_Gain', 'Media']
            
            for comment, row in resumo_auto.iterrows():
                losses_comment = len(df_auto[(df_auto['comment'] == comment) & (df_auto['profit'] < 0)])
                print(f"{comment}: {row['Trades']:3d} trades | "
                      f"Losses: {losses_comment:2d} | Total: ${row['Total_Profit']:8.2f}")
            print()
            
            # Periodo dos losses automaticos
            data_72h = datetime.now() - timedelta(hours=72)
            data_7d = datetime.now() - timedelta(days=7)
            data_30d = datetime.now() - timedelta(days=30)
            
            print("[TEMPO] LOSSES AUTOMATICOS POR PERIODO")
            print("-" * 40)
            
            # 72h
            losses_72h_auto = df_auto[(df_auto['profit'] < 0) & 
                                    (pd.to_datetime(df_auto['open_time'], format='mixed') >= data_72h)]
            print(f"Ultimas 72h: {len(losses_72h_auto)} losses (${losses_72h_auto['profit'].sum():.2f})")
            
            # 7 dias
            losses_7d_auto = df_auto[(df_auto['profit'] < 0) & 
                                   (pd.to_datetime(df_auto['open_time'], format='mixed') >= data_7d)]
            print(f"Ultimos 7 dias: {len(losses_7d_auto)} losses (${losses_7d_auto['profit'].sum():.2f})")
            
            # 30 dias
            losses_30d_auto = df_auto[(df_auto['profit'] < 0) & 
                                    (pd.to_datetime(df_auto['open_time'], format='mixed') >= data_30d)]
            print(f"Ultimos 30 dias: {len(losses_30d_auto)} losses (${losses_30d_auto['profit'].sum():.2f})")
            print()
            
            # Comparacao com operacoes manuais (se houver)
            query_todos = """
                SELECT COUNT(*) as total FROM trades WHERE symbol LIKE '%XAU%'
            """
            df_total = pd.read_sql_query(query_todos, conn)
            total_todos = df_total.iloc[0]['total']
            
            print(f"[COMPARACAO] Total XAUUSD: {total_todos} trades")
            print(f"Automaticos: {len(df_auto)} trades ({len(df_auto)/total_todos*100:.1f}%)")
            print(f"Manuais (estimado): {total_todos - len(df_auto)} trades ({(total_todos - len(df_auto))/total_todos*100:.1f}%)")
            
        else:
            print("[AVISO] Nenhuma operacao automatica identificada com os criterios atuais")
            print("Tentando criterio alternativo...")
            
            # Criterio alternativo: tickets com numeros altos (tipicamente automaticos)
            query_alt = """
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
                AND ticket > 100000000
                ORDER BY open_time DESC
            """
            
            df_alt = pd.read_sql_query(query_alt, conn)
            print(f"[ALTERNATIVO] Trades com ticket > 100M: {len(df_alt)}")
            
            if not df_alt.empty:
                losses_alt = df_alt[df_alt['profit'] < 0]
                print(f"Losses automaticos (ticket alt): {len(losses_alt)} (${losses_alt['profit'].sum():.2f})")
        
        print("\n" + "=" * 60)
        print("[FINAL] ANALISE AUTOMATICA FINALIZADA")
        
    except Exception as e:
        print(f"[ERRO] Erro na analise automatica: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    identificar_operacoes_automaticas()
