#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa últimas ordens do Gold Loss Zero Game
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client


def analyze_gold_game_trades():
    """Analisa trades do Gold Loss Zero Game"""

    mt5 = get_mt5_client()

    print("="*80)
    print("ANÁLISE - Gold Loss Zero Game - Últimas Ordens")
    print("="*80)
    print()

    # 1. Verificar posições abertas
    print("[1] POSIÇÕES ABERTAS:")
    print("-" * 80)
    positions = mt5.positions_get(symbol="XAUUSDc")

    if positions:
        for pos in positions:
            ticket = pos['ticket']
            pos_type = "BUY" if pos['type'] == 0 else "SELL"
            volume = pos['volume']
            price_open = pos['price_open']
            sl = pos['sl']
            tp = pos['tp']
            profit = pos['profit']
            comment = pos.get('comment', '')

            print(f"\nTicket: {ticket}")
            print(f"  Tipo: {pos_type}")
            print(f"  Volume: {volume}")
            print(f"  Preço Abertura: ${price_open:.2f}")
            print(f"  SL: ${sl:.2f}" if sl > 0 else "  SL: Não definido")
            print(f"  TP: ${tp:.2f}" if tp > 0 else "  TP: Não definido")
            print(f"  Lucro: ${profit:.2f}")
            print(f"  Comentário: {comment}")
    else:
        print("  OK - Nenhuma posicao aberta")

    print()

    # 2. Histórico das últimas 24h
    print("[2] HISTÓRICO DAS ÚLTIMAS 24H:")
    print("-" * 80)

    date_from = datetime.now() - timedelta(hours=24)
    deals = mt5.history_deals_get(date_from=date_from, date_to=datetime.now())

    if not deals:
        print("  ERRO - Nenhum trade encontrado nas ultimas 24h")
        return

    # Filtrar apenas deals do Gold Loss Zero Game
    game_deals = [d for d in deals if d.get('symbol') == 'XAUUSDc' and
                  ('GoldLossZeroGame' in d.get('comment', '') or
                   d.get('time', 0) > (datetime.now() - timedelta(hours=1)).timestamp())]

    if not game_deals:
        print("  AVISO - Nenhum trade do Gold Loss Zero Game encontrado")
        # Mostrar últimos 5 deals de Gold para debug
        print("\n  Últimos 5 deals de XAUUSDc:")
        gold_deals = [d for d in deals if d.get('symbol') == 'XAUUSDc'][-5:]
        for d in gold_deals:
            entry = d.get('entry', 0)
            entry_type = "IN" if entry == 0 else "OUT" if entry == 1 else "?"
            print(f"    {datetime.fromtimestamp(d.get('time', 0)):%H:%M:%S} - "
                  f"{entry_type} - Profit: ${d.get('profit', 0):.2f} - "
                  f"Comment: {d.get('comment', 'N/A')}")
        return

    # Agrupar deals por position_id
    positions_map = {}
    for deal in game_deals:
        pos_id = deal.get('position_id', 0)
        if pos_id not in positions_map:
            positions_map[pos_id] = []
        positions_map[pos_id].append(deal)

    # Analisar cada posição
    total_profit = 0
    wins = 0
    losses = 0

    for pos_id, pos_deals in positions_map.items():
        # Ordenar por tempo
        pos_deals.sort(key=lambda x: x.get('time', 0))

        # Deal de entrada (DEAL_ENTRY_IN = 0)
        entry_deal = next((d for d in pos_deals if d.get('entry') == 0), None)
        # Deal de saída (DEAL_ENTRY_OUT = 1)
        exit_deal = next((d for d in pos_deals if d.get('entry') == 1), None)

        if not entry_deal:
            continue

        entry_time = datetime.fromtimestamp(entry_deal.get('time', 0))
        entry_type = "BUY" if entry_deal.get('type') == 0 else "SELL"
        entry_price = entry_deal.get('price', 0)
        volume = entry_deal.get('volume', 0)

        print(f"\nPosição #{pos_id}:")
        print(f"  Abertura: {entry_time:%Y-%m-%d %H:%M:%S}")
        print(f"  Tipo: {entry_type}")
        print(f"  Volume: {volume}")
        print(f"  Preço Entrada: ${entry_price:.2f}")

        if exit_deal:
            exit_time = datetime.fromtimestamp(exit_deal.get('time', 0))
            exit_price = exit_deal.get('price', 0)
            profit = exit_deal.get('profit', 0)
            duration = exit_time - entry_time

            print(f"  Fechamento: {exit_time:%Y-%m-%d %H:%M:%S}")
            print(f"  Preço Saída: ${exit_price:.2f}")
            print(f"  Duração: {duration}")
            print(f"  Profit: ${profit:.2f}")

            # Calcular movimento de preço
            if entry_type == "BUY":
                price_move = exit_price - entry_price
            else:
                price_move = entry_price - exit_price

            print(f"  Movimento: ${price_move:.2f}")

            # Verificar se bateu SL
            if profit < 0:
                print(f"  [X] PERDA (provavelmente SL)")
                losses += 1
            else:
                print(f"  [OK] LUCRO")
                wins += 1

            total_profit += profit
        else:
            print(f"  Status: AINDA ABERTA ou fechada sem registro de saída")

    # Resumo
    print()
    print("="*80)
    print("RESUMO:")
    print("="*80)
    total_trades = wins + losses
    if total_trades > 0:
        win_rate = (wins / total_trades) * 100
        print(f"Total de Trades: {total_trades}")
        print(f"Vitórias: {wins}")
        print(f"Perdas: {losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${total_profit:.2f}")

        if losses > wins:
            print()
            print("PROBLEMA IDENTIFICADO:")
            print("   Sistema teve mais perdas que ganhos")
            print("   Possiveis causas:")
            print("   1. SL muito apertado ($2 pode ser pouco para Gold)")
            print("   2. Trailing nao ativou a tempo")
            print("   3. Predicao de sinais precisa ajuste")
            print("   4. Spread/slippage esta consumindo lucros")


if __name__ == "__main__":
    analyze_gold_game_trades()
