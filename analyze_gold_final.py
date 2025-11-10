"""
Analise final das ordens Gold do relatorio MT5
"""
import pandas as pd

file_path = r"C:\mcp-trader\docs\ReportHistory-163049186.xlsx"

# Ler pulando headers (linha 7 em diante contem dados)
df = pd.read_excel(file_path, skiprows=7, header=None)

# Nomear colunas corretamente
df.columns = [
    'open_time', 'position', 'symbol', 'type', 'volume',
    'open_price', 'sl', 'tp', 'close_time', 'close_price',
    'commission', 'swap', 'profit', 'extra'
]

# Filtrar Gold
gold_df = df[df['symbol'].str.contains('XAU', case=False, na=False)].copy()

# Converter para numeric
gold_df['open_price'] = pd.to_numeric(gold_df['open_price'], errors='coerce')
gold_df['close_price'] = pd.to_numeric(gold_df['close_price'], errors='coerce')
gold_df['sl'] = pd.to_numeric(gold_df['sl'], errors='coerce')
gold_df['tp'] = pd.to_numeric(gold_df['tp'], errors='coerce')
gold_df['profit'] = pd.to_numeric(gold_df['profit'], errors='coerce')

# Calcular SL distance para cada ordem
gold_df['sl_distance_expected'] = 0.0
gold_df['sl_distance_real'] = abs(gold_df['open_price'] - gold_df['close_price'])
gold_df['was_sl'] = False

# Para BUY: SL esta abaixo do entry
# Para SELL: SL esta acima do entry
for idx, row in gold_df.iterrows():
    if pd.notna(row['sl']) and pd.notna(row['open_price']):
        if 'buy' in str(row['type']).lower():
            sl_dist = row['open_price'] - row['sl']
        else:  # SELL
            sl_dist = row['sl'] - row['open_price']

        gold_df.at[idx, 'sl_distance_expected'] = sl_dist

        # Verificar se fechou no SL (diferenca < 1.0 do SL)
        if pd.notna(row['close_price']) and abs(row['close_price'] - row['sl']) < 1.0:
            gold_df.at[idx, 'was_sl'] = True

print("=" * 80)
print("ANALISE COMPLETA - ORDENS GOLD")
print("=" * 80)
print()

print(f"Total de ordens Gold: {len(gold_df)}")
print()

# ESTATISTICAS GERAIS
print("=" * 80)
print("ESTATISTICAS GERAIS")
print("=" * 80)
print()

profits = gold_df['profit'].dropna()
wins = profits[profits > 0]
losses = profits[profits < 0]

print(f"Total Profit: ${profits.sum():.2f}")
print(f"Total Trades: {len(profits)}")
print(f"Wins: {len(wins)} ({len(wins)/len(profits)*100:.1f}%)")
print(f"Losses: {len(losses)} ({len(losses)/len(profits)*100:.1f}%)")
print()

if len(wins) > 0:
    print(f"Avg Win: ${wins.mean():.2f}")
    print(f"Max Win: ${wins.max():.2f}")
print()

if len(losses) > 0:
    print(f"Avg Loss: ${losses.mean():.2f}")
    print(f"Max Loss (worst): ${losses.min():.2f}")
print()

# ANALISE DE SL
print("=" * 80)
print("ANALISE DE STOP LOSS")
print("=" * 80)
print()

sl_orders = gold_df[gold_df['was_sl'] == True]
print(f"Ordens fechadas no SL: {len(sl_orders)}")
print()

if len(sl_orders) > 0:
    print("SL DISTANCES ESPERADOS:")
    sl_expected = sl_orders['sl_distance_expected'].dropna()
    print(f"  Media: ${sl_expected.mean():.3f}")
    print(f"  Min: ${sl_expected.min():.3f}")
    print(f"  Max: ${sl_expected.max():.3f}")
    print()

    # Contar SL por faixa
    around_4 = sl_expected[(sl_expected >= 3.5) & (sl_expected <= 4.5)]
    around_10 = sl_expected[(sl_expected >= 9.0) & (sl_expected <= 11.0)]
    below_1 = sl_expected[sl_expected < 1.0]

    print(f"  SL ~ $4.00 (entre $3.5-4.5): {len(around_4)} ({len(around_4)/len(sl_expected)*100:.1f}%)")
    print(f"  SL ~ $10.00 (entre $9-11): {len(around_10)} ({len(around_10)/len(sl_expected)*100:.1f}%)")
    print(f"  SL < $1.00: {len(below_1)} ({len(below_1)/len(sl_expected)*100:.1f}%)")
    print()

    # Analise de lucros em SL
    sl_profits = sl_orders['profit'].dropna()
    print(f"PERDAS EM SL:")
    print(f"  Media: ${sl_profits.mean():.2f}")
    print(f"  Min (worst): ${sl_profits.min():.2f}")
    print(f"  Max: ${sl_profits.max():.2f}")
    print()

# ULTIMAS 30 ORDENS GOLD
print("=" * 80)
print("ULTIMAS 30 ORDENS GOLD")
print("=" * 80)
print()

for idx, row in gold_df.tail(30).iterrows():
    print(f"Position: {row['position']}")
    print(f"  Open:  {row['open_time']}")
    print(f"  Type: {row['type'].upper()}")
    print(f"  Entry: {row['open_price']:.3f}")

    if pd.notna(row['sl']):
        print(f"  SL Setting: {row['sl']:.3f} (distancia: ${row['sl_distance_expected']:.3f})")

    if pd.notna(row['close_price']):
        print(f"  Exit:  {row['close_price']:.3f} (distancia real: ${row['sl_distance_real']:.3f})")
        print(f"  Profit: ${row['profit']:.2f}")

        if row['was_sl']:
            print(f"  >>> FOI STOP LOSS! Perda: ${row['profit']:.2f}")
    else:
        print(f"  Status: AINDA ABERTA")

    print()

# ORDENS COM SL MUITO PEQUENO
print("=" * 80)
print("ORDENS COM SL < $1.00 (PROBLEMA!)")
print("=" * 80)
print()

small_sl = gold_df[gold_df['sl_distance_expected'] < 1.0]
if len(small_sl) > 0:
    print(f"Total: {len(small_sl)} ordens com SL muito apertado")
    print()

    for idx, row in small_sl.tail(10).iterrows():
        print(f"Position: {row['position']} | {row['type'].upper()}")
        print(f"  Entry: {row['open_price']:.3f} | SL: {row['sl']:.3f} | Distance: ${row['sl_distance_expected']:.3f}")
        print(f"  Exit: {row['close_price']:.3f} | Profit: ${row['profit']:.2f}")
        print()

# ORDENS COM SL ~$4.00
print("=" * 80)
print("ORDENS COM SL ~$4.00 (ESPERADO)")
print("=" * 80)
print()

good_sl = gold_df[(gold_df['sl_distance_expected'] >= 3.5) & (gold_df['sl_distance_expected'] <= 4.5)]
if len(good_sl) > 0:
    print(f"Total: {len(good_sl)} ordens")
    print()

    for idx, row in good_sl.tail(10).iterrows():
        print(f"Position: {row['position']} | {row['type'].upper()}")
        print(f"  Entry: {row['open_price']:.3f} | SL: {row['sl']:.3f} | Distance: ${row['sl_distance_expected']:.3f}")

        if pd.notna(row['close_price']):
            print(f"  Exit: {row['close_price']:.3f} | Profit: ${row['profit']:.2f}")
            if row['was_sl']:
                print(f"  >>> HIT SL")
        print()

print("=" * 80)
