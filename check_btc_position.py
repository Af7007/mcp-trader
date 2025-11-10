#!/usr/bin/env python3
"""
Verifica posicao BTC aberta e diagnostica break-even/trailing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()

print("=" * 60)
print("DIAGNOSTICO: Posicao BTC + Break-Even/Trailing")
print("=" * 60)
print()

# Posicoes abertas
positions = mt5.positions_get(symbol='BTCUSDc')

if not positions:
    print("Nenhuma posicao aberta em BTCUSDc")
else:
    for pos in positions:
        ticket = pos['ticket']
        pos_type = "BUY" if pos['type'] == 0 else "SELL"
        entry = pos['price_open']
        current = pos['price_current']
        sl = pos['sl']
        tp = pos.get('tp', 0)
        profit = pos['profit']

        print(f"POSICAO ABERTA:")
        print(f"   Ticket: {ticket}")
        print(f"   Tipo: {pos_type}")
        print(f"   Entry: ${entry:.2f}")
        print(f"   Preco Atual: ${current:.2f}")
        print(f"   SL: ${sl:.2f}")
        print(f"   TP: ${tp:.2f}" if tp else "   TP: Nenhum")
        print(f"   Lucro: ${profit:.2f}")
        print()

        # Calcular distancia
        if pos_type == "BUY":
            distance = current - entry
            sl_distance = entry - sl
        else:
            distance = entry - current
            sl_distance = sl - entry

        print(f"ANALISE:")
        print(f"   Distancia do entry: ${abs(distance):.2f} ({'lucro' if distance > 0 else 'prejuizo'})")
        print(f"   Distancia do SL: ${sl_distance:.2f}")
        print()

        # Verificar break-even (deveria ativar em $1.50)
        if profit >= 1.50:
            # Verificar se SL foi movido para entry
            if abs(sl - entry) < 1.0:  # SL proximo do entry
                print(f"   [OK] BREAK-EVEN ATIVADO! SL em ${sl:.2f} (entry ${entry:.2f})")
            else:
                print(f"   [PROBLEMA] Lucro ${profit:.2f} >= $1.50 mas SL NAO foi movido!")
                print(f"   [PROBLEMA] SL deveria estar em ${entry:.2f}, mas esta em ${sl:.2f}")
        else:
            print(f"   Break-Even: Aguardando $1.50 (atual ${profit:.2f})")

        print()

        # Verificar trailing (deveria ativar em $4.00)
        if profit >= 4.00:
            # Trailing deveria estar ativo
            if pos_type == "BUY":
                # SL deveria estar acima do entry
                if sl > entry:
                    protected = sl - entry
                    print(f"   [OK] TRAILING ATIVO! Protegendo ${protected:.2f}")
                else:
                    print(f"   [PROBLEMA] Lucro ${profit:.2f} >= $4.00 mas trailing NAO ATIVOU!")
            else:
                # SL deveria estar abaixo do entry
                if sl < entry:
                    protected = entry - sl
                    print(f"   [OK] TRAILING ATIVO! Protegendo ${protected:.2f}")
                else:
                    print(f"   [PROBLEMA] Lucro ${profit:.2f} >= $4.00 mas trailing NAO ATIVOU!")
        else:
            print(f"   Trailing: Aguardando $4.00 (atual ${profit:.2f})")

print()
print("=" * 60)

# Preco de mercado
tick = mt5.get_symbol_info_tick(symbol='BTCUSDc')
if tick:
    print("MERCADO ATUAL:")
    print(f"   Bid: ${tick['bid']:.2f}")
    print(f"   Ask: ${tick['ask']:.2f}")
    print(f"   Spread: ${tick['ask'] - tick['bid']:.2f}")
    print()

    if positions:
        pos = positions[0]
        entry = pos['price_open']
        pos_type = "BUY" if pos['type'] == 0 else "SELL"

        # Verificar se entry esta fora do candle atual
        if pos_type == "BUY":
            if entry > tick['ask']:
                print(f"   [ALERTA] Entry BUY ${entry:.2f} > Ask ${tick['ask']:.2f}")
                print(f"   Ordem pode ter sido aberta ACIMA do mercado!")
        else:
            if entry < tick['bid']:
                print(f"   [ALERTA] Entry SELL ${entry:.2f} < Bid ${tick['bid']:.2f}")
                print(f"   Ordem pode ter sido aberta ABAIXO do mercado!")

print("=" * 60)
