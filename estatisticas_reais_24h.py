#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estatísticas REAIS - Últimas 24h
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

def main():
    print("="*70)
    print("ESTATISTICAS REAIS - ULTIMAS 24H")
    print("="*70)
    print()

    # Conectar
    try:
        mt5 = get_mt5_client()
        print("[OK] Conectado ao MT5\n")
    except Exception as e:
        print(f"[ERRO] {e}")
        return

    symbol = "BTCUSDc"

    # 1. POSICOES ABERTAS
    print("1. POSICOES ABERTAS AGORA")
    print("-"*70)
    try:
        positions = mt5.positions_get(symbol=symbol)
        if positions and len(positions) > 0:
            print(f"ATENCAO: {len(positions)} posicoes abertas!")
            total_profit = sum([p.get('profit', 0) for p in positions])
            print(f"P&L total: ${total_profit:.2f}\n")
        else:
            print("Nenhuma posicao aberta\n")
    except Exception as e:
        print(f"Erro: {e}\n")

    # 2. HISTORICO
    print("2. HISTORICO DE OPERACOES (24H)")
    print("-"*70)

    try:
        date_from = datetime.now() - timedelta(hours=24)
        deals = mt5.history_deals_get(
            date_from=date_from,
            date_to=datetime.now(),
            symbol=symbol
        )

        if not deals or len(deals) == 0:
            print("Nenhuma operacao nas ultimas 24h\n")
            return

        # Agrupar por posição
        positions_map = {}
        for deal in deals:
            pos_id = deal.get('position_id', 0)
            if pos_id not in positions_map:
                positions_map[pos_id] = []
            positions_map[pos_id].append(deal)

        print(f"Total de deals: {len(deals)}")
        print(f"Posicoes unicas: {len(positions_map)}\n")

        # Analisar posições fechadas
        closed_positions = []

        for pos_id, pos_deals in positions_map.items():
            entry_deal = None
            exit_deal = None

            for deal in pos_deals:
                entry_type = deal.get('entry', 0)
                if entry_type == 0:  # ENTRY_IN
                    entry_deal = deal
                elif entry_type == 1:  # ENTRY_OUT
                    exit_deal = deal

            # Apenas posições fechadas
            if entry_deal and exit_deal:
                profit = exit_deal.get('profit', 0)
                volume = entry_deal.get('volume', 0)
                entry_price = entry_deal.get('price', 0)
                exit_price = exit_deal.get('price', 0)
                deal_type = 'BUY' if entry_deal.get('type') == 0 else 'SELL'

                # Calcular pontos
                if deal_type == 'BUY':
                    points = exit_price - entry_price
                else:
                    points = entry_price - exit_price

                closed_positions.append({
                    'profit': profit,
                    'volume': volume,
                    'points': points,
                    'type': deal_type
                })

        if len(closed_positions) == 0:
            print("Nenhuma posicao fechada nas ultimas 24h\n")
            return

        print("3. ESTATISTICAS DAS OPERACOES FECHADAS")
        print("-"*70)

        # Estatísticas
        total = len(closed_positions)
        wins = [p for p in closed_positions if p['profit'] > 0]
        losses = [p for p in closed_positions if p['profit'] < 0]

        total_profit = sum([p['profit'] for p in closed_positions])
        total_wins = len(wins)
        total_losses = len(losses)
        win_rate = (total_wins / total * 100) if total > 0 else 0

        print(f"\nTotal de operacoes fechadas: {total}")
        print(f"Vitorias: {total_wins} ({win_rate:.1f}%)")
        print(f"Derrotas: {total_losses} ({100-win_rate:.1f}%)")
        print(f"\nLucro/Prejuizo total: ${total_profit:.2f}")
        print(f"Lucro medio por trade: ${total_profit/total:.2f}")

        if wins:
            avg_win = sum([p['profit'] for p in wins]) / len(wins)
            max_win = max([p['profit'] for p in wins])
            print(f"\nLucro medio por vitoria: ${avg_win:.2f}")
            print(f"Maior vitoria: ${max_win:.2f}")

        if losses:
            avg_loss = sum([p['profit'] for p in losses]) / len(losses)
            max_loss = min([p['profit'] for p in losses])
            print(f"\nPrejuizo medio por derrota: ${avg_loss:.2f}")
            print(f"Maior derrota: ${max_loss:.2f}")

        if wins and losses:
            avg_win_abs = abs(sum([p['profit'] for p in wins]) / len(wins))
            avg_loss_abs = abs(sum([p['profit'] for p in losses]) / len(losses))
            rr = avg_win_abs / avg_loss_abs if avg_loss_abs > 0 else 0
            print(f"\nRisk/Reward Ratio: {rr:.2f}:1")

        # Análise de volumes
        print(f"\n4. ANALISE DE VOLUMES")
        print("-"*70)
        volumes = {}
        for p in closed_positions:
            vol = p['volume']
            if vol not in volumes:
                volumes[vol] = {'count': 0, 'profit': 0}
            volumes[vol]['count'] += 1
            volumes[vol]['profit'] += p['profit']

        for vol in sorted(volumes.keys()):
            count = volumes[vol]['count']
            profit = volumes[vol]['profit']
            print(f"Volume {vol} lotes: {count} trades | P&L: ${profit:.2f}")

        # Análise de pontos
        print(f"\n5. ANALISE DE PONTOS")
        print("-"*70)

        # SL de 50 pontos
        sl_50_count = len([p for p in losses if abs(p['points']) <= 55])
        if sl_50_count > 0:
            print(f"Operacoes que bateram SL ~50 pontos: {sl_50_count}/{total_losses} ({sl_50_count/total_losses*100:.1f}% das perdas)")

        # TP de 80 pontos
        tp_80_count = len([p for p in wins if abs(p['points']) >= 75])
        if tp_80_count > 0:
            print(f"Operacoes que atingiram TP ~80 pontos: {tp_80_count}/{total_wins} ({tp_80_count/total_wins*100:.1f}% das vitorias)")

        # Informações da conta
        print(f"\n6. INFORMACOES DA CONTA")
        print("-"*70)
        try:
            account_info = mt5.get_account_info()
            if account_info:
                print(f"Saldo: ${account_info.get('balance', 0):.2f}")
                print(f"Equity: ${account_info.get('equity', 0):.2f}")
                print(f"Margem livre: ${account_info.get('margin_free', 0):.2f}")
                profit_account = account_info.get('profit', 0)
                print(f"Lucro atual: ${profit_account:.2f}")
        except Exception as e:
            print(f"Erro: {e}")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
