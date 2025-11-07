#!/usr/bin/env python3
"""
Script para verificar posições abertas no MT5
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def main():
    print("Verificando posições abertas no MT5...")

    # Conectar ao MT5
    mt5 = get_mt5_client()
    if not mt5 or not mt5.is_connected():
        print("ERRO: MT5 não conectado!")
        return

    # Verificar posições abertas
    positions = mt5.positions_get()
    if not positions:
        print("Nenhuma posição aberta encontrada.")
        return

    print(f"Encontradas {len(positions)} posições abertas:")

    for pos in positions:
        ticket = pos.get('ticket')
        symbol = pos.get('symbol')
        pos_type = "BUY" if pos.get('type') == 0 else "SELL"
        volume = pos.get('volume')
        entry_price = pos.get('price_open')
        current_price = pos.get('price_current')
        profit = pos.get('profit')
        sl = pos.get('sl')
        tp = pos.get('tp')

        print(f"\nPosição #{ticket}:")
        print(f"  Símbolo: {symbol}")
        print(f"  Tipo: {pos_type}")
        print(f"  Volume: {volume}")
        print(f"  Entry Price: ${entry_price:.2f}")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  Profit: ${profit:.2f}")
        print(f"  Stop Loss: ${sl:.2f}")
        print(f"  Take Profit: ${tp:.2f}")

        # Verificar se trailing deveria estar ativo
        trailing_activation = 1.0  # $1
        if profit >= trailing_activation:
            print(f"  [OK] Trailing DEVERIA estar ativo (lucro >= ${trailing_activation:.2f})")
        else:
            print(f"  [AGUARDANDO] Trailing ainda nao ativo (lucro < ${trailing_activation:.2f})")

if __name__ == "__main__":
    main()
