#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do problema de SL
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def debug_sl():
    """
    Analisa a posição atual e verifica o SL
    """
    print("="*70)
    print("DEBUG - PROBLEMA DO SL")
    print("="*70)
    print()

    mt5 = get_mt5_client()

    # Obter posição atual
    positions = mt5.positions_get(symbol="BTCUSDc")

    if not positions:
        print("Nenhuma posição aberta")
        return

    pos = positions[0]

    print("[POSICAO ATUAL]")
    print(f"   Ticket: {pos.get('ticket')}")
    print(f"   Tipo: {'SELL' if pos.get('type') == 1 else 'BUY'}")
    print(f"   Volume: {pos.get('volume')}")
    print(f"   Entrada: ${pos.get('price_open', 0):.2f}")
    print(f"   SL: ${pos.get('sl', 0):.2f}")
    print(f"   TP: ${pos.get('tp', 0):.2f}")
    print()

    # Calcular SL esperado
    entry = pos.get('price_open', 0)
    sl_atual = pos.get('sl', 0)
    tp_atual = pos.get('tp', 0)

    if pos.get('type') == 1:  # SELL
        sl_esperado = entry + 30.0
        tp_esperado = entry - 50.0
    else:  # BUY
        sl_esperado = entry - 30.0
        tp_esperado = entry + 50.0

    print("[ANALISE]")
    print(f"   SL Esperado: ${sl_esperado:.2f}")
    print(f"   SL Atual: ${sl_atual:.2f}")
    print(f"   Diferenca: ${abs(sl_atual - sl_esperado):.2f}")
    print()

    if abs(sl_atual - sl_esperado) > 1.0:
        print("   STATUS: SL INCORRETO!")
        print(f"   O SL esta ${abs(sl_atual - sl_esperado):.2f} diferente do esperado")
        print()
        print("   Possivel causa:")
        print("   1. MT5 modificou o SL automaticamente")
        print("   2. Problema no calculo do codigo")
        print("   3. Problema no metodo sell_market()")
    else:
        print("   STATUS: SL CORRETO")

    print()
    print(f"   TP Esperado: ${tp_esperado:.2f}")
    print(f"   TP Atual: ${tp_atual:.2f}")
    print(f"   Diferenca: ${abs(tp_atual - tp_esperado):.2f}")

    print()
    print("="*70)

if __name__ == "__main__":
    debug_sl()
