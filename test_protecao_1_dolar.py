#!/usr/bin/env python3
"""
Testa a protecao progressiva com diferenca de $1
"""

print("=" * 60)
print("TESTE: Protecao Progressiva v3.4.0 (DIFERENCA $1)")
print("=" * 60)
print()

# Parametros
volume = 0.05
point_value = 0.01  # Por lote
symbol_point = 0.01
entry_price = 102000.00

print(f"CONFIGURACAO:")
print(f"   Entry: ${entry_price:.2f}")
print(f"   Volume: {volume}")
print()

print("FORMULA: protecao = lucro - $1.00")
print()

# Testar varios niveis de lucro
test_profits = [0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00, 8.00, 10.00]

print("=" * 60)
print("SIMULACAO: Protecao Progressiva")
print("=" * 60)
print()

for profit in test_profits:
    print(f"Lucro: ${profit:.2f}")

    if profit < 1.0:
        print(f"   [AGUARDANDO] Break-even ativa em $1.00")
    elif profit < 2.0:
        print(f"   [BREAK-EVEN]")
        print(f"   Protecao: $0.00")
        print(f"   SL: ${entry_price:.2f} (entry)")
    else:
        # A partir de $2, protege (lucro - $1)
        protected_profit = profit - 1.0

        # Calcular SL
        protected_points = protected_profit / (point_value * volume)
        protected_distance = protected_points * symbol_point

        # Para BUY
        sl_price = entry_price + protected_distance

        print(f"   [TRAILING]")
        print(f"   Protecao: ${protected_profit:.2f}")
        print(f"   SL: ${sl_price:.2f}")
        print(f"   Distancia do entry: ${sl_price - entry_price:.2f}")

    print()

print("=" * 60)
print("RESUMO:")
print("=" * 60)
print()
print("Break-Even: $1.00 -> SL vai para entry (protege $0)")
print("Trailing:")
print("   $2.00 lucro -> SL protege $1.00 (entry + $20)")
print("   $3.00 lucro -> SL protege $2.00 (entry + $40)")
print("   $4.00 lucro -> SL protege $3.00 (entry + $60)")
print("   $5.00 lucro -> SL protege $4.00 (entry + $80)")
print("   $8.00 lucro -> SL protege $7.00 (entry + $140)")
print("   $10.00 lucro -> SL protege $9.00 (entry + $180)")
print()
print("DIFERENCA CONSTANTE: $1.00 em todos os niveis!")
print()
print("=" * 60)
