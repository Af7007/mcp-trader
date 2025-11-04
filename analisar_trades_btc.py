#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Trades BTC Loss Zero
"""

import sqlite3
from datetime import datetime

def analisar_trades():
    """
    Analisa trades do banco de dados
    """
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    print("="*70)
    print("ANÁLISE DE TRADES BTC LOSS ZERO")
    print("="*70)
    print()

    # 1. Estatísticas gerais
    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'")
    trades_abertos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'CLOSED'")
    trades_fechados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'FAILED'")
    trades_falhados = cursor.fetchone()[0]

    print(f"[1] ESTATÍSTICAS GERAIS")
    print(f"   Total de trades: {total_trades}")
    print(f"   Trades abertos: {trades_abertos}")
    print(f"   Trades fechados: {trades_fechados}")
    print(f"   Trades falhados: {trades_falhados}")
    print()

    # 2. Últimos trades
    cursor.execute('''
        SELECT id, timestamp, trade_type, entry_price, sl_price, tp_price,
               volume, status, reason, comment
        FROM trades
        ORDER BY timestamp DESC
        LIMIT 10
    ''')

    trades = cursor.fetchall()

    print(f"[2] ÚLTIMOS 10 TRADES")
    print(f"{'ID':<5} {'Hora':<10} {'Tipo':<6} {'Entry':<12} {'SL':<12} {'TP':<12} {'Vol':<6} {'Status':<8} {'Razão'}")
    print("-"*110)

    for trade in trades:
        trade_id, timestamp, tipo, entry, sl, tp, volume, status, reason, comment = trade
        hora = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
        print(f"{trade_id:<5} {hora:<10} {tipo:<6} ${entry:<11.2f} ${sl:<11.2f} ${tp:<11.2f} {volume:<6.2f} {status:<8} {reason}")

    print()

    # 3. Análise por tipo
    cursor.execute('''
        SELECT trade_type, COUNT(*), AVG(entry_price)
        FROM trades
        GROUP BY trade_type
    ''')

    print(f"[3] ANÁLISE POR TIPO")
    for row in cursor.fetchall():
        tipo, count, avg_price = row
        print(f"   {tipo}: {count} trades | Preço médio: ${avg_price:.2f}")
    print()

    # 4. Análise por razão (sinal)
    cursor.execute('''
        SELECT reason, COUNT(*), status
        FROM trades
        GROUP BY reason, status
        ORDER BY COUNT(*) DESC
    ''')

    print(f"[4] ANÁLISE POR RAZÃO DO SINAL")
    for row in cursor.fetchall():
        reason, count, status = row
        print(f"   {reason} ({status}): {count} trades")
    print()

    # 5. Últimos ciclos
    cursor.execute('''
        SELECT cycle_number, timestamp, price, signal_type, signal_strength,
               signal_reason, order_result, order_error
        FROM cycles
        WHERE signal_type IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 10
    ''')

    print(f"[5] ÚLTIMOS 10 SINAIS GERADOS")
    print(f"{'Ciclo':<7} {'Hora':<10} {'Preço':<12} {'Tipo':<6} {'Força':<6} {'Razão':<20} {'Resultado'}")
    print("-"*90)

    for row in cursor.fetchall():
        cycle, timestamp, price, stype, strength, reason, result, error = row
        hora = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
        resultado = "OK" if result else (error[:20] if error else "N/A")
        print(f"{cycle:<7} {hora:<10} ${price:<11.2f} {stype or 'N/A':<6} {strength or 'N/A':<6} {reason or 'N/A':<20} {resultado}")

    print()

    # 6. Profit/Loss se disponível
    cursor.execute('''
        SELECT SUM(profit_loss), AVG(profit_loss),
               COUNT(CASE WHEN profit_loss > 0 THEN 1 END),
               COUNT(CASE WHEN profit_loss < 0 THEN 1 END)
        FROM trades
        WHERE profit_loss IS NOT NULL
    ''')

    result = cursor.fetchone()
    if result and result[0] is not None:
        total_pl, avg_pl, wins, losses = result
        print(f"[6] PROFIT/LOSS")
        print(f"   Total P/L: ${total_pl:.2f}")
        print(f"   P/L Médio: ${avg_pl:.2f}")
        print(f"   Trades vencedores: {wins}")
        print(f"   Trades perdedores: {losses}")
        if wins + losses > 0:
            win_rate = (wins / (wins + losses)) * 100
            print(f"   Win Rate: {win_rate:.1f}%")
    else:
        print(f"[6] PROFIT/LOSS")
        print(f"   Nenhum trade fechado com P/L registrado ainda")

    print()
    print("="*70)

    conn.close()

if __name__ == "__main__":
    analisar_trades()
