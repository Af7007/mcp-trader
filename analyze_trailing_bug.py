#!/usr/bin/env python3
"""
Analisa o bug do trailing stop que permitiu loss de -$1
"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

# Buscar a ordem problema
ticket = 115120603

print("=" * 100)
print(f"ANALISE DO TICKET {ticket} - FECHOU COM -$1.00")
print("=" * 100)

# Dados da trade
cursor.execute('''
    SELECT ticket, symbol, trade_type, volume, entry_price, exit_price,
           sl_price, tp_price, profit_loss, exit_reason, timestamp
    FROM trades
    WHERE ticket = ?
''', (ticket,))

trade = cursor.fetchone()
if trade:
    print("\nDADOS DA TRADE:")
    print(f"  Ticket: {trade[0]}")
    print(f"  Symbol: {trade[1]}")
    print(f"  Type: {trade[2]}")
    print(f"  Volume: {trade[3]}")
    print(f"  Entry Price: {trade[4]:.5f}")
    print(f"  Exit Price: {trade[5]:.5f}")
    print(f"  SL Price: {trade[6]:.5f}")
    print(f"  TP Price: {trade[7]}")
    print(f"  Profit/Loss: ${trade[8]:.2f}")
    print(f"  Exit Reason: {trade[9]}")
    print(f"  Timestamp: {trade[10]}")

    # Analise
    entry = trade[4]
    exit_price = trade[5]
    sl = trade[6]

    print("\n" + "=" * 100)
    print("ANALISE DO PROBLEMA:")
    print("=" * 100)

    if trade[2] == 'SELL':
        print("\nPosicao SELL:")
        print(f"  1. Entry: {entry:.5f}")
        print(f"  2. SL: {sl:.5f} (deve ficar ACIMA da entry)")
        print(f"  3. Exit: {exit_price:.5f}")
        print(f"  4. Diferenca Entry-Exit: {(entry - exit_price):.5f} (negativo = preco subiu = loss)")
        print(f"  5. Diferenca Entry-SL: {(sl - entry):.5f}")

        if exit_price > entry:
            print(f"\n  [PROBLEMA] Preco subiu de {entry:.5f} para {exit_price:.5f}")
            print(f"  [PROBLEMA] Loss: {(exit_price - entry):.5f} pontos")

        if sl > entry:
            print(f"\n  [OK] SL estava acima da entry (protecao inicial correta)")

        if exit_price < sl:
            print(f"\n  [ESTRANHO] Exit price ({exit_price:.5f}) ABAIXO do SL ({sl:.5f})")
            print(f"  [ESTRANHO] Deveria ter fechado no SL, nao abaixo dele")
        elif exit_price == sl:
            print(f"\n  [OK] Fechou exatamente no SL")
        else:
            print(f"\n  [PROBLEMA] Fechou ACIMA do SL!")
            print(f"  [PROBLEMA] SL era {sl:.5f}, mas fechou em {exit_price:.5f}")

# Buscar logs de trailing se existir
try:
    cursor.execute('''
        SELECT * FROM trailing_stops
        WHERE ticket = ?
        ORDER BY timestamp
    ''', (ticket,))

    trailing_logs = cursor.fetchall()

    if trailing_logs:
        print("\n" + "=" * 100)
        print("HISTORICO DE TRAILING STOP:")
        print("=" * 100)

        cursor.execute('PRAGMA table_info(trailing_stops)')
        cols = [c[1] for c in cursor.fetchall()]

        for log in trailing_logs:
            print(f"\n{log[cols.index('timestamp')]}:")
            print(f"  Action: {log[cols.index('action')]}")
            print(f"  Old SL: {log[cols.index('old_sl_price')]}")
            print(f"  New SL: {log[cols.index('new_sl_price')]}")
            print(f"  Current Price: {log[cols.index('current_price')]}")
            print(f"  Profit: ${log[cols.index('profit_dinheiro')]:.2f}")
            print(f"  Reason: {log[cols.index('reason')]}")
    else:
        print("\n[AVISO] Nenhum log de trailing stop encontrado para este ticket")

except sqlite3.OperationalError:
    print("\n[AVISO] Tabela trailing_stops nao existe no banco")

# Verificar se houve outras trades proximas
print("\n" + "=" * 100)
print("TRADES PROXIMAS NO TEMPO:")
print("=" * 100)

cursor.execute('''
    SELECT ticket, symbol, trade_type, entry_price, exit_price, profit_loss,
           exit_reason, timestamp
    FROM trades
    WHERE timestamp BETWEEN
        datetime((SELECT timestamp FROM trades WHERE ticket = ?), '-10 minutes')
        AND
        datetime((SELECT timestamp FROM trades WHERE ticket = ?), '+10 minutes')
    ORDER BY timestamp
''', (ticket, ticket))

nearby_trades = cursor.fetchall()
for t in nearby_trades:
    marker = " <-- PROBLEMA" if t[0] == ticket else ""
    print(f"{t[7]} | Ticket {t[0]} | {t[1]} {t[2]} | Entry {t[3]:.5f} | Exit {t[4]:.5f} | P/L ${t[5]:.2f} | {t[6]}{marker}")

conn.close()

print("\n" + "=" * 100)
print("CONCLUSAO:")
print("=" * 100)
print("""
O trailing stop NUNCA deve permitir que o SL recue (piore).

Para SELL:
- SL deve comecar ACIMA da entry
- SL so pode DESCER (melhorar protecao)
- SL NUNCA pode SUBIR (recuar protecao)

Para BUY:
- SL deve comecar ABAIXO da entry
- SL so pode SUBIR (melhorar protecao)
- SL NUNCA pode DESCER (recuar protecao)

Verificar o codigo em src/agents/gold_loss_zero_simple.py linhas 1541-1555
""")
