#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples de calculo de SL - sem unicode
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_ai_agent import GoldAIAgent

print("\n" + "="*80)
print("TESTE DE CALCULO DE SL - XAUUSD COM IA")
print("="*80)

# Inicializar agente
agent = GoldAIAgent(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=4.0,
    ai_enabled=False
)

print("\nParametros:")
print(f"  Symbol: {agent.symbol}")
print(f"  Fixed SL Dollars: ${agent.fixed_sl_dollars}")
print(f"  Symbol Point: {agent.symbol_point}")

# Preco de exemplo
market_price = 3995.50

print(f"\nSimulacao com preco: ${market_price:.3f}")
print("\n" + "="*80)
print("CALCULO DE SL")
print("="*80)

# Cálculo conforme código atual
sl_dinheiro = agent.fixed_sl_dollars
print(f"\n1. fixed_sl_dollars = ${sl_dinheiro:.2f}")

sl_price_distance = sl_dinheiro
print(f"2. sl_price_distance = ${sl_price_distance:.3f}")

# BUY
sl_price_buy = market_price - sl_price_distance
distance_buy = market_price - sl_price_buy
print(f"\n3. Para BUY:")
print(f"   market_price = ${market_price:.3f}")
print(f"   sl_price = ${market_price:.3f} - ${sl_price_distance:.3f} = ${sl_price_buy:.3f}")
print(f"   distance = ${distance_buy:.3f}")

# SELL
sl_price_sell = market_price + sl_price_distance
distance_sell = sl_price_sell - market_price
print(f"\n4. Para SELL:")
print(f"   market_price = ${market_price:.3f}")
print(f"   sl_price = ${market_price:.3f} + ${sl_price_distance:.3f} = ${sl_price_sell:.3f}")
print(f"   distance = ${distance_sell:.3f}")

print("\n" + "="*80)
print("RESULTADO")
print("="*80)

buy_ok = abs(distance_buy - 4.0) < 0.01
sell_ok = abs(distance_sell - 4.0) < 0.01

if buy_ok and sell_ok:
    print("\n[OK] SL ESTA CORRETO!")
    print(f"BUY distance: ${distance_buy:.3f} (esperado $4.00)")
    print(f"SELL distance: ${distance_sell:.3f} (esperado $4.00)")
else:
    print("\n[ERRO] SL INCORRETO!")
    print(f"BUY distance: ${distance_buy:.3f} (esperado $4.00) - {'OK' if buy_ok else 'ERRO'}")
    print(f"SELL distance: ${distance_sell:.3f} (esperado $4.00) - {'OK' if sell_ok else 'ERRO'}")

print("\n" + "="*80 + "\n")
