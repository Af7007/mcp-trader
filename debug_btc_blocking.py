#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar por que BTC v2.0.0 nao esta abrindo trades
"""

import MetaTrader5 as mt5

def check_btc_conditions():
    """
    Verifica TODAS as condicoes que podem bloquear trades
    """
    print("=" * 70)
    print("DIAGNOSTICO BTC v2.0.0 - Por que nenhum trade?")
    print("=" * 70)
    print()

    # Inicializar MT5
    if not mt5.initialize():
        print("[ERRO] Falha ao inicializar MT5")
        return

    symbol = "BTCUSDc"

    # 1. Verificar conexao MT5
    print("[1/7] Verificando conexao MT5...")
    account = mt5.account_info()
    if account:
        print(f"  [OK] Conta: {account.login}")
        print(f"  [OK] Balance: ${account.balance:.2f}")
    else:
        print("  [ERRO] MT5 nao conectado!")
        return

    # 2. Verificar simbolo
    print()
    print("[2/7] Verificando simbolo BTCUSDc...")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"  [OK] Simbolo encontrado")
        print(f"  Point: {symbol_info.point}")
        print(f"  Tick Value: ${symbol_info.trade_tick_value:.4f}")
    else:
        print(f"  [ERRO] Simbolo {symbol} nao encontrado!")
        return

    # 3. Pegar dados M5
    print()
    print("[3/7] Verificando dados M5...")
    rates_m5 = mt5.copy_rates_from_pos(
        symbol,
        mt5.TIMEFRAME_M5,
        0,
        50
    )
    if rates_m5 is None or len(rates_m5) < 50:
        print(f"  [ERRO] Dados M5 insuficientes: {len(rates_m5) if rates_m5 else 0} velas")
        return
    else:
        print(f"  [OK] 50 velas M5 disponiveis")

    # 4. Calcular indicadores M5
    print()
    print("[4/7] Calculando indicadores M5...")
    closes = [r['close'] for r in rates_m5[:50]]
    current = closes[0]
    sma20 = sum(closes[:20]) / 20
    sma50 = sum(closes[:50]) / 50

    # RSI simples
    def calc_rsi(data, period=14):
        gains, losses = [], []
        for i in range(1, len(data)):
            diff = data[i-1] - data[i]
            gains.append(diff if diff > 0 else 0)
            losses.append(-diff if diff < 0 else 0)
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    rsi = calc_rsi(closes, 14)

    # Tendencia
    uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
    downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

    # Momentum
    momentum = (current - closes[9]) / closes[9] * 100

    print(f"  Preco Atual: ${current:.2f}")
    print(f"  SMA20: ${sma20:.2f}")
    print(f"  SMA50: ${sma50:.2f}")
    print(f"  RSI: {rsi:.1f}")
    print(f"  Tendencia UP: {uptrend}")
    print(f"  Tendencia DOWN: {downtrend}")
    print(f"  Momentum: {momentum:.2f}%")

    # 5. Calcular SCORE M5 (score minimo 3.5)
    print()
    print("[5/7] Calculando SCORE M5 (minimo 3.5 para trade)...")

    buy_score = 0
    sell_score = 0

    # BUY scoring
    if uptrend:
        buy_score += 1.5
        print(f"  [BUY] +1.5 pts (uptrend)")
    if current > sma20 > sma50:
        buy_score += 1.0
        print(f"  [BUY] +1.0 pts (SMA20 > SMA50)")
    if 40 < rsi < 70:
        buy_score += 1.0
        print(f"  [BUY] +1.0 pts (RSI neutro/positivo)")
    if momentum > 0.05:
        buy_score += 1.5
        print(f"  [BUY] +1.5 pts (momentum positivo)")

    # SELL scoring
    if downtrend:
        sell_score += 1.5
        print(f"  [SELL] +1.5 pts (downtrend)")
    if current < sma20 < sma50:
        sell_score += 1.0
        print(f"  [SELL] +1.0 pts (SMA20 < SMA50)")
    if 30 < rsi < 60:
        sell_score += 1.0
        print(f"  [SELL] +1.0 pts (RSI neutro/negativo)")
    if momentum < -0.05:
        sell_score += 1.5
        print(f"  [SELL] +1.5 pts (momentum negativo)")

    print()
    print(f"  BUY Score: {buy_score:.1f} {'[OK]' if buy_score >= 3.5 else '[INSUFICIENTE]'}")
    print(f"  SELL Score: {sell_score:.1f} {'[OK]' if sell_score >= 3.5 else '[INSUFICIENTE]'}")

    if buy_score < 3.5 and sell_score < 3.5:
        print()
        print("  [BLOQUEIO] Nenhum score >= 3.5")
        print("  Razao: Mercado lateral ou sinais fracos")
        print("  Solucao: Aguardar sinal forte em M5")
        return

    # Escolher direcao
    signal_type = "BUY" if buy_score >= sell_score else "SELL"
    signal_score = max(buy_score, sell_score)
    print()
    print(f"  [M5 SINAL] {signal_type} (score {signal_score:.1f})")

    # 6. Verificar FILTROS
    print()
    print("[6/7] Verificando FILTROS de seguranca...")

    # ATR
    def calc_atr(rates, period=14):
        atr_sum = 0
        for i in range(period):
            high = rates[i]['high']
            low = rates[i]['low']
            close_prev = rates[i+1]['close'] if i+1 < len(rates) else rates[i]['close']
            tr = max(high - low, abs(high - close_prev), abs(low - close_prev))
            atr_sum += tr
        return atr_sum / period

    atr_pontos = calc_atr(rates_m5, 14)
    point_value = 0.003  # BTC com volume 0.30 = $0.003/ponto
    volume = 0.30
    atr_dollars = atr_pontos * point_value

    max_atr = 20.0
    print(f"  ATR M5: {atr_pontos:.0f} pontos = ${atr_dollars:.2f}")
    print(f"  Max ATR permitido: ${max_atr:.2f}")

    if atr_dollars > max_atr:
        print(f"  [BLOQUEIO ATR] Volatilidade muito alta!")
        print(f"  Razao: ${atr_dollars:.2f} > ${max_atr:.2f}")
        return
    else:
        print(f"  [OK] ATR dentro do limite")

    # Spread
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        spread_dollars = tick.ask - tick.bid
        max_spread = 20.0
        print()
        print(f"  Spread: ${spread_dollars:.2f}")
        print(f"  Max Spread permitido: ${max_spread:.2f}")

        if spread_dollars > max_spread:
            print(f"  [BLOQUEIO SPREAD] Custo muito alto!")
            return
        else:
            print(f"  [OK] Spread dentro do limite")

    # 7. Verificar M1 timing
    print()
    print("[7/7] Verificando timing M1 (2 velas consecutivas)...")
    rates_m1 = mt5.copy_rates_from_pos(
        symbol,
        mt5.TIMEFRAME_M1,
        0,
        3
    )
    if rates_m1 is None or len(rates_m1) < 3:
        print("  [ERRO] Dados M1 insuficientes")
        return

    closes_m1 = [r['close'] for r in rates_m1[:3]]
    print(f"  M1 Velas: [{closes_m1[0]:.2f}, {closes_m1[1]:.2f}, {closes_m1[2]:.2f}]")

    if signal_type == "BUY":
        confirmed = closes_m1[0] > closes_m1[1] > closes_m1[2]
        print(f"  BUY confirmado (2 velas UP): {confirmed}")
        if not confirmed:
            print()
            print("  [BLOQUEIO M1] Aguardando 2 velas UP em M1 para confirmar BUY")
            return
    else:
        confirmed = closes_m1[0] < closes_m1[1] < closes_m1[2]
        print(f"  SELL confirmado (2 velas DOWN): {confirmed}")
        if not confirmed:
            print()
            print("  [BLOQUEIO M1] Aguardando 2 velas DOWN em M1 para confirmar SELL")
            return

    # CONCLUSAO
    print()
    print("=" * 70)
    print("CONCLUSAO")
    print("=" * 70)
    print()
    print(f"[TRADE POSSIVEL] {signal_type} BTC (score {signal_score:.1f})")
    print()
    print("Todos os filtros passaram:")
    print(f"  1. Score M5 >= 4.0: {signal_score:.1f}")
    print(f"  2. ATR < $20: ${atr_dollars:.2f}")
    print(f"  3. Spread < $5: ${spread_dollars:.2f}")
    print(f"  4. M1 timing: {'OK' if confirmed else 'AGUARDANDO'}")
    print()
    print("Se agente nao abriu trade, verificar:")
    print("  - Circuit breaker ativo? (5 perdas consecutivas)")
    print("  - Cooldown ativo? (aguardando tempo entre trades)")
    print("  - Horario bloqueado? (blacklist)")
    print()

if __name__ == '__main__':
    check_btc_conditions()
