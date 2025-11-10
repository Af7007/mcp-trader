#!/usr/bin/env python3
"""
Analisa as ultimas ordens e mostra o movimento do mercado DEPOIS da entrada
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
print("ANALISE: Movimento do Mercado Apos Entrada")
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

# Pegar ultimas 5 posicoes
sorted_positions = sorted(positions_dict.keys(), reverse=True)[:5]

print(f"Analisando {len(sorted_positions)} ultimas posicoes...")
print()

for idx, pos_id in enumerate(sorted_positions, 1):
    deals_list = sorted(positions_dict[pos_id], key=lambda d: d.time)

    entry = deals_list[0]
    entry_type = "BUY" if entry.type == 0 else "SELL"
    entry_price = entry.price
    entry_time = datetime.fromtimestamp(entry.time)

    # Verificar se fechou
    if len(deals_list) < 2:
        print(f"{idx}. Pos #{pos_id} - AINDA ABERTA")
        continue

    exit_deal = deals_list[-1]
    exit_price = exit_deal.price
    exit_time = datetime.fromtimestamp(exit_deal.time)
    profit = exit_deal.profit
    duration = (exit_time - entry_time).total_seconds()

    print(f"{idx}. Pos #{pos_id} ({entry_type})")
    print(f"=" * 60)
    print(f"   Entry: ${entry_price:.2f} ({entry_time.strftime('%H:%M:%S')})")
    print(f"   Exit:  ${exit_price:.2f} ({exit_time.strftime('%H:%M:%S')})")
    print(f"   Duracao: {duration:.0f}s ({duration/60:.1f}min)")
    print(f"   Resultado: ${profit:.2f} ({'WIN' if profit > 0 else 'LOSS'})")
    print()

    # Buscar movimento do mercado APOS entrada (proximas 5 velas M1)
    time_after = entry_time + timedelta(minutes=5)
    rates_m1 = mt5.copy_rates_range("BTCUSDc", mt5.TIMEFRAME_M1, entry_time, time_after)

    if rates_m1 is None or len(rates_m1) < 2:
        print("   [!] Sem dados M1 para analise")
        print()
        continue

    # Analisar movimento
    max_profit_price = entry_price
    max_profit_dollars = 0
    min_profit_price = entry_price
    min_profit_dollars = 0

    print("   MOVIMENTO M1 APOS ENTRADA:")
    for i, rate in enumerate(rates_m1[:6]):  # Primeiras 6 velas
        candle_time = datetime.fromtimestamp(rate[0])
        candle_high = rate[2]
        candle_low = rate[3]

        # Calcular lucro maximo/minimo nesta vela
        if entry_type == "BUY":
            profit_high = (candle_high - entry_price) / 0.01 * 0.01 * 0.05
            profit_low = (candle_low - entry_price) / 0.01 * 0.01 * 0.05

            if profit_high > max_profit_dollars:
                max_profit_dollars = profit_high
                max_profit_price = candle_high

            if profit_low < min_profit_dollars:
                min_profit_dollars = profit_low
                min_profit_price = candle_low
        else:  # SELL
            profit_high = (entry_price - candle_low) / 0.01 * 0.01 * 0.05
            profit_low = (entry_price - candle_high) / 0.01 * 0.01 * 0.05

            if profit_high > max_profit_dollars:
                max_profit_dollars = profit_high
                max_profit_price = candle_low

            if profit_low < min_profit_dollars:
                min_profit_dollars = profit_low
                min_profit_price = candle_high

        if i < 3:  # Mostrar apenas primeiras 3 velas
            elapsed = (candle_time - entry_time).total_seconds()
            print(f"      +{elapsed:.0f}s: H=${candle_high:.2f} L=${candle_low:.2f}")

    print()
    print(f"   MAXIMO LUCRO ATINGIDO: ${max_profit_dollars:.2f} (${max_profit_price:.2f})")
    print(f"   MINIMO (MAIOR PERDA):  ${min_profit_dollars:.2f} (${min_profit_price:.2f})")
    print()

    # Analise
    if profit > 0:
        # WIN
        protecao_possivel = max_profit_dollars - 2.0  # Quanto poderia proteger
        if protecao_possivel > 0:
            print(f"   [ANALISE WIN] Maximo foi ${max_profit_dollars:.2f}")
            print(f"   [!] Poderia ter protegido ${protecao_possivel:.2f} (com trailing -$2)")
    else:
        # LOSS
        if max_profit_dollars >= 1.0:
            print(f"   [ANALISE LOSS] Trade chegou a ${max_profit_dollars:.2f} lucro!")
            if max_profit_dollars >= 3.0:
                print(f"   [!] CRITICO: Chegou a ${max_profit_dollars:.2f} mas virou LOSS!")
                print(f"   [!] Trailing deveria ter protegido ${max_profit_dollars - 2.0:.2f}")
            else:
                print(f"   [!] Chegou a ${max_profit_dollars:.2f} mas nao ativou trailing ($3)")
                print(f"   [!] Break-even poderia ter salvo (ativa em $1)")

    print()
    print("-" * 60)
    print()

print("=" * 60)
print("CONCLUSAO:")
print("=" * 60)
print()
print("Se vimos muitas posicoes que:")
print("1. Chegaram a lucro >= $3 mas viraram LOSS")
print("   -> Trailing NAO esta funcionando!")
print()
print("2. Chegaram a lucro >= $1 mas viraram LOSS")
print("   -> Break-even NAO esta funcionando!")
print()
print("3. Nunca chegaram a lucro positivo")
print("   -> Entradas contra tendencia (validacao M5 precisa melhorar)")
print()
print("=" * 60)

mt5.shutdown()
