#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug simples do calculo de SL - sem unicode
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=4.0
)

print("\nDEBUG - SL CALCULATION")
print("="*80)

print("\nParametros:")
print(f"  volume: {agent.volume}")
print(f"  fixed_sl_dollars: {agent.fixed_sl_dollars}")
print(f"  symbol_point: {agent.symbol_point}")
print(f"  point_value: {agent.point_value}")

market_price = 3995.50

print(f"\nCorrecto (direto):")
sl_distance = agent.fixed_sl_dollars
print(f"  distance = {sl_distance}")
print(f"  sl_price = {market_price} - {sl_distance} = {market_price - sl_distance}")

print(f"\nAlternativa 1 (dividido por point_value):")
sl_pontos = agent.fixed_sl_dollars / agent.point_value
print(f"  pontos = {agent.fixed_sl_dollars} / {agent.point_value} = {sl_pontos}")
sl_price = market_price - (sl_pontos * agent.symbol_point)
print(f"  sl_price = {market_price} - ({sl_pontos} * {agent.symbol_point}) = {sl_price}")
print(f"  distance = {market_price - sl_price}")

print(f"\nAlternativa 2 (dividido por point_value*volume):")
sl_pontos = agent.fixed_sl_dollars / (agent.point_value * agent.volume)
print(f"  pontos = {agent.fixed_sl_dollars} / ({agent.point_value} * {agent.volume}) = {sl_pontos}")
sl_price = market_price - (sl_pontos * agent.symbol_point)
print(f"  sl_price = {market_price} - ({sl_pontos} * {agent.symbol_point}) = {sl_price}")
print(f"  distance = {market_price - sl_price}")

print(f"\nAlternativa 3 (multiplicado por point_value):")
sl_distance = agent.fixed_sl_dollars * agent.point_value
print(f"  distance = {agent.fixed_sl_dollars} * {agent.point_value} = {sl_distance}")
sl_price = market_price - sl_distance
print(f"  sl_price = {market_price} - {sl_distance} = {sl_price}")

print(f"\nAlternativa 4 (multiplicado por volume):")
sl_distance = agent.fixed_sl_dollars * agent.volume
print(f"  distance = {agent.fixed_sl_dollars} * {agent.volume} = {sl_distance}")
sl_price = market_price - sl_distance
print(f"  sl_price = {market_price} - {sl_distance} = {sl_price}")

print(f"\nAlternativa 5 (dividido por symbol_point):")
sl_distance = agent.fixed_sl_dollars / agent.symbol_point
print(f"  distance = {agent.fixed_sl_dollars} / {agent.symbol_point} = {sl_distance}")
sl_price = market_price - sl_distance
print(f"  sl_price = {market_price} - {sl_distance} = {sl_price}")

print(f"\nAlternativa 6 (multiplicado por point_value * volume):")
sl_distance = agent.fixed_sl_dollars * agent.point_value * agent.volume
print(f"  distance = {agent.fixed_sl_dollars} * {agent.point_value} * {agent.volume} = {sl_distance}")
sl_price = market_price - sl_distance
print(f"  sl_price = {market_price} - {sl_distance} = {sl_price}")

print(f"\n" + "="*80)
print(f"QUAL PRODUZ DISTANCE PROXIMO DE 11.80?")
print(f"  ALT1 distance: {market_price - (agent.fixed_sl_dollars / agent.point_value * agent.symbol_point)}")
print(f"  ALT2 distance: {market_price - (agent.fixed_sl_dollars / (agent.point_value * agent.volume) * agent.symbol_point)}")
print(f"  ALT3 distance: {agent.fixed_sl_dollars * agent.point_value}")
print(f"  ALT4 distance: {agent.fixed_sl_dollars * agent.volume}")
print(f"  ALT5 distance: {agent.fixed_sl_dollars / agent.symbol_point}")
print(f"  ALT6 distance: {agent.fixed_sl_dollars * agent.point_value * agent.volume}")
