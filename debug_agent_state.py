#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do estado do agente Gold Loss Zero
Verifica se o trailing está sendo ativado corretamente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def debug_agent_state():
    """
    Cria uma instância do agente e verifica seu estado
    """
    print("DEBUG DO ESTADO DO AGENTE GOLD LOSS ZERO")
    print("="*50)

    # Criar agente com parâmetros de debug
    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.02,
        check_interval=15,
        trailing_activation_atr_multiplier=0.2  # Threshold reduzido
    )

    print("Agente criado com sucesso!")
    print(f"Symbol: {agent.symbol}")
    print(f"Volume: {agent.volume}")
    print(f"Trailing activation multiplier: {agent.trailing_activation_mult}")
    print(f"ATR atual: {agent.current_atr}")
    print()

    # Calcular thresholds atuais
    trailing_activation_pontos = agent.current_atr * agent.trailing_activation_mult
    trailing_activation_dinheiro = agent._pontos_para_dinheiro(trailing_activation_pontos)

    print("THRESHOLDS ATUAIS:")
    print(f"Trailing activation pontos: {trailing_activation_pontos:.0f}")
    print(f"Trailing activation dinheiro: ${trailing_activation_dinheiro:.2f}")
    print()

    # Verificar conexão MT5
    if agent.mt5:
        print("[OK] MT5 conectado")

        # Verificar posições abertas
        positions = agent.mt5.positions_get(symbol=agent.symbol)
        if positions:
            print(f"[INFO] {len(positions)} posições abertas para {agent.symbol}")
            for pos in positions:
                print(f"  Ticket: {pos['ticket']}, Tipo: {'BUY' if pos['type'] == 0 else 'SELL'}, Preço: ${pos['price_open']:.2f}, Lucro: ${pos['profit']:.2f}")
        else:
            print("[INFO] Nenhuma posição aberta")
    else:
        print("[ERRO] MT5 não conectado")

    print()
    print("ESTADO DO AGENTE:")
    print(f"Trailing ativo: {agent.trailing_active}")
    print(f"Entry price: ${agent.entry_price:.2f}")
    print(f"Trailing stop price: ${agent.trailing_stop_price:.2f}")
    print(f"Last position ticket: {agent.last_position_ticket}")
    print(f"Current trade ID: {agent.current_trade_id}")

    print()
    print("VERIFICAÇÃO DA LÓGICA:")
    print("1. Se trailing_active = False, o agente está aguardando lucro")
    print("2. Se trailing_active = True, o trailing já foi ativado")
    print("3. Se entry_price = 0, nenhuma posição foi aberta ainda")
    print("4. Se current_trade_id = None, trade não foi registrado no DB")

    print()
    print("TESTE MANUAL DE TRAILING:")
    if agent.entry_price > 0:
        # Simular cálculo de lucro
        current_price = agent.entry_price + 1.0  # Simular +$1.00
        profit_price_diff = current_price - agent.entry_price
        profit_pontos = profit_price_diff / agent.symbol_point
        profit_dinheiro = agent._pontos_para_dinheiro(profit_pontos)

        print(f"Preço simulado: ${current_price:.2f}")
        print(f"Lucro simulado pontos: {profit_pontos:.1f}")
        print(f"Lucro simulado dinheiro: ${profit_dinheiro:.2f}")

        should_activate = profit_pontos >= trailing_activation_pontos
        print(f"Deveria ativar trailing? {should_activate}")
    else:
        print("Nenhuma posição aberta para testar")

if __name__ == "__main__":
    debug_agent_state()
