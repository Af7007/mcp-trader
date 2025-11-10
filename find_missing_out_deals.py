"""
Busca deals OUT proximos aos IN conhecidos
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

# Tickets do DB que so tem IN
target_in_deals = {
    115076822: 73863895,  # Deal IN @ 2025-11-07 14:14:03
    115075708: 73862898,  # Deal IN @ 2025-11-07 14:13:03
    115075078: 73862300,  # Deal IN @ 2025-11-07 14:12:11
    115074415: 73861671,  # Deal IN @ 2025-11-07 14:11:20
    115073897: 73861237,  # Deal IN @ 2025-11-07 14:10:29
}

date_from = datetime.now() - timedelta(hours=48)
date_to = datetime.now()
all_deals = mt5.history_deals_get(date_from, date_to, group='*XAU*')

print('Buscando deals OUT proximos aos IN conhecidos:')
print('=' * 100)

for order_ticket, in_deal_ticket in target_in_deals.items():
    # Buscar o deal IN
    in_deal = next((d for d in all_deals if d.ticket == in_deal_ticket), None)

    if in_deal:
        in_time = datetime.fromtimestamp(in_deal.time)
        print(f'\nOrder {order_ticket}:')
        print(f'  IN Deal {in_deal.ticket}: {in_time} @ {in_deal.price:.3f} | Vol: {in_deal.volume:.2f}')

        # Buscar deals OUT proximos (ate 10 min depois)
        time_window_end = in_time + timedelta(minutes=10)

        nearby_out_deals = [
            d for d in all_deals
            if d.entry == 1  # OUT
            and d.volume == in_deal.volume
            and in_time <= datetime.fromtimestamp(d.time) <= time_window_end
        ]

        if nearby_out_deals:
            print(f'  Possiveis deals OUT proximos ({len(nearby_out_deals)}):')
            for d in nearby_out_deals:
                out_time = datetime.fromtimestamp(d.time)
                print(f'    Deal {d.ticket} (Order {d.order}): {out_time} @ {d.price:.3f} | Profit: ${d.profit:.2f}')
        else:
            print(f'  [ALERTA] Nenhum deal OUT encontrado ate 10min depois!')

print('\n' + '=' * 100)

mt5.shutdown()
