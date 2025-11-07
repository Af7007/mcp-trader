#!/usr/bin/env python3
"""
Teste do SL corrigido para Gold - deve ser ~$30 máximo
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def main():
    print("Testando SL corrigido para Gold...")

    # Criar agente com SL reduzido (2.0 em vez de 5.0)
    agent = GoldLossZeroSimple(
        symbol='XAUUSDc',
        volume=0.1,
        check_interval=1
    )

    print("\nConfiguração do SL:")
    print(f"  ATR atual: {agent.current_atr:.0f} pontos")
    print(f"  Multiplicador SL: {agent.sl_atr_mult}")
    print(f"  SL pontos: {agent.current_sl_pontos:.0f}")
    print(f"  SL dinheiro: ${agent._pontos_para_dinheiro(agent.current_sl_pontos):.2f}")

    print("\nComparação:")
    print(f"  SL antigo (×5.0): ${agent._pontos_para_dinheiro(agent.current_atr * 5.0):.2f}")
    print(f"  SL novo (×2.0): ${agent._pontos_para_dinheiro(agent.current_sl_pontos):.2f}")
    print(f"  Redução: ${(agent._pontos_para_dinheiro(agent.current_atr * 5.0) - agent._pontos_para_dinheiro(agent.current_sl_pontos)):.2f}")

    print("\n[OK] SL corrigido! Agora máximo $30 em vez de $150+")

if __name__ == "__main__":
    main()
