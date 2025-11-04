#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica posições abertas no MT5 para BTCUSDc
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def verificar_posicoes():
    """
    Verifica posições abertas
    """
    print("="*70)
    print("VERIFICAÇÃO DE POSIÇÕES ABERTAS - BTCUSDc")
    print("="*70)
    print()

    mt5 = get_mt5_client()

    # Verificar todas as posições
    print("[1] TODAS AS POSIÇÕES ABERTAS")
    all_positions = mt5.positions_get()

    if all_positions:
        print(f"   Total: {len(all_positions)} posições")
        print()
        for i, pos in enumerate(all_positions, 1):
            print(f"   [{i}] Ticket: {pos.get('ticket')}")
            print(f"       Símbolo: {pos.get('symbol')}")
            print(f"       Tipo: {'BUY' if pos.get('type') == 0 else 'SELL'}")
            print(f"       Volume: {pos.get('volume')}")
            print(f"       Preço: ${pos.get('price_open', 0):.2f}")
            print(f"       SL: ${pos.get('sl', 0):.2f}")
            print(f"       TP: ${pos.get('tp', 0):.2f}")
            print(f"       Lucro: ${pos.get('profit', 0):.2f}")
            print()
    else:
        print("   Nenhuma posição aberta")
        print()

    # Verificar posições específicas do BTCUSDc
    print("[2] POSIÇÕES ESPECÍFICAS - BTCUSDc")
    btc_positions = mt5.positions_get(symbol="BTCUSDc")

    if btc_positions:
        print(f"   Total BTCUSDc: {len(btc_positions)} posições")
        print()
        for i, pos in enumerate(btc_positions, 1):
            print(f"   [{i}] Ticket: {pos.get('ticket')}")
            print(f"       Tipo: {'BUY' if pos.get('type') == 0 else 'SELL'}")
            print(f"       Volume: {pos.get('volume')}")
            print(f"       Preço: ${pos.get('price_open', 0):.2f}")
            print(f"       Lucro: ${pos.get('profit', 0):.2f}")
            print()
    else:
        print("   Nenhuma posição BTCUSDc aberta")
        print()

    # Verificar se símbolo existe
    print("[3] VERIFICAÇÃO DO SÍMBOLO")
    symbol_info = mt5.get_symbol_info("BTCUSDc")

    if symbol_info:
        print(f"   ✓ Símbolo BTCUSDc encontrado")
        print(f"   Bid: ${symbol_info.get('bid', 0):.2f}")
        print(f"   Ask: ${symbol_info.get('ask', 0):.2f}")
    else:
        print(f"   ✗ Símbolo BTCUSDc NÃO encontrado no MT5!")
        print(f"   Verifique se o símbolo correto é BTCUSDc ou BTCUSDm")

    print()
    print("="*70)

if __name__ == "__main__":
    verificar_posicoes()
