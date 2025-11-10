#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug detalhado do cálculo de SL
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# Criar agente
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=4.0
)

print("\n" + "="*80)
print("DEBUG DETALHADO - SL CALCULATION")
print("="*80)

# Mostrar todos os valores importantes
print(f"\nParâmetros do Agente:")
print(f"  symbol: {agent.symbol}")
print(f"  volume: {agent.volume}")
print(f"  fixed_sl_dollars: {agent.fixed_sl_dollars}")
print(f"  symbol_point: {agent.symbol_point}")
print(f"  point_value: {agent.point_value}")
print(f"  current_sl_pontos: {agent.current_sl_pontos}")

print(f"\nTrailing Activation:")
print(f"  trailing_activation_dollar: {agent.trailing_activation_dollar}")
print(f"  trailing_distance_dollar: {agent.trailing_distance_dollar}")
print(f"  trailing_step_dollar: {agent.trailing_step_dollar}")

# Simular abertura
print(f"\nSimulação de Abertura BUY:")
market_price = 3995.50
print(f"  market_price (ASK): ${market_price:.3f}")

# Cálculo conforme código atual
sl_dinheiro = agent.fixed_sl_dollars
print(f"  sl_dinheiro (fixed_sl_dollars): ${sl_dinheiro:.3f}")

sl_price_distance = sl_dinheiro
print(f"  sl_price_distance (direto): ${sl_price_distance:.3f}")

sl_price = market_price - sl_price_distance
print(f"  sl_price (BUY): {market_price:.3f} - {sl_price_distance:.3f} = ${sl_price:.3f}")

# Cálculo alternativo (talvez o que está acontecendo)
print(f"\nAlternativas de cálculo (possíveis erros):")

# Alternativa 1: Usando point_value
sl_pontos_wrong1 = agent.fixed_sl_dollars / agent.point_value
print(f"  fixed_sl_dollars / point_value: {agent.fixed_sl_dollars} / {agent.point_value} = {sl_pontos_wrong1}")
sl_price_wrong1 = market_price - (sl_pontos_wrong1 * agent.symbol_point)
print(f"    → sl_price = {market_price:.3f} - ({sl_pontos_wrong1} * {agent.symbol_point}) = ${sl_price_wrong1:.3f}")

# Alternativa 2: Usando volume
sl_pontos_wrong2 = agent.fixed_sl_dollars / (agent.point_value * agent.volume)
print(f"  fixed_sl_dollars / (point_value * volume): {agent.fixed_sl_dollars} / ({agent.point_value} * {agent.volume}) = {sl_pontos_wrong2}")
sl_price_wrong2 = market_price - (sl_pontos_wrong2 * agent.symbol_point)
print(f"    → sl_price = {market_price:.3f} - ({sl_pontos_wrong2} * {agent.symbol_point}) = ${sl_price_wrong2:.3f}")

# Alternativa 3: Multiplicação acidental
sl_price_wrong3 = market_price - (agent.fixed_sl_dollars / agent.symbol_point)
print(f"  fixed_sl_dollars / symbol_point: {agent.fixed_sl_dollars} / {agent.symbol_point} = {agent.fixed_sl_dollars / agent.symbol_point}")
print(f"    → sl_price = {market_price:.3f} - {agent.fixed_sl_dollars / agent.symbol_point} = ${sl_price_wrong3:.3f}")

# Verificar qual está próximo de 11.80
print(f"\n{'='*80}")
print(f"Qual alternativa produz SL próximo de 11.80 de distância?")
print(f"  CORRETO: distância = {sl_price_distance:.3f}")
print(f"  WRONG1: distância = {abs(sl_price_wrong1 - market_price):.3f}")
print(f"  WRONG2: distância = {abs(sl_price_wrong2 - market_price):.3f}")
print(f"  WRONG3: distância = {abs(sl_price_wrong3 - market_price):.3f}")

if abs(11.80 - abs(sl_price_wrong1 - market_price)) < 0.1:
    print(f"\n⚠️  WRONG1 está gerando 11.80!")
elif abs(11.80 - abs(sl_price_wrong2 - market_price)) < 0.1:
    print(f"\n⚠️  WRONG2 está gerando 11.80!")
elif abs(11.80 - abs(sl_price_wrong3 - market_price)) < 0.1:
    print(f"\n⚠️  WRONG3 está gerando 11.80!")
else:
    print(f"\nNenhuma alternativa gera 11.80 exato...")
    print(f"Talvez o erro esteja em outro lugar.")
