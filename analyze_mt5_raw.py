"""
Le o relatorio MT5 de forma bruta para entender estrutura
"""
import pandas as pd

file_path = r"C:\mcp-trader\docs\ReportHistory-163049186.xlsx"

print("=" * 80)
print("LEITURA BRUTA DO RELATORIO MT5")
print("=" * 80)
print()

# Ler sem processar
df = pd.read_excel(file_path, header=None)

print(f"Total de linhas: {len(df)}")
print(f"Total de colunas: {len(df.columns)}")
print()

# Mostrar primeiras 30 linhas para encontrar headers
print("Primeiras 30 linhas:")
print()
for idx in range(min(30, len(df))):
    print(f"Linha {idx}:")
    row_data = []
    for col_idx in range(len(df.columns)):
        val = df.iloc[idx, col_idx]
        if pd.notna(val):
            row_data.append(f"Col{col_idx}: {val}")
    print("  " + " | ".join(row_data))
    print()

# Procurar linhas com "XAU"
print()
print("=" * 80)
print("LINHAS COM 'XAU' (primeiras 20):")
print("=" * 80)
print()

xau_count = 0
for idx in range(len(df)):
    row = df.iloc[idx]
    row_str = ' '.join([str(v) for v in row if pd.notna(v)])

    if 'XAU' in row_str.upper():
        xau_count += 1
        if xau_count <= 20:
            print(f"Linha {idx}:")
            for col_idx in range(len(df.columns)):
                val = df.iloc[idx, col_idx]
                if pd.notna(val):
                    print(f"  Col{col_idx}: {val}")
            print()

print(f"\nTotal de linhas com 'XAU': {xau_count}")
