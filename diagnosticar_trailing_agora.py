#!/usr/bin/env python3
"""
Diagnostico em tempo real: por que trailing nao funciona?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client

print("="*80)
print("DIAGNOSTICO EM TEMPO REAL - TRAILING NAO FUNCIONA")
print("="*80)

# Conectar MT5
mt5 = get_mt5_client()

# Obter posicoes
positions = mt5.positions_get(symbol="XAUUSDc")

if not positions:
    print("\n[ERRO] Nenhuma posicao aberta em XAUUSDc")
    exit(1)

pos = positions[0]
print(f"\n[POSICAO ABERTA]")
print(f"  Ticket: {pos['ticket']}")
print(f"  Tipo: {'BUY' if pos['type'] == 0 else 'SELL'}")
print(f"  Volume: {pos['volume']}")
print(f"  Entrada: ${pos['price_open']:.5f}")
print(f"  Atual: ${pos['price_current']:.5f}")
print(f"  Profit: ${pos['profit']:.2f}")
print(f"  SL: ${pos['sl']:.5f}")
print(f"  TP: ${pos['tp']:.5f}")

# Calcular diferenca
diff = pos['price_current'] - pos['price_open']
if pos['type'] == 0:  # BUY
    profit_pontos = diff / 0.001
else:  # SELL
    profit_pontos = -diff / 0.001

print(f"\n[CALCULO]")
print(f"  Diferenca de preco: {diff:.5f}")
print(f"  Profit em pontos: {profit_pontos:.0f} pts")
print(f"  Profit em dinheiro: ${pos['profit']:.2f}")

# Verificar se trailing deveria estar ativo
print(f"\n[ANALISE TRAILING]")
print(f"  SL atual: ${pos['sl']:.5f}")
print(f"  TP atual: ${pos['tp']:.5f}")

if pos['type'] == 0:  # BUY
    sl_pontos = (pos['price_open'] - pos['sl']) / 0.001
    print(f"  SL distance from entry: {sl_pontos:.0f} pts (${pos['price_open'] - pos['sl']:.5f})")
    
    if pos['profit'] >= 0.24:  # Deveria ativar em $0.24
        print(f"\n  [ESPERADO] Trailing DEVERIA estar ATIVO!")
        print(f"    - Lucro: ${pos['profit']:.2f} >= $0.24")
        print(f"    - SL deveria estar sendo atualizado")
        
        if pos['sl'] == pos['price_open'] - 5 * 0.001:  # SL original
            print(f"    - [PROBLEMA] SL NГAO foi movido! Trailing NAO funcionou!")
        else:
            print(f"    - [OK] SL foi movido (trailing ativo)")
    else:
        print(f"\n  [OK] Lucro ${pos['profit']:.2f} < $0.24, trailing ainda nao deveria ativar")

print(f"\n[PROXIMOS PASSOS]")
print(f"  1. Verifique se agente adaptive esta rodando")
print(f"  2. Verifique se ha erros no console do agente")
print(f"  3. Verifique se posicao foi aberta pelo agente")
print(f"  4. Mate agente e reinicie com: RUN_GOLD_ADAPTIVE.bat")

print("\n" + "="*80)
