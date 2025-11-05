#!/usr/bin/env python3
"""
Verificar últimas ordens do adaptive para diagnosticar BUY vs SELL
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("VERIFICANDO ÚLTIMAS ORDENS - DIAGNÓSTICO BUY/SELL")
print("="*80)

mt5 = get_mt5_client()

# Obter histórico das últimas 24 horas
now = datetime.now()
from_date = now - timedelta(hours=24)

deals = mt5.history_deals_get(from_date, now)

if not deals:
    print("\n[INFO] Nenhum deal encontrado nas últimas 24h")
else:
    print(f"\n[DEALS] {len(deals)} deals nas últimas 24h")
    
    # Filtrar apenas XAUUSDc
    gold_deals = [d for d in deals if d.get('symbol') == 'XAUUSDc']
    
    print(f"\n[GOLD] {len(gold_deals)} deals em XAUUSDc")
    print(f"\nÚltimas 10 ordens:")
    print(f"{'Time':^20} {'Ticket':^12} {'Type':^8} {'Price':^12} {'Profit':^10}")
    print("-"*80)
    
    for deal in gold_deals[-10:]:
        deal_time = datetime.fromtimestamp(deal.get('time', 0))
        ticket = deal.get('order', 0)
        deal_type = deal.get('type', 0)
        type_str = 'BUY' if deal_type == 0 else 'SELL' if deal_type == 1 else 'UNKNOWN'
        price = deal.get('price', 0)
        profit = deal.get('profit', 0)
        
        print(f"{deal_time.strftime('%Y-%m-%d %H:%M:%S'):^20} {ticket:^12} {type_str:^8} ${price:>10.2f} ${profit:>8.2f}")

# Verificar posições abertas
print(f"\n{'='*80}")
print("POSIÇÕES ABERTAS AGORA:")
print("="*80)

positions = mt5.positions_get(symbol="XAUUSDc")

if not positions:
    print("\n[INFO] Nenhuma posição aberta")
else:
    print(f"\n[TOTAL] {len(positions)} posições abertas:")
    print(f"\n{'Ticket':^12} {'Type':^8} {'Entry':^12} {'Current':^12} {'Profit':^10} {'SL':^12}")
    print("-"*80)
    
    for pos in positions:
        ticket = pos.get('ticket')
        pos_type = 'BUY' if pos.get('type') == 0 else 'SELL'
        entry = pos.get('price_open', 0)
        current = pos.get('price_current', 0)
        profit = pos.get('profit', 0)
        sl = pos.get('sl', 0)
        
        print(f"{ticket:^12} {pos_type:^8} ${entry:>10.2f} ${current:>10.2f} ${profit:>8.2f} ${sl:>10.2f}")

# Analisar direção do mercado
print(f"\n{'='*80}")
print("ANÁLISE DE DIREÇÃO:")
print("="*80)

tick = mt5.get_symbol_info_tick("XAUUSDc")
if tick:
    bid = tick.get('bid', 0)
    ask = tick.get('ask', 0)
    
    print(f"\nPreço atual:")
    print(f"  BID: ${bid:.2f} (para SELL)")
    print(f"  ASK: ${ask:.2f} (para BUY)")
    
    # Ver tendência das últimas ordens
    if gold_deals and len(gold_deals) >= 2:
        last_deal = gold_deals[-1]
        prev_deal = gold_deals[-2]
        
        last_price = last_deal.get('price', 0)
        prev_price = prev_deal.get('price', 0)
        
        print(f"\nÚltimas 2 ordens:")
        print(f"  Penúltima: ${prev_price:.2f}")
        print(f"  Última: ${last_price:.2f}")
        
        if last_price > prev_price:
            print(f"  Tendência: SUBINDO (+${last_price - prev_price:.2f})")
            print(f"  Deveria: VENDER (aproveitar topo)")
        else:
            print(f"  Tendência: DESCENDO (-${prev_price - last_price:.2f})")
            print(f"  Deveria: COMPRAR (aproveitar fundo)")

print("\n" + "="*80)
