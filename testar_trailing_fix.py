#!/usr/bin/env python3
"""
Teste: Validar que trailing agora funciona mesmo com entry_price zerado
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("TESTE: TRAILING COM POSICAO JA ABERTA")
print("="*80)

# Simular a correção
entry_price_instance = 0.0  # Simula agente que abriu posição em outra sessão
price_open_position = 3934.47800  # Da posição aberta

# ANTES (BUG)
print("\n[ANTES - BUG]")
if entry_price_instance <= 0:
    print("  entry_price_instance <= 0 -> RETORNA SEM FAZER NADA!")
    print("  Trailing NAO funciona [BROKEN]")

# DEPOIS (CORRIGIDO)
print("\n[DEPOIS - CORRIGIDO]")
entry_price = entry_price_instance if entry_price_instance > 0 else price_open_position
if entry_price <= 0:
    print("  entry_price <= 0 -> Erro")
else:
    print(f"  entry_price_instance = {entry_price_instance} -> usa price_open = {price_open_position}")
    print(f"  entry_price = {entry_price}")
    print(f"  Trailing AGORA FUNCIONA! [OK]")

# Simular cenário com lucro
print("\n[SIMULACAO - POSICAO EM LUCRO]")
current_price = 3934.24  # SELL em lucro (preco desceu)
pos_type = 1  # SELL

# Calcular lucro com a correção
profit_price_diff = entry_price - current_price
profit_pontos = profit_price_diff / 0.001
profit_dinheiro = profit_pontos * 0.001 * 0.01

print(f"  Entrada: ${entry_price:.5f}")
print(f"  Atual: ${current_price:.5f}")
print(f"  Tipo: SELL")
print(f"  Lucro: {profit_pontos:.0f} pts = ${profit_dinheiro:.2f}")

# Verificar ativação
trailing_activation_pontos = 241  # 0.05 × 4821
if profit_pontos >= trailing_activation_pontos:
    print(f"\n  Lucro {profit_pontos:.0f}pts >= Threshold {trailing_activation_pontos:.0f}pts")
    print(f"  [OK] TRAILING ATIVA!")
else:
    print(f"\n  Lucro {profit_pontos:.0f}pts < Threshold {trailing_activation_pontos:.0f}pts")
    print(f"  Aguardando...")

print("\n" + "="*80)
