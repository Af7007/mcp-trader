#!/usr/bin/env python3
"""
Debug detalhado das condicoes de entrada
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()
symbol = "BTCUSDc"

print("="*70)
print("DEBUG DETALHADO - CONDICOES DE ENTRADA")
print("="*70)
print()

# Obter dados M5
rates = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M5", start_pos=0, count=50)

if not rates or len(rates) < 20:
    print("ERRO: Sem dados M5")
    sys.exit(1)

# Preços
closes = [r['close'] for r in rates[:10]]
highs = [r['high'] for r in rates[:10]]
lows = [r['low'] for r in rates[:10]]
volumes = [r['tick_volume'] for r in rates[:10]]

current = closes[0]
prev_1 = closes[1]
prev_5 = closes[5]

# Tendência
uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

# Momentum
momentum = ((current - prev_5) / prev_5) * 100

# Volatilidade (NOVO: 1.0x)
last_range = highs[0] - lows[0]
avg_range = sum([highs[i] - lows[i] for i in range(1, 6)]) / 5
high_volatility = last_range > avg_range * 1.0

# Volume (NOVO: 1.1x)
current_volume = volumes[0]
avg_volume = sum(volumes[1:6]) / 5
volume_spike = current_volume > avg_volume * 1.1

# Preço vs média
avg_price = sum(closes[:5]) / 5
price_above_avg = current > avg_price
price_below_avg = current < avg_price

print("DADOS DE MERCADO:")
print(f"  Preco: ${current:,.2f}")
print(f"  Tendencia: {'UP' if uptrend else 'DOWN' if downtrend else 'LATERAL'}")
print(f"  Momentum: {momentum:+.4f}%")
print()

print("THRESHOLDS (v2.0):")
print(f"  Momentum BUY: 0.03% (${current * 0.0003:,.2f})")
print(f"  Momentum SELL: -0.03%")
print(f"  Volume spike: {avg_volume * 1.1:.0f} (atual: {current_volume:.0f})")
print(f"  Volatilidade: {avg_range * 1.0:.2f} (atual: {last_range:.2f})")
print()

print("="*70)
print("ANALISE BUY")
print("="*70)

conf_buy = 0

# Conf 1
if uptrend and momentum > 0.03:
    conf_buy += 1
    print("Conf 1: PASSOU - Tendencia UP + Momentum > 0.03%")
else:
    print(f"Conf 1: FALHOU - uptrend={uptrend}, momentum={momentum:.4f}% (precisa > 0.03%)")

# Conf 2
if momentum > 0.045:
    conf_buy += 1
    print("Conf 2: PASSOU - Momentum forte > 0.045%")
else:
    print(f"Conf 2: FALHOU - momentum={momentum:.4f}% (precisa > 0.045%)")

# Conf 3
if (high_volatility or volume_spike) and current > prev_1 and price_above_avg:
    conf_buy += 1
    print("Conf 3: PASSOU - (Volatilidade OU Volume) + Preco subindo")
else:
    print(f"Conf 3: FALHOU - high_vol={high_volatility}, vol_spike={volume_spike}, current>prev={current>prev_1}, above_avg={price_above_avg}")

print()
print(f"TOTAL CONFIRMACOES BUY: {conf_buy}/3 (precisa >= 2)")

if conf_buy >= 2:
    print("STATUS: PASSARIA PARA VALIDACAO M15")

    # Verificar M15
    rates_m15 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M15", start_pos=0, count=30)
    if rates_m15 and len(rates_m15) >= 20:
        current_m15 = rates_m15[-1]['close']
        sma20_m15 = sum([r['close'] for r in rates_m15[-20:]]) / 20
        m15_uptrend = current_m15 > sma20_m15

        print(f"M15: Preco ${current_m15:,.2f}, SMA20 ${sma20_m15:,.2f}")
        print(f"M15 Tendencia: {'UP' if m15_uptrend else 'DOWN'}")

        if m15_uptrend:
            print()
            print("="*70)
            print("SINAL BUY SERIA GERADO!")
            print("="*70)
        else:
            print()
            print("BLOQUEADO POR M15 (tendencia DOWN)")
else:
    print("STATUS: BLOQUEADO - Menos de 2 confirmacoes")

print()
print("="*70)
print("ANALISE SELL")
print("="*70)

conf_sell = 0

# Conf 1
if downtrend and momentum < -0.03:
    conf_sell += 1
    print("Conf 1: PASSOU - Tendencia DOWN + Momentum < -0.03%")
else:
    print(f"Conf 1: FALHOU - downtrend={downtrend}, momentum={momentum:.4f}% (precisa < -0.03%)")

# Conf 2
if momentum < -0.045:
    conf_sell += 1
    print("Conf 2: PASSOU - Momentum forte < -0.045%")
else:
    print(f"Conf 2: FALHOU - momentum={momentum:.4f}% (precisa < -0.045%)")

# Conf 3
if (high_volatility or volume_spike) and current < prev_1 and price_below_avg:
    conf_sell += 1
    print("Conf 3: PASSOU - (Volatilidade OU Volume) + Preco caindo")
else:
    print(f"Conf 3: FALHOU - high_vol={high_volatility}, vol_spike={volume_spike}, current<prev={current<prev_1}, below_avg={price_below_avg}")

print()
print(f"TOTAL CONFIRMACOES SELL: {conf_sell}/3 (precisa >= 2)")

if conf_sell >= 2:
    print("STATUS: PASSARIA PARA VALIDACAO M15")

    # Verificar M15
    rates_m15 = mt5.copy_rates_from_pos(symbol=symbol, timeframe="M15", start_pos=0, count=30)
    if rates_m15 and len(rates_m15) >= 20:
        current_m15 = rates_m15[-1]['close']
        sma20_m15 = sum([r['close'] for r in rates_m15[-20:]]) / 20
        m15_downtrend = current_m15 < sma20_m15

        print(f"M15: Preco ${current_m15:,.2f}, SMA20 ${sma20_m15:,.2f}")
        print(f"M15 Tendencia: {'DOWN' if m15_downtrend else 'UP'}")

        if m15_downtrend:
            print()
            print("="*70)
            print("SINAL SELL SERIA GERADO!")
            print("="*70)
        else:
            print()
            print("BLOQUEADO POR M15 (tendencia UP)")
else:
    print("STATUS: BLOQUEADO - Menos de 2 confirmacoes")

print()
print("="*70)
print("CONCLUSAO")
print("="*70)

if conf_buy >= 2 or conf_sell >= 2:
    print("Filtros estao FUNCIONANDO - condições M5 satisfeitas")
    print("Se nao gerou sinal, foi bloqueado por M15")
else:
    print("Mercado nao tem condicoes no momento")
    print("Aguarde alguns minutos e teste novamente")

print()
