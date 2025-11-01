#!/usr/bin/env python3
"""
Script simples para executar o Agente BTC Loss Zero Otimizado

USE: python EXECUTAR_LOSS_ZERO.py
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.btc_loss_zero_otimizado import BTCLossZeroOtimizado


def main():
    """Executa o agente Loss Zero"""
    print("\n" + "="*70)
    print("BTC LOSS ZERO - AGENTE OTIMIZADO")
    print("="*70)
    print("\nESTRATEGIA:")
    print("[OK] SL/TP de Seguranca - Protecao inicial")
    print("[OK] Trailing Stop Dinamico - Sobe com lucro")
    print("[OK] SL Dinamico - Defende o trailing")
    print("[OK] Lucros Potencialmente Ilimitados")
    print("[OK] Automatico - Sem intervencao manual")
    print("\nCONFIGURACAO:")
    print("  Symbol: BTCUSDc")
    print("  Volume: 0.05 lots")
    print("  SL Inicial (Seguranca): 1.5%")
    print("  TP Inicial (Seguranca): 5.0%")
    print("  Trailing Start: 0.2% (reduzido)")
    print("  Trailing Increment: +0.1%")
    print("\nPRESSIONE CTRL+C PARA PARAR")
    print("="*70 + "\n")

    try:
        # Criar agente com SL/TP dinâmicos
        agent = BTCLossZeroOtimizado(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            trailing_start_percent=0.2,  # Trailing em 0.2% (reduzido)
            trailing_increment=0.1,
            initial_sl_percent=1.5,      # SL de segurança
            initial_tp_percent=5.0,      # TP de segurança
            use_buy=True,
            use_sell=True
        )

        # Executar
        agent.run()

    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("Agente parado pelo usuario")
        print("="*70)
        sys.exit(0)

    except Exception as e:
        print("\n" + "="*70)
        print(f"[ERRO] {e}")
        print("="*70)
        print("\nVERIFIQUE:")
        print("   1. MetaTrader 5 esta aberto?")
        print("   2. Voce esta logado na conta?")
        print("   3. O simbolo BTCUSDc esta disponivel?")
        print("   4. Python 3.8+ esta instalado?")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
