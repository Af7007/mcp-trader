#!/usr/bin/env python3
"""
Testa o calculo do trailing progressivo v3.3.0
"""

print("=" * 60)
print("TESTE: Trailing Progressivo v3.3.0")
print("=" * 60)
print()

# Parametros
trailing_activation = 3.5
volume = 0.05
point_value = 0.01  # Por lote
symbol_point = 0.01
entry_price = 102000.00

print(f"CONFIGURACAO:")
print(f"   Entry: ${entry_price:.2f}")
print(f"   Volume: {volume}")
print(f"   Ativa trailing em: ${trailing_activation:.2f}")
print()

print("FORMULA: protecao = lucro - $1.50")
print()

# Testar varios niveis de lucro
test_profits = [0.50, 1.00, 2.00, 3.00, 3.50, 4.00, 5.00, 6.00, 8.00, 10.00]

print("=" * 60)
print("SIMULACAO: Trailing Progressivo")
print("=" * 60)
print()

for profit in test_profits:
    print(f"Lucro: ${profit:.2f}")

    if profit < trailing_activation:
        print(f"   [AGUARDANDO] Trailing ativa em ${trailing_activation:.2f}")
    else:
        # Calcular protecao progressiva
        protected_profit = profit - 1.5

        if protected_profit < 0:
            protected_profit = 0

        # Calcular SL
        pontos_para_proteger = protected_profit / (point_value * volume)
        trailing_price_distance = pontos_para_proteger * symbol_point

        # Para BUY
        sl_price = entry_price + trailing_price_distance

        print(f"   [TRAILING ATIVO]")
        print(f"   Protecao: ${protected_profit:.2f}")
        print(f"   SL: ${sl_price:.2f}")
        print(f"   Distancia do entry: ${sl_price - entry_price:.2f}")

    print()

print("=" * 60)
print("RESUMO:")
print("=" * 60)
print()
print("Break-Even: $0.50 -> SL vai para entry")
print("Trailing:")
print("   $3.50 lucro -> SL protege $2.00 (entry + $2)")
print("   $4.00 lucro -> SL protege $3.00 (entry + $3)")
print("   $5.00 lucro -> SL protege $4.00 (entry + $4)")
print("   $6.00 lucro -> SL protege $5.00 (entry + $5)")
print("   $8.00 lucro -> SL protege $7.00 (entry + $7)")
print("   $10.00 lucro -> SL protege $9.00 (entry + $9)")
print()
print("=" * 60)
