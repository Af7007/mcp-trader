#!/usr/bin/env python3
"""
Diagnostico: por que trailing nao esta ativando com $4 de lucro?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_adaptive_agent import GoldAdaptiveAgent
from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("DIAGNOSTICO - TRAILING NAO ATIVA COM $4")
print("="*80)

# Conectar MT5
mt5 = get_mt5_client()
positions = mt5.positions_get(symbol="XAUUSDc")

if not positions:
    print("\n[ERRO] Nenhuma posicao aberta em XAUUSDc")
    exit(1)

pos = positions[0]
print(f"\n[POSICAO ABERTA]")
print(f"  Ticket: {pos['ticket']}")
print(f"  Tipo: {'BUY' if pos['type'] == 0 else 'SELL'}")
print(f"  Entrada: ${pos['price_open']:.5f}")
print(f"  Atual: ${pos['price_current']:.5f}")
print(f"  Profit: ${pos['profit']:.2f}")

# Criar agente para pegar configuracoes
print(f"\n[CRIANDO AGENTE SIMPLES]")
agent_simple = GoldAdaptiveAgent(aggressive_profit_mode=False)
print(f"  Trailing activation (simples): {agent_simple.current_trailing_activation_pontos:.0f} pts")
print(f"  Em dinheiro: ${agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):.2f}")

print(f"\n[CRIANDO AGENTE AGRESSIVO]")
agent_agg = GoldAdaptiveAgent(aggressive_profit_mode=True)
print(f"  Trailing activation (agressivo): {agent_agg.current_trailing_activation_pontos:.0f} pts")
print(f"  Em dinheiro: ${agent_agg._pontos_para_dinheiro(agent_agg.current_trailing_activation_pontos):.2f}")

# Calcular se deveria ativar
print(f"\n[ANALISE]")
profit_dinheiro = pos['profit']
print(f"  Lucro atual: ${profit_dinheiro:.2f}")
print(f"  Simples precisaria: ${agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):.2f}")
print(f"  Agressivo precisaria: ${agent_agg._pontos_para_dinheiro(agent_agg.current_trailing_activation_pontos):.2f}")

if profit_dinheiro >= agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):
    print(f"\n  [DEVERIA ATIVAR] ${profit_dinheiro:.2f} >= ${agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):.2f}")
else:
    print(f"\n  [NAO DEVERIA ATIVAR] ${profit_dinheiro:.2f} < ${agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):.2f}")

# Verificar qual agente esta rodando
print(f"\n[VERIFICAR QUAL AGENTE RODANDO]")
print(f"  - Procure por 'RUN_GOLD_ADAPTIVE.bat' ou 'RUN_GOLD_AGGRESSIVE.bat'")
print(f"  - Agente simples: trailing ativa em ${agent_simple._pontos_para_dinheiro(agent_simple.current_trailing_activation_pontos):.2f}")
print(f"  - Agente agressivo: trailing ativa em ${agent_agg._pontos_para_dinheiro(agent_agg.current_trailing_activation_pontos):.2f}")

print(f"\n[PROBLEMA POTENCIAL]")
print(f"  1. Agente pode estar em modo conservador (0.2) ao invés de agressivo (0.15)")
print(f"  2. Código de ativacao pode ter bug de comparacao")
print(f"  3. Trailing pode ja estar ativo (nao mostra avisos adicionais)")
print(f"  4. Posicao pode estar no modo 'worker' diferente do 'main'")

print("\n" + "="*80)
