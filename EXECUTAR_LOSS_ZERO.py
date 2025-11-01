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
    print("🚀 BTC LOSS ZERO - AGENTE OTIMIZADO")
    print("="*70)
    print("\nESTRATÉGIA:")
    print("✅ Zero Losses - Trailing stop sempre protege")
    print("✅ Lucros Ilimitados - Sem TP fixo")
    print("✅ Trailing Dinâmico - Cresce com o preço")
    print("✅ Automático - Sem intervenção manual")
    print("\nCONFIGURAÇÃO:")
    print("  Symbol: BTCUSDc")
    print("  Volume: 0.05 lots")
    print("  Trailing Start: 0.5%")
    print("  Trailing Increment: +0.1%")
    print("\nPRESSIONE CTRL+C PARA PARAR")
    print("="*70 + "\n")

    try:
        # Criar agente
        agent = BTCLossZeroOtimizado(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            trailing_start_percent=0.5,
            trailing_increment=0.1,
            use_buy=True,
            use_sell=True
        )

        # Executar
        agent.run()

    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("⛔ Agente parado pelo usuário")
        print("="*70)
        sys.exit(0)

    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ ERRO: {e}")
        print("="*70)
        print("\n⚠️ VERIFIQUE:")
        print("   1. MetaTrader 5 está aberto?")
        print("   2. Você está logado na conta?")
        print("   3. O símbolo BTCUSDc está disponível?")
        print("   4. Python 3.8+ está instalado?")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
