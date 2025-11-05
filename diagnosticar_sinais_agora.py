#!/usr/bin/env python3
"""
Diagnosticar por que adaptive não está abrindo trades
"""

import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("DIAGNÓSTICO: Por que não está abrindo trades?")
print("="*80)

mt5 = get_mt5_client()

# 1. Preço atual
tick = mt5.get_symbol_info_tick("XAUUSDc")
if tick:
    bid = tick.get('bid', 0)
    ask = tick.get('ask', 0)
    print(f"\n[PREÇO ATUAL]")
    print(f"  BID: ${bid:.2f}")
    print(f"  ASK: ${ask:.2f}")

# 2. Análise M5
print(f"\n{'='*80}")
print("ANÁLISE M5 (Tendência)")
print("="*80)

rates_m5 = mt5.copy_rates_from_pos(
    symbol="XAUUSDc",
    timeframe="M5",
    start_pos=0,
    count=10
)

if rates_m5 and len(rates_m5) >= 6:
    closes = [r['close'] for r in rates_m5[:10]]
    highs = [r['high'] for r in rates_m5[:10]]
    lows = [r['low'] for r in rates_m5[:10]]
    volumes = [r['tick_volume'] for r in rates_m5[:10]]
    
    current = closes[0]
    prev_1 = closes[1]
    prev_2 = closes[2]
    prev_5 = closes[5]
    
    # Tendência
    uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
    downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3
    
    # Momentum
    momentum_5m = ((current - prev_5) / prev_5) * 100
    
    # Volatilidade
    last_range = highs[0] - lows[0]
    avg_range = sum([highs[i] - lows[i] for i in range(1, 6)]) / 5
    high_volatility = last_range > avg_range * 1.0
    
    # Volume
    volume_spike = volumes[0] > sum(volumes[1:6]) / 5 * 1.1
    
    # Preço vs média
    avg_price = sum(closes[:5]) / 5
    price_above_avg = current > avg_price
    price_below_avg = current < avg_price
    
    print(f"\n[M5 DADOS]")
    print(f"  Preço atual: ${current:.2f}")
    print(f"  Preço anterior: ${prev_1:.2f}")
    print(f"  Momentum 5m: {momentum_5m:.3f}%")
    print(f"  Tendência: {'UPTREND' if uptrend else 'DOWNTREND' if downtrend else 'LATERAL'}")
    print(f"  Volatilidade alta: {'SIM' if high_volatility else 'NÃO'} (range: ${last_range:.2f} vs avg: ${avg_range:.2f})")
    print(f"  Volume spike: {'SIM' if volume_spike else 'NÃO'} (vol: {volumes[0]} vs avg: {sum(volumes[1:6])/5:.0f})")
    print(f"  Preço vs média: {'ACIMA' if price_above_avg else 'ABAIXO'} (avg: ${avg_price:.2f})")
    
    # Thresholds
    MOMENTUM_BUY = 0.03
    MOMENTUM_SELL = -0.03
    
    print(f"\n[ANÁLISE BUY]")
    confirmations_buy = 0
    
    if uptrend and momentum_5m > MOMENTUM_BUY:
        print(f"  ✅ Uptrend + Momentum positivo ({momentum_5m:.3f}% > {MOMENTUM_BUY}%)")
        confirmations_buy += 1
    else:
        print(f"  ❌ Uptrend={uptrend}, Momentum={momentum_5m:.3f}% (precisa >{MOMENTUM_BUY}%)")
    
    if momentum_5m > MOMENTUM_BUY * 1.5:
        print(f"  ✅ Momentum forte ({momentum_5m:.3f}% > {MOMENTUM_BUY*1.5}%)")
        confirmations_buy += 1
    else:
        print(f"  ❌ Momentum não forte o suficiente ({momentum_5m:.3f}% <= {MOMENTUM_BUY*1.5}%)")
    
    if (high_volatility or volume_spike) and current > prev_1 and price_above_avg:
        print(f"  ✅ Volatilidade/Volume + Preço subindo + Acima média")
        confirmations_buy += 1
    else:
        print(f"  ❌ Vol={high_volatility}, VolSpike={volume_spike}, Preço>{prev_1}={current>prev_1}, Acima_avg={price_above_avg}")
    
    print(f"\n  TOTAL CONFIRMAÇÕES BUY: {confirmations_buy}/3 (precisa ≥2)")
    
    print(f"\n[ANÁLISE SELL]")
    confirmations_sell = 0
    
    if downtrend and momentum_5m < MOMENTUM_SELL:
        print(f"  ✅ Downtrend + Momentum negativo ({momentum_5m:.3f}% < {MOMENTUM_SELL}%)")
        confirmations_sell += 1
    else:
        print(f"  ❌ Downtrend={downtrend}, Momentum={momentum_5m:.3f}% (precisa <{MOMENTUM_SELL}%)")
    
    if momentum_5m < MOMENTUM_SELL * 1.5:
        print(f"  ✅ Momentum forte negativo ({momentum_5m:.3f}% < {MOMENTUM_SELL*1.5}%)")
        confirmations_sell += 1
    else:
        print(f"  ❌ Momentum não forte o suficiente ({momentum_5m:.3f}% >= {MOMENTUM_SELL*1.5}%)")
    
    if (high_volatility or volume_spike) and current < prev_1 and price_below_avg:
        print(f"  ✅ Volatilidade/Volume + Preço caindo + Abaixo média")
        confirmations_sell += 1
    else:
        print(f"  ❌ Vol={high_volatility}, VolSpike={volume_spike}, Preço<{prev_1}={current<prev_1}, Abaixo_avg={price_below_avg}")
    
    print(f"\n  TOTAL CONFIRMAÇÕES SELL: {confirmations_sell}/3 (precisa ≥2)")
    
    print(f"\n{'='*80}")
    if confirmations_buy >= 2:
        print("✅ SINAL BUY VÁLIDO!")
    elif confirmations_sell >= 2:
        print("✅ SINAL SELL VÁLIDO!")
    else:
        print("❌ NENHUM SINAL VÁLIDO (filtros bloquearam)")
        print("\nRAZÃO: Mercado lateral ou momentum insuficiente")

print(f"\n{'='*80}")
