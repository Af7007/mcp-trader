#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de cálculo de SL para XAUUSDc (Gold)
Verifica se o cálculo está correto para volume 0.02 e SL de $6
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def test_sl_calculation():
    """
    Testa o cálculo de SL para Gold
    """
    print("TESTE DE CÁLCULO DE SL PARA XAUUSDc (GOLD)")
    print("="*50)

    # Criar agente com parâmetros padrão
    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.02,  # Volume usado no teste
        stop_loss_atr_multiplier=5.0,
        trailing_activation_atr_multiplier=0.4,
        trailing_distance_atr_multiplier=0.3
    )

    print(f"Volume: {agent.volume}")
    print(f"Symbol Point: {agent.symbol_point}")
    print(f"Point Value: ${agent.point_value:.4f}")
    print()

    # Simular ATR calculado
    atr_pontos = 60000.0  # ATR padrão em pontos
    print(f"ATR (pontos MT5): {atr_pontos:,.0f}")

    # Calcular SL
    sl_pontos = atr_pontos * agent.sl_atr_mult
    sl_dinheiro = agent._pontos_para_dinheiro(sl_pontos)

    print(f"SL Multiplier: {agent.sl_atr_mult}")
    print(f"SL Pontos: {sl_pontos:,.0f}")
    print(f"SL Dinheiro: ${sl_dinheiro:.2f}")
    print()

    # Calcular Trailing Activation
    trailing_activation_pontos = atr_pontos * agent.trailing_activation_mult
    trailing_activation_dinheiro = agent._pontos_para_dinheiro(trailing_activation_pontos)

    print(f"Trailing Activation Multiplier: {agent.trailing_activation_mult}")
    print(f"Trailing Activation Pontos: {trailing_activation_pontos:,.0f}")
    print(f"Trailing Activation Dinheiro: ${trailing_activation_dinheiro:.2f}")
    print()

    # Calcular Trailing Distance
    trailing_distance_pontos = atr_pontos * agent.trailing_distance_mult
    trailing_distance_dinheiro = agent._pontos_para_dinheiro(trailing_distance_pontos)

    print(f"Trailing Distance Multiplier: {agent.trailing_distance_mult}")
    print(f"Trailing Distance Pontos: {trailing_distance_pontos:,.0f}")
    print(f"Trailing Distance Dinheiro: ${trailing_distance_dinheiro:.2f}")
    print()

    # Verificar se SL é $6
    expected_sl = 6.0
    if abs(sl_dinheiro - expected_sl) < 0.01:
        print(f"✅ SL CORRETO: ${sl_dinheiro:.2f} (esperado: ${expected_sl:.2f})")
    else:
        print(f"❌ SL INCORRETO: ${sl_dinheiro:.2f} (esperado: ${expected_sl:.2f})")

    # Verificar se Trailing Activation é razoável
    expected_trailing_activation = 4.8  # 24,000 pontos * 0.001 * 0.02
    if abs(trailing_activation_dinheiro - expected_trailing_activation) < 0.01:
        print(f"✅ Trailing Activation CORRETO: ${trailing_activation_dinheiro:.2f}")
    else:
        print(f"❌ Trailing Activation INCORRETO: ${trailing_activation_dinheiro:.2f} (esperado: ${expected_trailing_activation:.2f})")

    print()
    print("RESUMO:")
    print(f"- SL: ${sl_dinheiro:.2f} (deve ser $6.00)")
    print(f"- Trailing ativa com: ${trailing_activation_dinheiro:.2f} de lucro")
    print(f"- Trailing distancia: ${trailing_distance_dinheiro:.2f}")

if __name__ == "__main__":
    test_sl_calculation()
