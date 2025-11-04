#!/usr/bin/env python3
"""
Testa usando o código REAL do agente (não reimplementação)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.btc_loss_zero_simple import BTCLossZeroSimple

# Criar agente
agent = BTCLossZeroSimple(symbol="BTCUSDc")

print("="*70)
print("TESTE COM CODIGO REAL DO AGENTE")
print("="*70)
print()

# Obter dados M5 EXATAMENTE como o agente faz
rates_m5 = agent.mt5.copy_rates_from_pos(
    symbol=agent.symbol,
    timeframe="M5",
    start_pos=0,
    count=10
)

print(f"Dados M5 obtidos: {len(rates_m5)} candles")
print()

# Chamar _analyze_m5_trend (a função que deveria retornar sinal)
m5_signal = agent._analyze_m5_trend(rates_m5)

print("Resultado de _analyze_m5_trend:")
if m5_signal:
    print(f"  SINAL GERADO!")
    print(f"  Tipo: {m5_signal['type']}")
    print(f"  Preco: ${m5_signal['price']:,.2f}")
    print(f"  Razao: {m5_signal['reason']}")
else:
    print(f"  NENHUM SINAL (retornou None)")

print()

# Agora testar _get_simple_signal (a função completa)
print("="*70)
print("Testando _get_simple_signal (função completa):")
print("="*70)

full_signal = agent._get_simple_signal()

if full_signal:
    print(f"  SINAL GERADO!")
    print(f"  Tipo: {full_signal['type']}")
    print(f"  Preco: ${full_signal['price']:,.2f}")
    print(f"  Razao: {full_signal['reason']}")
else:
    print(f"  NENHUM SINAL (retornou None)")

print()
