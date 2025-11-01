#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Dados de Teste para Visualizador BTC Loss Zero
===========================================================

Este script gera dados simulados para testar o EA_BTC_Loss_Zero_Visualizer.mq5
sem precisar rodar o agente real.

Uso:
    python testar_visualizador_loss_zero.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

def generate_test_data(scenario: str = "trailing"):
    """
    Gera dados de teste para diferentes cenários

    Cenários:
    - "no_position": Sem posição aberta
    - "new_position": Posição recém aberta
    - "trailing": Posição com trailing ativo
    - "near_tp": Próximo do TP
    - "near_sl": Próximo do SL
    """

    base_data = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "BTCUSDc",
        "current_price": 110235.5,
        "has_position": False,
        "trailing_active": False,
        "trailing_amount_dollars": 0.0,
        "entry_price": 0.0,
        "entry_ticket": 0,
        "position_type": None,
        "sl": 0.0,
        "tp": 0.0,
        "profit": 0.0,
        "trailing_stop_level": 0.0
    }

    if scenario == "no_position":
        # Sem posição
        base_data["current_price"] = 110220.0

    elif scenario == "new_position":
        # Posição recém aberta (sem trailing ainda)
        base_data["has_position"] = True
        base_data["entry_price"] = 110220.0
        base_data["entry_ticket"] = 999999
        base_data["position_type"] = "BUY"
        base_data["current_price"] = 110221.5
        base_data["sl"] = 110216.0  # SL $4 abaixo
        base_data["tp"] = 110240.0  # TP ~$20 acima
        base_data["profit"] = 0.50  # Pequeno lucro, mas ainda não ativou trailing

    elif scenario == "trailing":
        # Posição com trailing ativo
        base_data["has_position"] = True
        base_data["trailing_active"] = True
        base_data["entry_price"] = 110220.0
        base_data["entry_ticket"] = 999999
        base_data["position_type"] = "BUY"
        base_data["current_price"] = 110235.5
        base_data["trailing_amount_dollars"] = 14.5
        base_data["sl"] = 110216.0
        base_data["tp"] = 110240.0
        base_data["profit"] = 15.5
        base_data["trailing_stop_level"] = 110230.5  # Trailing $14.50 abaixo do preço atual

    elif scenario == "near_tp":
        # Próximo do TP
        base_data["has_position"] = True
        base_data["trailing_active"] = True
        base_data["entry_price"] = 110220.0
        base_data["entry_ticket"] = 999999
        base_data["position_type"] = "BUY"
        base_data["current_price"] = 110238.0
        base_data["trailing_amount_dollars"] = 17.0
        base_data["sl"] = 110216.0
        base_data["tp"] = 110240.0
        base_data["profit"] = 18.0
        base_data["trailing_stop_level"] = 110233.0

    elif scenario == "near_sl":
        # Próximo do SL (simulando queda)
        base_data["has_position"] = True
        base_data["trailing_active"] = False  # Ainda não ativou
        base_data["entry_price"] = 110220.0
        base_data["entry_ticket"] = 999999
        base_data["position_type"] = "BUY"
        base_data["current_price"] = 110217.0  # Caindo
        base_data["sl"] = 110216.0
        base_data["tp"] = 110240.0
        base_data["profit"] = -3.0  # Prejuízo

    return base_data


def save_test_data(data: dict, filename: str = "btc_loss_zero_data.json"):
    """Salva dados de teste em JSON"""
    export_path = Path(__file__).parent / filename

    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Dados de teste salvos em: {export_path}")


def run_dynamic_test():
    """Executa teste dinâmico simulando movimento de preço"""
    print("=" * 70)
    print("TESTE DINÂMICO DO VISUALIZADOR BTC LOSS ZERO")
    print("=" * 70)
    print("\nSimulando movimento de preço com trailing stop...")
    print("Pressione Ctrl+C para parar\n")

    scenarios = [
        ("no_position", "Sem posição - Analisando mercado", 5),
        ("new_position", "Nova posição BUY aberta - Aguardando $1 de lucro", 10),
        ("trailing", "Trailing ativado! Defendendo $14.50 de lucro", 10),
        ("near_tp", "Próximo do TP - $18 de lucro", 10),
        ("trailing", "Voltou para trailing - $15.50 de lucro", 10),
        ("no_position", "Posição fechada - Buscando nova oportunidade", 5),
    ]

    try:
        cycle = 0
        while True:
            for scenario_name, description, duration in scenarios:
                print(f"\n[Ciclo {cycle + 1}] {description}")
                data = generate_test_data(scenario_name)
                save_test_data(data)

                # Aguardar duração do cenário
                for i in range(duration):
                    print(f"  Aguardando... {i+1}/{duration}s", end='\r')
                    time.sleep(1)

                cycle += 1

    except KeyboardInterrupt:
        print("\n\n✅ Teste finalizado pelo usuário")


def main():
    """Função principal"""
    print("=" * 70)
    print("GERADOR DE DADOS DE TESTE - VISUALIZADOR BTC LOSS ZERO")
    print("=" * 70)
    print("\nEscolha o modo de teste:")
    print("\n1. Gerar dados estáticos (snapshot único)")
    print("2. Teste dinâmico (simula movimento contínuo)")
    print("\n0. Sair")

    choice = input("\nEscolha (1/2/0): ").strip()

    if choice == "1":
        print("\n" + "=" * 70)
        print("CENÁRIOS DISPONÍVEIS")
        print("=" * 70)
        print("\n1. no_position     - Sem posição aberta")
        print("2. new_position    - Posição recém aberta (sem trailing)")
        print("3. trailing        - Posição com trailing ativo ($14.50)")
        print("4. near_tp         - Próximo do TP ($18 de lucro)")
        print("5. near_sl         - Próximo do SL (prejuízo)")

        scenario_choice = input("\nEscolha o cenário (1-5): ").strip()

        scenarios = {
            "1": "no_position",
            "2": "new_position",
            "3": "trailing",
            "4": "near_tp",
            "5": "near_sl"
        }

        scenario = scenarios.get(scenario_choice)
        if scenario:
            data = generate_test_data(scenario)
            save_test_data(data)

            print("\n" + "=" * 70)
            print("DADOS GERADOS")
            print("=" * 70)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("\n✅ Agora adicione o EA ao gráfico BTCUSDc no MT5")
            print("   O EA lerá este arquivo e mostrará as linhas!")
        else:
            print("❌ Opção inválida")

    elif choice == "2":
        run_dynamic_test()

    elif choice == "0":
        print("\n👋 Até logo!")
    else:
        print("\n❌ Opção inválida")


if __name__ == "__main__":
    main()
