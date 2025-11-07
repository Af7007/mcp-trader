#!/usr/bin/env python3
"""
Script para fechar posições abertas
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def main():
    print("Fechando posições abertas...")

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
        profit = pos.get('profit')

        print(f"Fechando posição #{ticket}: {pos_type} {symbol} {volume} lotes (Profit: ${profit:.2f})")

        # Fechar posição
        result = mt5.close_position(ticket)
        if result:
            print(f"[OK] Posicao #{ticket} fechada com sucesso!")
        else:
            print(f"[ERRO] Erro ao fechar posicao #{ticket}")

if __name__ == "__main__":
    main()
