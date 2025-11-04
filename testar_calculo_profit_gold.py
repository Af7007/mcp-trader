#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa cálculo de profit para Gold
"""

print("="*60)
print("TESTE - Cálculo de Profit para Gold")
print("="*60)
print()

# Configuração Gold
volume = 0.02  # lotes
contract_size = 100  # oz por lote
point_value = contract_size * volume  # 100 * 0.02 = 2

print(f"Volume: {volume} lotes")
print(f"Contract Size: {contract_size} oz/lote")
print(f"Point Value: {point_value} (valor em $ por $1 de movimento)")
print()

# Exemplo 1: Lucro de $2
print("="*60)
print("EXEMPLO 1: Usuário reportou lucro de $2")
print("="*60)

# Se o lucro real é $2, qual foi o movimento de preço?
profit_reported = 2.0
price_movement_needed = profit_reported / point_value

print(f"Lucro reportado: ${profit_reported:.2f}")
print(f"Movimento de preço necessário: ${price_movement_needed:.2f}")
print()

# Simulação
entry_price = 4000.00
current_price = entry_price + price_movement_needed

profit_calc = (current_price - entry_price) * point_value

print(f"Se Entry: ${entry_price:.2f}")
print(f"E Current: ${current_price:.2f}")
print(f"Então Profit: ${profit_calc:.2f}")
print()

# Exemplo 2: Movimento de $1
print("="*60)
print("EXEMPLO 2: Preço se moveu $1.00")
print("="*60)

entry = 4000.00
current = 4001.00
movement = current - entry
profit = movement * point_value

print(f"Entry: ${entry:.2f}")
print(f"Current: ${current:.2f}")
print(f"Movement: ${movement:.2f}")
print(f"Profit: ${profit:.2f}")
print()

# Exemplo 3: Trailing deve ativar
print("="*60)
print("EXEMPLO 3: Quando Trailing Ativa?")
print("="*60)

print("Trailing ativa quando: profit > $0")
print()

test_movements = [0.01, 0.05, 0.10, 0.50, 1.00, 2.00]

for mov in test_movements:
    profit = mov * point_value
    should_activate = "SIM" if profit > 0 else "NÃO"
    print(f"Movimento ${mov:.2f} → Profit ${profit:.2f} → Trailing: {should_activate}")

print()

# Exemplo 4: Níveis de trailing
print("="*60)
print("EXEMPLO 4: Níveis de Trailing (step $0.20)")
print("="*60)

trailing_step = 0.20

test_profits = [0.05, 0.10, 0.20, 0.40, 0.60, 1.00, 2.00]

for profit in test_profits:
    level = int(profit / trailing_step)
    print(f"Profit ${profit:.2f} → Nível {level}")

print()
print("="*60)
print("CONCLUSÃO:")
print("="*60)
print()
print("✓ Para lucro de $2.00, preço precisa mover $1.00")
print("✓ Trailing DEVE ativar com qualquer lucro > $0")
print("✓ Com step $0.20:")
print("  - Nível 0: $0.00 - $0.19")
print("  - Nível 1: $0.20 - $0.39")
print("  - Nível 2: $0.40 - $0.59")
print("  - Nível 10: $2.00 - $2.19")
print()
print("Se o sistema mostrou lucro de $2 e não ativou trailing,")
print("há um BUG na lógica de ativação ou no modify_position!")
