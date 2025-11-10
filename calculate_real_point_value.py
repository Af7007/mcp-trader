#!/usr/bin/env python3
"""
Calcula o point_value REAL atraves de dados empiricos da trade
"""

# Dados da posicao
ticket = 115120603
entry_price = 4005.02800
sl_price = 4006.69467
volume = 0.03
symbol_point = 0.001

# Calculo reverso: sabendo que o SL estava em 4006.69467
# e o fixed_sl_dollars = $5.00, podemos calcular o point_value real

# Formula: sl_dinheiro / (point_value × volume) = pontos
# Formula: pontos × symbol_point = price_distance
# Formula: sl_price = entry + price_distance (para SELL)

# Entao: price_distance = sl_price - entry
price_distance = sl_price - entry_price
print(f"Price distance (SL - Entry): {price_distance:.5f}")

# pontos = price_distance / symbol_point
pontos = price_distance / symbol_point
print(f"Pontos MT5: {pontos:.1f}")

# Agora: fixed_sl_dollars = pontos × point_value × volume
# Entao: point_value = fixed_sl_dollars / (pontos × volume)

fixed_sl_dollars = 5.0  # Valor configurado
point_value_real = fixed_sl_dollars / (pontos * volume)

print(f"\nCALCULO REVERSO:")
print(f"  fixed_sl_dollars: ${fixed_sl_dollars:.2f}")
print(f"  pontos: {pontos:.1f}")
print(f"  volume: {volume}")
print(f"  point_value_real: ${fixed_sl_dollars} / ({pontos:.1f} × {volume}) = ${point_value_real:.6f}")

print(f"\nVERIFICACAO:")
# Verificar se o calculo bate
sl_dinheiro_calculado = pontos * point_value_real * volume
price_distance_calculada = (sl_dinheiro_calculado / (point_value_real * volume)) * symbol_point
sl_price_calculado = entry_price + price_distance_calculada

print(f"  SL em dinheiro (verificacao): ${sl_dinheiro_calculado:.2f}")
print(f"  Price distance (verificacao): {price_distance_calculada:.5f}")
print(f"  SL price (verificacao): {sl_price_calculado:.5f}")
print(f"  SL price (real): {sl_price:.5f}")
print(f"  Diferenca: {abs(sl_price_calculado - sl_price):.6f}")

# Testar com os point_values comuns
print(f"\n" + "="*100)
print("TESTANDO COM VALORES COMUNS:")
print("="*100)

test_values = [0.01, 0.03, 0.003, 0.1, 1.0, 0.0299688]

for pv in test_values:
    pontos_test = fixed_sl_dollars / (pv * volume)
    distance_test = pontos_test * symbol_point
    sl_test = entry_price + distance_test

    print(f"\npoint_value = ${pv:.6f}:")
    print(f"  Pontos: {pontos_test:.1f}")
    print(f"  Distance: {distance_test:.5f}")
    print(f"  SL calculado: {sl_test:.5f}")
    print(f"  SL real: {sl_price:.5f}")
    print(f"  Diferenca: {abs(sl_test - sl_price):.6f}")

    if abs(sl_test - sl_price) < 0.001:
        print(f"  >>> [MATCH!] Este e o point_value correto!")

print(f"\n" + "="*100)
print("CONCLUSAO:")
print("="*100)
print(f"O point_value CORRETO para XAUUSDc com volume {volume} e: ${point_value_real:.6f}")
print(f"")
print(f"Isso significa:")
print(f"  1 ponto de variacao = ${point_value_real:.6f} × {volume} = ${point_value_real * volume:.6f}")
print(f"  1000 pontos (1.000 de preco) = ${point_value_real * volume * 1000:.2f}")
