#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise completa do historico de trades no banco de dados
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

print("\n" + "="*80)
print(" ANALISE DE HISTORICO - BANCO DE DADOS")
print("="*80)

# Localizar banco de dados
db_path = Path(__file__).parent / "trading_bot.db"

print(f"\nBuscando banco de dados: {db_path}")

if not db_path.exists():
    print(f"ERRO: Banco de dados nao encontrado em {db_path}")
    print("\nProcurando em outras locacoes...")

    # Procurar em outras pastas
    possible_paths = [
        Path(__file__).parent / "trading_bot.db",
        Path(__file__).parent / "trades.db",
        Path.home() / "trading_bot.db",
    ]

    for path in possible_paths:
        if path.exists():
            db_path = path
            print(f"Encontrado em: {db_path}")
            break
    else:
        print("ERRO: Nenhum banco de dados encontrado!")
        exit(1)

print(f"[OK] Banco de dados localizado: {db_path}\n")

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("="*80)
    print(" ESTRUTURA DO BANCO DE DADOS")
    print("="*80)

    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print(f"\nTabelas encontradas: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    # Analisar tabela 'trades'
    print("\n" + "="*80)
    print(" ANALISE DA TABELA 'trades'")
    print("="*80)

    try:
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]
        print(f"\nTotal de trades: {total_trades}")

        if total_trades == 0:
            print("\n[INFO] Nenhum trade registrado ainda")
        else:
            # Obter informacoes detalhadas
            cursor.execute("""
                SELECT
                    symbol,
                    COUNT(*) as total,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                    SUM(profit) as total_profit,
                    AVG(profit) as avg_profit,
                    MIN(profit) as min_profit,
                    MAX(profit) as max_profit
                FROM trades
                GROUP BY symbol
            """)

            results = cursor.fetchall()

            for row in results:
                symbol, total, wins, losses, total_profit, avg_profit, min_profit, max_profit = row
                win_rate = (wins / total * 100) if total > 0 else 0

                print(f"\n{symbol}:")
                print(f"  Total de trades: {total}")
                print(f"  Wins: {wins} ({win_rate:.1f}%)")
                print(f"  Losses: {losses}")
                print(f"  Lucro total: ${total_profit:+.2f}")
                print(f"  Lucro medio: ${avg_profit:+.2f}")
                print(f"  Menor perda: ${min_profit:.2f}")
                print(f"  Maior ganho: ${max_profit:.2f}")

            # Ultimos 10 trades
            print(f"\n" + "="*80)
            print(" ULTIMOS 10 TRADES")
            print("="*80)

            cursor.execute("""
                SELECT
                    ticket,
                    symbol,
                    type,
                    volume,
                    open_price,
                    close_price,
                    profit,
                    open_time,
                    close_time
                FROM trades
                ORDER BY close_time DESC
                LIMIT 10
            """)

            trades = cursor.fetchall()

            if trades:
                print(f"\n{len(trades)} ultimos trades:\n")
                for i, trade in enumerate(trades, 1):
                    ticket, symbol, trade_type, volume, open_price, close_price, profit, open_time, close_time = trade
                    status = "WIN" if profit > 0 else "LOSS"
                    print(f"{i}. Ticket #{ticket}")
                    print(f"   Symbol: {symbol} | Type: {trade_type} | Volume: {volume}")
                    print(f"   Entrada: ${open_price:.2f} -> Saida: ${close_price:.2f}")
                    print(f"   {status}: ${profit:+.2f}")
                    if close_time:
                        print(f"   Data: {close_time}")
                    print()

            # Analise por data
            print(f"\n" + "="*80)
            print(" ANALISE POR DATA")
            print("="*80)

            cursor.execute("""
                SELECT
                    DATE(close_time) as data,
                    COUNT(*) as total,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(profit) as total_profit
                FROM trades
                WHERE close_time IS NOT NULL
                GROUP BY DATE(close_time)
                ORDER BY data DESC
                LIMIT 10
            """)

            daily_results = cursor.fetchall()

            if daily_results:
                print(f"\nUltimos 10 dias:\n")
                for data, total, wins, total_profit in daily_results:
                    win_rate = (wins / total * 100) if total > 0 else 0
                    print(f"{data}: {total} trades | {wins} wins ({win_rate:.0f}%) | Lucro: ${total_profit:+.2f}")

    except sqlite3.OperationalError as e:
        print(f"\n[ERRO] Tabela 'trades' nao encontrada: {e}")

    # Analisar tabela 'agents'
    print("\n" + "="*80)
    print(" ANALISE DA TABELA 'agents'")
    print("="*80)

    try:
        cursor.execute("SELECT COUNT(*) FROM agents")
        total_agents = cursor.fetchone()[0]
        print(f"\nTotal de agentes: {total_agents}")

        if total_agents > 0:
            cursor.execute("SELECT id, name, symbol, status, created_at FROM agents ORDER BY created_at DESC LIMIT 5")
            agents = cursor.fetchall()

            print(f"\nUltimos 5 agentes:\n")
            for agent in agents:
                agent_id, name, symbol, status, created_at = agent
                print(f"ID: {agent_id} | {name} ({symbol}) | Status: {status}")
                if created_at:
                    print(f"Criado em: {created_at}")

    except sqlite3.OperationalError as e:
        print(f"\n[INFO] Tabela 'agents' nao encontrada ou vazia")

    # Resumo geral
    print("\n" + "="*80)
    print(" RESUMO GERAL")
    print("="*80)

    cursor.execute("SELECT COUNT(*) FROM trades WHERE profit > 0")
    total_wins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE profit <= 0")
    total_losses = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(profit) FROM trades")
    total_profit = cursor.fetchone()[0]
    total_profit = total_profit if total_profit else 0

    total = total_wins + total_losses
    win_rate = (total_wins / total * 100) if total > 0 else 0

    print(f"\nTotal de operacoes: {total}")
    print(f"Total de wins: {total_wins} ({win_rate:.1f}%)")
    print(f"Total de losses: {total_losses}")
    print(f"Lucro/Prejuizo total: ${total_profit:+.2f}")

    if total > 0:
        avg_profit = total_profit / total
        print(f"Lucro medio por trade: ${avg_profit:+.2f}")

    print(f"\nAnalise realizada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    conn.close()

except Exception as e:
    print(f"\n[ERRO] Falha ao acessar banco de dados: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
