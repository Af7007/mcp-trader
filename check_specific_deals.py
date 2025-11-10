"""
Busca DEALS especificos das orders Gold suspeitas
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

# Orders suspeitas
TICKETS = [114804259, 114584296, 114567031]

def init_mt5():
    """Inicializa MT5"""
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        return False
    print("[OK] MT5 inicializado")
    return True

def main():
    print("=" * 80)
    print("ANALISE DETALHADA - DEALS DAS ORDERS SUSPEITAS")
    print("=" * 80)
    print()

    if not init_mt5():
        return

    # Buscar deals das ultimas 48 horas
    date_from = datetime.now() - timedelta(hours=48)
    date_to = datetime.now()

    print(f"Buscando deals de {date_from} ate {date_to}")
    print()

    # Buscar todos os deals Gold
    deals = mt5.history_deals_get(date_from, date_to, group="*XAU*")

    if not deals:
        print("Nenhum deal encontrado!")
        mt5.shutdown()
        return

    print(f"Total de deals Gold: {len(deals)}")
    print()

    # Filtrar deals das orders suspeitas
    for ticket in TICKETS:
        print("=" * 80)
        print(f"ORDER TICKET: {ticket}")
        print("=" * 80)

        order_deals = [d for d in deals if d.order == ticket]

        if not order_deals:
            print(f"  [ALERTA] Nenhum deal encontrado para order {ticket}")
            print()
            continue

        print(f"  [INFO] {len(order_deals)} deal(s) encontrado(s)")
        print()

        for i, deal in enumerate(order_deals, 1):
            print(f"  Deal {i}:")
            print(f"    Deal Ticket: {deal.ticket}")
            print(f"    Order: {deal.order}")
            print(f"    Position ID: {deal.position_id}")
            print(f"    Symbol: {deal.symbol}")
            print(f"    Type: {deal.type} ({'BUY' if deal.type == 0 else 'SELL' if deal.type == 1 else 'UNKNOWN'})")
            print(f"    Entry: {deal.entry} ({'IN' if deal.entry == 0 else 'OUT' if deal.entry == 1 else 'INOUT'})")
            print(f"    Volume: {deal.volume}")
            print(f"    Price: {deal.price:.3f}")
            print(f"    Profit: ${deal.profit:.2f}")
            print(f"    Commission: ${deal.commission:.2f}")
            print(f"    Swap: ${deal.swap:.2f}")
            print(f"    Time: {datetime.fromtimestamp(deal.time)}")
            print(f"    Comment: {deal.comment}")
            print()

        # Analise da order completa
        entry_deals = [d for d in order_deals if d.entry == 0]  # ENTRY_IN
        exit_deals = [d for d in order_deals if d.entry == 1]   # ENTRY_OUT

        if entry_deals:
            entry_deal = entry_deals[0]
            print(f"  [ENTRY] Price: {entry_deal.price:.3f} | Volume: {entry_deal.volume} | Time: {datetime.fromtimestamp(entry_deal.time)}")

        if exit_deals:
            exit_deal = exit_deals[0]
            print(f"  [EXIT]  Price: {exit_deal.price:.3f} | Volume: {exit_deal.volume} | Profit: ${exit_deal.profit:.2f} | Time: {datetime.fromtimestamp(exit_deal.time)}")
            print(f"  [EXIT]  Comment: {exit_deal.comment}")

            # Calcular SL real
            if entry_deals:
                entry_price = entry_deal.price
                exit_price = exit_deal.price
                sl_distance = abs(entry_price - exit_price)

                print(f"  [SL REAL] Distancia: ${sl_distance:.3f}")

                # Se fechou com loss, foi SL
                if exit_deal.profit < 0:
                    print(f"  [CONFIRMACAO] Fechado com LOSS (${exit_deal.profit:.2f}) - FOI STOP LOSS!")
                    print(f"  [SL EXECUTADO] Entry: {entry_price:.3f} -> Exit: {exit_price:.3f} = ${sl_distance:.3f}")

                    # Comparar com o esperado ($4.00)
                    expected_sl = 4.0
                    sl_diff = abs(sl_distance - expected_sl)

                    if sl_diff > 0.5:
                        print(f"  [ALERTA] SL ERRADO! Esperado: ${expected_sl:.2f} | Real: ${sl_distance:.3f} | Diferenca: ${sl_diff:.3f}")
                    else:
                        print(f"  [OK] SL correto (esperado ${expected_sl:.2f}, real ${sl_distance:.3f})")
        else:
            print(f"  [INFO] Posicao ainda ABERTA (sem deal de saida)")

        print()

    # Buscar orders dessas posicoes
    print()
    print("=" * 80)
    print("ORDERS RELACIONADAS (ultimas 48h)")
    print("=" * 80)
    print()

    orders = mt5.history_orders_get(date_from, date_to, group="*XAU*")

    for ticket in TICKETS:
        related_orders = [o for o in orders if o.ticket == ticket or (hasattr(o, 'position_id') and o.position_id == ticket)]

        if related_orders:
            print(f"Order {ticket}:")
            for order in related_orders:
                print(f"  Ticket: {order.ticket}")
                print(f"  Type: {order.type}")
                print(f"  Price Open: {order.price_open:.3f}")
                print(f"  SL: {order.sl:.3f}")
                print(f"  TP: {order.tp:.3f}")
                print(f"  Volume: {order.volume_initial}")
                print(f"  State: {order.state}")
                print(f"  Comment: {order.comment}")
                print()

    mt5.shutdown()

if __name__ == "__main__":
    main()
