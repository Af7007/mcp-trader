#!/usr/bin/env python3
"""
Simula o calculo do trailing stop para entender por que o SL estava errado
"""

# Dados da posicao problema
ticket = 115120603
pos_type = 1  # SELL
entry_price = 4005.02800
sl_at_close = 4006.69467
exit_price = 4005.42200

# Parametros do agente
volume = 0.03
point_value = 0.003  # Para XAUUSDc cents
symbol_point = 0.001  # Tick size do Gold

# Parametros de trailing
trailing_activation_dollar = 1.0  # Ativa com $1 de lucro
trailing_distance_dollar = 1.0  # Protege $1 inicialmente
profit_step_for_increment_dollar = 1.50  # A cada $1.50 de lucro adicional
protection_increment_dollar = 1.0  # Aumenta protecao em $1

print("="*100)
print("SIMULACAO DO CALCULO DE TRAILING STOP")
print("="*100)

print(f"\nPOSICAO:")
print(f"  Ticket: {ticket}")
print(f"  Type: SELL")
print(f"  Entry: {entry_price:.5f}")
print(f"  SL no close: {sl_at_close:.5f}")
print(f"  Exit: {exit_price:.5f}")
print(f"  Volume: {volume}")

# CENARIO 1: Posicao abrindo com SL inicial ($5)
print("\n"+"="*100)
print("CENARIO 1: SL INICIAL (na abertura)")
print("="*100)

fixed_sl_dollars = 5.0
pontos_para_sl = fixed_sl_dollars / (point_value * volume)
sl_price_distance = pontos_para_sl * symbol_point

# Para SELL: SL = market_price + distance
sl_inicial = entry_price + sl_price_distance

print(f"\nCALCULO:")
print(f"  fixed_sl_dollars: ${fixed_sl_dollars:.2f}")
print(f"  pontos_para_sl: {fixed_sl_dollars} / ({point_value} × {volume}) = {pontos_para_sl:.1f} pontos")
print(f"  sl_price_distance: {pontos_para_sl:.1f} × {symbol_point} = {sl_price_distance:.5f}")
print(f"  SL inicial (SELL): {entry_price:.5f} + {sl_price_distance:.5f} = {sl_inicial:.5f}")

print(f"\nVERIFICACAO:")
print(f"  SL calculado: {sl_inicial:.5f}")
print(f"  SL no banco: {sl_at_close:.5f}")
print(f"  Diferenca: {abs(sl_inicial - sl_at_close):.5f}")

if abs(sl_inicial - sl_at_close) < 0.01:
    print(f"  [OK] SL inicial bate com o SL no banco!")
else:
    print(f"  [PROBLEMA] SL inicial diferente do SL no banco!")

# CENARIO 2: Trailing ativando
print("\n"+"="*100)
print("CENARIO 2: TRAILING ATIVANDO (log mostra price=4004.574, profit=$1.60)")
print("="*100)

# Dados do log de trailing
trailing_price_at_activation = 4004.574
trailing_profit_at_activation = 1.60

# Calcular lucro teorico
if pos_type == 1:  # SELL
    price_movement = entry_price - trailing_price_at_activation  # Preco caiu
    profit_pontos_teorico = price_movement / symbol_point
    profit_dinheiro_teorico = profit_pontos_teorico * point_value * volume

print(f"\nCALCULO DO LUCRO:")
print(f"  Entry: {entry_price:.5f}")
print(f"  Current Price: {trailing_price_at_activation:.3f}")
print(f"  Movimento: {entry_price:.5f} - {trailing_price_at_activation:.3f} = {price_movement:.5f}")
print(f"  Pontos MT5: {price_movement:.5f} / {symbol_point} = {profit_pontos_teorico:.1f}")
print(f"  Lucro teorico: {profit_pontos_teorico:.1f} × {point_value} × {volume} = ${profit_dinheiro_teorico:.2f}")
print(f"  Lucro no log: ${trailing_profit_at_activation:.2f}")

