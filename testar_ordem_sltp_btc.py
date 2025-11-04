#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa ordem com SL/TP no BTCUSDc
ATENÇÃO: Este script IRÁ ABRIR UMA ORDEM REAL de 0.01 lote!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client
import time

def testar_ordem_sltp():
    """
    Testa abertura de ordem com SL/TP
    """
    print("="*70)
    print("TESTE DE ORDEM COM SL/TP - BTCUSDc")
    print("="*70)
    print()

    print("ATENÇÃO: Este script IRÁ ABRIR UMA ORDEM REAL!")
    print("Volume: 0.01 lote (mínimo)")
    print("SL: $30 de distância")
    print("TP: $50 de distância")
    print()

    confirma = input("Deseja continuar? (digite SIM): ")
    if confirma.upper() != "SIM":
        print("Teste cancelado.")
        return

    print()
    print("Iniciando teste...")
    print()

    mt5 = get_mt5_client()

    # Obter preço atual
    tick = mt5.get_symbol_info_tick("BTCUSDc")
    if not tick:
        print("ERRO: Não foi possível obter preço do BTCUSDc")
        return

    current_price = tick['bid']
    print(f"[1] PREÇO ATUAL")
    print(f"   Bid: ${tick['bid']:.2f}")
    print(f"   Ask: ${tick['ask']:.2f}")
    print()

    # Preparar ordem SELL com SL e TP
    sl_distance = 30.0
    tp_distance = 50.0

    market_price = tick['bid']
    sl_price = market_price + sl_distance
    tp_price = market_price - tp_distance

    print(f"[2] PARÂMETROS DA ORDEM SELL")
    print(f"   Volume: 0.01 lote")
    print(f"   Preço de entrada: ${market_price:.2f}")
    print(f"   Stop Loss: ${sl_price:.2f} (+${sl_distance})")
    print(f"   Take Profit: ${tp_price:.2f} (-${tp_distance})")
    print()

    # Enviar ordem
    print("[3] ENVIANDO ORDEM...")
    result = mt5.sell_market(
        symbol="BTCUSDc",
        volume=0.01,
        sl=sl_price,
        tp=tp_price,
        comment="Teste_SLTP"
    )

    print()
    if result:
        print(f"[4] RESULTADO DA ORDEM")
        print(f"   Retcode: {result.get('retcode')} ({result.get('retcode_external', 'N/A')})")
        print(f"   Deal: {result.get('deal')}")
        print(f"   Order: {result.get('order')}")
        print(f"   Volume: {result.get('volume')}")
        print(f"   Price: ${result.get('price', 0):.2f}")
        print(f"   Comment: {result.get('comment', 'N/A')}")

        if result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
            print()
            print("   STATUS: ORDEM EXECUTADA COM SUCESSO!")

            # Verificar posição aberta
            time.sleep(2)
            positions = mt5.positions_get(symbol="BTCUSDc")

            if positions:
                print()
                print("[5] VERIFICANDO POSIÇÃO ABERTA")
                for pos in positions:
                    if pos.get('comment') == "Teste_SLTP":
                        print(f"   Ticket: {pos.get('ticket')}")
                        print(f"   Tipo: {'BUY' if pos.get('type') == 0 else 'SELL'}")
                        print(f"   Volume: {pos.get('volume')}")
                        print(f"   Preço de abertura: ${pos.get('price_open', 0):.2f}")
                        print(f"   SL definido: ${pos.get('sl', 0):.2f}")
                        print(f"   TP definido: ${pos.get('tp', 0):.2f}")
                        print()

                        if pos.get('sl', 0) > 0 and pos.get('tp', 0) > 0:
                            print("   RESULTADO: SL e TP FORAM DEFINIDOS CORRETAMENTE!")
                        elif pos.get('sl', 0) == 0 and pos.get('tp', 0) == 0:
                            print("   PROBLEMA: SL e TP NÃO FORAM DEFINIDOS!")
                            print("   A ordem foi aceita mas os stops não foram aplicados.")
                        else:
                            print("   PARCIAL: Apenas um dos stops foi definido.")

                        print()
                        print("   Verifique no MT5:")
                        print("   1. Abra a aba 'Trade' (Ctrl+T)")
                        print("   2. Localize a posição com comentário 'Teste_SLTP'")
                        print("   3. Verifique se as linhas de SL/TP aparecem no gráfico")
                        print()
                        print("   FECHAR POSIÇÃO MANUALMENTE após verificar!")
                        break
        else:
            print()
            print(f"   STATUS: ORDEM REJEITADA")
            print(f"   Motivo: {result.get('comment', 'Desconhecido')}")
    else:
        print("[4] ERRO: Nenhum resultado retornado")

    print()
    print("="*70)

if __name__ == "__main__":
    testar_ordem_sltp()
