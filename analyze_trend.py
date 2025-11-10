#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisar qual tendência está sendo detectada em tempo real
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()

if not mt5.is_connected():
    print("❌ MT5 não conectado!")
    exit(1)

# Analisar ambos símbolos
for symbol in ["XAUUSDc", "GBPUSDc"]:
    print("\n" + "="*80)
    print(f"ANÁLISE TÉCNICA - {symbol}")
    print("="*80)

    # M5
    rates_m5 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M5", start_pos=0, count=15)
    if rates_m5:
        closes_m5 = [r['close'] for r in rates_m5][::-1]

        print(f"\n📊 M5 (últimas 15 velas = 75 minutos)")
        print(f"   Closes (antigo → recente): {[f'{c:.2f}' for c in closes_m5[:5]]} ... {[f'{c:.2f}' for c in closes_m5[-3:]]}")

        uptrend_m5 = sum(1 for i in range(7) if closes_m5[i] < closes_m5[i+1])
        downtrend_m5 = sum(1 for i in range(7) if closes_m5[i] > closes_m5[i+1])

        print(f"   Comparações de subida (closes[i] < closes[i+1]): {uptrend_m5}/7")
        print(f"   Comparações de descida (closes[i] > closes[i+1]): {downtrend_m5}/7")

        if uptrend_m5 >= 5:
            print(f"   ✅ M5 UPTREND (DEVE FAZER BUY)")
        elif downtrend_m5 >= 5:
            print(f"   ✅ M5 DOWNTREND (DEVE FAZER SELL)")
        else:
            print(f"   ⚠️  M5 LATERAL/INDEFINIDO (NÃO ABRIR)")

    # M15
    rates_m15 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M15", start_pos=0, count=6)
    if rates_m15:
        closes_m15 = [r['close'] for r in rates_m15][::-1]

        print(f"\n📊 M15 (últimas 6 velas = 90 minutos)")
        print(f"   Closes (antigo → recente): {[f'{c:.2f}' for c in closes_m15]}")

        # Verificar uptrend M15
        if closes_m15[0] < closes_m15[1] < closes_m15[2]:
            print(f"   ✅ M15 UPTREND (confirma BUY)")
        else:
            print(f"   ❌ M15 NÃO uptrend (rejeita BUY)")

        # Verificar downtrend M15
        if closes_m15[0] > closes_m15[1] > closes_m15[2]:
            print(f"   ✅ M15 DOWNTREND (confirma SELL)")
        else:
            print(f"   ❌ M15 NÃO downtrend (rejeita SELL)")

    # Preço atual
    tick = mt5.get_symbol_info_tick(symbol)
    if tick:
        print(f"\n💰 Preço Atual")
        print(f"   Bid: ${tick['bid']:.3f} | Ask: ${tick['ask']:.3f} | Mid: ${(tick['bid']+tick['ask'])/2:.3f}")

print("\n" + "="*80)
