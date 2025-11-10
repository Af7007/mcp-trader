"""
Compara dados de ordens Gold entre MT5 (via MCP) e banco de dados
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import sqlite3
from core.mt5_direct_client import get_mt5_client
from datetime import datetime, timedelta
import MetaTrader5 as mt5

def get_db_orders():
    """Busca últimas ordens Gold do banco de dados"""
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    # Buscar ordens Gold das últimas 24 horas
    cursor.execute("""
        SELECT ticket, symbol, type, volume, entry_price, sl_price, tp_price,
               result, open_time, close_time
        FROM trades
        WHERE (symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%')
        ORDER BY open_time DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    orders = []
    for row in rows:
        orders.append({
            'ticket': row[0],
            'symbol': row[1],
            'type': row[2],
            'volume': row[3],
            'entry_price': row[4],
            'sl_price': row[5],
            'tp_price': row[6],
            'result': row[7],
            'open_time': row[8],
            'close_time': row[9]
        })

    return orders

def get_mt5_positions():
    """Busca posições abertas no MT5"""
    mt5 = get_mt5_client()

    try:
        # Posições abertas
        positions = mt5.positions_get(symbol="XAUUSDc")
        if not positions:
            positions = mt5.positions_get(symbol="XAUUSDm")

        return positions if positions else []
    except Exception as e:
        print(f"Erro ao buscar posições: {e}")
        return []

def get_mt5_history():
    """Busca histórico de deals no MT5"""
    mt5 = get_mt5_client()

    try:
        # Últimas 24 horas
        date_from = datetime.now() - timedelta(hours=24)
        date_to = datetime.now()

        # Deals para XAUUSDc
        deals = mt5.history_deals_get(date_from, date_to, group="*XAU*")

        return deals if deals else []
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return []

def get_mt5_orders_history():
    """Busca histórico de orders no MT5"""
    mt5 = get_mt5_client()

    try:
        # Últimas 24 horas
        date_from = datetime.now() - timedelta(hours=24)
        date_to = datetime.now()

        # Orders para XAU
        orders = mt5.history_orders_get(date_from, date_to, group="*XAU*")

        return orders if orders else []
    except Exception as e:
        print(f"Erro ao buscar orders: {e}")
        return []

def main():
    print("=" * 80)
    print("COMPARACAO: MT5 vs BANCO DE DADOS - ORDENS GOLD")
    print("=" * 80)
    print()

    # 1. BANCO DE DADOS
    print("[1] BANCO DE DADOS (btc_trading_logs.db)")
    print("-" * 80)
    db_orders = get_db_orders()

    if db_orders:
        for order in db_orders:
            sl_distance = abs(order['entry_price'] - order['sl_price']) if order['sl_price'] else 0
            print(f"Ticket: {order['ticket']}")
            print(f"  Symbol: {order['symbol']}")
            print(f"  Type: {order['type']}")
            print(f"  Volume: {order['volume']}")
            print(f"  Entry: {order['entry_price']}")
            print(f"  SL: {order['sl_price']} (distancia: ${sl_distance:.2f})")
            print(f"  TP: {order['tp_price']}")
            print(f"  Result: {order['result']}")
            print(f"  Open: {order['open_time']}")
            print()
    else:
        print("  [VAZIO] Nenhuma ordem Gold no banco")

    print()
    print("[2] MT5 - POSICOES ABERTAS")
    print("-" * 80)

    positions = get_mt5_positions()
    if positions:
        for pos in positions:
            print(f"Ticket: {pos.get('ticket')}")
            print(f"  Symbol: {pos.get('symbol')}")
            print(f"  Type: {pos.get('type')}")
            print(f"  Volume: {pos.get('volume')}")
            print(f"  Price Open: {pos.get('price_open')}")
            print(f"  SL: {pos.get('sl')}")
            print(f"  TP: {pos.get('tp')}")
            print(f"  Profit: {pos.get('profit')}")
            print(f"  Time: {pos.get('time')}")

            # Calcular distância SL
            if pos.get('sl') and pos.get('price_open'):
                sl_distance = abs(pos.get('price_open') - pos.get('sl'))
                print(f"  SL Distance: ${sl_distance:.2f}")
            print()
    else:
        print("  [VAZIO] Nenhuma posição Gold aberta no MT5")

    print()
    print("[3] MT5 - HISTORICO DE DEALS (ultimas 24h)")
    print("-" * 80)

    deals = get_mt5_history()
    if deals:
        for deal in deals[:10]:  # Limitar a 10
            print(f"Ticket: {deal.get('ticket')} | Order: {deal.get('order')}")
            print(f"  Symbol: {deal.get('symbol')}")
            print(f"  Type: {deal.get('type')}")
            print(f"  Volume: {deal.get('volume')}")
            print(f"  Price: {deal.get('price')}")
            print(f"  Profit: {deal.get('profit')}")
            print(f"  Time: {deal.get('time')}")
            print()
    else:
        print("  [VAZIO] Nenhum deal Gold nas ultimas 24h")

    print()
    print("[4] MT5 - HISTORICO DE ORDERS (ultimas 24h)")
    print("-" * 80)

    orders = get_mt5_orders_history()
    if orders:
        for order in orders[:10]:  # Limitar a 10
            print(f"Ticket: {order.get('ticket')}")
            print(f"  Symbol: {order.get('symbol')}")
            print(f"  Type: {order.get('type')}")
            print(f"  Volume: {order.get('volume_initial')}")
            print(f"  Price Open: {order.get('price_open')}")
            print(f"  SL: {order.get('sl')}")
            print(f"  TP: {order.get('tp')}")
            print(f"  State: {order.get('state')}")
            print(f"  Time Setup: {order.get('time_setup')}")
            print(f"  Time Done: {order.get('time_done')}")

            # Calcular distância SL
            if order.get('sl') and order.get('price_open'):
                sl_distance = abs(order.get('price_open') - order.get('sl'))
                print(f"  SL Distance: ${sl_distance:.2f}")
            print()
    else:
        print("  [VAZIO] Nenhuma order Gold nas ultimas 24h")

    print()
    print("[5] COMPARACAO DE TICKETS")
    print("-" * 80)

    # Comparar tickets que aparecem em ambos
    db_tickets = {order['ticket']: order for order in db_orders}
    mt5_tickets = {order.get('ticket'): order for order in orders}

    common_tickets = set(db_tickets.keys()) & set(mt5_tickets.keys())

    if common_tickets:
        print(f"Encontrados {len(common_tickets)} tickets em comum:")
        print()

        for ticket in common_tickets:
            db_order = db_tickets[ticket]
            mt5_order = mt5_tickets[ticket]

            print(f"Ticket: {ticket}")
            print(f"  [DB]  Entry: {db_order['entry_price']:.3f} | SL: {db_order['sl_price']:.3f}")
            print(f"  [MT5] Entry: {mt5_order.get('price_open'):.3f} | SL: {mt5_order.get('sl'):.3f}")

            # Comparar SL
            db_sl_dist = abs(db_order['entry_price'] - db_order['sl_price'])
            mt5_sl_dist = abs(mt5_order.get('price_open', 0) - mt5_order.get('sl', 0))

            print(f"  [DB]  SL Distance: ${db_sl_dist:.2f}")
            print(f"  [MT5] SL Distance: ${mt5_sl_dist:.2f}")

            if abs(db_sl_dist - mt5_sl_dist) > 0.01:
                print(f"  [ALERTA] DISCREPANCIA DETECTADA: ${abs(db_sl_dist - mt5_sl_dist):.2f}")
            else:
                print(f"  [OK] Valores consistentes")
            print()
    else:
        print("Nenhum ticket em comum encontrado")
        print()
        print(f"DB tem {len(db_tickets)} tickets")
        print(f"MT5 tem {len(mt5_tickets)} tickets")

    print("=" * 80)

if __name__ == "__main__":
    main()
