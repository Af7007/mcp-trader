#!/usr/bin/env python3
"""Testa se símbolos Forex estão disponíveis e funcionando"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def test_symbol(symbol_name: str):
    """Testa um símbolo específico."""
    mt5 = get_mt5_client()

    print(f"[•] Testando {symbol_name}...")
    symbol_info = mt5.get_symbol_info(symbol_name)

    if not symbol_info:
        print(f"    ❌ {symbol_name} NÃO encontrado")
        return False

    print(f"    ✅ {symbol_name} encontrado!")
    print(f"       Bid: {symbol_info.get('bid', 0):.5f}")
    print(f"       Ask: {symbol_info.get('ask', 0):.5f}")
    print(f"       Spread: {symbol_info.get('spread', 0)} points")
    print(f"       Volume Min: {symbol_info.get('volume_min', 0)}")
    print(f"       Volume Max: {symbol_info.get('volume_max', 0)}")
    print(f"       Volume Step: {symbol_info.get('volume_step', 0)}")

    # Testar rates
    rates = mt5.copy_rates_from_pos(
        symbol=symbol_name,
        timeframe="M5",
        start_pos=0,
        count=10
    )

    if rates:
        print(f"    ✅ {len(rates)} barras obtidas!")
        print(f"       Última barra:")
        print(f"       Open:  {rates[-1].get('open', 0):.5f}")
        print(f"       High:  {rates[-1].get('high', 0):.5f}")
        print(f"       Low:   {rates[-1].get('low', 0):.5f}")
        print(f"       Close: {rates[-1].get('close', 0):.5f}")
        return True
    else:
        print(f"    ❌ Erro ao obter rates para {symbol_name}")
        return False

def main():
    """Testa todos os símbolos Forex."""
    print("="*60)
    print("🧪 TESTANDO SÍMBOLOS FOREX")
    print("="*60)
    print()

    symbols = [
        ("GBPUSDc", "Libra Esterlina"),
        ("EURUSDc", "Euro"),
        ("USDJPYc", "Yen Japonês")
    ]

    results = {}

    for symbol, name in symbols:
        print(f"{'='*60}")
        print(f"💱 {name} ({symbol})")
        print(f"{'='*60}")
        results[symbol] = test_symbol(symbol)
        print()

    print("="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print()

    all_ok = True
    for symbol, name in symbols:
        status = "✅ OK" if results[symbol] else "❌ FALHOU"
        print(f"   {status} - {symbol} ({name})")
        if not results[symbol]:
            all_ok = False

    print()
    print("="*60)

    if all_ok:
        print("✅ TODOS OS SÍMBOLOS ESTÃO OK!")
        print()
        print("💡 Volumes recomendados para Forex:")
        print("   GBPUSDc: 0.10 lots")
        print("   EURUSDc: 0.10 lots")
        print("   USDJPYc: 0.10 lots")
        print()
        print("▶️  Scripts disponíveis:")
        print("   RUN_GBP_AGENT.bat")
        print("   RUN_EUR_AGENT.bat")
        print("   RUN_JPY_AGENT.bat")
        print("   RUN_ALL_FOREX_AGENTS.bat")
        print()
        return True
    else:
        print("❌ ALGUNS SÍMBOLOS NÃO ESTÃO DISPONÍVEIS")
        print()
        print("Verifique:")
        print("   1. Símbolos estão no Market Watch do MT5?")
        print("   2. Adicione os símbolos manualmente no MT5")
        print()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
