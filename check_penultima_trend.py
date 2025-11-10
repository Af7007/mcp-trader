#!/usr/bin/env python3
"""
Verifica se a penultima ordem SELL estava contra o mercado
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

entry_price = 102080.01
entry_time = datetime(2025, 11, 9, 9, 35, 52)

print("=" * 60)
print("ANALISE: Penultima SELL vs Tendencia")
print("=" * 60)
print()

print(f"ENTRADA SELL:")
print(f"   Preco: ${entry_price:.2f}")
print(f"   Horario: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

# M5 antes da entrada
time_before = entry_time - timedelta(minutes=30)
rates_m5 = mt5.copy_rates_range("BTCUSDc", mt5.TIMEFRAME_M5, time_before, entry_time)

if rates_m5 is not None and len(rates_m5) > 0:
    closes = [r[4] for r in rates_m5]

    print(f"TENDENCIA M5 (30min antes):")
    print(f"   Preco inicial: ${closes[0]:.2f}")
    print(f"   Preco final: ${closes[-1]:.2f}")
    movement = closes[-1] - closes[0]
    print(f"   Movimento: ${movement:.2f} ({movement/closes[0]*100:.2f}%)")

    if movement > 0:
        print(f"   Tendencia: UPTREND (preco subindo)")
        print(f"   [ALERTA] SELL contra UPTREND!")
    else:
        print(f"   Tendencia: DOWNTREND (preco caindo)")
        print(f"   [OK] SELL a favor do DOWNTREND")
    print()

    # Micro-tendencia
    if len(closes) >= 3:
        last_3 = closes[-3:]
        print(f"MICRO-TENDENCIA (ultimas 3 velas):")
        print(f"   Vela -3: ${last_3[0]:.2f}")
        print(f"   Vela -2: ${last_3[1]:.2f}")
        print(f"   Vela -1: ${last_3[2]:.2f}")

        if last_3[0] > last_3[1] > last_3[2]:
            print(f"   Micro: DOWNTREND")
            print(f"   [OK] SELL alinhado")
        elif last_3[0] < last_3[1] < last_3[2]:
            print(f"   Micro: UPTREND")
            print(f"   [ALERTA] SELL contra micro-uptrend!")
        else:
            print(f"   Micro: LATERAL")
        print()

    # Ultimas 5 velas
    print("ULTIMAS 5 VELAS M5:")
    for i in range(max(0, len(rates_m5)-5), len(rates_m5)):
        r = rates_m5[i]
        t = datetime.fromtimestamp(r[0])
        o, h, l, c = r[1], r[2], r[3], r[4]
        color = "VERDE" if c > o else "VERMELHA"
        size = abs(c - o)
        print(f"   {t.strftime('%H:%M')} - O:${o:.2f} C:${c:.2f} ({color}, ${size:.2f})")

print()
print("=" * 60)

mt5.shutdown()
