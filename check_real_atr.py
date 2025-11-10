#!/usr/bin/env python3
"""
Verifica o ATR real do BTC para ajustar a formula
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

print("=" * 60)
print("VERIFICANDO ATR REAL DO BTC")
print("=" * 60)
print()

# Pegar dados M5
rates_m5 = mt5.copy_rates_from_pos("BTCUSDc", mt5.TIMEFRAME_M5, 0, 20)

if rates_m5 is None or len(rates_m5) < 15:
    print("Erro ao obter dados M5")
    mt5.shutdown()
    sys.exit(1)

# Calcular ATR manualmente
def calculate_atr(rates, period=14):
    atr_sum = 0
    for i in range(period):
        high = rates[i]['high']
        low = rates[i]['low']
        close_prev = rates[i+1]['close'] if i+1 < len(rates) else rates[i]['close']

        tr = max(
            high - low,
            abs(high - close_prev),
            abs(low - close_prev)
        )
        atr_sum += tr

    return atr_sum / period if period > 0 else 0

atr = calculate_atr(rates_m5, 14)

# Preco atual
current_price = rates_m5[0]['close']

# Symbol info
symbol_info = mt5.symbol_info("BTCUSDc")
point = symbol_info.point
tick_value = symbol_info.trade_tick_value

print(f"Preco atual: ${current_price:.2f}")
print(f"ATR (14): {atr:.4f}")
print()
print(f"Symbol Info:")
print(f"   Point: {point}")
print(f"   Tick Value: ${tick_value:.4f}")
print()

# Entender a escala do ATR
print("INTERPRETACAO:")
if atr < 1:
    print(f"   ATR {atr:.4f} parece estar em pontos de tick (0.01)")
    print(f"   Em dolares de preco: ${atr * 100:.2f}")
elif atr < 100:
    print(f"   ATR {atr:.2f} pode ser em dolares de preco")
else:
    print(f"   ATR {atr:.2f} provavelmente em pontos grandes")

print()
print("TESTE DE CONVERSAO:")
print()

# Para volume 0.05
volume = 0.05

# Cenario 1: ATR em pontos de tick
if atr < 1:
    atr_price = atr * 100  # Converter para dolares
    print(f"1. Se ATR esta em tick points (0.01):")
    print(f"   ATR em dolares: ${atr_price:.2f}")

    # SL = 60% do ATR em preco
    sl_distance_price = atr_price * 0.6
    print(f"   60% do ATR: ${sl_distance_price:.2f}")

    # Cada $1 de preco = tick_value * volume
    dollars_per_price_point = tick_value * volume
    sl_dollars = sl_distance_price * dollars_per_price_point

    print(f"   Cada $1 preco = ${dollars_per_price_point:.4f} P&L")
    print(f"   SL final: ${sl_dollars:.2f}")

print()

# Cenario 2: ATR ja em dolares
print(f"2. Se ATR ja esta em dolares de preco:")
atr_price = atr
print(f"   ATR: ${atr_price:.2f}")

sl_distance_price = atr_price * 0.6
print(f"   60% do ATR: ${sl_distance_price:.2f}")

dollars_per_price_point = tick_value * volume
sl_dollars = sl_distance_price * dollars_per_price_point

print(f"   Cada $1 preco = ${dollars_per_price_point:.4f} P&L")
print(f"   SL final: ${sl_dollars:.2f}")

print()
print("=" * 60)
print("CONCLUSAO:")
print("=" * 60)
print()
print("Para ajustar a formula, precisamos saber:")
print("1. Em que unidade o ATR esta (pontos ou dolares)?")
print("2. Qual a conversao correta para P&L?")
print()

mt5.shutdown()
