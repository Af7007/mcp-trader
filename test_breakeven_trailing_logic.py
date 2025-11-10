#!/usr/bin/env python3
"""
Testa a logica de break-even e trailing stop
"""

print("=" * 60)
print("TESTE: Logica Break-Even e Trailing Stop")
print("=" * 60)
print()

# Parametros BTC AI
fixed_sl_dollars = 8.0
breakeven_activation_dollar = 1.50
trailing_activation_dollar = 4.00
trailing_distance_dollar = 2.00
volume = 0.05
point_value = 0.01  # Por lote
symbol_point = 0.01

print("CONFIGURACAO:")
print(f"   SL Fixo: ${fixed_sl_dollars:.2f}")
print(f"   Break-Even ativa em: ${breakeven_activation_dollar:.2f}")
print(f"   Trailing ativa em: ${trailing_activation_dollar:.2f}")
print(f"   Trailing protege: ${trailing_distance_dollar:.2f}")
print(f"   Volume: {volume}")
print(f"   Point value: ${point_value:.4f} por lote")
print()

# Simular trade BUY
print("=" * 60)
print("SIMULACAO: Trade BUY")
print("=" * 60)
print()

entry_price = 102000.00
print(f"Entry BUY: ${entry_price:.2f}")

# Calcular SL inicial
sl_distance = fixed_sl_dollars / (point_value * volume / symbol_point)
sl_price = entry_price - sl_distance

print(f"SL inicial: ${sl_price:.2f} (distancia ${sl_distance:.2f})")
print()

# Testar varios niveis de lucro
test_profits = [0.50, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00, 6.00, 8.00]

for profit_dollars in test_profits:
    print(f"--- Lucro: ${profit_dollars:.2f} ---")

    # Calcular preco atual para esse lucro
    profit_points = profit_dollars / (point_value * volume)
    price_move = profit_points * symbol_point
    current_price = entry_price + price_move

    print(f"   Preco atual: ${current_price:.2f} (moveu ${price_move:.2f})")

    # Verificar break-even
    if profit_dollars >= breakeven_activation_dollar:
        if sl_price < entry_price:  # SL ainda nao movido
            print(f"   [BREAK-EVEN] ATIVA! Mover SL para ${entry_price:.2f}")
            sl_price = entry_price
        else:
            print(f"   [BREAK-EVEN] Ja ativado (SL em ${sl_price:.2f})")
    else:
        print(f"   Break-Even: Aguardando ${breakeven_activation_dollar:.2f}")

    # Verificar trailing
    if profit_dollars >= trailing_activation_dollar:
        # Calcular trailing stop
        pontos_para_proteger = trailing_distance_dollar / (point_value * volume)
        trailing_price_distance = pontos_para_proteger * symbol_point
        trailing_stop = current_price - trailing_price_distance

        if trailing_stop > sl_price:
            print(f"   [TRAILING] ATIVA! Mover SL para ${trailing_stop:.2f}")
            print(f"   [TRAILING] Protegendo ${trailing_stop - entry_price:.2f} de lucro")
            sl_price = trailing_stop
        else:
            print(f"   [TRAILING] Trailing ${trailing_stop:.2f} nao superior ao SL atual ${sl_price:.2f}")
    else:
        print(f"   Trailing: Aguardando ${trailing_activation_dollar:.2f}")

    print()

print("=" * 60)
print("CONCLUSOES:")
print("=" * 60)
print()
print("1. Break-Even DEVE ativar quando lucro >= $1.50")
print("   - Movendo SL de ${:.2f} para ${:.2f} (entry)".format(entry_price - sl_distance, entry_price))
print()
print("2. Trailing DEVE ativar quando lucro >= $4.00")
print("   - Calculando trailing_stop = current_price - $40.00")
print("   - Movendo SL para trailing_stop se > SL atual")
print()
print("3. Se NENHUM dos dois ativou, verificar:")
print("   a. Worker iniciou? Procurar log: [WORKER] Monitor de trailing iniciado")
print("   b. Worker rodando? Deve mostrar logs a cada 20ms")
print("   c. Erro no callback? Procurar [BREAK-EVEN] ou [TRAILING] nos logs")
print()
print("=" * 60)
