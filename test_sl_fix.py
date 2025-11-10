#!/usr/bin/env python3
"""
Testa o calculo CORRETO do SL com a nova formula simplificada
"""

# Parametros BTC
fixed_sl_dollars = 8.0
volume = 0.05
point_value = 0.01  # Por lote (NAO multiplicado por volume)
symbol_point = 0.01

print("=" * 60)
print("TESTE: Calculo SL Simplificado")
print("=" * 60)
print()
print(f"Parametros:")
print(f"  fixed_sl_dollars: ${fixed_sl_dollars:.2f}")
print(f"  volume: {volume}")
print(f"  point_value (por lote): ${point_value:.4f}")
print(f"  symbol_point: {symbol_point}")
print()

# NOVA FORMULA (CORRIGIDA)
print("NOVA FORMULA:")
print(f"  sl_distance = fixed_sl_dollars / (point_value * volume / symbol_point)")
print()

sl_distance = fixed_sl_dollars / (point_value * volume / symbol_point)

print(f"  sl_distance = {fixed_sl_dollars} / ({point_value} * {volume} / {symbol_point})")
print(f"  sl_distance = {fixed_sl_dollars} / ({point_value * volume / symbol_point})")
print(f"  sl_distance = ${sl_distance:.2f}")
print()

# Verificacao
print("VERIFICACAO:")
print(f"  Se preco entry = $102,000")
print(f"  SL BUY = $102,000 - ${sl_distance:.2f} = ${102000 - sl_distance:.2f}")
print(f"  SL SELL = $102,000 + ${sl_distance:.2f} = ${102000 + sl_distance:.2f}")
print()

# Calcular loss real
print("LOSS REAL:")
print(f"  Distance em pontos: {sl_distance / symbol_point:.0f} pontos")
print(f"  Loss por ponto: ${point_value * volume:.4f}")
print(f"  Loss total: {sl_distance / symbol_point:.0f} * ${point_value * volume:.4f} = ${(sl_distance / symbol_point) * (point_value * volume):.2f}")
print()

if abs((sl_distance / symbol_point) * (point_value * volume) - fixed_sl_dollars) < 0.01:
    print("[OK] Calculo CORRETO! Loss = ${:.2f}".format((sl_distance / symbol_point) * (point_value * volume)))
else:
    print("[ERRO] Calculo ERRADO! Loss = ${:.2f} (esperado ${:.2f})".format(
        (sl_distance / symbol_point) * (point_value * volume),
        fixed_sl_dollars
    ))

print()
print("=" * 60)
