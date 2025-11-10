"""
Analisa o relatorio de historico exportado do MT5 - Versao 2
"""
import pandas as pd

# Ler o arquivo Excel
file_path = r"C:\mcp-trader\docs\ReportHistory-163049186.xlsx"

try:
    # Ler arquivo (formato MT5 tem headers na linha 5)
    df = pd.read_excel(file_path, skiprows=5)

    print("=" * 80)
    print("ANALISE DO RELATORIO MT5 - HISTORICO DE POSICOES")
    print("=" * 80)
    print()

    print(f"Total de posicoes: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print()

    # Renomear colunas para facilitar
    # Colunas esperadas: Horario, Position, Ativo, Tipo, Volume, Preco, S/L, T/P, Horario, Preco, Comissao, Swap, Lucro
    col_mapping = {}
    for i, col in enumerate(df.columns):
        if i == 0:
            col_mapping[col] = 'open_time'
        elif i == 1:
            col_mapping[col] = 'position'
        elif i == 2:
            col_mapping[col] = 'symbol'
        elif i == 3:
            col_mapping[col] = 'type'
        elif i == 4:
            col_mapping[col] = 'volume'
        elif i == 5:
            col_mapping[col] = 'open_price'
        elif i == 6:
            col_mapping[col] = 'sl'
        elif i == 7:
            col_mapping[col] = 'tp'
        elif i == 8:
            col_mapping[col] = 'close_time'
        elif i == 9:
            col_mapping[col] = 'close_price'
        elif i == 10:
            col_mapping[col] = 'commission'
        elif i == 11:
            col_mapping[col] = 'swap'
        elif i == 12:
            col_mapping[col] = 'profit'

    df.rename(columns=col_mapping, inplace=True)

    print("Colunas renomeadas:")
    print(list(df.columns))
    print()

    # Filtrar Gold
    gold_df = df[df['symbol'].str.contains('XAU', case=False, na=False)].copy()

    print(f"Posicoes GOLD (XAU): {len(gold_df)}")
    print()

    if len(gold_df) == 0:
        print("Nenhuma posicao Gold encontrada!")
        print()
        print("Simbolos unicos no relatorio:")
        print(df['symbol'].value_counts().head(20))
        exit()

    # Converter profit para numerico
    gold_df['profit'] = pd.to_numeric(gold_df['profit'], errors='coerce')
    gold_df['open_price'] = pd.to_numeric(gold_df['open_price'], errors='coerce')
    gold_df['close_price'] = pd.to_numeric(gold_df['close_price'], errors='coerce')
    gold_df['sl'] = pd.to_numeric(gold_df['sl'], errors='coerce')

    # Calcular SL distance para ordens fechadas
    gold_df['sl_distance'] = abs(gold_df['open_price'] - gold_df['close_price'])

    # Mostrar ultimas 20 ordens
    print("=" * 80)
    print("ULTIMAS 20 POSICOES GOLD")
    print("=" * 80)
    print()

    for idx, row in gold_df.tail(20).iterrows():
        print(f"Position: {row['position']}")
        print(f"  Open:  {row['open_time']}")
        print(f"  Close: {row['close_time']}")
        print(f"  Type: {row['type']}")
        print(f"  Volume: {row['volume']}")
        print(f"  Entry: {row['open_price']:.3f}")
        print(f"  Exit:  {row['close_price']:.3f}")
        print(f"  SL Setting: {row['sl']}")
        print(f"  TP Setting: {row['tp']}")
        print(f"  SL Distance (real): ${row['sl_distance']:.3f}")
        print(f"  Profit: ${row['profit']:.2f}")

        # Verificar se foi SL
        if pd.notna(row['sl']) and pd.notna(row['close_price']):
            # Para BUY, SL esta abaixo do entry
            if 'buy' in str(row['type']).lower():
                expected_sl_dist = row['open_price'] - row['sl']
                if abs(row['close_price'] - row['sl']) < 1.0:
                    print(f"  >>> FOI STOP LOSS! (fechou proximo ao SL {row['sl']:.3f})")
                    print(f"  >>> SL ESPERADO: ${expected_sl_dist:.3f} de distancia")
            # Para SELL, SL esta acima do entry
            else:
                expected_sl_dist = row['sl'] - row['open_price']
                if abs(row['close_price'] - row['sl']) < 1.0:
                    print(f"  >>> FOI STOP LOSS! (fechou proximo ao SL {row['sl']:.3f})")
                    print(f"  >>> SL ESPERADO: ${expected_sl_dist:.3f} de distancia")

        print()

    # ESTATISTICAS
    print("=" * 80)
    print("ESTATISTICAS GOLD")
    print("=" * 80)
    print()

    gold_profits = gold_df['profit'].dropna()

    print(f"Total Trades: {len(gold_profits)}")
    print(f"Total Profit: ${gold_profits.sum():.2f}")
    print()

    wins = gold_profits[gold_profits > 0]
    losses = gold_profits[gold_profits < 0]

    print(f"Wins: {len(wins)}")
    if len(wins) > 0:
        print(f"  Avg Win: ${wins.mean():.2f}")
        print(f"  Max Win: ${wins.max():.2f}")
        print(f"  Min Win: ${wins.min():.2f}")
    print()

    print(f"Losses: {len(losses)}")
    if len(losses) > 0:
        print(f"  Avg Loss: ${losses.mean():.2f}")
        print(f"  Max Loss: ${losses.min():.2f}")
        print(f"  Min Loss: ${losses.max():.2f}")
    print()

    if len(wins) + len(losses) > 0:
        win_rate = len(wins) / (len(wins) + len(losses)) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    print()

    # Analisar SL distances
    print("=" * 80)
    print("ANALISE DE SL DISTANCES")
    print("=" * 80)
    print()

    sl_dists = gold_df['sl_distance'].dropna()
    if len(sl_dists) > 0:
        print(f"Total trades analisados: {len(sl_dists)}")
        print(f"Media de SL Distance: ${sl_dists.mean():.3f}")
        print(f"Min SL Distance: ${sl_dists.min():.3f}")
        print(f"Max SL Distance: ${sl_dists.max():.3f}")
        print()

        # Contar quantos tem ~$4.00
        around_4 = sl_dists[(sl_dists >= 3.0) & (sl_dists <= 5.0)]
        print(f"SL distances entre $3-5: {len(around_4)} ({len(around_4)/len(sl_dists)*100:.1f}%)")

        # Contar quantos tem ~$10+
        above_10 = sl_dists[sl_dists >= 10.0]
        print(f"SL distances >= $10: {len(above_10)} ({len(above_10)/len(sl_dists)*100:.1f}%)")

    print()
    print("=" * 80)

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
