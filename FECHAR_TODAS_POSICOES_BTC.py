#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE EMERGÊNCIA - FECHAR TODAS AS POSIÇÕES BTC

ATENÇÃO: Este script fecha TODAS as posições de BTCUSDc abertas
Use com cuidado!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_mcp_client import get_mt5_client
import time

def main():
    """
    Fecha todas as posições de BTC abertas
    """
    print("=" * 70)
    print("SCRIPT DE EMERGÊNCIA - FECHAR TODAS AS POSIÇÕES BTC")
    print("=" * 70)
    print()

    # Conectar ao MT5
    try:
        mt5 = get_mt5_client()
        print("✅ Conectado ao MT5 MCP Server")
    except Exception as e:
        print(f"❌ Erro ao conectar ao MT5: {e}")
        print()
        print("SOLUÇÃO:")
        print("1. Verifique se o MT5 MCP Server está rodando:")
        print("   python start_mt5_http.py")
        print()
        return

    # Símbolo
    symbol = "BTCUSDc"

    # Buscar posições abertas
    print()
    print(f"Buscando posições abertas de {symbol}...")

    try:
        positions = mt5.positions_get(symbol=symbol)

        if not positions or len(positions) == 0:
            print(f"✅ Nenhuma posição aberta de {symbol}")
            print()
            return

        print(f"⚠️ Encontradas {len(positions)} posições abertas!")
        print()

        # Mostrar resumo
        total_volume = sum([p.get('volume', 0) for p in positions])
        buy_count = sum([1 for p in positions if p.get('type') == 0])
        sell_count = sum([1 for p in positions if p.get('type') == 1])

        print(f"Resumo:")
        print(f"  BUY:  {buy_count} posições")
        print(f"  SELL: {sell_count} posições")
        print(f"  Volume total: {total_volume} lotes")
        print()

        # Calcular P&L atual
        total_profit = 0
        for pos in positions:
            profit = pos.get('profit', 0)
            total_profit += profit

        print(f"  P&L total atual: ${total_profit:.2f}")
        print()

        # Confirmação
        print("⚠️⚠️⚠️ ATENÇÃO ⚠️⚠️⚠️")
        print()
        print(f"Você está prestes a fechar {len(positions)} posições.")
        print(f"P&L atual: ${total_profit:.2f}")
        print()

        resposta = input("Deseja continuar? Digite 'SIM' para confirmar: ")

        if resposta.upper() != "SIM":
            print()
            print("❌ Operação cancelada pelo usuário")
            print()
            return

        # Fechar posições
        print()
        print("="*70)
        print("FECHANDO POSIÇÕES...")
        print("="*70)
        print()

        closed_count = 0
        failed_count = 0
        total_realized_profit = 0

        for i, pos in enumerate(positions, 1):
            ticket = pos.get('ticket')
            pos_type = 'BUY' if pos.get('type') == 0 else 'SELL'
            volume = pos.get('volume', 0)
            profit = pos.get('profit', 0)

            print(f"[{i}/{len(positions)}] Fechando posição #{ticket} ({pos_type} {volume} lotes)...")
            print(f"            P&L: ${profit:.2f}")

            try:
                # Fechar posição
                result = mt5.close_position(ticket)

                if result and result.get('retcode') == 10009:
                    closed_count += 1
                    total_realized_profit += profit
                    print(f"            ✅ FECHADA com sucesso")
                else:
                    failed_count += 1
                    error_msg = result.get('comment', 'Erro desconhecido') if result else 'Sem resposta'
                    print(f"            ❌ FALHA: {error_msg}")

                # Aguardar um pouco entre fechamentos
                time.sleep(0.5)

            except Exception as e:
                failed_count += 1
                print(f"            ❌ ERRO: {e}")

            print()

        # Resumo final
        print("="*70)
        print("RESUMO FINAL")
        print("="*70)
        print()
        print(f"Total de posições: {len(positions)}")
        print(f"Fechadas com sucesso: {closed_count}")
        print(f"Falhas: {failed_count}")
        print(f"P&L realizado: ${total_realized_profit:.2f}")
        print()

        # Verificar posições restantes
        remaining = mt5.positions_get(symbol=symbol)
        if remaining and len(remaining) > 0:
            print(f"⚠️ ATENÇÃO: {len(remaining)} posições ainda abertas!")
            print("Execute o script novamente para fechar as restantes.")
        else:
            print("✅ Todas as posições foram fechadas com sucesso!")

        print()
        print("="*70)

    except Exception as e:
        print(f"❌ Erro ao buscar/fechar posições: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
