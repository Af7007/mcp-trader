#!/usr/bin/env python3
"""
Analisa o ultimo trade BTC para diagnosticar problemas
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()

print("=" * 60)
print("ANALISE: Ultimo Trade BTC")
print("=" * 60)
print()

# Buscar deals das ultimas 24h
now = datetime.now()
from_date = now - timedelta(hours=24)

deals = mt5.history_deals_get(
    symbol='BTCUSDc',
    from_date=from_date.isoformat(),
    to_date=now.isoformat()
)

if not deals:
    print("Nenhum deal encontrado nas ultimas 24h")
else:
    # Agrupar deals por position_id
    positions_dict = {}
    for deal in deals:
        pos_id = deal.get('position_id', 0)
        if pos_id not in positions_dict:
            positions_dict[pos_id] = []
        positions_dict[pos_id].append(deal)

    # Pegar a ultima posicao
    last_pos_id = max(positions_dict.keys())
    last_deals = positions_dict[last_pos_id]

    # Ordenar por time
    last_deals.sort(key=lambda d: d['time'])

    print(f"ULTIMA POSICAO (ID: {last_pos_id}):")
    print()

    entry_deal = last_deals[0]
    exit_deal = last_deals[-1] if len(last_deals) > 1 else None

    # Entry
    entry_type = "BUY" if entry_deal['type'] == 0 else "SELL"
    entry_price = entry_deal['price']
    entry_time = datetime.fromtimestamp(entry_deal['time'])
    volume = entry_deal['volume']

    print(f"ABERTURA:")
    print(f"   Ticket: {entry_deal['ticket']}")
    print(f"   Tipo: {entry_type}")
    print(f"   Entry: ${entry_price:.2f}")
    print(f"   Volume: {volume}")
    print(f"   Horario: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if exit_deal:
        # Exit
        exit_price = exit_deal['price']
        exit_time = datetime.fromtimestamp(exit_deal['time'])
        profit = exit_deal['profit']
        duration = (exit_time - entry_time).total_seconds()

        print(f"FECHAMENTO:")
        print(f"   Ticket: {exit_deal['ticket']}")
        print(f"   Exit: ${exit_price:.2f}")
        print(f"   Horario: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duracao: {duration:.0f}s ({duration/60:.1f}min)")
        print(f"   Profit: ${profit:.2f}")
        print()

        # Calcular distancia
        if entry_type == "BUY":
            distance = exit_price - entry_price
            max_possible = exit_price - entry_price
        else:
            distance = entry_price - exit_price
            max_possible = entry_price - exit_price

        print(f"ANALISE:")
        print(f"   Distancia: ${abs(distance):.2f} ({'lucro' if distance > 0 else 'prejuizo'})")
        print(f"   Resultado: {'WIN' if profit > 0 else 'LOSS'}")
        print()

        # Verificar se break-even deveria ter ativado
        if abs(profit) >= 1.50 and profit > 0:
            print(f"   [!] Lucro atingiu ${profit:.2f} >= $1.50")
            print(f"   [!] Break-Even DEVERIA ter ativado!")
            print()

        # Verificar se trailing deveria ter ativado
        if abs(profit) >= 4.00 and profit > 0:
            print(f"   [!] Lucro atingiu ${profit:.2f} >= $4.00")
            print(f"   [!] Trailing Stop DEVERIA ter ativado!")
            print()

        # Verificar entry vs mercado (slippage)
        tick = mt5.get_symbol_info_tick(symbol='BTCUSDc')
        if tick:
            current_bid = tick['bid']
            current_ask = tick['ask']

            print(f"PRECO MERCADO (agora):")
            print(f"   Bid: ${current_bid:.2f}")
            print(f"   Ask: ${current_ask:.2f}")
            print()

    else:
        print("Posicao ainda aberta (sem deal de saida)")

    print()
    print("TODOS OS DEALS DA POSICAO:")
    for i, deal in enumerate(last_deals):
        deal_type = "IN" if deal['entry'] == 0 else "OUT" if deal['entry'] == 1 else "?"
        deal_time = datetime.fromtimestamp(deal['time'])
        print(f"   {i+1}. {deal_type} - ${deal['price']:.2f} - {deal_time.strftime('%H:%M:%S')} - Profit: ${deal['profit']:.2f}")

print()
print("=" * 60)

# Buscar orders (para ver SL)
orders = mt5.history_orders_get(
    symbol='BTCUSDc',
    from_date=from_date.isoformat(),
    to_date=now.isoformat()
)

if orders:
    print()
    print("ORDENS RELACIONADAS (ultimas 5):")
    for order in orders[-5:]:
        order_time = datetime.fromtimestamp(order['time_setup'])
        order_type = order['type']
        type_str = "BUY" if order_type == 0 else "SELL" if order_type == 1 else f"Type {order_type}"
        sl = order.get('sl', 0)
        tp = order.get('tp', 0)

        print(f"   Ticket: {order['ticket']}")
        print(f"   Tipo: {type_str}")
        print(f"   Price: ${order.get('price_open', 0):.2f}")
        if sl:
            print(f"   SL: ${sl:.2f}")
        if tp:
            print(f"   TP: ${tp:.2f}")
        print(f"   Status: {order['state']}")
        print()

print("=" * 60)
