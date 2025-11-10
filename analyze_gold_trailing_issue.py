#!/usr/bin/env python3
"""
Analisa por que trailing do Gold parou em $3.9 quando chegou a $7
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
print("ANALISE: Trailing Gold - Por que parou em $3.9?")
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

# Filtrar GOLD
gold_deals = [d for d in deals if 'XAU' in d.symbol]

if not gold_deals:
    print("Nenhum deal de GOLD encontrado")
    mt5.shutdown()
    sys.exit(0)

# Agrupar por posicao
positions_dict = {}
for deal in gold_deals:
    pos_id = deal.position_id
    if pos_id not in positions_dict:
        positions_dict[pos_id] = []
    positions_dict[pos_id].append(deal)

# Pegar ultima posicao
sorted_positions = sorted(positions_dict.keys(), reverse=True)[:1]

print(f"Analisando ultima posicao Gold...")
print()

for pos_id in sorted_positions:
    deals_list = sorted(positions_dict[pos_id], key=lambda d: d.time)

    entry = deals_list[0]
    entry_type = "BUY" if entry.type == 0 else "SELL"
    entry_price = entry.price
    entry_time = datetime.fromtimestamp(entry.time)

    # Verificar se fechou
    if len(deals_list) < 2:
        print(f"Posicao #{pos_id} - AINDA ABERTA")
        continue

    exit_deal = deals_list[-1]
    exit_price = exit_deal.price
    exit_time = datetime.fromtimestamp(exit_deal.time)
    profit = exit_deal.profit
    duration = (exit_time - entry_time).total_seconds()

    print(f"Posicao #{pos_id} ({entry_type})")
    print(f"=" * 60)
    print(f"   Entry: ${entry_price:.3f} ({entry_time.strftime('%H:%M:%S')})")
    print(f"   Exit:  ${exit_price:.3f} ({exit_time.strftime('%H:%M:%S')})")
    print(f"   Duracao: {duration:.0f}s ({duration/60:.1f}min)")
    print(f"   Resultado: ${profit:.2f}")
    print()

    # Buscar movimento do mercado APOS entrada (proximas velas M1)
    time_after = entry_time + timedelta(minutes=int(duration/60) + 2)
    rates_m1 = mt5.copy_rates_range("XAUUSDc", mt5.TIMEFRAME_M1, entry_time, time_after)

    if rates_m1 is None or len(rates_m1) < 2:
        print("   [!] Sem dados M1 para analise")
        print()
        continue

    # Volume e point value para Gold
    volume = 0.02
    point_value = 0.01
    symbol_point = 0.001

    # Analisar movimento
    max_profit_price = entry_price
    max_profit_dollars = 0
    min_profit_price = entry_price
    min_profit_dollars = 0

    print("   MOVIMENTO M1 APOS ENTRADA:")
    for i, rate in enumerate(rates_m1):
        candle_time = datetime.fromtimestamp(rate[0])
        candle_high = rate[2]
        candle_low = rate[3]

        elapsed = (candle_time - entry_time).total_seconds()

        # Calcular lucro maximo/minimo nesta vela
        if entry_type == "BUY":
            # Para BUY: lucro = (preco_atual - entry) em pontos * point_value * volume
            profit_high_points = (candle_high - entry_price) / symbol_point
            profit_high = profit_high_points * point_value * volume

            profit_low_points = (candle_low - entry_price) / symbol_point
            profit_low = profit_low_points * point_value * volume

            if profit_high > max_profit_dollars:
                max_profit_dollars = profit_high
                max_profit_price = candle_high

            if profit_low < min_profit_dollars:
                min_profit_dollars = profit_low
                min_profit_price = candle_low
        else:  # SELL
            profit_high_points = (entry_price - candle_low) / symbol_point
            profit_high = profit_high_points * point_value * volume

            profit_low_points = (entry_price - candle_high) / symbol_point
            profit_low = profit_low_points * point_value * volume

            if profit_high > max_profit_dollars:
                max_profit_dollars = profit_high
                max_profit_price = candle_low

            if profit_low < min_profit_dollars:
                min_profit_dollars = profit_low
                min_profit_price = candle_high

        if i < 5 or (i % 10 == 0):  # Mostrar primeiras 5 e depois a cada 10
            print(f"      +{elapsed:.0f}s: H=${candle_high:.3f} L=${candle_low:.3f} (lucro aprox ${profit_high:.2f})")

    print()
    print(f"   MAXIMO LUCRO ATINGIDO: ${max_profit_dollars:.2f} (preco ${max_profit_price:.3f})")
    print(f"   MINIMO (MAIOR PERDA):  ${min_profit_dollars:.2f} (preco ${min_profit_price:.3f})")
    print()

    # Analise do trailing
    print("   ANALISE DO TRAILING:")
    print(f"   - Lucro final: ${profit:.2f}")
    print(f"   - Maximo atingido: ${max_profit_dollars:.2f}")
    print(f"   - Diferenca: ${max_profit_dollars - profit:.2f} perdidos")
    print()

    # Trailing deveria proteger
    if max_profit_dollars >= 1.5:
        print(f"   [TRAILING] Deveria ter ativado em $1.50")

        # Simular protecao progressiva
        if max_profit_dollars >= 1.5:
            protected = max_profit_dollars - 1.0  # Protege (lucro - $1)
            print(f"   - Com lucro ${max_profit_dollars:.2f}, deveria proteger ${protected:.2f}")

            if profit < protected:
                print(f"   [ERRO CRITICO] Trailing NAO funcionou!")
                print(f"   - Deveria proteger: ${protected:.2f}")
                print(f"   - Lucro real: ${profit:.2f}")
                print(f"   - PERDA: ${protected - profit:.2f}")
            else:
                print(f"   [OK] Trailing funcionou corretamente")

    print()
    print("-" * 60)
    print()

print("=" * 60)
print("DIAGNOSTICO:")
print("=" * 60)
print()
print("Se o lucro maximo foi MUITO maior que o lucro final:")
print("   -> Trailing NAO acompanhou ou parou de atualizar")
print()
print("Possiveis causas:")
print("   1. Worker nao rodando (20ms)")
print("   2. Calculo de protecao errado")
print("   3. SL nao atualizando no MT5")
print("   4. Formula de trailing incorreta")
print()
print("=" * 60)

mt5.shutdown()
