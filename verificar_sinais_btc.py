#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica por que nenhum sinal está sendo gerado
Mostra detalhes de TODAS as condições
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

def main():
    print("="*70)
    print("DIAGNOSTICO DE SINAIS - BTC LOSS ZERO")
    print("="*70)
    print()

    mt5 = get_mt5_client()
    symbol = "BTCUSDc"

    # Obter dados M5
    rates_m5 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M5", start_pos=0, count=50)

    if not rates_m5 or len(rates_m5) < 20:
        print("ERRO: Nao foi possivel obter dados M5")
        return

    # Calcular métricas
    current = rates_m5[-1]['close']
    prev_1 = rates_m5[-2]['close']
    prev_5 = rates_m5[-6]['close'] if len(rates_m5) >= 6 else prev_1

    # Momentum
    momentum_5m = ((current - prev_5) / prev_5) * 100

    # ATR simplificado
    true_ranges = []
    for i in range(1, min(15, len(rates_m5))):
        high_low = rates_m5[i]['high'] - rates_m5[i]['low']
        high_close = abs(rates_m5[i]['high'] - rates_m5[i - 1]['close'])
        low_close = abs(rates_m5[i]['low'] - rates_m5[i - 1]['close'])
        true_range = max(high_low, high_close, low_close)
        true_ranges.append(true_range)

    atr = sum(true_ranges) / len(true_ranges) if true_ranges else 100
    atr = max(atr, 80)

    # Volatilidade
    volatility = ((rates_m5[-1]['high'] - rates_m5[-1]['low']) / rates_m5[-1]['close']) * 100
    avg_volatility = sum([((r['high'] - r['low']) / r['close']) * 100 for r in rates_m5[-10:]]) / 10
    high_volatility = volatility > avg_volatility * 1.2

    # Volume spike
    current_volume = rates_m5[-1]['tick_volume']
    avg_volume = sum([r['tick_volume'] for r in rates_m5[-10:]]) / 10
    volume_spike = current_volume > avg_volume * 1.3

    # Tendência (SMA20)
    sma20 = sum([r['close'] for r in rates_m5[-20:]]) / 20
    uptrend = current > sma20
    downtrend = current < sma20

    # Preço vs média
    avg_price = sum([r['close'] for r in rates_m5[-5:]]) / 5
    price_above_avg = current > avg_price
    price_below_avg = current < avg_price

    print("DADOS DE MERCADO:")
    print(f"  Preco atual: ${current:,.2f}")
    print(f"  Preco anterior (1 candle): ${prev_1:,.2f}")
    print(f"  Preco anterior (5 candles): ${prev_5:,.2f}")
    print()

    print("METRICAS CALCULADAS:")
    print(f"  Momentum 5M: {momentum_5m:+.4f}%")
    print(f"  ATR: {atr:.1f} pontos")
    print(f"  Volatilidade atual: {volatility:.3f}%")
    print(f"  Volatilidade média: {avg_volatility:.3f}%")
    print(f"  High volatility: {high_volatility}")
    print(f"  Volume atual: {current_volume:,.0f}")
    print(f"  Volume médio: {avg_volume:,.0f}")
    print(f"  Volume spike: {volume_spike}")
    print(f"  SMA20: ${sma20:,.2f}")
    print(f"  Tendência: {'UP' if uptrend else 'DOWN' if downtrend else 'LATERAL'}")
    print(f"  Preço vs avg: {'ACIMA' if price_above_avg else 'ABAIXO'}")
    print()

    # THRESHOLDS
    MOMENTUM_BUY = 0.04
    MOMENTUM_SELL = -0.04

    print("="*70)
    print("ANALISE DE SINAIS BUY")
    print("="*70)

    confirmations_buy = 0

    # Confirmação 1: Tendência + Momentum
    conf1 = uptrend and momentum_5m > MOMENTUM_BUY
    print(f"1. Tendência UP + Momentum > {MOMENTUM_BUY}%:")
    print(f"   uptrend={uptrend}, momentum={momentum_5m:+.4f}% > {MOMENTUM_BUY}%")
    print(f"   Resultado: {'✓ OK' if conf1 else '✗ FALHOU'}")
    if conf1:
        confirmations_buy += 1
    print()

    # Confirmação 2: Momentum Forte
    conf2 = momentum_5m > MOMENTUM_BUY * 1.5
    print(f"2. Momentum FORTE > {MOMENTUM_BUY * 1.5}%:")
    print(f"   momentum={momentum_5m:+.4f}% > {MOMENTUM_BUY * 1.5}%")
    print(f"   Resultado: {'✓ OK' if conf2 else '✗ FALHOU'}")
    if conf2:
        confirmations_buy += 1
    print()

    # Confirmação 3: Volatilidade + Volume + Preço
    conf3 = high_volatility and volume_spike and current > prev_1 and price_above_avg
    print(f"3. Volatilidade + Volume + Preço subindo:")
    print(f"   high_volatility={high_volatility}")
    print(f"   volume_spike={volume_spike}")
    print(f"   current > prev_1: {current > prev_1}")
    print(f"   price_above_avg={price_above_avg}")
    print(f"   Resultado: {'✓ OK' if conf3 else '✗ FALHOU'}")
    if conf3:
        confirmations_buy += 1
    print()

    print(f"TOTAL CONFIRMACOES BUY: {confirmations_buy}/3")
    print(f"Necessário: >= 2")
    print(f"Status: {'✓ PASSARIA PARA M15' if confirmations_buy >= 2 else '✗ BLOQUEADO'}")
    print()

    # Verificar M15 se passou
    if confirmations_buy >= 2:
        rates_m15 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M15", start_pos=0, count=30)
        if rates_m15 and len(rates_m15) >= 20:
            current_m15 = rates_m15[-1]['close']
            sma20_m15 = sum([r['close'] for r in rates_m15[-20:]]) / 20
            m15_uptrend = current_m15 > sma20_m15

            print("VALIDACAO M15:")
            print(f"  Preco M15: ${current_m15:,.2f}")
            print(f"  SMA20 M15: ${sma20_m15:,.2f}")
            print(f"  Tendencia M15: {'UP' if m15_uptrend else 'DOWN'}")
            print(f"  Status: {'✓ SINAL BUY SERIA GERADO!' if m15_uptrend else '✗ BLOQUEADO POR M15'}")
        print()

    print("="*70)
    print("ANALISE DE SINAIS SELL")
    print("="*70)

    confirmations_sell = 0

    # Confirmação 1: Tendência + Momentum
    conf1 = downtrend and momentum_5m < MOMENTUM_SELL
    print(f"1. Tendência DOWN + Momentum < {MOMENTUM_SELL}%:")
    print(f"   downtrend={downtrend}, momentum={momentum_5m:+.4f}% < {MOMENTUM_SELL}%")
    print(f"   Resultado: {'✓ OK' if conf1 else '✗ FALHOU'}")
    if conf1:
        confirmations_sell += 1
    print()

    # Confirmação 2: Momentum Forte
    conf2 = momentum_5m < MOMENTUM_SELL * 1.5
    print(f"2. Momentum FORTE < {MOMENTUM_SELL * 1.5}%:")
    print(f"   momentum={momentum_5m:+.4f}% < {MOMENTUM_SELL * 1.5}%")
    print(f"   Resultado: {'✓ OK' if conf2 else '✗ FALHOU'}")
    if conf2:
        confirmations_sell += 1
    print()

    # Confirmação 3: Volatilidade + Volume + Preço
    conf3 = high_volatility and volume_spike and current < prev_1 and price_below_avg
    print(f"3. Volatilidade + Volume + Preço caindo:")
    print(f"   high_volatility={high_volatility}")
    print(f"   volume_spike={volume_spike}")
    print(f"   current < prev_1: {current < prev_1}")
    print(f"   price_below_avg={price_below_avg}")
    print(f"   Resultado: {'✓ OK' if conf3 else '✗ FALHOU'}")
    if conf3:
        confirmations_sell += 1
    print()

    print(f"TOTAL CONFIRMACOES SELL: {confirmations_sell}/3")
    print(f"Necessário: >= 2")
    print(f"Status: {'✓ PASSARIA PARA M15' if confirmations_sell >= 2 else '✗ BLOQUEADO'}")
    print()

    # Verificar M15 se passou
    if confirmations_sell >= 2:
        rates_m15 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M15", start_pos=0, count=30)
        if rates_m15 and len(rates_m15) >= 20:
            current_m15 = rates_m15[-1]['close']
            sma20_m15 = sum([r['close'] for r in rates_m15[-20:]]) / 20
            m15_downtrend = current_m15 < sma20_m15

            print("VALIDACAO M15:")
            print(f"  Preco M15: ${current_m15:,.2f}")
            print(f"  SMA20 M15: ${sma20_m15:,.2f}")
            print(f"  Tendencia M15: {'DOWN' if m15_downtrend else 'UP'}")
            print(f"  Status: {'✓ SINAL SELL SERIA GERADO!' if m15_downtrend else '✗ BLOQUEADO POR M15'}")
        print()

    print("="*70)
    print("RESUMO")
    print("="*70)

    if confirmations_buy >= 2 or confirmations_sell >= 2:
        print("STATUS: Condições M5 PASSARAM, verificar M15")
    else:
        print("STATUS: BLOQUEADO - Menos de 2 confirmações")
        print()
        print("SUGESTOES PARA GERAR MAIS SINAIS:")
        print("1. Reduzir momentum para 0.03% (mais sensível)")
        print("2. Aceitar 1 confirmação em vez de 2 (menos rigoroso)")
        print("3. Remover validação M15 (mais sinais, menos qualidade)")
        print("4. Reduzir threshold de volume spike")
    print()


if __name__ == "__main__":
    main()
