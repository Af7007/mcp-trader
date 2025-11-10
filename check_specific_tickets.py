"""
Verifica deals especificos no MT5
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()
date_from = datetime.now() - timedelta(hours=48)
date_to = datetime.now()
deals = mt5.history_deals_get(date_from, date_to, group='*XAU*')

# Buscar tickets especificos do DB
target_tickets = [115076822, 115075708, 115075078, 115074415, 115073897]

print('Buscando deals para tickets do DB:')
print('=' * 80)

for ticket in target_tickets:
    order_deals = [d for d in deals if d.order == ticket]
    if order_deals:
        print(f'\nTicket {ticket}: {len(order_deals)} deals')
        for d in order_deals:
            entry_type = 'IN' if d.entry == 0 else 'OUT' if d.entry == 1 else 'INOUT'
            deal_time = datetime.fromtimestamp(d.time).strftime('%Y-%m-%d %H:%M:%S')
            print(f'  Deal {d.ticket}: {entry_type} @ {d.price:.3f} | Profit: ${d.profit:.2f} | Time: {deal_time}')
    else:
        print(f'Ticket {ticket}: Nenhum deal encontrado')

print('\n' + '=' * 80)
print('Total de deals Gold nas ultimas 48h:', len(deals))

mt5.shutdown()
