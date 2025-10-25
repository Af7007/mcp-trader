#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise completa dos trades de BTC do banco de dados
Identifica padrões de perdas e sugere melhorias
"""

import sys
import sqlite3
from datetime import datetime
from collections import defaultdict

# Configurar encoding UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Conectar ao banco
conn = sqlite3.connect('C:/mcp-trader/trading_bot.db')
cursor = conn.cursor()

print("="*80)
print("📊 ANÁLISE DE TRADES - BTCUSDm")
print("="*80)
print()

# 1. ESTATÍSTICAS GERAIS
print("[1] ESTATÍSTICAS GERAIS")
print("-"*80)

cursor.execute("""
    SELECT
        COUNT(*) as total_trades,
        SUM(CASE WHEN result > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN result <= 0 THEN 1 ELSE 0 END) as losses,
        ROUND(AVG(result), 2) as avg_profit,
        ROUND(SUM(result), 2) as total_profit,
        ROUND(MIN(result), 2) as worst_loss,
        ROUND(MAX(result), 2) as best_win,
        ROUND(AVG(CASE WHEN result > 0 THEN result ELSE NULL END), 2) as avg_win,
        ROUND(AVG(CASE WHEN result <= 0 THEN result ELSE NULL END), 2) as avg_loss
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed'
""")

stats = cursor.fetchone()
if stats and stats[0] > 0:
    total, wins, losses, avg_profit, total_profit, worst_loss, best_win, avg_win, avg_loss = stats
    win_rate = (wins / total * 100) if total > 0 else 0

    print(f"Total de Operações: {total}")
    print(f"✅ Ganhos: {wins} ({win_rate:.1f}%)")
    print(f"❌ Perdas: {losses} ({100-win_rate:.1f}%)")
    print(f"💰 Lucro Total: ${total_profit:+.2f}")
    print(f"📊 Lucro Médio: ${avg_profit:+.2f}")
    print(f"🏆 Melhor Ganho: ${best_win:+.2f}")
    print(f"💔 Pior Perda: ${worst_loss:+.2f}")
    print(f"📈 Média de Ganhos: ${avg_win:.2f}" if avg_win else "📈 Média de Ganhos: N/A")
    print(f"📉 Média de Perdas: ${avg_loss:.2f}" if avg_loss else "📉 Média de Perdas: N/A")

    # Risk/Reward Ratio
    if avg_loss and avg_loss != 0:
        rr_ratio = abs(avg_win / avg_loss) if avg_win else 0
        print(f"⚖️  Risk/Reward Ratio: {rr_ratio:.2f}:1")
else:
    print("❌ Nenhum trade encontrado para BTCUSDm")
    conn.close()
    sys.exit(0)

print()

# 2. ANÁLISE POR TIPO DE OPERAÇÃO
print("[2] ANÁLISE POR TIPO (BUY vs SELL)")
print("-"*80)

cursor.execute("""
    SELECT
        CASE
            WHEN entry_price < (SELECT AVG(entry_price) FROM trades WHERE symbol = 'BTCUSDm' AND status = 'closed')
            THEN 'BUY'
            ELSE 'SELL'
        END as type,
        COUNT(*) as total,
        SUM(CASE WHEN result > 0 THEN 1 ELSE 0 END) as wins,
        ROUND(AVG(result), 2) as avg_profit,
        ROUND(SUM(result), 2) as total_profit
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed'
    GROUP BY type
""")

for row in cursor.fetchall():
    trade_type, total, wins, avg_profit, total_profit = row
    win_rate = (wins / total * 100) if total > 0 else 0
    print(f"{trade_type}:")
    print(f"  Operações: {total} | Win Rate: {win_rate:.1f}% | Lucro: ${total_profit:+.2f} | Média: ${avg_profit:+.2f}")

print()

# 3. DISTRIBUIÇÃO DE LUCROS/PERDAS
print("[3] DISTRIBUIÇÃO DE RESULTADOS")
print("-"*80)

cursor.execute("""
    SELECT
        CASE
            WHEN result >= 6 THEN 'Lucro Alto (≥$6)'
            WHEN result > 0 AND result < 6 THEN 'Lucro Baixo ($0-$6)'
            WHEN result > -6 AND result <= 0 THEN 'Perda Pequena ($0 a -$6)'
            ELSE 'Perda Grande (< -$6)'
        END as categoria,
        COUNT(*) as quantidade,
        ROUND(AVG(result), 2) as media,
        ROUND(SUM(result), 2) as total
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed'
    GROUP BY categoria
    ORDER BY media DESC
