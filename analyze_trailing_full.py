#!/usr/bin/env python3
"""
Analisa o historico COMPLETO de trailing stops do ticket 115120603
"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

ticket = 115120603

print("=" * 150)
print(f"HISTORICO COMPLETO DE TRAILING STOPS - Ticket {ticket}")
print("=" * 150)

# Buscar todos os registros de trailing
cursor.execute('''
    SELECT id, timestamp, trade_id, ticket, symbol, action,
           old_sl_price, new_sl_price, current_price,
           profit_pontos, profit_dinheiro,
           trailing_distance_pontos, trailing_distance_dinheiro,
           reason, agent_version
    FROM trailing_stops
    WHERE ticket = ?
    ORDER BY timestamp
''', (ticket,))

rows = cursor.fetchall()

if not rows:
    print(f"[AVISO] Nenhum registro de trailing stop encontrado para ticket {ticket}")
else:
    print(f"\nTotal de registros: {len(rows)}\n")

    for i, row in enumerate(rows, 1):
        (id_, timestamp, trade_id, ticket, symbol, action,
         old_sl, new_sl, current_price,
         profit_pontos, profit_dinheiro,
         trailing_dist_pontos, trailing_dist_dinheiro,
         reason, agent_version) = row

        print(f"[{i}] ID: {id_} | {timestamp}")
        print(f"    Action: {action}")
        print(f"    Old SL: {old_sl if old_sl else 'None'}")
        print(f"    New SL: {new_sl:.5f}")
        print(f"    Current Price: {current_price:.5f}")
        print(f"    Profit: ${profit_dinheiro:.2f} ({profit_pontos:.1f} pts)")
        print(f"    Trailing Distance: ${trailing_dist_dinheiro:.2f} ({trailing_dist_pontos:.1f} pts)")
        print(f"    Reason: {reason}")

        # ANALISE DO MOVIMENTO
        if action == "ACTIVATED":
            print(f"    >>> Trailing ATIVADO com ${profit_dinheiro:.2f} de lucro")
            print(f"    >>> SL inicial definido em {new_sl:.5f}")
        elif action == "UPDATED":
            if old_sl:
                sl_movement = new_sl - old_sl
                if sl_movement > 0:
                    print(f"    >>> [PROBLEMA] SL SUBIU de {old_sl:.5f} para {new_sl:.5f} (+{sl_movement:.5f})")
                    print(f"    >>> [PROBLEMA] Isso e RECUAR o SL em posicao SELL!")
                elif sl_movement < 0:
                    print(f"    >>> [OK] SL DESCEU de {old_sl:.5f} para {new_sl:.5f} ({sl_movement:.5f})")
                    print(f"    >>> [OK] Melhorando protecao em posicao SELL")
                else:
                    print(f"    >>> SL mantido em {new_sl:.5f}")

        print()

# Buscar dados da trade
cursor.execute('''
    SELECT ticket, trade_type, entry_price, exit_price, sl_price,
           profit_loss, exit_reason, timestamp
    FROM trades
    WHERE ticket = ?
''', (ticket,))

trade = cursor.fetchone()

if trade:
    print("=" * 150)
    print("DADOS DA TRADE:")
    print("=" * 150)
    print(f"Ticket: {trade[0]}")
    print(f"Type: {trade[1]}")
    print(f"Entry: {trade[2]:.5f}")
    print(f"Exit: {trade[3]:.5f}")
    print(f"SL (no close): {trade[4]:.5f}")
    print(f"Profit/Loss: ${trade[5]:.2f}")
    print(f"Exit Reason: {trade[6]}")
    print(f"Close Time: {trade[7]}")

    print("\n" + "=" * 150)
    print("ANALISE:")
    print("=" * 150)

    if trade[1] == "SELL":
        entry = trade[2]
        exit_price = trade[3]
        sl_at_close = trade[4]

        print(f"Posicao SELL:")
        print(f"  Entry: {entry:.5f}")
        print(f"  SL no fechamento: {sl_at_close:.5f}")
        print(f"  Exit Price: {exit_price:.5f}")
        print(f"  Diferenca Entry-Exit: {(entry - exit_price):.5f}")

        # Verificar se trailing logs mostram SL diferente do SL no fechamento
        if rows:
            last_trailing_sl = rows[-1][7]  # new_sl_price
            print(f"\n  Ultimo SL no log de trailing: {last_trailing_sl:.5f}")
            print(f"  SL salvo na trade: {sl_at_close:.5f}")

            if abs(last_trailing_sl - sl_at_close) > 0.01:
                print(f"\n  [PROBLEMA] SL no trailing log DIFERENTE do SL na trade!")
                print(f"  [PROBLEMA] Diferenca: {abs(last_trailing_sl - sl_at_close):.5f}")

conn.close()

print("\n" + "=" * 150)
print("CONCLUSAO:")
print("=" * 150)
print("""
Para posicao SELL:
- SL deve comecar ACIMA da entry
- SL so pode DESCER (melhorar protecao quando preco cai)
- SL NUNCA pode SUBIR (isso seria recuar protecao quando preco sobe)

Se o log mostrar SL SUBINDO em posicao SELL, isso e o BUG!
""")
