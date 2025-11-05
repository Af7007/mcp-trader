#!/usr/bin/env python3
"""
Teste: Verificar se posicao esta aberta e conseguir entry_price
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("TESTE: POSICAO ABERTA E ENTRY_PRICE")
print("="*80)

mt5 = get_mt5_client()

# Obter TODAS as posicoes
print("\n[BUSCANDO POSICOES]")
positions = mt5.positions_get(symbol="XAUUSDc")

if not positions:
    print("  Nenhuma posicao aberta em XAUUSDc")
else:
    print(f"  {len(positions)} posicoes abertas:")
    for i, pos in enumerate(positions):
        print(f"\n  [{i}] Ticket: {pos['ticket']}")
        print(f"      Type: {'BUY' if pos['type'] == 0 else 'SELL'}")
        print(f"      Price Open: ${pos['price_open']:.5f}")
        print(f"      Price Current: ${pos['price_current']:.5f}")
        print(f"      Profit: ${pos['profit']:.2f}")
        print(f"      SL: ${pos['sl']:.5f}")
        print(f"      TP: ${pos['tp']:.5f}")

# Tentar obter por ticket
if positions:
    ticket = positions[-1]['ticket']
    print(f"\n[TESTE BY TICKET]")
    print(f"  Buscando ticket {ticket}...")
    try:
        pos_by_ticket = mt5.positions_get(ticket=ticket)
        if pos_by_ticket:
            print(f"  [OK] Encontrada: ${pos_by_ticket[0]['price_open']:.5f}")
        else:
            print(f"  [ERRO] Nao encontrada por ticket")
    except Exception as e:
        print(f"  [ERRO] {e}")

print("\n" + "="*80)
