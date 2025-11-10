#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico rápido do cálculo de SL
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# Criar agente com parâmetros explícitos
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=4.0
)

print("="*80)
print("DIAGNÓSTICO DE CÁLCULO DE SL")
print("="*80)
print(f"Symbol: {agent.symbol}")
print(f"Volume: {agent.volume} lotes")
print(f"Fixed SL Dollars: ${agent.fixed_sl_dollars:.2f}")
print(f"Symbol Point: {agent.symbol_point}")
print(f"Point Value: {agent.point_value}")
print(f"Current SL Pontos: {agent.current_sl_pontos}")
print(f"")

# Simular cálculo de abertura
print("CÁLCULO INICIAL DE SL (na abertura):")
print("-" * 80)

sl_dinheiro = agent.fixed_sl_dollars
print(f"  sl_dinheiro: ${sl_dinheiro:.2f}")
print(f"  symbol_point: {agent.symbol_point}")

# SL é preço absoluto
sl_price_distance = sl_dinheiro
print(f"  sl_price_distance (distância direta): ${sl_price_distance:.3f}")

# Simular preço atual
market_price = 3995.50  # Preço de exemplo
print(f"  market_price (exemplo): ${market_price:.3f}")

sl_price = market_price - sl_price_distance  # BUY
print(f"  sl_price (BUY): ${market_price:.3f} - {sl_price_distance:.3f} = ${sl_price:.3f}")
print(f"")

# Cálculo de trailing activation
print("CÁLCULO DE ATIVAÇÃO DO TRAILING:")
print("-" * 80)

trailing_distance_dollar = agent.trailing_distance_dollar
volume = agent.volume
point_value = agent.point_value

pontos_para_proteger = trailing_distance_dollar / (point_value * volume)
print(f"  trailing_distance_dollar: ${trailing_distance_dollar:.2f}")
print(f"  point_value: {point_value}")
print(f"  volume: {volume}")
print(f"  pontos_para_proteger: {pontos_para_proteger:.4f}")

trailing_price_distance = pontos_para_proteger * agent.symbol_point
print(f"  trailing_price_distance (pontos × symbol_point): {trailing_price_distance:.5f}")

trailing_stop_price = market_price - trailing_price_distance  # BUY
print(f"  trailing_stop_price (BUY): ${market_price:.3f} - {trailing_price_distance:.5f} = ${trailing_stop_price:.3f}")
print(f"")

print("="*80)
print(f"⚠️  DIFERENÇA DETECTADA:")
print(f"  SL Inicial: ${sl_price:.3f}")
print(f"  Trailing Ativação: ${trailing_stop_price:.3f}")
print(f"  Diferença: ${abs(sl_price - trailing_stop_price):.3f}")
print("="*80)

# Verificar se há problema
if abs(sl_price - trailing_stop_price) > 0.1:
    print(f"❌ PROBLEMA ENCONTRADO: Os valores de SL inicial e trailing são diferentes!")
    print(f"   O SL inicial deveria ser consistente com a ativação do trailing.")
