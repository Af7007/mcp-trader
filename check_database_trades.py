#!/usr/bin/env python3
"""
Verifica estrutura e dados da tabela trades
"""

import sqlite3
from datetime import datetime

db_path = "btc_trading_logs.db"

print("="*70)
print("VERIFICACAO DE BANCO DE DADOS - TABELA TRADES")
print("="*70)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Estrutura da tabela
print("\n[1] ESTRUTURA DA TABELA TRADES:")
print("-"*70)
cursor.execute("PRAGMA table_info(trades);")
columns = cursor.fetchall()

for col in columns:
    col_id, name, col_type, notnull, default, pk = col
    print(f"  {name:20s} {col_type:15s} {'NOT NULL' if notnull else ''} {'PK' if pk else ''}")

# 2. Total de trades
print("\n[2] TOTAL DE TRADES:")
print("-"*70)
cursor.execute("SELECT COUNT(*) FROM trades;")
total = cursor.fetchone()[0]
print(f"  Total de registros: {total}")

# 3. Distribuição por status
print("\n[3] DISTRIBUICAO POR STATUS:")
print("-"*70)
cursor.execute("""
    SELECT status, COUNT(*) as count 
    FROM trades 
    GROUP BY status 
    ORDER BY count DESC;
""")
for row in cursor.fetchall():
    status, count = row
    print(f"  {status:20s}: {count}")

# 4. Últimos 5 trades
print("\n[4] ULTIMOS 5 TRADES:")
print("-"*70)
cursor.execute("""
    SELECT id, symbol, trade_type, entry_price, exit_price, profit_loss, status, 
           substr(timestamp, 1, 19) as time
    FROM trades 
    ORDER BY id DESC 
    LIMIT 5;
""")

trades = cursor.fetchall()
if trades:
    for trade in trades:
        trade_id, symbol, trade_type, entry, exit_p, profit, status, time = trade
        print(f"\n  ID: {trade_id} | {symbol} | {trade_type} | Status: {status}")
        print(f"    Timestamp: {time}")
        print(f"    Entry: ${entry:.2f}" if entry else "    Entry: N/A")
        print(f"    Exit: ${exit_p:.2f}" if exit_p else "    Exit: N/A")
        print(f"    Profit: ${profit:.2f}" if profit else "    Profit: N/A")
else:
    print("  Nenhum trade encontrado")

# 5. Verificar colunas críticas
print("\n[5] VERIFICACAO DE COLUNAS CRITICAS:")
print("-"*70)

# Verificar se exit_price está sendo preenchido
cursor.execute("""
    SELECT COUNT(*) 
    FROM trades 
    WHERE status LIKE 'CLOSED%' AND exit_price IS NULL;
""")
missing_exit = cursor.fetchone()[0]
print(f"  Trades fechados SEM exit_price: {missing_exit}")

# Verificar se profit_loss está sendo preenchido
cursor.execute("""
    SELECT COUNT(*) 
    FROM trades 
    WHERE status LIKE 'CLOSED%' AND profit_loss IS NULL;
""")
missing_profit = cursor.fetchone()[0]
print(f"  Trades fechados SEM profit_loss: {missing_profit}")

# 6. Estatísticas gerais
print("\n[6] ESTATISTICAS GERAIS:")
print("-"*70)

cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'CLOSED_WIN' THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN status = 'CLOSED_LOSS' THEN 1 ELSE 0 END) as losses,
        SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_trades,
        SUM(CASE WHEN profit_loss IS NOT NULL THEN profit_loss ELSE 0 END) as total_profit
    FROM trades;
""")

stats = cursor.fetchone()
if stats:
    total, wins, losses, open_t, profit = stats
    if total > 0:
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        print(f"  Total trades: {total}")
        print(f"  Wins: {wins}")
        print(f"  Losses: {losses}")
        print(f"  Open: {open_t}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Total Profit: ${profit:.2f}")

# 7. Verificar se dados MT5 estão sendo coletados
print("\n[7] DADOS DO MT5 (exit_price e profit_loss):")
print("-"*70)

cursor.execute("""
    SELECT id, symbol, exit_price, profit_loss, exit_reason, status
    FROM trades 
    WHERE status LIKE 'CLOSED%'
    ORDER BY id DESC 
    LIMIT 3;
""")

closed_trades = cursor.fetchall()
if closed_trades:
    for trade in closed_trades:
        trade_id, symbol, exit_p, profit, reason, status = trade
        has_exit = "SIM" if exit_p else "NAO"
        has_profit = "SIM" if profit else "NAO"
        print(f"\n  Trade ID {trade_id} ({symbol}):")
        print(f"    Exit Price: {has_exit} {'($%.2f)' % exit_p if exit_p else ''}")
        print(f"    Profit/Loss: {has_profit} {'($%.2f)' % profit if profit else ''}")
        print(f"    Exit Reason: {reason or 'N/A'}")
        print(f"    Status: {status}")
else:
    print("  Nenhum trade fechado ainda")

conn.close()

print("\n" + "="*70)
print("ANALISE:")
print("="*70)

if missing_exit > 0 or missing_profit > 0:
    print("""
[PROBLEMA DETECTADO]

Trades fechados estao faltando dados do MT5:
  - exit_price e/ou profit_loss estao NULL
  
CAUSA PROVAVEL:
  - history_deals_get() nao esta retornando dados
  - Ticket nao esta sendo encontrado no historico
  - Dados sendo salvos ANTES do fechamento real no MT5
  
SOLUCAO:
  1. Verificar se MT5 esta salvando historico corretamente
  2. Aumentar janela de busca (24h ao inves de 1h)
  3. Adicionar delay antes de buscar historico
  4. Usar position.profit diretamente antes de fechar
""")
else:
    print("""
[OK] Dados MT5 estao sendo coletados corretamente!
  - exit_price preenchido
  - profit_loss preenchido
  - Integracao MT5 funcionando
""")

print("\n" + "="*70)
