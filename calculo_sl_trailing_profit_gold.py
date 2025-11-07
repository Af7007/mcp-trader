#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CÁLCULO CORRETO DE SL, TRAILING E PROFIT PARA GOLD XAUUSDc
Demonstração dos cálculos em dólares para conta cents
"""

def calcular_sl_trailing_profit_gold():
    """
    Demonstração completa dos cálculos para Gold XAUUSDc
    """

    print("="*60)
    print("CÁLCULO CORRETO - GOLD XAUUSDc (Conta Cents)")
    print("="*60)

    # === PARÂMETROS BÁSICOS ===
    symbol = "XAUUSDc"
    volume = 0.1  # lotes
    symbol_point = 0.001  # variação mínima do preço
    point_value = 0.10  # $ por ponto por lote

    print(f"Símbolo: {symbol}")
    print(f"Volume: {volume} lotes")
    print(f"Symbol Point: {symbol_point}")
    print(f"Point Value: ${point_value:.2f} por lote")
    print(f"Valor por ponto com volume {volume}: ${point_value * volume:.4f}")
    print()

    # === CÁLCULO DO ATR ===
    # ATR calculado das últimas 14 velas M5
    current_atr = 2994  # pontos MT5 (exemplo real)
    print(f"ATR atual: {current_atr} pontos MT5")
    print(f"ATR em preço: {current_atr * symbol_point:.3f} pontos de preço")
    print()

    # === CÁLCULO DO STOP LOSS ===
    sl_atr_multiplier = 1.0  # multiplicador ATR
    sl_pontos_mt5 = current_atr * sl_atr_multiplier
    sl_preco_distance = sl_pontos_mt5 * symbol_point
    sl_dinheiro = sl_pontos_mt5 * point_value * volume

    print("STOP LOSS CALCULATION:")
    print(f"  Multiplicador ATR: {sl_atr_multiplier}")
    print(f"  SL pontos MT5: {current_atr} × {sl_atr_multiplier} = {sl_pontos_mt5:.0f}")
    print(f"  SL distância preço: {sl_pontos_mt5:.0f} × {symbol_point} = {sl_preco_distance:.3f}")
    print(f"  SL em dólares: {sl_pontos_mt5:.0f} × ${point_value:.2f} × {volume} = ${sl_dinheiro:.2f}")
    print()

    # === CÁLCULO DO TRAILING STOP ===
    print("TRAILING STOP CALCULATION:")

    # Cenário 1: Posição BUY com lucro
    entry_price_buy = 3987.184
    current_price_buy = 4003.407  # preço atual (ASK)
    profit_pontos_buy = (current_price_buy - entry_price_buy) / symbol_point
    profit_dinheiro_buy = profit_pontos_buy * point_value * volume

    print("  POSIÇÃO BUY:")
    print(f"    Entry Price: ${entry_price_buy:.3f}")
    print(f"    Current Price (ASK): ${current_price_buy:.3f}")
    print(f"    Profit pontos MT5: ({current_price_buy:.3f} - {entry_price_buy:.3f}) / {symbol_point} = {profit_pontos_buy:.0f}")
    print(f"    Profit dólares: {profit_pontos_buy:.0f} × ${point_value:.2f} × {volume} = ${profit_dinheiro_buy:.2f}")
    print()

    # Trailing ativado quando profit >= $1
    trailing_activated = profit_dinheiro_buy >= 1.0
    print(f"    Trailing ativado ($1+): {trailing_activated}")

    if trailing_activated:
        # Trailing protege $0.50 inicialmente + $1 a cada $1 adicional
        trailing_activation = 1.0
        trailing_base = 0.5
        trailing_step = 1.0

        # Quantos "níveis" de $1 atingiu
        profit_levels = int(profit_dinheiro_buy // trailing_step) + 1
        trailing_distance_dinheiro = trailing_base + (profit_levels - 1) * trailing_step

        # Garantir que não protege mais que o lucro atual
        trailing_distance_dinheiro = min(trailing_distance_dinheiro, profit_dinheiro_buy - 0.01)

        # Converter para pontos MT5 e preço
        trailing_pontos_mt5 = trailing_distance_dinheiro / (point_value * volume)
        trailing_price_distance = trailing_pontos_mt5 * symbol_point

        # Trailing stop price (para BUY: SL abaixo do preço atual)
        trailing_stop_price = current_price_buy - trailing_price_distance

        print(f"    Níveis de lucro: {profit_levels}")
        print(f"    Distância trailing: ${trailing_distance_dinheiro:.2f}")
        print(f"    Trailing pontos MT5: ${trailing_distance_dinheiro:.2f} / (${point_value:.2f} × {volume}) = {trailing_pontos_mt5:.1f}")
        print(f"    Trailing distância preço: {trailing_pontos_mt5:.1f} × {symbol_point} = {trailing_price_distance:.3f}")
        print(f"    Trailing Stop Price: ${current_price_buy:.3f} - {trailing_price_distance:.3f} = ${trailing_stop_price:.3f}")
        print(f"    Lucro protegido: ${profit_dinheiro_buy:.2f} - ${trailing_distance_dinheiro:.2f} = ${profit_dinheiro_buy - trailing_distance_dinheiro:.2f}")
    print()

    # Cenário 2: Posição SELL com prejuízo
    entry_price_sell = 3987.184
    current_price_sell = 3987.024  # preço atual (BID)
    profit_pontos_sell = (entry_price_sell - current_price_sell) / symbol_point
    profit_dinheiro_sell = profit_pontos_sell * point_value * volume

    print("  POSIÇÃO SELL:")
    print(f"    Entry Price: ${entry_price_sell:.3f}")
    print(f"    Current Price (BID): ${current_price_sell:.3f}")
    print(f"    Profit pontos MT5: ({entry_price_sell:.3f} - {current_price_sell:.3f}) / {symbol_point} = {profit_pontos_sell:.0f}")
    print(f"    Profit dólares: {profit_pontos_sell:.0f} × ${point_value:.2f} × {volume} = ${profit_dinheiro_sell:.2f}")
    print(f"    Status: {'LUCRO' if profit_dinheiro_sell > 0 else 'PREJUÍZO'}")
    print()

    # === RESUMO FINAL ===
    print("="*60)
    print("RESUMO DOS CÁLCULOS:")
    print("="*60)
    print(f"Stop Loss máximo: ${sl_dinheiro:.2f}")
    print(f"Trailing ativado em: $1.00 de lucro")
    print(f"Trailing protege: $0.50 + $1.00 por nível adicional")
    print(f"Exemplo BUY: ${profit_dinheiro_buy:.2f} lucro protege ${trailing_distance_dinheiro:.2f}")
    print(f"Exemplo SELL: ${profit_dinheiro_sell:.2f} prejuizo aguarda reversao")
    print()
    print("FÓRMULAS CORRETAS:")
    print("• Pontos MT5 para dólares: pontos × point_value × volume")
    print("• Preço para pontos MT5: variação_preço / symbol_point")
    print("• SL em dólares: ATR × multiplicador × point_value × volume")
    print("• Trailing em dólares: lucro × proteção_percentual")
    print("="*60)

if __name__ == "__main__":
    calcular_sl_trailing_profit_gold()
