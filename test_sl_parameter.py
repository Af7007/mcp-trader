#!/usr/bin/env python3
"""
Testa se o parametro fixed_sl_dollars esta sendo passado corretamente
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.btc_ai_agent import BTCAIAgent

print("=" * 60)
print("TESTE: Parametro fixed_sl_dollars")
print("=" * 60)
print()

# Test 1: Usando default (5.0 da classe pai)
print("Test 1: Default (sem passar parametro)")
try:
    # Nao podemos instanciar sem MT5, mas podemos ver o erro
    agent1 = BTCAIAgent(symbol="BTCUSDc", volume=0.05)
    print(f"   fixed_sl_dollars = ${agent1.fixed_sl_dollars:.2f}")
except Exception as e:
    print(f"   Erro esperado (MT5 nao conectado): {type(e).__name__}")

print()

# Test 2: Passando 8.0 explicitamente
print("Test 2: fixed_sl_dollars=8.0 (via parametro)")
try:
    agent2 = BTCAIAgent(symbol="BTCUSDc", volume=0.05, fixed_sl_dollars=8.0)
    print(f"   fixed_sl_dollars = ${agent2.fixed_sl_dollars:.2f}")
except Exception as e:
    print(f"   Erro esperado (MT5 nao conectado): {type(e).__name__}")

print()

# Test 3: Verificar se o valor hardcoded foi removido
print("Test 3: Verificando codigo fonte...")
import inspect
from agents.btc_loss_zero_v3 import BTCLossZeroV3

source = inspect.getsource(BTCLossZeroV3.__init__)
if "self.fixed_sl_dollars = 20.0" in source:
    print("   [ERRO] Valor hardcoded 20.0 ainda presente!")
elif "self.fixed_sl_dollars = fixed_sl_dollars" in source:
    print("   [OK] Parametro fixed_sl_dollars sendo usado corretamente")
else:
    print("   [?] Codigo nao encontrado")

print()
print("=" * 60)
