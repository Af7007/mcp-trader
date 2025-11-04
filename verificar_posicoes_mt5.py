#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica posições abertas no MT5 e calcula perdas/ganhos atuais
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import MT5Client

def verificar_posicoes():
    """
    Verifica todas as posições abertas no MT5 e calcula P&L
    """
    print("=" * 80)
    print("VERIFICACAO DE POSICOES ABERTAS - MT5")
    print("=" * 80)

    try:
        # Obter cliente MT5 direto
        mt5_client = MT5Client()

        # Obter informações da conta
        print("\n[CONTA] Informacoes:")
        account_info = mt5_client.get_account_info()
        if account_info:
            print(f"   Balance: ${account_info['balance']:.2f}")
            print(f"   Equity: ${account_info['equity']:.2f}")
            print(f"   Profit: ${account_info['profit']:.2f}")
            print(f"   Margin: ${account_info['margin']:.2f}")
            print(f"   Free Margin: ${account_info['margin_free']:.2f}")
            print(f"   Margin Level: {account_info['margin_level']:.2f}%")

        # Obter posições abertas
        print("\n[POSICOES] Trades abertos:")
        positions = mt5_client.positions_get()

        if not positions:
            print("   Nenhuma posicao aberta no momento.")
            return

        print(f"   Total de posicoes: {len(positions)}")

        # Análise por símbolo
        simbolos = {}
        total_profit = 0
        total_volume = 0

        for pos in positions:
            symbol = pos['symbol']
            profit = pos['profit']
            volume = pos['volume']
            tipo = pos['type']

            if symbol not in simbolos:
                simbolos[symbol] = {
                    'count': 0,
                    'profit': 0,
                    'volume': 0,
                    'buy': 0,
                    'sell': 0,
                    'positions': []
                }

            simbolos[symbol]['count'] += 1
            simbolos[symbol]['profit'] += profit
            simbolos[symbol]['volume'] += volume

            if tipo == 0:  # BUY
                simbolos[symbol]['buy'] += 1
            else:  # SELL
                simbolos[symbol]['sell'] += 1

            simbolos[symbol]['positions'].append(pos)

            total_profit += profit
            total_volume += volume

        # Resumo geral
        print(f"\n[RESUMO]")
        print(f"   Lucro/Prejuizo total: ${total_profit:.2f}")
        print(f"   Volume total: {total_volume:.2f} lotes")
        print(f"   Simbolos diferentes: {len(simbolos)}")

        # Análise por símbolo
        print(f"\n[ANALISE POR SIMBOLO]")
        for symbol, data in sorted(simbolos.items(), key=lambda x: x[1]['profit']):
            print(f"\n   {symbol}:")
            print(f"      Posicoes: {data['count']} (BUY: {data['buy']}, SELL: {data['sell']})")
            print(f"      Volume: {data['volume']:.2f} lotes")
            print(f"      P&L: ${data['profit']:.2f}")

            # Top 5 piores/melhores posições deste símbolo
            positions_sorted = sorted(data['positions'], key=lambda x: x['profit'])

            print(f"      Top 3 piores:")
            for i, pos in enumerate(positions_sorted[:3], 1):
                tipo_str = "BUY" if pos['type'] == 0 else "SELL"
                print(f"         {i}. Ticket {pos['ticket']} | {tipo_str} | ${pos['profit']:.2f}")
                print(f"            Entrada: ${pos['price_open']:.2f} | Atual: ${pos['price_current']:.2f}")

        # Identificar posições com maior perda
        print(f"\n[ALERTA] TOP 10 POSICOES COM MAIOR PERDA:")
        all_positions = []
        for data in simbolos.values():
            all_positions.extend(data['positions'])

        all_positions_sorted = sorted(all_positions, key=lambda x: x['profit'])

        for i, pos in enumerate(all_positions_sorted[:10], 1):
            tipo_str = "BUY" if pos['type'] == 0 else "SELL"
            print(f"\n   {i}. {pos['symbol']} | Ticket {pos['ticket']}")
            print(f"      Tipo: {tipo_str} | Volume: {pos['volume']:.2f}")
            print(f"      Entrada: ${pos['price_open']:.2f}")
            print(f"      Atual: ${pos['price_current']:.2f}")
            print(f"      SL: ${pos['sl']:.2f} | TP: ${pos['tp']:.2f}")
            print(f"      Perda: ${pos['profit']:.2f}")
            print(f"      Comment: {pos.get('comment', 'N/A')}")

        # Alertas e recomendações
        print(f"\n[ALERTAS]")

        # Muitas posições abertas
        if len(positions) > 20:
            print(f"   CRITICO: {len(positions)} posicoes abertas! Risco muito alto.")
        elif len(positions) > 10:
            print(f"   ALERTA: {len(positions)} posicoes abertas. Considere reduzir exposicao.")

        # Perda total significativa
        if total_profit < -100:
            print(f"   CRITICO: Perda total de ${abs(total_profit):.2f}! Revisar estrategia urgentemente.")
        elif total_profit < -50:
            print(f"   ALERTA: Perda total de ${abs(total_profit):.2f}. Monitorar de perto.")

        # Verificar margin level
        if account_info and account_info['margin_level'] < 200:
            print(f"   CRITICO: Margin level {account_info['margin_level']:.2f}% muito baixo!")

        # Posições sem SL
        sem_sl = [p for p in all_positions if p['sl'] == 0]
        if sem_sl:
            print(f"   ALERTA: {len(sem_sl)} posicoes sem Stop Loss!")

        print("\n" + "=" * 80)
        print("[RECOMENDACOES]")
        print("=" * 80)
        print("""
   1. URGENTE: Reduzir numero de posicoes abertas (maximo 10)
   2. Revisar estrategia de entrada - muitos trades ao mesmo tempo
   3. Implementar limite maximo de posicoes simultaneas
   4. Considerar fechar posicoes com maior perda
   5. Adicionar confirmacao adicional antes de abrir novos trades
   6. Verificar se sistema de hedge esta funcionando corretamente
   7. Analisar por que agente nao esta fechando posicoes perdedoras
        """)
        print("=" * 80)

    except Exception as e:
        print(f"\nERRO ao verificar posicoes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_posicoes()
