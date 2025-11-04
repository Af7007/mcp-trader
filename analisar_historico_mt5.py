#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa histórico de trades no MT5 das últimas 24 horas
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import MT5Client

def analisar_historico():
    """
    Analisa histórico de trades das últimas 24 horas
    """
    print("=" * 80)
    print("ANALISE DE HISTORICO DE TRADES - MT5")
    print("=" * 80)

    try:
        mt5_client = MT5Client()

        # Obter histórico das últimas 24 horas
        data_inicio = datetime.now() - timedelta(hours=24)
        data_fim = datetime.now()

        print(f"\n[PERIODO] {data_inicio.strftime('%Y-%m-%d %H:%M')} ate {data_fim.strftime('%Y-%m-%d %H:%M')}")

        # Obter deals (execuções)
        print("\n[DEALS] Buscando historico de deals...")
        deals = mt5_client.history_deals_get(
            date_from=data_inicio,
            date_to=data_fim
        )

        if not deals:
            print("   Nenhum deal encontrado no periodo.")
            return

        print(f"   Total de deals: {len(deals)}")

        # Filtrar apenas deals de entrada e saída
        deals_entrada = [d for d in deals if d.get('entry', 0) == 0]  # DEAL_ENTRY_IN
        deals_saida = [d for d in deals if d.get('entry', 0) == 1]  # DEAL_ENTRY_OUT

        print(f"   Deals de entrada: {len(deals_entrada)}")
        print(f"   Deals de saida: {len(deals_saida)}")

        # Análise de lucro/prejuízo
        total_profit = sum(d.get('profit', 0) for d in deals)
        total_commission = sum(d.get('commission', 0) for d in deals)
        total_swap = sum(d.get('swap', 0) for d in deals)

        print(f"\n[RESUMO FINANCEIRO]")
        print(f"   Lucro/Prejuizo bruto: ${total_profit:.2f}")
        print(f"   Comissoes: ${total_commission:.2f}")
        print(f"   Swap: ${total_swap:.2f}")
        print(f"   Lucro/Prejuizo liquido: ${total_profit + total_commission + total_swap:.2f}")

        # Análise de trades fechados (apenas saídas)
        if deals_saida:
            lucros = [d.get('profit', 0) for d in deals_saida if d.get('profit', 0) > 0]
            perdas = [d.get('profit', 0) for d in deals_saida if d.get('profit', 0) < 0]

            print(f"\n[PERFORMANCE]")
            print(f"   Trades fechados: {len(deals_saida)}")
            print(f"   Vitórias: {len(lucros)} ({len(lucros)/len(deals_saida)*100:.1f}%)")
            print(f"   Perdas: {len(perdas)} ({len(perdas)/len(deals_saida)*100:.1f}%)")

            if lucros:
                print(f"   Lucro médio: ${sum(lucros)/len(lucros):.2f}")
                print(f"   Maior lucro: ${max(lucros):.2f}")
            if perdas:
                print(f"   Perda média: ${sum(perdas)/len(perdas):.2f}")
                print(f"   Maior perda: ${min(perdas):.2f}")

        # Top 10 maiores perdas
        print(f"\n[PERDAS] TOP 10 MAIORES PERDAS:")
        deals_com_perda = [d for d in deals_saida if d.get('profit', 0) < 0]
        deals_com_perda_sorted = sorted(deals_com_perda, key=lambda x: x.get('profit', 0))

        if not deals_com_perda:
            print("   Nenhuma perda encontrada!")
        else:
            for i, deal in enumerate(deals_com_perda_sorted[:10], 1):
                ticket = deal.get('position_id', deal.get('ticket', 'N/A'))
                symbol = deal.get('symbol', 'N/A')
                profit = deal.get('profit', 0)
                volume = deal.get('volume', 0)
                price = deal.get('price', 0)
                time = deal.get('time', 0)

                # Converter timestamp
                if isinstance(time, (int, float)):
                    time_str = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = str(time)

                print(f"\n   {i}. Perda: ${profit:.2f}")
                print(f"      Symbol: {symbol} | Ticket: {ticket}")
                print(f"      Volume: {volume:.2f} | Preco: ${price:.2f}")
                print(f"      Time: {time_str}")
                print(f"      Comment: {deal.get('comment', 'N/A')}")

        # Análise por símbolo
        print(f"\n[SIMBOLOS] Performance por simbolo:")
        simbolos = {}

        for deal in deals_saida:
            symbol = deal.get('symbol', 'UNKNOWN')
            profit = deal.get('profit', 0)

            if symbol not in simbolos:
                simbolos[symbol] = {
                    'count': 0,
                    'profit': 0,
                    'wins': 0,
                    'losses': 0
                }

            simbolos[symbol]['count'] += 1
            simbolos[symbol]['profit'] += profit

            if profit > 0:
                simbolos[symbol]['wins'] += 1
            elif profit < 0:
                simbolos[symbol]['losses'] += 1

        for symbol, data in sorted(simbolos.items(), key=lambda x: x[1]['profit']):
            winrate = (data['wins'] / data['count'] * 100) if data['count'] > 0 else 0
            print(f"\n   {symbol}:")
            print(f"      Trades: {data['count']} | Wins: {data['wins']} ({winrate:.1f}%) | Losses: {data['losses']}")
            print(f"      P&L Total: ${data['profit']:.2f}")

        # Análise temporal (por hora)
        print(f"\n[TEMPORAL] Distribuicao por hora do dia:")
        horas = {}

        for deal in deals_saida:
            time = deal.get('time', 0)
            if isinstance(time, (int, float)):
                hora = datetime.fromtimestamp(time).hour
                if hora not in horas:
                    horas[hora] = {'count': 0, 'profit': 0}
                horas[hora]['count'] += 1
                horas[hora]['profit'] += deal.get('profit', 0)

        for hora in sorted(horas.keys()):
            data = horas[hora]
            print(f"   {hora:02d}:00 - Trades: {data['count']:2d} | P&L: ${data['profit']:7.2f}")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nERRO ao analisar historico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analisar_historico()
