#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar TODOS os trades do MT5 com o banco de dados.
"""

import MetaTrader5 as mt5
import sqlite3
from datetime import datetime, timedelta
from src.core.database import get_db_connection

print('=' * 80)
print('  SINCRONIZANDO TRADES DO MT5 COM BANCO DE DADOS')
print('=' * 80)
print()

# Inicializar MT5
if not mt5.initialize():
    print('[ERRO] Nao consegui conectar ao MT5')
    exit(1)

print('[OK] Conectado ao MT5')
print()

# Obter TODOS os deals (últimos 30 dias)
from_date = datetime.now() - timedelta(days=30)
all_deals = mt5.history_deals_get(from_date, datetime.now())

if all_deals is None:
    all_deals = []

print(f'Total de deals no MT5: {len(all_deals)}')
print()

# Agrupar por posição para determinar BUY/SELL
deals_by_position = {}
for deal in all_deals:
    pos_id = deal.position_id
    if pos_id not in deals_by_position:
        deals_by_position[pos_id] = []
    deals_by_position[pos_id].append(deal)

print(f'Total de posicoes: {len(deals_by_position)}')
print()

# Conectar ao banco
conn = get_db_connection()
cursor = conn.cursor()

# Obter trades já salvos
cursor.execute("SELECT ticket FROM trades")
saved_tickets = set(row[0] for row in cursor.fetchall())
print(f'Trades ja salvos no banco: {len(saved_tickets)}')
print()

# Processar cada posição
saved = 0
skipped = 0
errors = 0

print('SINCRONIZANDO TRADES:')
print('-' * 80)

for pos_id, deals_list in deals_by_position.items():
    if len(deals_list) < 2:
        # Posição ainda aberta ou incompleta
        skipped += 1
        continue

    # Primeira deal = entrada, última = saída
    open_deal = deals_list[0]
    close_deal = deals_list[-1]

    # Pular se já está salvo
    if open_deal.ticket in saved_tickets:
        skipped += 1
        continue

    # Extrair dados
    ticket = open_deal.ticket
    symbol = open_deal.symbol if open_deal.symbol else 'UNKNOWN'
    trade_type = 'BUY' if open_deal.type == 0 else 'SELL'
    volume = open_deal.volume
    open_price = open_deal.price
    close_price = close_deal.price
    profit = sum(d.profit for d in deals_list)  # Soma de todos os deals da posição

    # Tentar extrair SL/TP dos deals (MT5 pode ter esses campos)
    sl = getattr(open_deal, 'sl', 0)
    tp = getattr(open_deal, 'tp', 0)

    # Converter timestamps
    try:
        open_time = datetime.fromtimestamp(open_deal.time) if open_deal.time else datetime.now()
        open_time = open_time.isoformat()
    except:
        open_time = datetime.now().isoformat()

    try:
        close_time = datetime.fromtimestamp(close_deal.time) if close_deal.time else datetime.now()
        close_time = close_time.isoformat()
    except:
        close_time = datetime.now().isoformat()

    # Salvar no banco
    try:
        cursor.execute("""
            INSERT INTO trades (
                ticket, symbol, type, volume,
                open_price, close_price, open_time, close_time,
                sl, tp, profit, comment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket,
            symbol,
            trade_type,
            volume,
            open_price,
            close_price,
            open_time,
            close_time,
            sl,
            tp,
            profit,
            "Sincronizado_do_MT5"
        ))

        profit_str = f"+${profit:.2f}" if profit >= 0 else f"-${abs(profit):.2f}"
        print(f'[OK] Ticket {ticket:10d} | {symbol:9s} | {trade_type:4s} | {volume:6.2f} lots | {profit_str:10s}')
        saved += 1

    except sqlite3.IntegrityError:
        # Já existe
        skipped += 1
    except Exception as e:
        print(f'[ERRO] Ticket {ticket}: {e}')
        errors += 1

conn.commit()
conn.close()

print()
print('-' * 80)
print(f'Resultado:')
print(f'  Trades sincronizados: {saved}')
print(f'  Trades pulados (já existem): {skipped}')
print(f'  Erros: {errors}')
print()

# Verificar resultado
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM trades")
total = cursor.fetchone()[0]

cursor.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
        ROUND(SUM(profit), 2) as total_profit,
        ROUND(AVG(profit), 2) as avg_profit
    FROM trades
""")

total, wins, losses, total_profit, avg_profit = cursor.fetchone()
win_rate = (wins / total * 100) if total > 0 else 0

print('=' * 80)
print(f'BANCO DE DADOS ATUALIZADO:')
print('=' * 80)
print(f'Total de trades: {total}')
print(f'Vitórias: {wins} ({win_rate:.1f}%)')
print(f'Derrotas: {losses}')
print(f'Lucro Total: ${total_profit:.2f}')
print(f'Lucro Médio: ${avg_profit:.2f}')

conn.close()
mt5.shutdown()

print()
print('[OK] Sincronização concluída!')
