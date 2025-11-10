"""
Consulta historico de ordens Gold direto do MT5
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

def init_mt5():
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        return False
    print("[OK] MT5 inicializado")
    return True

def main():
    print("=" * 80)
    print("HISTORICO DE ORDENS GOLD - MT5")
    print("=" * 80)
    print()

    if not init_mt5():
        return

    # Buscar ultimas 48 horas
    date_from = datetime.now() - timedelta(hours=48)
    date_to = datetime.now()

    print(f"Periodo: {date_from.strftime('%Y-%m-%d %H:%M')} ate {date_to.strftime('%Y-%m-%d %H:%M')}")
    print()

    # 1. POSICOES ABERTAS
    print("[1] POSICOES ABERTAS")
    print("-" * 80)

    positions = mt5.positions_get(symbol="XAUUSDc")
    if not positions:
        positions = mt5.positions_get(symbol="XAUUSDm")

    if positions:
        for pos in positions:
            sl_dist = abs(pos.price_open - pos.sl) if pos.sl else 0
            print(f"Ticket: {pos.ticket}")
            print(f"  Type: {'BUY' if pos.type == 0 else 'SELL'}")
            print(f"  Volume: {pos.volume}")
            print(f"  Entry: {pos.price_open:.3f}")
            print(f"  Current: {pos.price_current:.3f}")
            print(f"  SL: {pos.sl:.3f} (distancia: ${sl_dist:.3f})")
            print(f"  TP: {pos.tp:.3f}")
            print(f"  Profit: ${pos.profit:.2f}")
            print(f"  Time: {datetime.fromtimestamp(pos.time)}")
            print()
    else:
        print("  Nenhuma posicao aberta")
        print()

    # 2. HISTORICO DE ORDERS
    print("[2] HISTORICO DE ORDERS (ultimas 48h)")
    print("-" * 80)

    orders = mt5.history_orders_get(date_from, date_to, group="*XAU*")

    if orders:
        print(f"Total: {len(orders)} orders")
        print()

        # Mostrar ultimas 15
        for order in orders[-15:]:
            sl_dist = abs(order.price_open - order.sl) if (order.price_open and order.sl) else 0

            print(f"Ticket: {order.ticket}")
            print(f"  Time: {datetime.fromtimestamp(order.time_setup)}")
            print(f"  Type: {order.type} ({'BUY' if order.type == 0 else 'SELL' if order.type == 1 else 'CLOSE'})")
            print(f"  Volume: {order.volume_initial}")
            print(f"  Price Open: {order.price_open:.3f}")
            print(f"  SL: {order.sl:.3f}")
            print(f"  TP: {order.tp:.3f}")

            if sl_dist > 0:
                print(f"  SL Distance: ${sl_dist:.3f}")

            print(f"  State: {order.state} ({['STARTED','PLACED','CANCELED','PARTIAL','FILLED','REJECTED','EXPIRED','REQUEST_ADD','REQUEST_MODIFY','REQUEST_CANCEL'][order.state] if order.state < 10 else 'UNKNOWN'})")
            print(f"  Comment: {order.comment}")
            print()
    else:
        print("  Nenhuma order no historico")
        print()

    # 3. HISTORICO DE DEALS (execucoes)
    print("[3] HISTORICO DE DEALS - EXECUCOES REAIS (ultimas 48h)")
    print("-" * 80)

    deals = mt5.history_deals_get(date_from, date_to, group="*XAU*")

    if deals:
        print(f"Total: {len(deals)} deals")
        print()

        # Agrupar por order
        deal_groups = {}
        for deal in deals:
            order_id = deal.order
            if order_id not in deal_groups:
                deal_groups[order_id] = []
            deal_groups[order_id].append(deal)

        print(f"Agrupados em {len(deal_groups)} orders unicas")
        print()

        # Mostrar ultimas 10 orders
        for order_id in list(deal_groups.keys())[-10:]:
            order_deals = deal_groups[order_id]

            print(f"Order: {order_id}")

            entry_deal = None
            exit_deal = None

            for deal in order_deals:
                if deal.entry == 0:  # ENTRY_IN
                    entry_deal = deal
                elif deal.entry == 1:  # ENTRY_OUT
                    exit_deal = deal

                print(f"  Deal: {deal.ticket}")
                print(f"    Type: {'BUY' if deal.type == 0 else 'SELL'} | Entry: {'IN' if deal.entry == 0 else 'OUT' if deal.entry == 1 else 'INOUT'}")
                print(f"    Price: {deal.price:.3f} | Volume: {deal.volume}")
                print(f"    Profit: ${deal.profit:.2f}")
                print(f"    Time: {datetime.fromtimestamp(deal.time)}")
                print(f"    Comment: {deal.comment}")

            # Calcular SL real se tiver entrada e saida
            if entry_deal and exit_deal:
                sl_real = abs(entry_deal.price - exit_deal.price)
                print(f"  >>> SL REAL EXECUTADO: ${sl_real:.3f}")
                print(f"  >>> PROFIT FINAL: ${exit_deal.profit:.2f}")

                # Verificar se foi SL ou TP
                if exit_deal.profit < 0:
                    print(f"  >>> RESULTADO: STOP LOSS (perda)")
                elif exit_deal.profit > 0:
                    print(f"  >>> RESULTADO: TAKE PROFIT ou Trailing (lucro)")
                else:
                    print(f"  >>> RESULTADO: Break-even")

            print()
    else:
        print("  Nenhum deal no historico")
        print()

    # 4. ESTATISTICAS
    print("[4] ESTATISTICAS")
    print("-" * 80)

    if deals:
        total_profit = sum(d.profit for d in deals)
        wins = [d for d in deals if d.profit > 0 and d.entry == 1]
        losses = [d for d in deals if d.profit < 0 and d.entry == 1]

        print(f"Total Profit: ${total_profit:.2f}")
        print(f"Wins: {len(wins)}")
        print(f"Losses: {len(losses)}")

        if wins:
            avg_win = sum(d.profit for d in wins) / len(wins)
            print(f"Avg Win: ${avg_win:.2f}")

        if losses:
            avg_loss = sum(d.profit for d in losses) / len(losses)
            print(f"Avg Loss: ${avg_loss:.2f}")

        if (len(wins) + len(losses)) > 0:
            win_rate = len(wins) / (len(wins) + len(losses)) * 100
            print(f"Win Rate: {win_rate:.1f}%")

    print()
    print("=" * 80)

    mt5.shutdown()

if __name__ == "__main__":
    main()
