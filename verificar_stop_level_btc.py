#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica Stop Level mínimo para BTCUSDc
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def verificar_stop_level():
    """
    Verifica configurações de stop level
    """
    print("="*70)
    print("VERIFICAÇÃO DE STOP LEVEL - BTCUSDc")
    print("="*70)
    print()

    mt5 = get_mt5_client()

    # Verificar informações do símbolo
    symbol_info = mt5.get_symbol_info("BTCUSDc")

    if not symbol_info:
        print("ERRO: Símbolo BTCUSDc não encontrado!")
        return

    print("[1] INFORMAÇÕES DO SÍMBOLO BTCUSDc")
    print(f"   Descrição: {symbol_info.get('description', 'N/A')}")
    print(f"   Bid: ${symbol_info.get('bid', 0):.2f}")
    print(f"   Ask: ${symbol_info.get('ask', 0):.2f}")
    print(f"   Spread: {symbol_info.get('spread', 0)} points")
    print()

    print("[2] CONFIGURAÇÕES DE STOPS")
    stops_level = symbol_info.get('trade_stops_level', 0)
    freeze_level = symbol_info.get('trade_freeze_level', 0)
    point = symbol_info.get('point', 0.01)

    print(f"   Stops Level: {stops_level} points")
    print(f"   Freeze Level: {freeze_level} points")
    print(f"   Point Size: {point}")
    print()

    # Calcular distância mínima em dólares
    if stops_level > 0:
        min_distance_dollars = stops_level * point
        print(f"   Distância Mínima SL/TP: {stops_level} points = ${min_distance_dollars:.2f}")
    else:
        print(f"   Distância Mínima SL/TP: Não há limite (stops_level = 0)")
    print()

    print("[3] CONFIGURAÇÃO ATUAL DO AGENTE")
    current_price = symbol_info.get('bid', 110000)
    sl_distance = 30.0
    tp_distance = 50.0

    print(f"   Preço Atual: ${current_price:.2f}")
    print(f"   SL Configurado: ${sl_distance} de distância")
    print(f"   TP Configurado: ${tp_distance} de distância")
    print()

    # Verificar se está dentro do permitido
    if stops_level > 0:
        min_distance_dollars = stops_level * point
        print("[4] VALIDAÇÃO")

        if sl_distance >= min_distance_dollars:
            print(f"   SL: OK (${sl_distance} >= ${min_distance_dollars:.2f})")
        else:
            print(f"   SL: INVALIDO! (${sl_distance} < ${min_distance_dollars:.2f})")
            print(f"       Sugestão: Use no mínimo ${min_distance_dollars:.2f}")

        if tp_distance >= min_distance_dollars:
            print(f"   TP: OK (${tp_distance} >= ${min_distance_dollars:.2f})")
        else:
            print(f"   TP: INVALIDO! (${tp_distance} < ${min_distance_dollars:.2f})")
            print(f"       Sugestão: Use no mínimo ${min_distance_dollars:.2f}")
    else:
        print("[4] VALIDAÇÃO")
        print("   Sem restrições de stop level (qualquer distância permitida)")

    print()

    # Testar ordem de exemplo
    print("[5] TESTE DE ORDEM (SEM EXECUTAR)")
    print(f"   Para SELL a ${current_price:.2f}:")
    print(f"   - SL seria: ${current_price + sl_distance:.2f} (+${sl_distance})")
    print(f"   - TP seria: ${current_price - tp_distance:.2f} (-${tp_distance})")

    print()
    print("="*70)

if __name__ == "__main__":
    verificar_stop_level()
