#!/usr/bin/env python3
"""
Analisa as ultimas 10 ordens para ver se foram contra tendencia
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Erro ao inicializar MT5")
    sys.exit(1)

print("=" * 60)
print("ANALISE: Ultimas 10 Ordens vs Tendencia M5")
print("=" * 60)
print()

# Buscar historico de deals (ultimas 24h)
from_time = datetime.now() - timedelta(hours=24)
to_time = datetime.now()

deals = mt5.history_deals_get(from_time, to_time)

if not deals or len(deals) == 0:
    print("Nenhum deal encontrado")
    mt5.shutdown()
    sys.exit(0)

# Filtrar BTC
btc_deals = [d for d in deals if 'BTC' in d.symbol]

# Agrupar por posicao
positions_dict = {}
for deal in btc_deals:
    pos_id = deal.position_id
    if pos_id not in positions_dict:
        positions_dict[pos_id] = []
    positions_dict[pos_id].append(deal)

# Pegar ultimas 10 posicoes
sorted_positions = sorted(positions_dict.keys(), reverse=True)[:10]

losses_counter_trend = 0
wins_counter_trend = 0
losses_with_trend = 0
wins_with_trend = 0

for pos_id in sorted_positions:
    deals_list = sorted(positions_dict[pos_id], key=lambda d: d.time)

    entry = deals_list[0]
    entry_type = "BUY" if entry.type == 0 else "SELL"
    entry_price = entry.price
    entry_time = datetime.fromtimestamp(entry.time)

    # Verificar se fechou
    if len(deals_list) < 2:
        continue

    exit_deal = deals_list[-1]
    profit = exit_deal.profit
    result = "WIN" if profit > 0 else "LOSS"

    # Analisar tendencia M5 no momento da entrada
    time_before = entry_time - timedelta(minutes=30)
    rates_m5 = mt5.copy_rates_range("BTCUSDc", mt5.TIMEFRAME_M5, time_before, entry_time)

    if rates_m5 is None or len(rates_m5) < 8:
        continue

    closes = [r[4] for r in rates_m5]

    # Tendencia M5
    uptrend = sum(1 for i in range(7) if closes[i] < closes[i+1]) >= 5
    downtrend = sum(1 for i in range(7) if closes[i] > closes[i+1]) >= 5

    # Micro-tendencia
    micro_uptrend = False
    micro_downtrend = False

    for i in range(len(closes) - 2):
        if closes[i] < closes[i+1] < closes[i+2]:
            micro_uptrend = True
        if closes[i] > closes[i+1] > closes[i+2]:
            micro_downtrend = True

    # Verificar se estava alinhado
    aligned = False

    if entry_type == "BUY":
        aligned = uptrend or micro_uptrend
    else:  # SELL
        aligned = downtrend or micro_downtrend

    # Contar
    if aligned:
        if profit > 0:
            wins_with_trend += 1
        else:
            losses_with_trend += 1
    else:
        if profit > 0:
            wins_counter_trend += 1
        else:
            losses_counter_trend += 1

    # Mostrar
    print(f"Pos #{pos_id}:")
    print(f"   Tipo: {entry_type}")
    print(f"   Hora: {entry_time.strftime('%H:%M:%S')}")
    print(f"   M5: {'UP' if uptrend else 'DOWN' if downtrend else 'LATERAL'}")
    print(f"   Micro: {'UP' if micro_uptrend else 'DOWN' if micro_downtrend else 'LATERAL'}")
    print(f"   Alinhado: {'SIM' if aligned else 'NAO (CONTRA TENDENCIA!)'}")
    print(f"   Resultado: {result} (${profit:.2f})")
    print()

print("=" * 60)
print("ESTATISTICAS:")
print("=" * 60)
print()
print(f"COM TENDENCIA:")
print(f"   Wins: {wins_with_trend}")
print(f"   Losses: {losses_with_trend}")
if (wins_with_trend + losses_with_trend) > 0:
    wr = wins_with_trend / (wins_with_trend + losses_with_trend) * 100
    print(f"   Win Rate: {wr:.1f}%")
print()
print(f"CONTRA TENDENCIA:")
print(f"   Wins: {wins_counter_trend}")
print(f"   Losses: {losses_counter_trend}")
if (wins_counter_trend + losses_counter_trend) > 0:
    wr = wins_counter_trend / (wins_counter_trend + losses_counter_trend) * 100
    print(f"   Win Rate: {wr:.1f}%")
print()

if losses_counter_trend > 0:
    print("[ALERTA] Ordens CONTRA tendencia estao gerando PERDAS!")
    print("RECOMENDACAO: Voltar validacao de AND (ambas tendencias devem confirmar)")

print("=" * 60)

mt5.shutdown()
