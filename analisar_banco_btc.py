#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise do banco de dados BTC Trading Logs
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def analisar_banco():
    """
    Analisa o banco de dados BTC
    """
    db_path = Path('btc_trading_logs.db')
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ANALISE DO BANCO DE DADOS BTC TRADING LOGS")
    print("=" * 60)
    
    # 1. Estatísticas gerais
    print("\n📈 ESTATÍSTICAS GERAIS:")
    cursor.execute('SELECT COUNT(*) FROM cycles')
    total_ciclos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL')
    total_sinais = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]
    
    print(f"   Total de ciclos: {total_ciclos}")
    print(f"   Total de sinais: {total_sinais}")
    print(f"   Total de trades: {total_trades}")
    print(f"   Taxa de sinais: {(total_sinais/total_ciclos)*100:.2f}%")
    
    # 2. Última hora
    print("\n⏰ ÚLTIMA HORA:")
    uma_hora_atras = datetime.now() - timedelta(hours=1)
    
    cursor.execute('SELECT COUNT(*) FROM cycles WHERE timestamp > ?', (uma_hora_atras,))
    ciclos_ultima_hora = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL AND timestamp > ?', (uma_hora_atras,))
    sinais_ultima_hora = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM trades WHERE timestamp > ?', (uma_hora_atras,))
    trades_ultima_hora = cursor.fetchone()[0]
    
    print(f"   Ciclos (1h): {ciclos_ultima_hora}")
    print(f"   Sinais (1h): {sinais_ultima_hora}")
    print(f"   Trades (1h): {trades_ultima_hora}")
    print(f"   Taxa de sinais (1h): {(sinais_ultima_hora/ciclos_ultima_hora)*100:.2f}%")
    
    # 3. Últimos sinais
    print("\n🎯 ÚLTIMOS 10 SINAIS:")
    cursor.execute('''
        SELECT signal_type, signal_reason, price, timestamp 
        FROM cycles 
        WHERE signal_type IS NOT NULL 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    ultimos_sinais = cursor.fetchall()
    
    for i, (tipo, razao, preco, timestamp) in enumerate(ultimos_sinais, 1):
        print(f"   {i:2d}. {tipo:8} | {razao:20} | ${preco:8.2f} | {timestamp}")
    
    # 4. Distribuição de sinais
    print("\n📊 DISTRIBUIÇÃO DE SINAIS:")
    cursor.execute('''
        SELECT signal_type, COUNT(*) as count 
        FROM cycles 
        WHERE signal_type IS NOT NULL 
        GROUP BY signal_type
    ''')
    distribuicao = cursor.fetchall()
    
    for tipo, count in distribuicao:
        print(f"   {tipo}: {count} ({(count/total_sinais)*100:.1f}%)")
    
    # 5. Trades recentes
    print("\n💰 TRADES RECENTES:")
    cursor.execute('''
        SELECT trade_type, entry_price, status, reason, timestamp 
        FROM trades 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''')
    trades_recentes = cursor.fetchall()
    
    for i, (tipo, preco, status, razao, timestamp) in enumerate(trades_recentes, 1):
        print(f"   {i}. {tipo:6} | ${preco:8.2f} | {status:8} | {razao:15} | {timestamp}")
    
    # 6. Verificar se há sinais mas sem trades
    print("\n⚠️  ANÁLISE DE PROBLEMAS:")
    
    # Sinais sem trades correspondentes
    cursor.execute('''
        SELECT COUNT(*) FROM cycles c
        LEFT JOIN trades t ON c.timestamp = t.timestamp AND c.signal_type = t.trade_type
        WHERE c.signal_type IS NOT NULL 
        AND c.timestamp > ?
        AND t.trade_type IS NULL
    ''', (uma_hora_atras,))
    sinais_sem_trades = cursor.fetchone()[0]
    
    if sinais_sem_trades > 0:
        print(f"   ⚠️  {sinais_sem_trades} sinais sem trades correspondentes (última hora)")
    
    # Verificar se agente está gerando sinais
    cursor.execute('''
        SELECT MAX(timestamp) as ultimo_sinal 
        FROM cycles 
        WHERE signal_type IS NOT NULL
    ''')
    ultimo_sinal = cursor.fetchone()[0]
    
    if ultimo_sinal:
        tempo_desde_ultimo = datetime.now() - datetime.strptime(ultimo_sinal, '%Y-%m-%d %H:%M:%S')
        minutos_desde = tempo_desde_ultimo.total_seconds() / 60
        print(f"   ⏰ Último sinal: {minutos_desde:.1f} minutos atrás")
        
        if minutos_desde > 30:
            print(f"   ⚠️  ATENÇÃO: Sem sinais há {minutos_desde:.1f} minutos!")
    
    # 7. Performance por razão
    print("\n📈 PERFORMANCE POR RAZÃO:")
    cursor.execute('''
        SELECT signal_reason, COUNT(*) as count 
        FROM cycles 
        WHERE signal_type IS NOT NULL 
        GROUP BY signal_reason 
        ORDER BY count DESC
        LIMIT 10
    ''')
    performance_razao = cursor.fetchall()
    
    for razao, count in performance_razao:
        print(f"   {razao:25}: {count}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("✅ Análise concluída!")
    print("=" * 60)

if __name__ == "__main__":
    analisar_banco()
