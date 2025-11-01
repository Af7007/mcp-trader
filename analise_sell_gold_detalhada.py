#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise detalhada das operacoes SELL em GOLD (XAUUSDm)
para identificar oportunidades de melhoria
"""

import sqlite3
from collections import defaultdict

DB_FILE = "trading_bot.db"

print('=' * 100)
print('  ANALISE DETALHADA: ESTRATEGIA SELL PARA GOLD (XAUUSDm)')
print('=' * 100)
print()

# Conectar ao banco
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Buscar todos os trades SELL de GOLD
cursor.execute("""
    SELECT ticket, symbol, type, volume, open_price, close_price,
           sl, tp, profit, open_time, close_time
    FROM trades
    WHERE symbol = 'XAUUSDm' AND type = 'SELL'
    ORDER BY ticket DESC
""")

sells = cursor.fetchall()
print(f'Total de SELL trades encontrados: {len(sells)}')
print()

# Separar wins e losses
winners = []
losers = []

for trade in sells:
    ticket, symbol, ttype, volume, open_p, close_p, sl, tp, profit, open_t, close_t = trade
    if profit >= 0:
        winners.append(trade)
    else:
        losers.append(trade)

print(f'Vitorias (SELL): {len(winners)} ({100*len(winners)/len(sells):.1f}%)')
print(f'Derrotas (SELL): {len(losers)} ({100*len(losers)/len(sells):.1f}%)')
print()

# Analise de winners
print('=' * 100)
print('  ANALISE DE VITORIAS (SELL)')
print('=' * 100)
print()

if winners:
    profits_winners = [w[8] for w in winners]
    distances_sl = []
    distances_tp = []
    tp_hit_count = 0
    sl_hit_count = 0

    print('Detalhes de cada vitoria:')
    print('-' * 100)
    print('Ticket      | Entry       | Exit        | SL          | TP          | Profit      | Distance to TP | Distance to SL')
    print('-' * 100)

    for ticket, symbol, ttype, volume, open_p, close_p, sl, tp, profit, open_t, close_t in sorted(winners, key=lambda x: x[0]):
        dist_tp = abs(open_p - tp)
        dist_sl = abs(open_p - sl)
        dist_exit_tp = abs(close_p - tp)
        dist_exit_sl = abs(close_p - sl)

        # Verificar se TP foi atingido
        if ttype == 'SELL':
            tp_hit = close_p <= tp  # Para SELL, TP eh abaixo
            sl_hit = close_p >= sl  # Para SELL, SL eh acima

        distances_tp.append(dist_tp)
        distances_sl.append(dist_sl)

        if tp_hit:
            tp_hit_count += 1
        if sl_hit:
            sl_hit_count += 1

        print(f'{ticket:10d} | ${open_p:10.2f} | ${close_p:10.2f} | ${sl:10.2f} | ${tp:10.2f} | +${profit:10.2f} | ${dist_exit_tp:10.4f} | ${dist_exit_sl:10.4f}')

    print()
    print('Estatisticas das Vitorias SELL:')
    print('-' * 100)
    print(f'Total Wins: {len(winners)}')
    print(f'Lucro Total: +${sum(profits_winners):.2f}')
    print(f'Lucro Medio: +${sum(profits_winners)/len(winners):.2f}')
    print(f'Lucro Min: +${min(profits_winners):.2f}')
    print(f'Lucro Max: +${max(profits_winners):.2f}')
    print(f'Desvio Padrao: ${(sum([(p - sum(profits_winners)/len(winners))**2 for p in profits_winners]) / len(profits_winners))**0.5:.2f}')

    if distances_tp:
        print(f'Distancia Media ao TP: ${sum(distances_tp)/len(distances_tp):.2f}')
        print(f'TP atingido: {tp_hit_count} vezes')

    print()

# Analise de losers
print('=' * 100)
print('  ANALISE DE DERROTAS (SELL)')
print('=' * 100)
print()

if losers:
    profits_losers = [l[8] for l in losers]

    print('Detalhes de cada derrota:')
    print('-' * 100)
    print('Ticket      | Entry       | Exit        | SL          | TP          | Profit      | Hit SL?     | Pips from SL')
    print('-' * 100)

    for ticket, symbol, ttype, volume, open_p, close_p, sl, tp, profit, open_t, close_t in sorted(losers, key=lambda x: x[0]):
        if ttype == 'SELL':
            hit_sl = close_p >= sl
            pips_from_sl = close_p - sl if sl > 0 else 0

        print(f'{ticket:10d} | ${open_p:10.2f} | ${close_p:10.2f} | ${sl:10.2f} | ${tp:10.2f} | -${abs(profit):10.2f} | {str(hit_sl):11s} | ${pips_from_sl:10.4f}')

    print()
    print('Estatisticas das Derrotas SELL:')
    print('-' * 100)
    print(f'Total Losses: {len(losers)}')
    print(f'Prejuizo Total: -${sum([abs(p) for p in profits_losers]):.2f}')
    print(f'Prejuizo Medio: -${sum([abs(p) for p in profits_losers])/len(losers):.2f}')
    print(f'Prejuizo Min: -${min(profits_losers):.2f}')
    print(f'Prejuizo Max: -${max([abs(p) for p in profits_losers]):.2f}')

    print()

# Comparacao Winners vs Losers
print('=' * 100)
print('  COMPARACAO: VITORIAS vs DERROTAS')
print('=' * 100)
print()

if winners and losers:
    avg_win = sum([w[8] for w in winners]) / len(winners)
    avg_loss = sum([abs(l[8]) for l in losers]) / len(losers)

    print(f'Lucro Medio por Vitoria: +${avg_win:.2f}')
    print(f'Prejuizo Medio por Derrota: -${avg_loss:.2f}')
    print(f'Razao Win/Loss: {avg_win/avg_loss:.2f}x')
    print(f'Profit Factor: {sum([w[8] for w in winners]) / sum([abs(l[8]) for l in losers]):.2f}x')
    print()

    total_profit = sum([w[8] for w in winners]) - sum([abs(l[8]) for l in losers])
    print(f'Total P&L: ${total_profit:.2f}')
    print(f'Win Rate: {100*len(winners)/(len(winners)+len(losers)):.1f}%')
    print()

# Analise de Entry Price Patterns
print('=' * 100)
print('  ANALISE DE PADROES DE ENTRADA')
print('=' * 100)
print()

# Agrupar por ranges de preco
price_ranges = {
    '3900-3950': [],
    '3950-4000': [],
    '4000-4050': [],
    '4050-4100': [],
    '4100+': []
}

for trade in sells:
    entry_price = trade[4]
    if entry_price < 3950:
        price_ranges['3900-3950'].append(trade)
    elif entry_price < 4000:
        price_ranges['3950-4000'].append(trade)
    elif entry_price < 4050:
        price_ranges['4000-4050'].append(trade)
    elif entry_price < 4100:
        price_ranges['4050-4100'].append(trade)
    else:
        price_ranges['4100+'].append(trade)

print('Performance por Faixa de Preco (SELL entry):')
print('-' * 100)

for range_name, trades in price_ranges.items():
    if trades:
        wins = len([t for t in trades if t[8] >= 0])
        losses = len([t for t in trades if t[8] < 0])
        total_profit = sum([t[8] for t in trades])
        avg_profit = total_profit / len(trades)

        print(f'{range_name:15s} | {len(trades):2d} trades | Win: {wins:2d} ({100*wins/len(trades):5.1f}%) | Profit: ${total_profit:10.2f} | Avg: ${avg_profit:8.2f}')

print()

# Analise de SL/TP distances
print('=' * 100)
print('  ANALISE DE DISTANCIAS SL/TP')
print('=' * 100)
print()

valid_sells = [t for t in sells if t[6] != 0 and t[7] != 0]  # com SL e TP setados
print(f'SELL trades com SL/TP setados: {len(valid_sells)}/{len(sells)}')
print()

if valid_sells:
    for trade in sorted(valid_sells, key=lambda x: x[0])[:10]:  # Primeiros 10
        ticket, symbol, ttype, volume, open_p, close_p, sl, tp, profit, open_t, close_t = trade

        # Para SELL: entrada em open_p, SL acima, TP abaixo
        risk = abs(sl - open_p)  # distancia ate SL
        reward = abs(open_p - tp)  # distancia ate TP
        ratio = reward / risk if risk > 0 else 0

        actual_move = open_p - close_p  # quanto o preco caiu (positivo eh bom para SELL)

        status = "WIN" if profit >= 0 else "LOSS"

        print(f'Ticket {ticket:10d} | Risk: ${risk:7.2f} | Reward: ${reward:7.2f} | R:R {ratio:5.2f} | Move: ${actual_move:7.2f} | {status}')

print()

# Recomendacoes
print('=' * 100)
print('  RECOMENDACOES PARA MELHORAR SELL STRATEGY')
print('=' * 100)
print()

if winners and losers:
    avg_win = sum([w[8] for w in winners]) / len(winners)
    avg_loss = sum([abs(l[8]) for l in losers]) / len(losers)
    current_rr = avg_win / avg_loss

    print(f'1. RISKxREWARD RATIO:')
    print(f'   - Atual: {current_rr:.2f}x (Ganhando ${avg_win:.2f} para cada ${avg_loss:.2f} perdido)')

    if current_rr < 2.0:
        print(f'   - RECOMENDACAO: Aumentar TP (Take Profit) para melhorar razao')
        print(f'   - Novo TP sugerido: TP atual + 0.50 (para chegar a 2.0x R:R)')
    else:
        print(f'   - Status: BOM - Ratio esta saudavel')

    print()
    print(f'2. TAXA DE ACERTO:')
    print(f'   - Atual: {100*len(winners)/(len(winners)+len(losers)):.1f}% ({len(winners)}/{len(winners)+len(losers)})')
    print(f'   - Objetivo: Manter acima de 60%')

    if 100*len(winners)/(len(winners)+len(losers)) > 70:
        print(f'   - Status: EXCELENTE - Taxa acima de 70%!')

    print()
    print(f'3. CONSISTENCIA:')
    print(f'   - Lucro Medio: ${avg_win:.2f}')
    print(f'   - Desvio: Analisar se profits sao consistentes ou volateis')
    print(f'   - Recomendacao: Manter TP menor e mais consistente vs TP maior mas volatil')

    print()
    print(f'4. GERENCIAMENTO DE RISCO:')
    print(f'   - SL Medio: Necessario analisar distances')
    print(f'   - Recomendacao: ATR-based SL com multiplier 1.5-2.0x')
    print(f'   - Garantir que maior loss nunca > 2x do maior win')

print()
conn.close()

print('=' * 100)
print('FIM DA ANALISE')
print('=' * 100)
