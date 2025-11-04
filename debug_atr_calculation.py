#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do cálculo de ATR para Gold Loss Zero
Verifica por que o ATR está retornando 0
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.mt5_direct_client import get_mt5_client

def debug_atr_calculation():
    """
    Testa o cálculo de ATR diretamente
    """
    print("DEBUG DO CÁLCULO DE ATR")
    print("="*50)

    # Conectar ao MT5
    mt5 = get_mt5_client()
    if not mt5:
        print("[ERRO] Não foi possível conectar ao MT5")
        return

    symbol = "XAUUSDc"
    print(f"Testando ATR para {symbol}")

    # Obter dados históricos
    try:
        rates = mt5.copy_rates_from_pos(
            symbol=symbol,
            timeframe="M5",
            start_pos=0,
            count=20  # 100 minutos de histórico
        )

        if rates is None or len(rates) == 0:
            print("[ERRO] Não foi possível obter dados históricos")
            return

        print(f"[OK] Obtidos {len(rates)} candles de M5")

        # Mostrar alguns dados
        print("Últimos 5 candles:")
        for i, rate in enumerate(rates[:5]):
            print(f"  {i+1}: Close=${rate['close']:.2f}, High=${rate['high']:.2f}, Low=${rate['low']:.2f}")

        # Calcular ATR manualmente
        if len(rates) >= 14:
            true_ranges = []
            for i in range(1, min(14, len(rates))):
                high = rates[i-1]['high']
                low = rates[i-1]['low']
                prev_close = rates[i]['close']

                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)
                print(f"  TR[{i}]: {tr:.4f}")

            # ATR em preço
            atr_preco = sum(true_ranges) / len(true_ranges)
            print(f"ATR em preço: {atr_preco:.4f}")

            # Obter symbol info para converter para pontos
            symbol_info = mt5.get_symbol_info(symbol)
            if symbol_info:
                symbol_point = symbol_info.get('point', 0.001)
                print(f"Symbol point: {symbol_point}")

                # ATR em pontos MT5
                atr_pontos = atr_preco / symbol_point
                print(f"ATR em pontos MT5: {atr_pontos:.0f}")

                # ATR mínimo para Gold
                atr_final = max(atr_pontos, 60000.0)
                print(f"ATR final (com mínimo): {atr_final:.0f}")
            else:
                print("[ERRO] Não foi possível obter symbol info")
        else:
            print(f"[ERRO] Poucos dados históricos: {len(rates)} < 14")

    except Exception as e:
        print(f"[ERRO] Exceção ao calcular ATR: {e}")

def test_agent_atr():
    """
    Testa o cálculo de ATR dentro do agente
    """
    print("\nTESTE DO ATR NO AGENTE")
    print("="*50)

    from agents.gold_loss_zero_simple import GoldLossZeroSimple

    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.02,
        check_interval=15,
        trailing_activation_atr_multiplier=0.2
    )

    print(f"ATR calculado pelo agente: {agent.current_atr}")

    # Forçar recálculo
    print("Forçando recálculo de ATR...")
    rates = agent.mt5.copy_rates_from_pos(
        symbol=agent.symbol,
        timeframe="M5",
        start_pos=0,
        count=20
    )

    if rates and len(rates) >= 14:
        agent.current_atr = agent._calculate_atr_simple(rates[:14])
        print(f"ATR recalculado: {agent.current_atr}")

        # Calcular thresholds
        trailing_activation_pontos = agent.current_atr * agent.trailing_activation_mult
        trailing_activation_dinheiro = agent._pontos_para_dinheiro(trailing_activation_pontos)

        print(f"Trailing activation pontos: {trailing_activation_pontos:.0f}")
        print(f"Trailing activation dinheiro: ${trailing_activation_dinheiro:.2f}")
    else:
        print("[ERRO] Não foi possível obter dados para recálculo")

if __name__ == "__main__":
    debug_atr_calculation()
    test_agent_atr()
