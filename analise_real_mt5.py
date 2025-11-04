#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise REAL do MT5 - Últimas 24 horas
Busca dados direto do MT5 para análise precisa
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

def main():
    print("="*70)
    print("ANÁLISE REAL - HISTÓRICO MT5 (ÚLTIMAS 24H)")
    print("="*70)
    print()

    # Conectar ao MT5
    try:
        mt5 = get_mt5_client()
        print("[OK] Conectado ao MT5")
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {e}")
        return

    symbol = "BTCUSDc"

    # 1. VERIFICAR POSIÇÕES ABERTAS AGORA
    print("\n" + "="*70)
    print("1. POSIÇÕES ABERTAS NO MOMENTO")
    print("="*70)

    try:
        positions = mt5.positions_get(symbol=symbol)

        if positions and len(positions) > 0:
            print(f"\n {len(positions)} POSIÇÕES ABERTAS:\n")

            total_profit = 0
            for i, pos in enumerate(positions, 1):
                ticket = pos.get('ticket')
                pos_type = 'BUY' if pos.get('type') == 0 else 'SELL'
                volume = pos.get('volume', 0)
                open_price = pos.get('price_open', 0)
                current_price = pos.get('price_current', 0)
                sl = pos.get('sl', 0)
                tp = pos.get('tp', 0)
                profit = pos.get('profit', 0)
                open_time = pos.get('time', 0)

                total_profit += profit

                print(f"[{i}] Ticket: {ticket}")
                print(f"    Tipo: {pos_type} | Volume: {volume} lotes")
                print(f"    Abertura: ${open_price:.2f} | Atual: ${current_price:.2f}")
                print(f"    SL: ${sl:.2f} | TP: ${tp:.2f}")
                print(f"    P&L: ${profit:.2f}")
                print(f"    Tempo aberto: {datetime.fromtimestamp(open_time).strftime('%Y-%m-%d %H:%M:%S')}")

                # Calcular distância do SL
                if sl > 0:
                    if pos_type == 'BUY':
                        sl_distance = open_price - sl
                    else:
                        sl_distance = sl - open_price
                    print(f"    Distância SL: ${sl_distance:.2f}")
                print()

            print(f" P&L TOTAL DAS POSIÇÕES ABERTAS: ${total_profit:.2f}")

        else:
            print("\n Nenhuma posição aberta no momento")

    except Exception as e:
        print(f" Erro ao buscar posições: {e}")

    # 2. HISTÓRICO DE DEALS (ÚLTIMAS 24H)
    print("\n" + "="*70)
    print("2. HISTÓRICO DE OPERAÇÕES (ÚLTIMAS 24H)")
    print("="*70)

    try:
        date_from = datetime.now() - timedelta(hours=24)
        date_to = datetime.now()

        deals = mt5.history_deals_get(
            date_from=date_from,
            date_to=date_to,
            symbol=symbol
        )

        if not deals or len(deals) == 0:
            print("\n Nenhuma operação nas últimas 24h")
        else:
            print(f"\n {len(deals)} DEALS ENCONTRADOS:\n")

            # Agrupar deals por posição
            positions_map = {}

            for deal in deals:
                pos_id = deal.get('position_id', 0)
                if pos_id not in positions_map:
                    positions_map[pos_id] = []
                positions_map[pos_id].append(deal)

            print(f"Total de posições únicas: {len(positions_map)}")
            print()

            # Analisar cada posição
            total_profit_closed = 0
            wins = 0
            losses = 0

            for pos_id, pos_deals in positions_map.items():
                # Separar entrada e saída
                entry_deal = None
                exit_deal = None

                for deal in pos_deals:
                    entry_type = deal.get('entry', 0)
                    if entry_type == 0:  # DEAL_ENTRY_IN
                        entry_deal = deal
                    elif entry_type == 1:  # DEAL_ENTRY_OUT
                        exit_deal = deal

                # Só mostrar se tiver entrada E saída (posição fechada)
                if entry_deal and exit_deal:
                    ticket = pos_id
                    deal_type = 'BUY' if entry_deal.get('type') == 0 else 'SELL'
                    volume = entry_deal.get('volume', 0)
                    entry_price = entry_deal.get('price', 0)
                    exit_price = exit_deal.get('price', 0)
                    profit = exit_deal.get('profit', 0)
                    entry_time = datetime.fromtimestamp(entry_deal.get('time', 0))
                    exit_time = datetime.fromtimestamp(exit_deal.get('time', 0))

                    total_profit_closed += profit
                    if profit > 0:
                        wins += 1
                    else:
                        losses += 1

                    print(f"Posição #{ticket} ({deal_type})")
                    print(f"  Volume: {volume} lotes")
                    print(f"  Entrada: ${entry_price:.2f} em {entry_time.strftime('%H:%M:%S')}")
                    print(f"  Saída: ${exit_price:.2f} em {exit_time.strftime('%H:%M:%S')}")

                    # Calcular pontos de movimento
                    if deal_type == 'BUY':
                        points = exit_price - entry_price
                    else:
                        points = entry_price - exit_price

                    print(f"  Movimento: {points:+.2f} pontos")
                    print(f"  P&L: ${profit:+.2f} {' WIN' if profit > 0 else ' LOSS'}")
                    print()

            # Estatísticas
            print("="*70)
            print("ESTATÍSTICAS DAS POSIÇÕES FECHADAS")
            print("="*70)
            total_closed = wins + losses
            win_rate = (wins / total_closed * 100) if total_closed > 0 else 0

            print(f"\nTotal de posições fechadas: {total_closed}")
            print(f"Vitórias: {wins} ({win_rate:.1f}%)")
            print(f"Perdas: {losses} ({100-win_rate:.1f}%)")
            print(f"Lucro total: ${total_profit_closed:.2f}")
            if total_closed > 0:
                print(f"Lucro médio por trade: ${total_profit_closed/total_closed:.2f}")

            if wins > 0 and losses > 0:
                avg_win = sum([d.get('profit', 0) for d in deals if d.get('entry') == 1 and d.get('profit', 0) > 0]) / wins
                avg_loss = abs(sum([d.get('profit', 0) for d in deals if d.get('entry') == 1 and d.get('profit', 0) < 0]) / losses)
                print(f"Lucro médio por win: ${avg_win:.2f}")
                print(f"Perda média por loss: ${avg_loss:.2f}")
                if avg_loss > 0:
                    print(f"Risk/Reward ratio: {avg_win/avg_loss:.2f}:1")

    except Exception as e:
        print(f" Erro ao buscar histórico: {e}")
        import traceback
        traceback.print_exc()

    # 3. INFORMAÇÕES DO SÍMBOLO
    print("\n" + "="*70)
    print("3. INFORMAÇÕES DO SÍMBOLO")
    print("="*70)

    try:
        symbol_info = mt5.get_symbol_info(symbol)
        if symbol_info:
            print(f"\nSímbolo: {symbol}")
            print(f"Preço atual Bid: ${symbol_info.get('bid', 0):.2f}")
            print(f"Preço atual Ask: ${symbol_info.get('ask', 0):.2f}")
            print(f"Spread: {symbol_info.get('spread', 0)} pontos")
            print(f"Volume mínimo: {symbol_info.get('volume_min', 0)} lotes")
            print(f"Volume máximo: {symbol_info.get('volume_max', 0)} lotes")
            print(f"Step: {symbol_info.get('volume_step', 0)}")

            # Informações de contrato
            contract_size = symbol_info.get('trade_contract_size', 1)
            print(f"Tamanho do contrato: {contract_size}")

            # Valor do ponto
            point = symbol_info.get('point', 0)
            print(f"Tamanho do ponto: {point}")

            # Calcular valor de 1 ponto para 0.01 lotes
            if point > 0:
                point_value = point * contract_size * 0.01
                print(f"\nValor de 1 ponto com 0.01 lotes: ${point_value:.2f}")
                print(f"SL de 50 pontos com 0.01 lotes = ${50 * point_value:.2f}")
                print(f"SL de 50 pontos com 0.3 lotes = ${50 * point_value * 30:.2f}")

    except Exception as e:
        print(f" Erro ao buscar informações do símbolo: {e}")

    # 4. INFORMAÇÕES DA CONTA
    print("\n" + "="*70)
    print("4. INFORMAÇÕES DA CONTA")
    print("="*70)

    try:
        account_info = mt5.get_account_info()
        if account_info:
            print(f"\nBalance: ${account_info.get('balance', 0):.2f}")
            print(f"Equity: ${account_info.get('equity', 0):.2f}")
            print(f"Margin: ${account_info.get('margin', 0):.2f}")
            print(f"Free Margin: ${account_info.get('margin_free', 0):.2f}")
            print(f"Margin Level: {account_info.get('margin_level', 0):.2f}%")
            print(f"Profit: ${account_info.get('profit', 0):.2f}")

    except Exception as e:
        print(f" Erro ao buscar informações da conta: {e}")

    print("\n" + "="*70)
    print("FIM DA ANÁLISE")
    print("="*70)


if __name__ == "__main__":
    main()
