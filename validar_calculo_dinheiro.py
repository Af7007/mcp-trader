#!/usr/bin/env python3
"""Valida calculo de pontos para dinheiro"""

print("="*60)
print("VALIDACAO DO CALCULO PONTOS -> DINHEIRO")
print("="*60)

pontos = 3000
point_value = 0.1
volume = 0.02

print(f"\nParametros:")
print(f"  Pontos: {pontos}")
print(f"  Point Value: ${point_value}")
print(f"  Volume: {volume}")

print(f"\nCalculo:")
dinheiro = pontos * point_value * volume
print(f"  {pontos} x ${point_value} x {volume} = ${dinheiro:.2f}")

print(f"\nRESULTADO: ${dinheiro:.2f}")

if abs(dinheiro - 6.0) < 0.01:
    print("VALIDACAO: CORRETO!")
else:
    print(f"VALIDACAO: INCORRETO! Esperado $6.00")

print("\n" + "="*60)
