#!/usr/bin/env python3
"""
Testa se os cálculos de pontos para dinheiro estão corretos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_loss_zero_simple import GoldLossZeroSimple
from src.agents.btc_loss_zero_simple import BTCLossZeroSimple

print("="*70)
print("TESTE DE CÁLCULO: PONTOS PARA DINHEIRO")
print("="*70)
print()

# Testar GOLD
print("="*70)
print("GOLD (XAUUSDc)")
print("="*70)

gold_agent = GoldLossZeroSimple(symbol="XAUUSDc")
print()

# Testar conversões
test_pontos = [1, 10, 24, 50, 100]

print("Conversões de pontos para dinheiro:")
for pontos in test_pontos:
    dinheiro = gold_agent._pontos_para_dinheiro(pontos)
    print(f"  {pontos:3.0f} pontos = ${dinheiro:.4f}")

print()

# Simular trailing
atr_gold = 60  # Gold ATR típico
sl_pontos = atr_gold * gold_agent.sl_atr_mult
trailing_act = atr_gold * gold_agent.trailing_activation_mult
trailing_dist = atr_gold * gold_agent.trailing_distance_mult

print(f"Simulação com ATR={atr_gold} pontos:")
print(f"  SL: {sl_pontos:.0f} pts = ${gold_agent._pontos_para_dinheiro(sl_pontos):.2f}")
print(f"  Trailing ativa: {trailing_act:.0f} pts = ${gold_agent._pontos_para_dinheiro(trailing_act):.2f}")
print(f"  Trailing dist: {trailing_dist:.0f} pts = ${gold_agent._pontos_para_dinheiro(trailing_dist):.2f}")
print()

# Testar BTC
print("="*70)
print("BTC (BTCUSDc)")
print("="*70)

btc_agent = BTCLossZeroSimple(symbol="BTCUSDc")
print()

print("Conversões de pontos para dinheiro:")
for pontos in test_pontos:
    dinheiro = btc_agent._pontos_para_dinheiro(pontos)
    print(f"  {pontos:3.0f} pontos = ${dinheiro:.4f}")

print()

# Simular trailing
atr_btc = 100  # BTC ATR típico
sl_pontos = atr_btc * btc_agent.sl_atr_mult
trailing_act = atr_btc * btc_agent.trailing_activation_mult
trailing_dist = atr_btc * btc_agent.trailing_distance_mult

print(f"Simulação com ATR={atr_btc} pontos:")
print(f"  SL: {sl_pontos:.0f} pts = ${btc_agent._pontos_para_dinheiro(sl_pontos):.2f}")
print(f"  Trailing ativa: {trailing_act:.0f} pts = ${btc_agent._pontos_para_dinheiro(trailing_act):.2f}")
print(f"  Trailing dist: {trailing_dist:.0f} pts = ${btc_agent._pontos_para_dinheiro(trailing_dist):.2f}")
print()

print("="*70)
print("VALIDAÇÃO")
print("="*70)
print()
print("Execute o agente e verifique se os valores fazem sentido:")
print("  1. Compare com valores mostrados no MT5")
print("  2. 1 ponto deve valer ~$0.01 para Gold 0.01 lote")
print("  3. 1 ponto deve valer ~$0.03 para BTC 0.03 lote")
print()
