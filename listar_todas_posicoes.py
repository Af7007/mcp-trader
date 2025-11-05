#!/usr/bin/env python3
"""
Listar TODAS as posicoes abertas
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("TODAS AS POSICOES ABERTAS")
print("="*80)

mt5 = get_mt5_client()

# Obter TODAS as posicoes (sem filtrar por symbol)
positions = mt5.positions_get()

if not positions:
    print("\n[INFO] Nenhuma posicao aberta")
    exit(0)

print(f"\n[TOTAL] {len(positions)} posicoes abertas:\n")

for i, pos in enumerate(positions, 1):
    tipo = "BUY" if pos['type'] == 0 else "SELL"
    print(f"{i}. Ticket {pos['ticket']}: {pos['symbol']} {tipo}")
    print(f"   Entrada: ${pos['price_open']:.5f} | Atual: ${pos['price_current']:.5f}")
    print(f"   Profit: ${pos['profit']:.2f}")
    print(f"   SL: ${pos['sl']:.5f} | TP: ${pos['tp']:.5f}")
    print()

print("="*80)
