"""
Calcula parametros equivalentes Gold -> BTC mantendo mesma expectativa em dolares
"""

print("="*80)
print("CALCULO DE PARAMETROS EQUIVALENTES: GOLD -> BTC")
print("="*80)

# === GOLD (XAUUSDc) ===
print("\n[GOLD - XAUUSDc]")
gold_point = 0.001  # $0.001
gold_tick_value = 0.10  # $0.10 por lote
gold_volume = 0.03  # lotes
gold_point_value_per_lot = gold_tick_value  # $0.10/lote

# Valor do ponto com volume
gold_point_value = gold_point_value_per_lot * gold_volume  # $0.10 * 0.03 = $0.003
print(f"Point: ${gold_point}")
print(f"Tick Value (por lote): ${gold_tick_value}")
print(f"Volume: {gold_volume} lotes")
print(f"Point Value (com volume): ${gold_point_value}")

# SL/TP em dolares
gold_sl_dollars = 5.0
gold_ts_activation = 2.0
gold_ts_distance = 1.0

print(f"\nSL: ${gold_sl_dollars}")
print(f"TS Activation: ${gold_ts_activation}")
print(f"TS Distance: ${gold_ts_distance}")

# Calcular distancia em pontos
gold_sl_points = gold_sl_dollars / gold_point_value
gold_ts_activation_points = gold_ts_activation / gold_point_value
gold_ts_distance_points = gold_ts_distance / gold_point_value

print(f"\nSL em pontos: {gold_sl_points:.0f} pts")
print(f"TS Activation em pontos: {gold_ts_activation_points:.0f} pts")
print(f"TS Distance em pontos: {gold_ts_distance_points:.0f} pts")

# === BTC (BTCUSDc) ===
print("\n" + "="*80)
print("[BTC - BTCUSDc]")
btc_point = 0.01  # $0.01
btc_tick_value = 0.01  # $0.01 por lote
btc_contract_size = 0.01

# Para manter MESMA expectativa em dolares, calcular volume necessario
# gold_point_value = $0.003 por ponto (com 0.03 lotes)
# btc_point_value_per_lot = $0.01 por lote
# btc_volume = gold_point_value / btc_point_value_per_lot

btc_point_value_per_lot = btc_tick_value  # $0.01/lote
btc_volume = gold_point_value / btc_point_value_per_lot

print(f"Point: ${btc_point}")
print(f"Tick Value (por lote): ${btc_tick_value}")
print(f"Volume necessario: {btc_volume} lotes")
print(f"Point Value (com volume): ${btc_volume * btc_point_value_per_lot}")

# SL/TP em dolares (MESMOS valores que Gold)
btc_sl_dollars = gold_sl_dollars
btc_ts_activation = gold_ts_activation
btc_ts_distance = gold_ts_distance

print(f"\nSL: ${btc_sl_dollars}")
print(f"TS Activation: ${btc_ts_activation}")
print(f"TS Distance: ${btc_ts_distance}")

# Calcular distancia em pontos
btc_sl_points = btc_sl_dollars / (btc_volume * btc_point_value_per_lot)
btc_ts_activation_points = btc_ts_activation / (btc_volume * btc_point_value_per_lot)
btc_ts_distance_points = btc_ts_distance / (btc_volume * btc_point_value_per_lot)

print(f"\nSL em pontos: {btc_sl_points:.0f} pts")
print(f"TS Activation em pontos: {btc_ts_activation_points:.0f} pts")
print(f"TS Distance em pontos: {btc_ts_distance_points:.0f} pts")

# Conversao para preco (BTC)
# 1 ponto BTC = $0.01
btc_sl_price_distance = btc_sl_points * btc_point
btc_ts_activation_price = btc_ts_activation_points * btc_point
btc_ts_distance_price = btc_ts_distance_points * btc_point

print(f"\nSL em preco BTC: ${btc_sl_price_distance:.2f}")
print(f"TS Activation em preco: ${btc_ts_activation_price:.2f}")
print(f"TS Distance em preco: ${btc_ts_distance_price:.2f}")

print("\n" + "="*80)
print("RESUMO - PARAMETROS PARA BTC v2.0.0")
print("="*80)
print(f"""
volume = {btc_volume}  # lotes (equivalente a Gold 0.03)
fixed_sl_dollars = {btc_sl_dollars}  # SL fixo em dolares
trailing_activation_dollar = {btc_ts_activation}  # Ativar TS
trailing_distance_dollar = {btc_ts_distance}  # Distancia TS

# Valores em pontos BTC (para referencia):
# SL = {btc_sl_points:.0f} pts = ${btc_sl_price_distance:.2f}
# TS Activation = {btc_ts_activation_points:.0f} pts = ${btc_ts_activation_price:.2f}
# TS Distance = {btc_ts_distance_points:.0f} pts = ${btc_ts_distance_price:.2f}
""")

print("="*80)
print("COMPARACAO GOLD vs BTC (mesma expectativa em $)")
print("="*80)
print(f"{'Parametro':<30} {'GOLD':<20} {'BTC':<20}")
print("-"*80)
print(f"{'Volume':<30} {gold_volume:<20} {btc_volume:<20}")
print(f"{'SL ($)':<30} {gold_sl_dollars:<20} {btc_sl_dollars:<20}")
print(f"{'TS Activation ($)':<30} {gold_ts_activation:<20} {btc_ts_activation:<20}")
print(f"{'TS Distance ($)':<30} {gold_ts_distance:<20} {btc_ts_distance:<20}")
print(f"{'Point Value':<30} ${gold_point_value:<19} ${btc_volume * btc_point_value_per_lot:<19}")
print("-"*80)
print("Resultado: MESMA expectativa em dolares para ambos os simbolos")

# ATR e Spread para BTC
print("\n" + "="*80)
print("FILTROS ATR E SPREAD - BTC")
print("="*80)

# Gold: ATR max = $2.00
# BTC: Calcular ATR equivalente
# BTC tem movimentos maiores, entao ATR em pontos sera maior
# Mas em DOLARES deve ser proporcional

# Gold: $2.00 ATR = 2.00 / 0.003 = ~667 pontos
# BTC: $2.00 ATR = 2.00 / (btc_volume * btc_point_value_per_lot) = ~667 pontos
# Em preco BTC: 667 * 0.01 = $6.67

gold_atr_max = 2.0
btc_atr_max_points = gold_atr_max / (btc_volume * btc_point_value_per_lot)
btc_atr_max_price = btc_atr_max_points * btc_point

print(f"Gold ATR max: ${gold_atr_max}")
print(f"BTC ATR max (pontos): {btc_atr_max_points:.0f} pts")
print(f"BTC ATR max (preco): ${btc_atr_max_price:.2f}")
print(f"\nPara manter mesma expectativa: max_atr_m5_dollars = ${gold_atr_max}")

# Spread
gold_spread_max = 0.5
print(f"\nGold Spread max: ${gold_spread_max}")
print(f"BTC Spread max: ${gold_spread_max} (manter mesmo valor em dolares)")
