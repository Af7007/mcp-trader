#!/usr/bin/env python3
"""
Analisa ultima ordem BTC - VERSAO SIMPLIFICADA
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client
import MetaTrader5 as mt5

mt5_client = get_mt5_client()

print("=" * 60)
print("ANALISE: Ultima Ordem BTC")
print("=" * 60)
print()

# Buscar historico de ordens (ultimas 24h)
from_time = datetime.now() - timedelta(hours=24)
to_time = datetime.now()

# Usar MT5 direto para evitar problemas de API
if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

# Buscar deals
deals = mt5.history_deals_get(from_time, to_time, group="BTCUSDc")

if not deals or len(deals) == 0:
    print("Nenhum deal encontrado nas ultimas 24h")
    deals = mt5.history_deals_get(from_time, to_time)
    if deals:
        btc_deals = [d for d in deals if 'BTC' in d.symbol]
        if btc_deals:
            deals = btc_deals
        else:
            print("Nenhum deal BTC encontrado")
            sys.exit(0)

print(f"Total de deals encontrados: {len(deals)}")
print()

# Agrupar por posicao
positions_dict = {}
for deal in deals:
    pos_id = deal.position_id
    if pos_id not in positions_dict:
        positions_dict[pos_id] = []
    positions_dict[pos_id].append(deal)

# Ultima posicao
last_pos_id = max(positions_dict.keys())
last_deals = sorted(positions_dict[last_pos_id], key=lambda d: d.time)

print(f"ULTIMA POSICAO: #{last_pos_id}")
print("=" * 60)
print()

# Deal de entrada
entry = last_deals[0]
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
if len(last_deals) > 1:
    exit_deal = last_deals[-1]
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
    else:
        distance = entry_price - exit_price

    print(f"ANALISE:")
    print(f"   Movimento: ${abs(distance):.2f} ({'lucro' if distance > 0 else 'prejuizo'})")
    print(f"   Resultado: {'WIN' if profit > 0 else 'LOSS'}")
    print()

    # DIAGNOSTICO BREAK-EVEN / TRAILING
    print("=" * 60)
    print("DIAGNOSTICO: Break-Even e Trailing")
    print("=" * 60)
    print()

    if profit >= 1.50 and profit > 0:
        print(f"[!] PROBLEMA DETECTADO!")
        print(f"    Lucro atingiu ${profit:.2f} >= $1.50")
        print(f"    Break-Even DEVERIA ter ativado (mover SL para entry)")
        print()

    if profit >= 4.00 and profit > 0:
        print(f"[!] PROBLEMA CRITICO!")
        print(f"    Lucro atingiu ${profit:.2f} >= $4.00")
        print(f"    Trailing Stop DEVERIA ter ativado!")
        print()

    # Verificar preco do mercado atual
    tick = mt5.symbol_info_tick("BTCUSDc")
    if tick:
        print(f"MERCADO ATUAL:")
        print(f"   Bid: ${tick.bid:.2f}")
        print(f"   Ask: ${tick.ask:.2f}")
        print()

        # Verificar slippage na entrada
        if entry_type == "BUY":
            expected_price = tick.ask  # Aproximacao
            if abs(entry_price - expected_price) > 50:  # Mais de $50 de diferenca
                print(f"[ALERTA] SLIPPAGE NA ENTRADA!")
                print(f"   Entry: ${entry_price:.2f}")
                print(f"   Ask atual: ${tick.ask:.2f}")
                print(f"   Possivel slippage ou ordem fora do candle")
                print()

else:
    print("Posicao ainda aberta (nao fechou)")

# Buscar ordens relacionadas (para ver SL original)
print()
print("=" * 60)
print("ORDENS RELACIONADAS:")
print("=" * 60)
print()

orders = mt5.history_orders_get(from_time, to_time, group="BTCUSDc")
if not orders:
    orders = mt5.history_orders_get(from_time, to_time)
    if orders:
        orders = [o for o in orders if 'BTC' in o.symbol]

if orders:
    # Filtrar ordens da posicao
    pos_orders = [o for o in orders if o.position_id == last_pos_id]

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

            # Calcular loss em dolares
            sl_points = sl_distance / 0.01  # Point size BTC
            sl_loss = sl_points * 0.01 * volume  # Point value * volume

            print(f"   SL Distance: ${sl_distance:.2f}")
            print(f"   SL Loss: ${sl_loss:.2f}")
            print()

print("=" * 60)

mt5.shutdown()