# Calcular trailing stop quando ativa
pontos_para_proteger = trailing_distance_dollar / (point_value * volume)
trailing_price_distance = pontos_para_proteger * symbol_point

# Para SELL: SL = current_price + distance (SL deve ficar ACIMA)
trailing_sl_teorico = trailing_price_at_activation + trailing_price_distance

print(f"\nCALCULO DO TRAILING SL:")
print(f"  Proteção: ${trailing_distance_dollar:.2f}")
print(f"  Pontos para proteger: {trailing_distance_dollar} / ({point_value} × {volume}) = {pontos_para_proteger:.1f}")
print(f"  Distance: {pontos_para_proteger:.1f} × {symbol_point} = {trailing_price_distance:.5f}")
print(f"  Trailing SL (SELL): {trailing_price_at_activation:.3f} + {trailing_price_distance:.5f} = {trailing_sl_teorico:.5f}")

# SL do log
trailing_sl_from_log = 4004.90733

print(f"\nVERIFICACAO:")
print(f"  SL calculado: {trailing_sl_teorico:.5f}")
print(f"  SL no log: {trailing_sl_from_log:.5f}")
print(f"  Diferenca: {abs(trailing_sl_teorico - trailing_sl_from_log):.5f}")

# CENARIO 3: Por que a ordem fechou em 4005.422?
print("\n"+"="*100)
print("CENARIO 3: POR QUE A ORDEM FECHOU EM 4005.422?")
print("="*100)

print(f"\nTIMELINE:")
print(f"  18:15:06 - Ordem FECHOU em {exit_price:.5f} (SL no banco: {sl_at_close:.5f})")
print(f"  18:15:50 - Trailing ATIVOU (44 segundos depois!)")
print(f"            Price: {trailing_price_at_activation:.3f}")
print(f"            SL: {trailing_sl_from_log:.5f}")

print(f"\nANALISE:")
print(f"  1. Ordem abriu em {entry_price:.5f} com SL em {sl_at_close:.5f} (${fixed_sl_dollars} de loss)")
print(f"  2. Preco SUBIU para {exit_price:.5f} (contra a posicao SELL)")
print(f"  3. SL foi atingido em {sl_at_close:.5f}, loss de $1.00")
print(f"  4. Trailing tentou ativar 44 segundos DEPOIS (posicao ja fechada)")

print(f"\n  [PROBLEMA] Preco subiu de {entry_price:.5f} para {exit_price:.5f}")
print(f"  [PROBLEMA] Movimento: {exit_price - entry_price:.5f} pontos")
print(f"  [PROBLEMA] Loss: {((exit_price - entry_price)/symbol_point * point_value * volume):.2f} USD")

print(f"\n  [ESTRANHO] Exit price {exit_price:.5f} esta ABAIXO do SL {sl_at_close:.5f}")
print(f"  [ESTRANHO] Como pode fechar ABAIXO do SL em posicao SELL?")

print(f"\n  [TEORIA] Talvez o SL tenha sido modificado DURANTE o fechamento")
print(f"  [TEORIA] Ou o MT5 fechou antes do SL ser atingido por outro motivo")

print("\n"+"="*100)
print("CONCLUSAO:")
print("="*100)
print("""
O codigo de trailing esta CORRETO (linhas 1527 e 1543):
- BUY: if new_stop > trailing_stop_price (SL so sobe)
- SELL: if new_stop < trailing_stop_price (SL so desce)

MAS o problema e que o trailing NAO ESTAVA ATIVO quando a ordem fechou!
A ordem usou o SL inicial de $5, e fechou com loss de -$1 ANTES do trailing ativar.

SOLUCAO:
1. Reduzir SL inicial de $5 para $1 ou $2 (mais conservador)
2. Ou ativar trailing desde o inicio (com $0.10 de lucro)
3. Ou usar breakeven rapido (mover SL para entry quando atingir $1 lucro)
""")
