#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da ativação do trailing stop para Gold Loss Zero
Verifica por que o trailing não foi ativado em uma ordem que fechou com lucro
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.btc_logger import BTCLogger

def debug_trailing_logic():
    """
    Simula a lógica de ativação do trailing para entender o problema
    """
    print("DEBUG DA LÓGICA DE TRAILING")
    print("="*50)

    # Parâmetros do agente
    symbol = "XAUUSDc"
    volume = 0.02
    sl_atr_mult = 5.0  # ATR × 5.0
    trailing_activation_mult = 0.4  # ATR × 0.4
    trailing_distance_mult = 0.3  # ATR × 0.3

    # Simular ATR calculado (baseado no código)
    current_atr = 60000.0  # ATR padrão para Gold: 60,000 pontos

    # Calcular thresholds
    current_sl_pontos = current_atr * sl_atr_mult
    current_trailing_activation_pontos = current_atr * trailing_activation_mult
    current_trailing_distance_pontos = current_atr * trailing_distance_mult

    print(f"ATR atual: {current_atr:.0f} pontos")
    print(f"SL pontos: {current_sl_pontos:.0f}")
    print(f"Trailing activation pontos: {current_trailing_activation_pontos:.0f}")
    print(f"Trailing distance pontos: {current_trailing_distance_pontos:.0f}")
    print()

    # Simular symbol_point (variação de preço por ponto)
    symbol_point = 0.001  # Para Gold XAUUSDc

    # Função para converter pontos para dinheiro
    def pontos_para_dinheiro(pontos):
        return pontos * symbol_point * volume

    # Valores em dinheiro
    sl_dinheiro = pontos_para_dinheiro(current_sl_pontos)
    trailing_activation_dinheiro = pontos_para_dinheiro(current_trailing_activation_pontos)
    trailing_distance_dinheiro = pontos_para_dinheiro(current_trailing_distance_pontos)

    print(f"SL dinheiro: ${sl_dinheiro:.2f}")
    print(f"Trailing activation dinheiro: ${trailing_activation_dinheiro:.2f}")
    print(f"Trailing distance dinheiro: ${trailing_distance_dinheiro:.2f}")
    print()

    # Simular cenário: ordem fechou com $17 de lucro
    profit_dinheiro = 17.00
    print(f"Lucro da ordem fechada: ${profit_dinheiro:.2f}")

    # Converter lucro em dinheiro para pontos MT5
    profit_pontos = profit_dinheiro / (symbol_point * volume)
    print(f"Lucro em pontos MT5: {profit_pontos:.1f}")

    # Verificar se deveria ter ativado trailing
    should_activate = profit_pontos >= current_trailing_activation_pontos
    print(f"Deveria ter ativado trailing? {should_activate}")

    if should_activate:
        print("[OK] Trailing DEVERIA ter sido ativado!")
        print(f"   Lucro necessário: {current_trailing_activation_pontos:.1f} pontos (${trailing_activation_dinheiro:.2f})")
        print(f"   Lucro alcançado: {profit_pontos:.1f} pontos (${profit_dinheiro:.2f})")
    else:
        print("[ERRO] Trailing NAO deveria ter sido ativado ainda")
        pontos_faltando = current_trailing_activation_pontos - profit_pontos
        dinheiro_faltando = pontos_para_dinheiro(pontos_faltando)
        print(f"   Faltavam: {pontos_faltando:.1f} pontos (${dinheiro_faltando:.2f})")

    print()
    print("ANÁLISE DO PROBLEMA:")
    print("1. Se a ordem fechou com $17 mas trailing não ativou, pode ser:")
    print("   - ATR foi calculado incorretamente (muito alto)")
    print("   - Threshold de ativação está muito alto")
    print("   - Worker de monitoramento não estava ativo")
    print("   - Erro na lógica de verificação de posições")
    print()
    print("2. Verificar se o worker estava rodando:")
    print("   - Worker deve verificar posições a cada 1.5s (check_interval/10)")
    print("   - Se worker falhou, usa fallback a cada 15s")
    print()
    print("3. Possível solução:")
    print("   - Reduzir trailing_activation_mult de 0.4 para 0.2 (metade)")
    print("   - Ou verificar se ATR está sendo calculado corretamente")

def check_recent_trades():
    """
    Verifica trades recentes no banco de dados
    """
    print("\nVERIFICAÇÃO DE TRADES RECENTES")
    print("="*50)

    db_path = "btc_trading_logs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar trades recentes de XAUUSDc
    cursor.execute("""
        SELECT id, trade_type, entry_price, exit_price, profit_loss, status, exit_reason
        FROM trades
        WHERE symbol = 'XAUUSDc' AND status IN ('CLOSED_WIN', 'CLOSED_LOSS')
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    trades = cursor.fetchall()

    if trades:
        print("Trades fechados recentes:")
        for trade in trades:
            trade_id, trade_type, entry_price, exit_price, profit_loss, status, exit_reason = trade
            print(f"  ID: {trade_id}, Tipo: {trade_type}, Status: {status}")
            print(f"     Entry: ${entry_price}, Exit: ${exit_price}, Profit: ${profit_loss}")
            print(f"     Reason: {exit_reason}")
            print()
    else:
        print("Nenhum trade fechado encontrado recentemente")

    # Verificar trailing stops
    cursor.execute("""
        SELECT trade_id, action, profit_dinheiro, reason
        FROM trailing_stops
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    trailings = cursor.fetchall()

    if trailings:
        print("Trailing stops recentes:")
        for trailing in trailings:
            trade_id, action, profit, reason = trailing
            print(f"  Trade ID: {trade_id}, Action: {action}, Profit: ${profit}, Reason: {reason}")
    else:
        print("Nenhum trailing stop encontrado")

    conn.close()

if __name__ == "__main__":
    debug_trailing_logic()
    check_recent_trades()
