#!/usr/bin/env python3
"""
Verifica os calculos de trailing com point_value CORRETO
"""

# VALORES CORRETOS
point_value = 0.10  # CORRETO!
symbol_point = 0.001
volume = 0.03

# Parametros de trailing
trailing_activation_dollar = 1.0
trailing_distance_dollar = 1.0

# Dados do log de trailing
ticket = 115120603
entry_price = 4005.02800
current_price_at_activation = 4004.574
profit_at_activation = 1.60  # Do log
sl_from_log = 4004.90733

print("="*100)
print("RECALCULANDO TRAILING COM POINT_VALUE CORRETO")
print("="*100)

print(f"\nPARAMETROS CORRETOS:")
print(f"  point_value: ${point_value:.6f}")
print(f"  symbol_point: {symbol_point}")
print(f"  volume: {volume}")

# CALCULO 1: Lucro quando trailing ativou
print(f"\n" + "="*100)
print("CALCULO 1: LUCRO QUANDO TRAILING ATIVOU")
print("="*100)

price_movement = entry_price - current_price_at_activation  # SELL: preco caiu
pontos_mt5 = price_movement / symbol_point
lucro_dinheiro = pontos_mt5 * point_value * volume

print(f"\nEntry: {entry_price:.5f}")
print(f"Current Price: {current_price_at_activation:.3f}")
print(f"Movimento: {price_movement:.5f}")
print(f"Pontos MT5: {pontos_mt5:.1f}")
print(f"Lucro calculado: {pontos_mt5:.1f} × ${point_value} × {volume} = ${lucro_dinheiro:.2f}")
print(f"Lucro no log: ${profit_at_activation:.2f}")

if abs(lucro_dinheiro - profit_at_activation) < 0.01:
    print(f"[OK] Lucro bate!")
else:
    print(f"[PROBLEMA] Lucro calculado diferente do log!")

# CALCULO 2: SL de trailing quando ativou
print(f"\n" + "="*100)
print("CALCULO 2: SL DE TRAILING QUANDO ATIVOU")
print("="*100)

pontos_para_proteger = trailing_distance_dollar / (point_value * volume)
trailing_price_distance = pontos_para_proteger * symbol_point
trailing_sl_calculado = current_price_at_activation + trailing_price_distance  # SELL: SL acima

print(f"\nProtecao desejada: ${trailing_distance_dollar:.2f}")
print(f"Pontos necessarios: ${trailing_distance_dollar} / (${point_value} × {volume}) = {pontos_para_proteger:.1f}")
print(f"Distance em preco: {pontos_para_proteger:.1f} × {symbol_point} = {trailing_price_distance:.5f}")
print(f"SL calculado (SELL): {current_price_at_activation:.3f} + {trailing_price_distance:.5f} = {trailing_sl_calculado:.5f}")
print(f"SL no log: {sl_from_log:.5f}")

if abs(trailing_sl_calculado - sl_from_log) < 0.01:
    print(f"[OK] SL de trailing bate!")
else:
    print(f"[PROBLEMA] SL calculado diferente do log!")
    print(f"Diferenca: {abs(trailing_sl_calculado - sl_from_log):.5f}")

# CALCULO 3: Verificar se o SL de trailing protegeria $1
print(f"\n" + "="*100)
print("CALCULO 3: VERIFICACAO DE PROTECAO")
print("="*100)

# Se o preco voltar para o SL de trailing, qual seria o lucro?
price_at_sl = sl_from_log
price_movement_at_sl = entry_price - price_at_sl
pontos_at_sl = price_movement_at_sl / symbol_point
profit_at_sl = pontos_at_sl * point_value * volume

print(f"\nSe o preco atingir o SL de trailing ({sl_from_log:.5f}):")
print(f"  Movimento desde entry: {price_movement_at_sl:.5f}")
print(f"  Pontos: {pontos_at_sl:.1f}")
print(f"  Lucro protegido: ${profit_at_sl:.2f}")
print(f"  Protecao desejada: ${trailing_distance_dollar:.2f}")

if abs(profit_at_sl - trailing_distance_dollar) < 0.10:
    print(f"  [OK] Protecao correta!")
else:
    print(f"  [PROBLEMA] Protecao nao e de ${trailing_distance_dollar:.2f}!")

# CALCULO 4: Por que a ordem fechou com -$1?
print(f"\n" + "="*100)
print("CALCULO 4: POR QUE A ORDEM FECHOU COM -$1.00?")
print("="*100)

exit_price = 4005.42200
sl_at_close = 4006.69467

print(f"\nDados do fechamento:")
print(f"  Entry: {entry_price:.5f}")
print(f"  Exit: {exit_price:.5f}")
print(f"  SL no close: {sl_at_close:.5f}")

# Calcular loss
price_movement_at_close = entry_price - exit_price  # SELL: negativo = loss
pontos_at_close = price_movement_at_close / symbol_point
loss_at_close = pontos_at_close * point_value * volume

print(f"\nMovimento: {price_movement_at_close:.5f} (negativo = preco subiu = loss)")
print(f"Pontos: {pontos_at_close:.1f}")
print(f"Loss calculado: ${loss_at_close:.2f}")
print(f"Loss registrado: $-1.00")

if abs(loss_at_close - (-1.0)) < 0.01:
    print(f"[OK] Loss calculado bate com o registrado!")

# Distancia do exit ao SL
distance_to_sl = sl_at_close - exit_price
print(f"\nDistancia do exit ao SL: {sl_at_close:.5f} - {exit_price:.5f} = {distance_to_sl:.5f}")
print(f"Isso corresponde a: {distance_to_sl / symbol_point:.1f} pontos")
print(f"Que valeria: ${(distance_to_sl / symbol_point) * point_value * volume:.2f} adicionais de loss")

print(f"\n[CONCLUSAO] A ordem fechou ANTES de atingir o SL inicial de ${5.0}!")
print(f"[CONCLUSAO] Ela fechou com apenas $-1.00 de loss, nao atingiu os $-5.00 do SL!")
print(f"[CONCLUSAO] O trailing ativou 44 segundos DEPOIS, em uma situacao diferente!")
