"""
Verifica a razao de fechamento dos deals OUT
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

# Deals OUT que encontramos
out_deal_tickets = [73864470, 73863279, 73862404, 73861326]

date_from = datetime.now() - timedelta(hours=48)
date_to = datetime.now()
all_deals = mt5.history_deals_get(date_from, date_to, group='*XAU*')

print('Analisando razao de fechamento dos deals OUT:')
print('=' * 100)

for deal_ticket in out_deal_tickets:
    deal = next((d for d in all_deals if d.ticket == deal_ticket), None)

    if deal:
        deal_time = datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d %H:%M:%S')

        # Mapear reason
        reason_map = {
            0: 'DEAL_REASON_CLIENT (manual)',
            1: 'DEAL_REASON_MOBILE',
            2: 'DEAL_REASON_WEB',
            3: 'DEAL_REASON_EXPERT (EA/Bot)',
            4: 'DEAL_REASON_SL (Stop Loss)',
            5: 'DEAL_REASON_TP (Take Profit)',
            6: 'DEAL_REASON_SO (Stop Out)',
            7: 'DEAL_REASON_ROLLOVER',
            8: 'DEAL_REASON_VMARGIN',
            9: 'DEAL_REASON_SPLIT'
        }

        reason = reason_map.get(deal.reason, f'UNKNOWN ({deal.reason})')

        print(f'\nDeal {deal.ticket}:')
        print(f'  Order: {deal.order}')
        print(f'  Type: {"BUY" if deal.type == 0 else "SELL"}')
        print(f'  Entry: {"IN" if deal.entry == 0 else "OUT" if deal.entry == 1 else "INOUT"}')
        print(f'  Price: {deal.price:.3f}')
        print(f'  Profit: ${deal.profit:.2f}')
        print(f'  Time: {deal_time}')
        print(f'  Reason: {reason}')
        print(f'  Comment: {deal.comment if hasattr(deal, "comment") else "N/A"}')

print('\n' + '=' * 100)

mt5.shutdown()
