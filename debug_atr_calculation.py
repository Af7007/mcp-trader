#!/usr/bin/env python3
"""
Debug: por que ATR esta tao alto?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("DEBUG ATR - POR QUE TVALORES TÃO ALTOS?")
print("="*80)

# Conectar MT5
mt5 = get_mt5_client()

# Obter dados M5
print("\n[OBTENDO DADOS M5]")
rates = mt5.copy_rates_from_pos(
    symbol="XAUUSDc",
    timeframe="M5",
    start_pos=0,
    count=20
)

print(f"Candles obtidos: {len(rates)}")

if rates and len(rates) >= 14:
    print(f"\nPrimeiros 14 candles M5:")
    print(f"{'#':>3} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'TR':>10}")
    print("-"*60)
    
    true_ranges = []
    for i in range(1, min(14, len(rates))):
        high = rates[i-1]['high']
        low = rates[i-1]['low']
        prev_close = rates[i]['close']
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
        
        print(f"{i:>3} {rates[i-1]['open']:>10.5f} {high:>10.5f} {low:>10.5f} {prev_close:>10.5f} {tr:>10.5f}")
    
    # Calcular ATR
    atr_preco = sum(true_ranges) / len(true_ranges)
    atr_pontos = atr_preco / 0.001  # symbol_point
    
    print(f"\n[CALCULO ATR]")
    print(f"  True Ranges: {[f'{t:.5f}' for t in true_ranges[:3]]}...")
    print(f"  Media True Range (preco): ${atr_preco:.5f}")
    print(f"  ATR em pontos (÷ 0.001): {atr_pontos:.0f} pontos")
    print(f"  ATR minimo: {max(atr_pontos, 400.0):.0f} pontos")
    
    print(f"\n[PROBLEMA?]")
    if atr_pontos > 1000:
        print(f"  WARNING: ATR muito alto ({atr_pontos:.0f})!")
        print(f"  Isso pode significar:")
        print(f"    1. High volatilidade no momento")
        print(f"    2. Problema no cálculo de True Range")
        print(f"    3. Dados com gap/abertura grande")
    else:
        print(f"  ATR normal: {atr_pontos:.0f} pontos ✓")
        
else:
    print(f"[ERRO] Nao conseguiu obter dados M5 suficientes")

print("\n" + "="*80)
