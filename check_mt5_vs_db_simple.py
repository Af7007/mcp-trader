"""
Compara dados de ordens Gold entre MT5 e banco de dados - Versao Simplificada
"""
import sqlite3
import MetaTrader5 as mt5
from datetime import datetime, timedelta

def init_mt5():
    """Inicializa MT5"""
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        print("Certifique-se que o MetaTrader 5 esta aberto!")
        return False
    print("[OK] MT5 inicializado")
    return True

def get_db_orders():
    """Busca ultimas ordens Gold do banco de dados"""
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    # Buscar ordens Gold
    cursor.execute("""
        SELECT ticket, symbol, trade_type, volume, entry_price, sl_price, tp_price,
               profit_loss, timestamp, exit_price, status
        FROM trades
        WHERE (symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%')
        ORDER BY timestamp DESC
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
            'exit_price': row[9],
            'status': row[10]
        })

    return orders

def main():
    print("=" * 80)
    print("COMPARACAO: MT5 vs BANCO DE DADOS - ORDENS GOLD")
    print("=" * 80)
    print()

    # Inicializar MT5
    if not init_mt5():
        return

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
            print(f"  Entry: {order['entry_price']:.3f}")
            print(f"  SL: {order['sl_price']:.3f} (distancia: ${sl_distance:.3f})")
            print(f"  TP: {order['tp_price']}")
            print(f"  Result: {order['result']}")
            print(f"  Open: {order['open_time']}")
            print()
    else:
        print("  [VAZIO] Nenhuma ordem Gold no banco")

    print()
    print("[2] MT5 - POSICOES ABERTAS (XAUUSDc)")
    print("-" * 80)

    # Tentar XAUUSDc
    positions = mt5.positions_get(symbol="XAUUSDc")
    if not positions:
        # Tentar XAUUSDm
        positions = mt5.positions_get(symbol="XAUUSDm")
        if positions:
            print("  [INFO] Encontradas posicoes em XAUUSDm")

    if positions:
        for pos in positions:
            print(f"Ticket: {pos.ticket}")
            print(f"  Symbol: {pos.symbol}")
            print(f"  Type: {pos.type} ({'BUY' if pos.type == 0 else 'SELL'})")
            print(f"  Volume: {pos.volume}")
            print(f"  Price Open: {pos.price_open:.3f}")
            print(f"  Current Price: {pos.price_current:.3f}")
            print(f"  SL: {pos.sl:.3f}")
            print(f"  TP: {pos.tp:.3f}")
            print(f"  Profit: ${pos.profit:.2f}")
            print(f"  Time: {datetime.fromtimestamp(pos.time)}")

            # Calcular distancia SL
            if pos.sl and pos.price_open:
                sl_distance = abs(pos.price_open - pos.sl)
                print(f"  SL Distance: ${sl_distance:.3f}")
            print()
    else:
        print("  [VAZIO] Nenhuma posicao Gold aberta no MT5")

    print()
    print("[3] MT5 - HISTORICO DE ORDERS (ultimas 24h)")
    print("-" * 80)

    # Buscar historico de orders
    date_from = datetime.now() - timedelta(hours=24)
    date_to = datetime.now()

    # Tentar XAUUSDc
    orders = mt5.history_orders_get(date_from, date_to, group="*XAU*")

    if orders:
        print(f"  [INFO] Encontradas {len(orders)} orders no historico")
        print()

        for order in orders[:10]:  # Limitar a 10
            print(f"Ticket: {order.ticket}")
            print(f"  Symbol: {order.symbol}")
            print(f"  Type: {order.type}")
            print(f"  Type Description: {order.type_description if hasattr(order, 'type_description') else 'N/A'}")
            print(f"  Volume: {order.volume_initial}")
            print(f"  Price Open: {order.price_open:.3f}")
            print(f"  SL: {order.sl:.3f}")
            print(f"  TP: {order.tp:.3f}")
            print(f"  State: {order.state}")
            print(f"  Time Setup: {datetime.fromtimestamp(order.time_setup)}")
            print(f"  Time Done: {datetime.fromtimestamp(order.time_done) if order.time_done else 'N/A'}")

            # Calcular distancia SL
            if order.sl and order.price_open:
                sl_distance = abs(order.price_open - order.sl)
                print(f"  SL Distance: ${sl_distance:.3f}")
            print()
    else:
        print("  [VAZIO] Nenhuma order Gold nas ultimas 24h")

    print()
    print("[4] MT5 - HISTORICO DE DEALS (ultimas 24h)")
    print("-" * 80)

    # Buscar historico de deals
    deals = mt5.history_deals_get(date_from, date_to, group="*XAU*")

    if deals:
        print(f"  [INFO] Encontrados {len(deals)} deals no historico")
        print()

        # Agrupar deals por order
        deal_groups = {}
        for deal in deals:
            order_id = deal.order
            if order_id not in deal_groups:
                deal_groups[order_id] = []
            deal_groups[order_id].append(deal)

        print(f"  [INFO] {len(deal_groups)} orders unicas com deals")
        print()

        for order_id, order_deals in list(deal_groups.items())[:5]:  # Primeiras 5 orders
            print(f"Order: {order_id}")
            for deal in order_deals:
                print(f"  Deal Ticket: {deal.ticket}")
                print(f"    Symbol: {deal.symbol}")
                print(f"    Type: {deal.type} ({'IN' if deal.entry == 0 else 'OUT' if deal.entry == 1 else 'INOUT'})")
                print(f"    Volume: {deal.volume}")
                print(f"    Price: {deal.price:.3f}")
                print(f"    Profit: ${deal.profit:.2f}")
                print(f"    Time: {datetime.fromtimestamp(deal.time)}")
                print()
    else:
        print("  [VAZIO] Nenhum deal Gold nas ultimas 24h")

    print()
    print("[5] COMPARACAO DETALHADA - TICKETS EM COMUM")
    print("-" * 80)

    # Comparar tickets que aparecem em ambos (DB e MT5)
    db_tickets = {order['ticket']: order for order in db_orders}

    if orders:
        mt5_orders_dict = {order.ticket: order for order in orders}

        common_tickets = set(db_tickets.keys()) & set(mt5_orders_dict.keys())

        if common_tickets:
            print(f"Encontrados {len(common_tickets)} tickets em comum:")
            print()

            for ticket in sorted(common_tickets, reverse=True):
                db_order = db_tickets[ticket]
                mt5_order = mt5_orders_dict[ticket]

                print(f"Ticket: {ticket}")
                print(f"  [DB]  Entry: {db_order['entry_price']:.3f} | SL: {db_order['sl_price']:.3f} | Volume: {db_order['volume']}")
                print(f"  [MT5] Entry: {mt5_order.price_open:.3f} | SL: {mt5_order.sl:.3f} | Volume: {mt5_order.volume_initial}")

                # Comparar SL
                db_sl_dist = abs(db_order['entry_price'] - db_order['sl_price']) if db_order['sl_price'] else 0
                mt5_sl_dist = abs(mt5_order.price_open - mt5_order.sl) if mt5_order.sl else 0

                print(f"  [DB]  SL Distance: ${db_sl_dist:.3f}")
                print(f"  [MT5] SL Distance: ${mt5_sl_dist:.3f}")

                if abs(db_sl_dist - mt5_sl_dist) > 0.1:
                    print(f"  [ALERTA] *** DISCREPANCIA DETECTADA: ${abs(db_sl_dist - mt5_sl_dist):.3f} ***")
                else:
                    print(f"  [OK] Valores consistentes")

                # Comparar Entry Price
                entry_diff = abs(db_order['entry_price'] - mt5_order.price_open)
                if entry_diff > 0.1:
                    print(f"  [ALERTA] *** ENTRY PRICE DIFERENTE: ${entry_diff:.3f} ***")

                print()
        else:
            print("Nenhum ticket em comum encontrado")
            print()
            print(f"DB tem {len(db_tickets)} tickets: {list(db_tickets.keys())[:5]}")
            if mt5_orders_dict:
                print(f"MT5 tem {len(mt5_orders_dict)} tickets: {list(mt5_orders_dict.keys())[:5]}")

    print("=" * 80)

    # Shutdown MT5
    mt5.shutdown()

if __name__ == "__main__":
    main()
