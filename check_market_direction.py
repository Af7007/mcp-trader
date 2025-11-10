#!/usr/bin/env python3
"""
Verifica se a ordem SELL foi aberta CONTRA o mercado
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

print("=" * 60)
print("ANALISE: Ordem SELL vs Direcao do Mercado")
print("=" * 60)
print()

# Ultima ordem SELL
entry_price = 102215.40
entry_time_str = "2025-11-09 09:37:44"
entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")

print(f"ORDEM ABERTA:")
print(f"   Tipo: SELL")
print(f"   Entry: ${entry_price:.2f}")
print(f"   Horario: {entry_time_str}")
print()

# Pegar dados M5 no momento da entrada
from datetime import timedelta
time_before = entry_time - timedelta(minutes=30)
time_after = entry_time + timedelta(minutes=5)

# Buscar rates M5
rates_m5 = mt5.copy_rates_range("BTCUSDc", mt5.TIMEFRAME_M5, time_before, time_after)

if rates_m5 is not None and len(rates_m5) > 0:
    print(f"VELAS M5 (30min antes da entrada):")
    print(f"   Total: {len(rates_m5)} velas")
    print()

    # Analisar tendencia
    closes = [r[4] for r in rates_m5]  # Close prices

    print("ANALISE DE TENDENCIA:")
    print(f"   Preco inicial (30min antes): ${closes[0]:.2f}")
    print(f"   Preco final (momento entrada): ${closes[-1]:.2f}")

    movement = closes[-1] - closes[0]
    print(f"   Movimento: ${movement:.2f} ({movement/closes[0]*100:.2f}%)")

    if movement > 0:
        print(f"   Tendencia M5: UPTREND (preco subindo)")
        print(f"   [ALERTA] Ordem SELL contra uptrend!")
    else:
        print(f"   Tendencia M5: DOWNTREND (preco caindo)")
        print(f"   [OK] Ordem SELL a favor do downtrend")
    print()

    # Micro-tendencia (ultimas 3 velas)
    if len(closes) >= 3:
        last_3 = closes[-3:]
        print(f"MICRO-TENDENCIA (ultimas 3 velas):")
        print(f"   Vela -3: ${last_3[0]:.2f}")
        print(f"   Vela -2: ${last_3[1]:.2f}")
        print(f"   Vela -1: ${last_3[2]:.2f}")

        if last_3[0] > last_3[1] > last_3[2]:
            print(f"   Micro: DOWNTREND (3 velas caindo)")
            print(f"   [OK] SELL alinhado com micro-downtrend")
        elif last_3[0] < last_3[1] < last_3[2]:
            print(f"   Micro: UPTREND (3 velas subindo)")
            print(f"   [ALERTA] SELL contra micro-uptrend!")
        else:
            print(f"   Micro: LATERAL (sem tendencia clara)")
        print()

    # Mostrar ultimas 5 velas
    print("ULTIMAS 5 VELAS M5:")
    for i in range(max(0, len(rates_m5)-5), len(rates_m5)):
        r = rates_m5[i]
        candle_time = datetime.fromtimestamp(r[0])
        o, h, l, c = r[1], r[2], r[3], r[4]
        color = "VERDE" if c > o else "VERMELHA"
        size = abs(c - o)

        print(f"   {candle_time.strftime('%H:%M')} - O:${o:.2f} H:${h:.2f} L:${l:.2f} C:${c:.2f} ({color}, ${size:.2f})")

print()
print("=" * 60)

# Preco atual
tick = mt5.symbol_info_tick("BTCUSDc")
if tick:
    print("MERCADO ATUAL:")
    print(f"   Bid: ${tick.bid:.2f}")
    print(f"   Ask: ${tick.ask:.2f}")

    # Calcular lucro/prejuizo da ordem SELL
    current_profit_points = (entry_price - tick.bid) / 0.01
    current_profit_dollars = current_profit_points * 0.01 * 0.05

    print()
    print(f"POSICAO SELL ATUAL:")
    print(f"   Entry: ${entry_price:.2f}")
    print(f"   Bid atual: ${tick.bid:.2f}")
    print(f"   Movimento: ${entry_price - tick.bid:.2f}")
    print(f"   Profit: ${current_profit_dollars:.2f}")

    if current_profit_dollars > 0:
        print(f"   [OK] Em LUCRO (preco caiu)")
    else:
        print(f"   [PREJUIZO] Preco subiu apos entrada SELL")

print()
print("=" * 60)

mt5.shutdown()