""")

print(f"{'Categoria':<25} {'Quantidade':<12} {'Média':<12} {'Total':<12}")
print("-"*80)
for row in cursor.fetchall():
    categoria, qtd, media, total = row
    print(f"{categoria:<25} {qtd:<12} ${media:+.2f}      ${total:+.2f}")

print()

# 4. ANÁLISE DE DURAÇÃO
print("[4] ANÁLISE DE DURAÇÃO DAS OPERAÇÕES")
print("-"*80)

cursor.execute("""
    SELECT
        ticket,
        CASE
            WHEN entry_price < tp_price THEN 'BUY'
            ELSE 'SELL'
        END as type,
        result,
        open_time,
        close_time,
        ROUND((julianday(close_time) - julianday(open_time)) * 24 * 60, 1) as duration_minutes
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed' AND close_time IS NOT NULL
    ORDER BY duration_minutes DESC
    LIMIT 10
""")

print("10 Operações Mais Longas:")
for row in cursor.fetchall():
    ticket, trade_type, profit, open_time, close_time, duration = row
    print(f"  Ticket {ticket} | {trade_type} | {duration:.1f}min | ${profit:+.2f}")

print()

# 5. PADRÃO DE PERDAS CONSECUTIVAS
print("[5] ANÁLISE DE STREAKS")
print("-"*80)

cursor.execute("""
    SELECT
        ticket,
        CASE
            WHEN entry_price < tp_price THEN 'BUY'
            ELSE 'SELL'
        END as type,
        result,
        open_time,
        close_time
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed'
    ORDER BY open_time
""")

trades = cursor.fetchall()
losing_streak = 0
max_losing_streak = 0
winning_streak = 0
max_winning_streak = 0

for trade in trades:
    profit = trade[2]
    if profit > 0:
        winning_streak += 1
        losing_streak = 0
        max_winning_streak = max(max_winning_streak, winning_streak)
    else:
        losing_streak += 1
        winning_streak = 0
        max_losing_streak = max(max_losing_streak, losing_streak)

print(f"Maior Winning Streak: {max_winning_streak}")
print(f"Maior Losing Streak: {max_losing_streak}")

print()

# 6. ÚLTIMAS 20 OPERAÇÕES
print("[6] ÚLTIMAS 20 OPERAÇÕES")
print("-"*80)

cursor.execute("""
    SELECT
        ticket,
        CASE
            WHEN entry_price < tp_price THEN 'BUY'
            ELSE 'SELL'
        END as type,
        volume,
        entry_price,
        COALESCE((SELECT entry_price FROM trades t2 WHERE t2.ticket = trades.ticket AND t2.close_time IS NOT NULL), 0) as close_price,
        result,
        strftime('%Y-%m-%d %H:%M', open_time) as open_time
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed'
    ORDER BY open_time DESC
    LIMIT 20
""")

print(f"{'Ticket':<10} {'Tipo':<6} {'Volume':<8} {'Open':<12} {'Close':<12} {'Profit':<10} {'Data/Hora':<20}")
print("-"*80)
for row in cursor.fetchall():
    ticket, ttype, vol, open_p, close_p, profit, open_t = row
    emoji = "✅" if profit > 0 else "❌"
    print(f"{ticket:<10} {ttype:<6} {vol:<8.2f} ${open_p:<11.2f} ${close_p:<11.2f} {emoji} ${profit:+.2f}    {open_t}")

print()

# 7. ANÁLISE DE SL vs TP
print("[7] ANÁLISE DE STOP LOSS vs TAKE PROFIT")
print("-"*80)

cursor.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN result >= 5.5 THEN 1 ELSE 0 END) as hit_tp,
        SUM(CASE WHEN result < 0 THEN 1 ELSE 0 END) as hit_sl
    FROM trades
    WHERE symbol = 'BTCUSDm' AND status = 'closed' AND tp_price IS NOT NULL AND sl_price IS NOT NULL
""")

sl_tp_stats = cursor.fetchone()
if sl_tp_stats and sl_tp_stats[0] > 0:
    total, hit_tp, hit_sl = sl_tp_stats
    print(f"Total de operações com SL/TP: {total}")
    print(f"Bateram TP: {hit_tp} ({hit_tp/total*100:.1f}%)")
    print(f"Bateram SL: {hit_sl} ({hit_sl/total*100:.1f}%)")

print()
print("="*80)

conn.close()

print()
print("💡 RECOMENDAÇÕES SERÃO APRESENTADAS APÓS ANÁLISE DOS DADOS")
