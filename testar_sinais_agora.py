#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido se sinais estão sendo gerados AGORA
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.btc_loss_zero_simple import BTCLossZeroSimple

def main():
    print("="*70)
    print("TESTE DE SINAIS - BTC LOSS ZERO v2.0 BALANCEADO")
    print("="*70)
    print()

    agent = BTCLossZeroSimple(symbol="BTCUSDc")

    print("Configuracoes:")
    print(f"  Volume: {agent.volume} lotes")
    print(f"  SL multiplier: {agent.sl_atr_mult}")
    print(f"  Trailing activation: {agent.trailing_activation_mult}")
    print()

    print("Testando geracao de sinais...")
    print()

    # Tentar gerar sinal
    signal = agent._get_simple_signal()

    if signal:
        print("="*70)
        print("SINAL GERADO!")
        print("="*70)
        print(f"  Tipo: {signal['type']}")
        print(f"  Preco: ${signal['price']:,.2f}")
        print(f"  Razao: {signal['reason']}")
        print()
        print("STATUS: SUCESSO - Filtros estao funcionando!")
    else:
        print("="*70)
        print("NENHUM SINAL GERADO")
        print("="*70)
        print()
        print("Isso pode ser normal se:")
        print("  - Mercado esta em tendencia lateral")
        print("  - Momentum insuficiente no momento")
        print("  - M15 nao confirmou a tendencia")
        print()
        print("Execute novamente em alguns minutos.")

    print()


if __name__ == "__main__":
    main()
