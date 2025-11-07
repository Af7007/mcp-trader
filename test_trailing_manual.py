#!/usr/bin/env python3
"""
Script para testar trailing stop manualmente
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def main():
    print("Testando trailing stop manualmente...")

    # Criar agente
    agent = GoldLossZeroSimple(
        symbol='XAUUSDc',
        volume=0.1,
        check_interval=1
    )

    # Simular uma posição lucrativa
    mock_position = {
        'ticket': 999999,
        'type': 0,  # BUY
        'price_open': 3980.00,  # Entry price
        'profit': 5.0,  # $5 de lucro
        'volume': 0.1,
        'sl': 3970.00,
        'tp': 0.0
    }

    print("Simulando posição com $5 de lucro...")
    print(f"Entry Price: ${mock_position['price_open']:.2f}")
    print(f"Profit: ${mock_position['profit']:.2f}")
    print(f"Trailing Activation: ${agent.trailing_activation_dollar:.2f}")

    # Testar se trailing ativaria
    if mock_position['profit'] >= agent.trailing_activation_dollar:
        print("✅ Trailing DEVERIA ativar!")

        # Calcular trailing stop
        pontos_para_proteger = agent.trailing_distance_dollar / (agent.point_value * agent.volume)
        trailing_price_distance = pontos_para_proteger * agent.symbol_point

        current_price = mock_position['price_open'] + (mock_position['profit'] / (agent.point_value * agent.volume) / agent.symbol_point)

        trailing_stop_price = current_price - trailing_price_distance

        print(f"Current Price (calculado): ${current_price:.2f}")
        print(f"Trailing Stop Price: ${trailing_stop_price:.2f}")
        print(f"Protege: ${agent.trailing_distance_dollar:.2f} de lucro")
    else:
        print("❌ Trailing NÃO ativaria ainda")

    print("\nPara testar com posição real lucrativa:")
    print("1. Abra uma posição BUY no MT5")
    print("2. Deixe o preço subir até ter pelo menos $1 de lucro")
    print("3. Execute o agente - o trailing deve ativar automaticamente")

if __name__ == "__main__":
    main()
