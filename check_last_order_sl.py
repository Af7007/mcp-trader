#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica qual foi o SL da última ordem aberta no MT5
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()

if not mt5.is_connected():
    print("MT5 nao conectado!")
    exit(1)

print("\n" + "="*80)
print("ULTIMA ORDEM ABERTA - VERIFICACAO DE SL")
print("="*80)

# Procurar por posicoes abertas
positions = mt5.positions_get(symbol="XAUUSDc")

if not positions:
    print("\nNenhuma posicao aberta em XAUUSDc!")
    positions_gbp = mt5.positions_get(symbol="GBPUSDc")
    if positions_gbp:
        print("Verificando GBPUSDc...")
        positions = positions_gbp
        symbol = "GBPUSDc"
    else:
        print("Nenhuma posicao aberta em GBPUSDc tambem!")
        exit(1)
else:
    symbol = "XAUUSDc"

print(f"\nPosicoes em {symbol}:")
print("-" * 80)

for pos in positions:
    ticket = pos.get('ticket', 'N/A')
    type_str = "BUY" if pos.get('type') == 0 else "SELL"
    volume = pos.get('volume', 0)
    entry_price = pos.get('price_open', 0)
    current_price = pos.get('price_current', 0)
    sl = pos.get('sl', 0)
    tp = pos.get('tp', 0)
    profit = pos.get('profit', 0)

    print(f"\nTicket: {ticket}")
    print(f"  Tipo: {type_str}")
    print(f"  Volume: {volume} lotes")
    print(f"  Entrada: ${entry_price:.3f}")
    print(f"  Preco atual: ${current_price:.3f}")
    print(f"  SL: ${sl:.3f}")
    print(f"  TP: ${tp:.3f}")
    print(f"  Lucro: ${profit:.2f}")

    # Calcular distancia do SL
    if type_str == "BUY":
        sl_distance = entry_price - sl
        print(f"  Distancia SL (entrada - SL): ${entry_price:.3f} - ${sl:.3f} = ${sl_distance:.3f}")
    else:
        sl_distance = sl - entry_price
        print(f"  Distancia SL (SL - entrada): ${sl:.3f} - ${entry_price:.3f} = ${sl_distance:.3f}")

    # Comparar com esperado
    if abs(sl_distance - 4.0) < 0.1:
        print(f"  CORRETO: SL distance = {sl_distance:.2f} (esperado 4.00)")
    elif abs(sl_distance - 11.80) < 0.1:
        print(f"  ERRADO: SL distance = {sl_distance:.2f} (problema detectado - deveria ser 4.00)")
    else:
        print(f"  DESCONHECIDO: SL distance = {sl_distance:.2f}")

print("\n" + "="*80)
