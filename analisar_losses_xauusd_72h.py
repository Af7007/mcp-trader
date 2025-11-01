#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise de Losses Expressivos XAUUSD - Ultimas 72h
Analise detalhada de perdas no ouro nas ultimas 72 horas
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

def conectar_banco():
    """Conecta ao banco de dados de trading"""
    try:
        # Tentar diferentes localizacoes do banco
        db_paths = [
            'trading_bot.db',
            'src/core/database.db', 
            'data/trading.db',
            '../trading.db'
        ]
        
        for db_path in db_paths:
            try:
                conn = sqlite3.connect(db_path)
                print(f"[OK] Conectado ao banco: {db_path}")
                return conn
            except sqlite3.Error as e:
                continue
        
        print("[ERRO] Banco de dados nao encontrado nos caminhos padrao")
        return None
    except Exception as e:
        print(f"[ERRO] Erro ao conectar com banco: {e}")
        return None

def analisar_losses_xauusd_72h():
    """Analisa losses expressivos do XAUUSD nas ultimas 72h"""
    
    print("ANALISE DE LOSSES XAUUSD - ULTIMAS 72H")
    print("=" * 60)
    
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # Calcular data limite (72h atras)
        data_limite = datetime.now() - timedelta(hours=72)
        
        # Queries para analisar dados
        queries = {
            'trades_72h': """
                SELECT 
                    symbol, 
                    type, 
                    volume, 
                    open_price, 
                    close_price, 
                    sl, 
                    tp,
                    open_time, 
                    close_time,
                    profit,
                    (close_price - open_price) as price_change,
                    ABS(profit) as loss_amount
                FROM trades 
                WHERE symbol LIKE '%XAU%' 
                AND open_time >= ?
                AND profit < 0
                ORDER BY loss_amount DESC
            """,
            
            'resumo_por_dia': """
                SELECT 
                    DATE(open_time) as dia,
                    COUNT(*) as num_trades,
                    SUM(profit) as total_profit,
                    AVG(profit) as profit_medio,
                    MIN(profit) as maior_loss,
                    SUM(CASE WHEN profit < 0 THEN ABS(profit) ELSE 0 END) as total_losses
                FROM trades 
                WHERE symbol LIKE '%XAU%' 
                AND open_time >= ?
                GROUP BY DATE(open_time)
                ORDER BY dia DESC
            """,
            
            'volumes_impactantes': """
                SELECT 
                    symbol,
                    type,
                    volume,
                    open_price,
                    close_price,
                    profit,
                    (close_price - open_price) * volume as impacto_direto
                FROM trades 
                WHERE symbol LIKE '%XAU%' 
                AND open_time >= ?
                AND profit < -50
                ORDER BY profit ASC
            """,
            
            'horarios_perda': """
                SELECT 
                    strftime('%H', open_time) as hora,
                    COUNT(*) as trades_perda,
                    AVG(profit) as profit_medio_hora,
                    SUM(profit) as total_perda_hora
                FROM trades 
                WHERE symbol LIKE '%XAU%' 
                AND open_time >= ?
                AND profit < 0
                GROUP BY strftime('%H', open_time)
                ORDER BY total_perda_hora ASC
            """
        }
        
        print(f"[INFO] Analisando dados de {data_limite.strftime('%Y-%m-%d %H:%M')} ate agora")
        print()
        
        # Executar analises
        for nome, query in queries.items():
            print(f"[QUERY] {nome.upper().replace('_', ' ')}")
            print("-" * 40)
            
            try:
                df = pd.read_sql_query(query, conn, params=[data_limite])
                
                if df.empty:
                    print("[AVISO] Nenhum dado encontrado")
                else:
                    print(f"[OK] {len(df)} registros encontrados")
                    
                    if nome == 'trades_72h':
                        print("\n[CRITICO] TOP 10 LOSSES MAIS EXPRESSIVOS:")
                        for i, row in df.head(10).iterrows():
                            print(f"{i+1:2d}. {row['type']} {row['volume']:.2f} | "
                                  f"${row['open_price']:.2f} -> ${row['close_price']:.2f} | "
                                  f"LOSS: ${row['profit']:.2f}")
                    
                    elif nome == 'resumo_por_dia':
                        print("\n[RESUMO] RESUMO POR DIA:")
                        for i, row in df.iterrows():
                            print(f"{row['dia']}: {row['num_trades']} trades | "
                                  f"Total: ${row['total_profit']:.2f} | "
                                  f"Maior loss: ${row['maior_loss']:.2f}")
                    
                    elif nome == 'volumes_impactantes':
                        print("\n[IMPACTO] TRADES COM MAIOR IMPACTO ($50+):")
                        impacto_total = 0
                        for i, row in df.iterrows():
                            print(f"{i+1:2d}. Volume {row['volume']:.2f} | "
                                  f"Impacto: ${row['impacto_direto']:.2f} | "
                                  f"Loss: ${row['profit']:.2f}")
                            impacto_total += row['impacto_direto']
                        print(f"\n[TOTAL] IMPACTO TOTAL: ${impacto_total:.2f}")
                    
                    elif nome == 'horarios_perda':
                        print("\n[TEMPO] PERDAS POR HORARIO:")
                        for i, row in df.iterrows():
                            print(f"{row['hora']:02d}h: {row['trades_perda']} perdas | "
                                  f"Media: ${row['profit_medio_hora']:.2f}")
                
                print()
                
            except Exception as e:
                print(f"[ERRO] Erro na query {nome}: {e}")
        
        # Analise adicional de padroes
        print("[ANALISE] ANALISE DE PADROES")
        print("-" * 40)
        
        # Pattern analysis
        pattern_query = """
            SELECT 
                type,
                COUNT(*) as quantidade,
                AVG(profit) as profit_medio,
                SUM(profit) as total_profit,
                COUNT(CASE WHEN profit < -100 THEN 1 END) as losses_100plus,
                COUNT(CASE WHEN profit < -50 THEN 1 END) as losses_50plus
            FROM trades 
            WHERE symbol LIKE '%XAU%' 
            AND close_time >= ?
            GROUP BY type
        """
        
        df_patterns = pd.read_sql_query(pattern_query, conn, params=[data_limite])
        
        if not df_patterns.empty:
            print("[PADROES] PADROES POR TIPO DE OPERACAO:")
            for i, row in df_patterns.iterrows():
                print(f"{row['type']:4s}: {row['quantidade']:2d} trades | "
                      f"Media: ${row['profit_medio']:6.2f} | "
                      f"Losses $50+: {row['losses_50plus']:2d} | "
                      f"Losses $100+: {row['losses_100plus']:2d}")
        
        # Estatisticas gerais
        stats_query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(profit) as resultado_total,
                AVG(profit) as profit_medio,
                MIN(profit) as maior_loss,
                MAX(profit) as maior_gain,
                COUNT(CASE WHEN profit < 0 THEN 1 END) as num_losses,
                COUNT(CASE WHEN profit > 0 THEN 1 END) as num_gains
            FROM trades 
            WHERE symbol LIKE '%XAU%' 
            AND close_time >= ?
        """
        
        df_stats = pd.read_sql_query(stats_query, conn, params=[data_limite])
        
        if not df_stats.empty:
            stats = df_stats.iloc[0]
            win_rate = (stats['num_gains'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
            
            print("\n[ESTATISTICAS] ESTATISTICAS GERAIS 72H:")
            print(f"Total de trades: {stats['total_trades']}")
            print(f"Wins: {stats['num_gains']} | Losses: {stats['num_losses']}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Resultado total: ${stats['resultado_total']:.2f}")
            print(f"Profit medio: ${stats['profit_medio']:.2f}")
            print(f"Maior loss: ${stats['maior_loss']:.2f}")
            print(f"Maior gain: ${stats['maior_gain']:.2f}")
            
            if stats['num_losses'] > 0:
                avg_loss = stats['resultado_total'] / stats['num_losses'] if stats['num_losses'] > 0 else 0
                print(f"Loss medio: ${avg_loss:.2f}")
        
        print("\n" + "=" * 60)
        print("[FINAL] ANALISE COMPLETA")
        
    except Exception as e:
        print(f"[ERRO] Erro geral na analise: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    analisar_losses_xauusd_72h()
