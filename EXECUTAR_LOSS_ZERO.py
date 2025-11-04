#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOSS ZERO - SCRIPT DE EXECUÇÃO
Executa a estratégia Loss Zero otimizada para BTC ou GOLD

USO:
- BTC: python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc
- GOLD: python EXECUTAR_LOSS_ZERO.py --live --symbol XAUUSDc
- DEMO: python EXECUTAR_LOSS_ZERO.py --demo --symbol BTCUSDc
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Loss Zero Trading Agent - Multi-Asset Support')
    parser.add_argument('--live', action='store_true', help='Modo live (real)')
    parser.add_argument('--symbol', default='BTCUSDc', help='Símbolo para trading (BTCUSDc, XAUUSDc, etc)')

    args = parser.parse_args()

    # Auto-detect agent based on symbol
    if 'XAU' in args.symbol.upper():
        from src.agents.gold_loss_zero_simple import GoldLossZeroSimple
        agent_class = GoldLossZeroSimple
        asset_name = "GOLD"
        config_info = {
            'volume': '0.01 lotes',
            'sl_mult': '1.5',
            'trailing_act': '0.4',
            'trailing_dist': '0.3',
            'atr_min': '60 pontos'
        }
    else:
        from src.agents.btc_loss_zero_simple import BTCLossZeroSimple
        agent_class = BTCLossZeroSimple
        asset_name = "BTC"
        config_info = {
            'volume': '0.03 lotes',
            'sl_mult': '1.2',
            'trailing_act': '0.3',
            'trailing_dist': '0.2',
            'atr_min': '80 pontos'
        }

    if args.live:
        print("=" * 60)
        print(f"{asset_name} LOSS ZERO - ESTRATEGIA TRAILING STOP")
        print("=" * 60)
        print("")
        print(f"Simbolo: {args.symbol}")
        print("CONFIGURACAO:")
        print(f"  Volume: {config_info['volume']}")
        print(f"  SL: ATR × {config_info['sl_mult']} (dinamico)")
        print("  TP: SEM TP FIXO (lucro ilimitado!)")
        print(f"  Trailing ativa: ATR × {config_info['trailing_act']} de lucro")
        print(f"  Trailing distancia: ATR × {config_info['trailing_dist']}")
        print(f"  ATR minimo: {config_info['atr_min']}")
        print("")
        print("ESTRATEGIA LOSS ZERO:")
        print("  1. Abre posicao com SL (sem TP)")
        print(f"  2. Quando lucrando >= ATR×{config_info['trailing_act']}, trailing ATIVA")
        print("  3. Trailing protege e maximiza lucros")
        print("  4. NUNCA fecha no prejuizo!")
        print("")
        print("=" * 60)
        print("")
    else:
        print("ERRO: Use --live para executar o agente")
        print("Exemplos:")
        print("  python EXECUTAR_LOSS_ZERO.py --live --symbol BTCUSDc")
        print("  python EXECUTAR_LOSS_ZERO.py --live --symbol XAUUSDc")
        return

    # Criar e executar agente
    try:
        agent = agent_class(symbol=args.symbol)
        agent.run()
    except KeyboardInterrupt:
        print("\nAgente parado pelo usuario")
    except Exception as e:
        print(f"Erro fatal: {e}")


if __name__ == "__main__":
    main()
