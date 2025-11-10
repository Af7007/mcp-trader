#!/usr/bin/env python3
"""
Analisa a PENULTIMA ordem BTC (anterior a atual)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

print("=" * 60)
print("ANALISE: Penultima Ordem BTC")
print("=" * 60)
print()

# Buscar deals das ultimas 24h
from_time = datetime.now() - timedelta(hours=24)
to_time = datetime.now()

deals = mt5.history_deals_get(from_time, to_time)

if not deals:
    print("Nenhum deal encontrado")
    sys.exit(0)

# Filtrar deals BTC
btc_deals = [d for d in deals if 'BTC' in d.symbol]

if len(btc_deals) < 2:
    print(f"Apenas {len(btc_deals)} deals BTC encontrados, precisa de pelo menos 2")
    sys.exit(0)

# Agrupar por posicao
positions_dict = {}
for deal in btc_deals:
    pos_id = deal.position_id
    if pos_id not in positions_dict:
        positions_dict[pos_id] = []
    positions_dict[pos_id].append(deal)

# Ordenar posicoes por ID
sorted_positions = sorted(positions_dict.keys())

if len(sorted_positions) < 2:
    print(f"Apenas {len(sorted_positions)} posicoes encontradas, precisa de pelo menos 2")
    sys.exit(0)

# Penultima posicao (segunda mais recente)
second_last_pos_id = sorted_positions[-2]
second_last_deals = sorted(positions_dict[second_last_pos_id], key=lambda d: d.time)

print(f"PENULTIMA POSICAO: #{second_last_pos_id}")
print("=" * 60)
print()

# Deal de entrada
entry = second_last_deals[0]
entry_type = "BUY" if entry.type == mt5.ORDER_TYPE_BUY else "SELL"
entry_price = entry.price
entry_time = datetime.fromtimestamp(entry.time)
volume = entry.volume

print(f"ENTRADA:")
print(f"   Tipo: {entry_type}")
print(f"   Preco: ${entry_price:.2f}")
print(f"   Volume: {volume}")
print(f"   Horario: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   Ticket: {entry.ticket}")
print()

# Deal de saida (se existir)
if len(second_last_deals) > 1:
    exit_deal = second_last_deals[-1]
    exit_price = exit_deal.price
    exit_time = datetime.fromtimestamp(exit_deal.time)
    profit = exit_deal.profit
    duration = (exit_time - entry_time).total_seconds()

    print(f"SAIDA:")
    print(f"   Preco: ${exit_price:.2f}")
    print(f"   Horario: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Duracao: {duration:.0f}s ({duration/60:.1f}min)")
    print(f"   Profit: ${profit:.2f}")
    print(f"   Ticket: {exit_deal.ticket}")
    print()

    # Analise
    if entry_type == "BUY":
        distance = exit_price - entry_price
        max_possible = exit_price - entry_price
    else:
        distance = entry_price - exit_price
        max_possible = entry_price - exit_price

    print(f"ANALISE:")
    print(f"   Movimento: ${abs(distance):.2f} ({'lucro' if distance > 0 else 'prejuizo'})")
    print(f"   Resultado: {'WIN' if profit > 0 else 'LOSS'}")
    print()

    # DIAGNOSTICO BREAK-EVEN / TRAILING
    print("=" * 60)
    print("DIAGNOSTICO: Break-Even e Trailing")
    print("=" * 60)
    print()

    # Calcular lucro maximo possivel
    # Buscar todas as velas M1 durante a duracao do trade
    rates_m1 = mt5.copy_rates_range("BTCUSDc", mt5.TIMEFRAME_M1, entry_time, exit_time)

    if rates_m1 is not None and len(rates_m1) > 0:
        if entry_type == "BUY":
            # BUY: lucro maximo quando preco atingiu maior high
            max_high = max([r[2] for r in rates_m1])
            max_profit_points = (max_high - entry_price) / 0.01
            max_profit_dollars = max_profit_points * 0.01 * volume

            print(f"LUCRO MAXIMO POSSIVEL:")
            print(f"   Preco maximo: ${max_high:.2f}")
            print(f"   Lucro maximo: ${max_profit_dollars:.2f}")
            print()

            if max_profit_dollars >= 1.50:
                print(f"[!] LUCRO ATINGIU ${max_profit_dollars:.2f} >= $1.50")
                print(f"[!] Break-Even DEVERIA ter ativado!")
                print()

            if max_profit_dollars >= 4.00:
                print(f"[!] LUCRO ATINGIU ${max_profit_dollars:.2f} >= $4.00")
                print(f"[!] Trailing Stop DEVERIA ter ativado!")
                print()

        else:  # SELL
            # SELL: lucro maximo quando preco atingiu menor low
            min_low = min([r[3] for r in rates_m1])
            max_profit_points = (entry_price - min_low) / 0.01
            max_profit_dollars = max_profit_points * 0.01 * volume

            print(f"LUCRO MAXIMO POSSIVEL:")
            print(f"   Preco minimo: ${min_low:.2f}")
            print(f"   Lucro maximo: ${max_profit_dollars:.2f}")
            print()

            if max_profit_dollars >= 1.50:
                print(f"[!] LUCRO ATINGIU ${max_profit_dollars:.2f} >= $1.50")
                print(f"[!] Break-Even DEVERIA ter ativado!")
                print()

            if max_profit_dollars >= 4.00:
                print(f"[!] LUCRO ATINGIU ${max_profit_dollars:.2f} >= $4.00")
                print(f"[!] Trailing Stop DEVERIA ter ativado!")
                print()

    # Buscar ordens relacionadas (para ver SL)
    print("=" * 60)
    print("ORDENS RELACIONADAS:")
    print("=" * 60)
    print()

    orders = mt5.history_orders_get(from_time, to_time)
    if orders:
        orders = [o for o in orders if 'BTC' in o.symbol]
        pos_orders = [o for o in orders if o.position_id == second_last_pos_id]

        for order in pos_orders:
            order_time = datetime.fromtimestamp(order.time_setup)
            type_str = "BUY" if order.type == mt5.ORDER_TYPE_BUY else "SELL" if order.type == mt5.ORDER_TYPE_SELL else f"Type {order.type}"

            print(f"Order #{order.ticket}:")
            print(f"   Tipo: {type_str}")
            print(f"   Preco: ${order.price_open:.2f}")
            print(f"   SL: ${order.sl:.2f}" if order.sl else "   SL: Nenhum")
            print(f"   TP: ${order.tp:.2f}" if order.tp else "   TP: Nenhum")
            print(f"   Status: {order.state}")
            print(f"   Horario: {order_time.strftime('%H:%M:%S')}")
            print()

            # Calcular SL em dolares
            if order.sl:
                if entry_type == "BUY":
                    sl_distance = entry_price - order.sl
                else:
                    sl_distance = order.sl - entry_price

                sl_points = sl_distance / 0.01
                sl_loss = sl_points * 0.01 * volume

                print(f"   SL Distance: ${sl_distance:.2f}")
                print(f"   SL Loss: ${sl_loss:.2f}")
                print()

else:
    print("Posicao ainda aberta (sem deal de saida)")

print("=" * 60)

mt5.shutdown()
