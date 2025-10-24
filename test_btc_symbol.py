#!/usr/bin/env python3
"""Testa se BTCUSDm está disponível e funcionando"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def test_btc_symbol():
    """Testa BTCUSD com e sem 'c'."""
    print("="*60)
    print("🧪 TESTANDO SÍMBOLOS BTC")
    print("="*60)
    print()

    mt5 = get_mt5_client()

    # Testar BTCUSDm
    print("[1] Testando BTCUSDm...")
    symbol_info = mt5.get_symbol_info("BTCUSDm")
    if symbol_info:
        print(f"    ✅ BTCUSDm encontrado!")
        print(f"       Bid: ${symbol_info.get('bid', 0):,.2f}")
        print(f"       Ask: ${symbol_info.get('ask', 0):,.2f}")
        print(f"       Spread: {symbol_info.get('spread', 0)} points")
        print(f"       Volume Min: {symbol_info.get('volume_min', 0)}")
        print(f"       Volume Max: {symbol_info.get('volume_max', 0)}")
    else:
        print("    ❌ BTCUSDm NÃO encontrado")

    print()

    # Testar BTCUSD (sem c)
    print("[2] Testando BTCUSD (sem c)...")
    symbol_info = mt5.get_symbol_info("BTCUSD")
    if symbol_info:
        print(f"    ✅ BTCUSD encontrado!")
        print(f"       Bid: ${symbol_info.get('bid', 0):,.2f}")
        print(f"       Ask: ${symbol_info.get('ask', 0):,.2f}")
    else:
        print("    ❌ BTCUSD NÃO encontrado")

    print()

    # Testar rates
    print("[3] Testando obtenção de rates para BTCUSDm...")
    rates = mt5.copy_rates_from_pos(
        symbol="BTCUSDm",
        timeframe="M5",
        start_pos=0,
        count=10
    )

    if rates:
        print(f"    ✅ {len(rates)} barras obtidas!")
        print(f"       Última barra:")
        print(f"       Open:  ${rates[-1].get('open', 0):,.2f}")
        print(f"       High:  ${rates[-1].get('high', 0):,.2f}")
        print(f"       Low:   ${rates[-1].get('low', 0):,.2f}")
        print(f"       Close: ${rates[-1].get('close', 0):,.2f}")
    else:
        print("    ❌ Erro ao obter rates")

    print()
    print("="*60)
    print("✅ TESTE CONCLUÍDO!")
    print("="*60)
    print()

    if symbol_info and rates:
        print("🎯 BTCUSDm está OK para usar no agente!")
        return True
    else:
        print("❌ BTCUSDm não está disponível. Verifique:")
        print("   1. BTCUSDm está no Market Watch do MT5?")
        print("   2. Adicione o símbolo no MT5")
        return False

if __name__ == "__main__":
    test_btc_symbol()
