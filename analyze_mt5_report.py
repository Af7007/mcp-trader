"""
Analisa o relatorio de historico exportado do MT5
"""
import pandas as pd
from datetime import datetime

# Ler o arquivo Excel
file_path = r"C:\mcp-trader\docs\ReportHistory-163049186.xlsx"

try:
    # Tentar ler todas as sheets
    xls = pd.ExcelFile(file_path)

    print("=" * 80)
    print("ANALISE DO RELATORIO MT5 - ReportHistory-163049186.xlsx")
    print("=" * 80)
    print()

    print(f"Sheets encontradas: {xls.sheet_names}")
    print()

    # Ler cada sheet
    for sheet_name in xls.sheet_names:
        print("=" * 80)
        print(f"SHEET: {sheet_name}")
        print("=" * 80)
        print()

        df = pd.read_excel(file_path, sheet_name=sheet_name)

        print(f"Total de linhas: {len(df)}")
        print(f"Colunas: {list(df.columns)}")
        print()

        # Mostrar primeiras linhas
        print("Primeiras 10 linhas:")
        print(df.head(10).to_string())
        print()

        # Se tiver coluna de simbolo, filtrar Gold
        symbol_cols = [col for col in df.columns if 'symbol' in col.lower() or 'simbolo' in col.lower()]
        if symbol_cols:
            symbol_col = symbol_cols[0]
            gold_df = df[df[symbol_col].str.contains('XAU', case=False, na=False)]

            print(f"\nOrdens GOLD (XAU): {len(gold_df)}")
            print()

            if len(gold_df) > 0:
                print("Ultimas 15 ordens Gold:")
                print(gold_df.tail(15).to_string())
                print()

                # Analisar SL
                sl_cols = [col for col in df.columns if 'sl' in col.lower() or 'stop' in col.lower()]
                profit_cols = [col for col in df.columns if 'profit' in col.lower() or 'lucro' in col.lower()]
                price_cols = [col for col in df.columns if 'price' in col.lower() or 'preco' in col.lower()]

                print(f"\nColunas relevantes encontradas:")
                print(f"  SL: {sl_cols}")
                print(f"  Profit: {profit_cols}")
                print(f"  Price: {price_cols}")
                print()

                # Estatisticas
                if profit_cols:
                    profit_col = profit_cols[0]
                    gold_profits = gold_df[profit_col].dropna()

                    if len(gold_profits) > 0:
                        print("ESTATISTICAS GOLD:")
                        print(f"  Total Profit: ${gold_profits.sum():.2f}")
                        print(f"  Trades: {len(gold_profits)}")

                        wins = gold_profits[gold_profits > 0]
                        losses = gold_profits[gold_profits < 0]

                        if len(wins) > 0:
                            print(f"  Wins: {len(wins)}")
                            print(f"  Avg Win: ${wins.mean():.2f}")
                            print(f"  Max Win: ${wins.max():.2f}")

                        if len(losses) > 0:
                            print(f"  Losses: {len(losses)}")
                            print(f"  Avg Loss: ${losses.mean():.2f}")
                            print(f"  Max Loss: ${losses.min():.2f}")

                        if len(wins) + len(losses) > 0:
                            win_rate = len(wins) / (len(wins) + len(losses)) * 100
                            print(f"  Win Rate: {win_rate:.1f}%")

        print()

except Exception as e:
    print(f"Erro ao ler arquivo: {e}")
    print()
    print("Tentando abordagem alternativa...")

    # Tentar ler sem header especifico
    try:
        df = pd.read_excel(file_path)
        print(f"\nArquivo lido com {len(df)} linhas")
        print(f"Colunas: {list(df.columns)}")
        print()
        print("Primeiras 20 linhas:")
        print(df.head(20).to_string())
    except Exception as e2:
        print(f"Erro na abordagem alternativa: {e2}")
