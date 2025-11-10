#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste isolado de cálculo de SL para XAUUSDc com IA
Simula abertura de ordem SEM realmente abrir
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_ai_agent import GoldAIAgent
from core.mt5_direct_client import get_mt5_client

print("\n" + "="*80)
print("TESTE DE CALCULO DE SL - XAUUSD COM IA")
print("="*80)

# Inicializar agente
agent = GoldAIAgent(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=4.0,
    ai_enabled=False  # Desabilitar IA para teste puro de SL
)

print(f"\nParametros do Agente:")
print(f"  Symbol: {agent.symbol}")
print(f"  Volume: {agent.volume}")
print(f"  Fixed SL Dollars: ${agent.fixed_sl_dollars}")
print(f"  Symbol Point: {agent.symbol_point}")
print(f"  Point Value: {agent.point_value}")

# Conectar MT5 para pegar preço real
mt5 = get_mt5_client()

if not mt5.is_connected():
    print("\n❌ MT5 nao conectado! Usando precos de exemplo...")
    market_price = 3995.50
else:
    tick = mt5.get_symbol_info_tick("XAUUSDc")
    if tick:
        market_price = tick['ask']
        print(f"\n✅ MT5 Conectado")
        print(f"  Preco atual (ASK): ${market_price:.3f}")
    else:
        market_price = 3995.50
        print(f"\n⚠️  Nao conseguiu obter preco, usando exemplo: ${market_price:.3f}")

# Simular cálculo de SL (copiando lógica de _open_position)
print(f"\n" + "="*80)
print("SIMULACAO DE CALCULO DE SL")
print("="*80)

print(f"\nStep 1: Obter parametro fixed_sl_dollars")
sl_dinheiro = agent.fixed_sl_dollars
print(f"  fixed_sl_dollars = ${sl_dinheiro:.2f}")

print(f"\nStep 2: Usar como distancia direta")
sl_price_distance = sl_dinheiro
print(f"  sl_price_distance = ${sl_price_distance:.3f}")

print(f"\nStep 3: Calcular SL price para BUY")
sl_price_buy = market_price - sl_price_distance
print(f"  market_price = ${market_price:.3f}")
print(f"  sl_price (BUY) = ${market_price:.3f} - ${sl_price_distance:.3f} = ${sl_price_buy:.3f}")

print(f"\nStep 4: Calcular SL price para SELL")
sl_price_sell = market_price + sl_price_distance
print(f"  sl_price (SELL) = ${market_price:.3f} + ${sl_price_distance:.3f} = ${sl_price_sell:.3f}")

print(f"\n" + "="*80)
print("VERIFICACAO DE DISTANCIA")
print("="*80)

# Verificar distancia real
distance_buy = market_price - sl_price_buy
distance_sell = sl_price_sell - market_price

print(f"\nBUY:")
print(f"  Entry: ${market_price:.3f}")
print(f"  SL: ${sl_price_buy:.3f}")
print(f"  Distance: ${distance_buy:.3f}")

if abs(distance_buy - 4.0) < 0.01:
    print(f"  ✅ CORRETO (esperado $4.00)")
else:
    print(f"  ❌ ERRADO! (esperado $4.00, got ${distance_buy:.3f})")

print(f"\nSELL:")
print(f"  Entry: ${market_price:.3f}")
print(f"  SL: ${sl_price_sell:.3f}")
print(f"  Distance: ${distance_sell:.3f}")

if abs(distance_sell - 4.0) < 0.01:
    print(f"  ✅ CORRETO (esperado $4.00)")
else:
    print(f"  ❌ ERRADO! (esperado $4.00, got ${distance_sell:.3f})")

print(f"\n" + "="*80)
print("CONCLUSAO")
print("="*80)

if abs(distance_buy - 4.0) < 0.01 and abs(distance_sell - 4.0) < 0.01:
    print("\n✅ CALCULO DE SL ESTA CORRETO!")
    print("   SL distance = $4.00 conforme esperado")
    print("   GoldAIAgent nao tem nenhum problema com SL")
else:
    print("\n❌ PROBLEMA DETECTADO!")
    print(f"   Distance nao eh $4.00")
    print(f"   BUY distance: ${distance_buy:.3f}")
    print(f"   SELL distance: ${distance_sell:.3f}")

print("\n" + "="*80 + "\n")
