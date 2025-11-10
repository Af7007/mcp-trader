#!/usr/bin/env python3
"""
Diagnostica por que trailing nao ativou em ordem com $4 de lucro
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("DIAGNOSTICO: Por que Trailing nao ativou?")
print("=" * 60)
print()

# Simular calculo
volume = 0.05
point_value = 0.01  # Por lote
symbol_point = 0.01
entry_price = 102000.00
trailing_activation = 3.5

print("CONFIGURACAO:")
print(f"   Entry: ${entry_price:.2f}")
print(f"   Volume: {volume}")
print(f"   Point value: ${point_value:.4f} por lote")
print(f"   Trailing ativa em: ${trailing_activation:.2f}")
print()

# Testar com $4 de lucro
profit_dollars = 4.00
current_price = entry_price + 80.00  # BUY subiu $80

print(f"SITUACAO REPORTADA:")
print(f"   Lucro: ${profit_dollars:.2f}")
print(f"   Preco atual: ${current_price:.2f}")
print()

# Verificar se deveria ativar
print("CHECAGEM:")
print(f"   profit_dollars ({profit_dollars:.2f}) >= trailing_activation ({trailing_activation:.2f})?")

if profit_dollars >= trailing_activation:
    print(f"   [OK] SIM - Trailing DEVERIA ter ativado!")
    print()

    # Calcular protecao progressiva
    protected_profit = profit_dollars - 1.5
    print(f"   Protecao calculada: ${protected_profit:.2f} (lucro - $1.50)")

    # Calcular SL
    pontos_para_proteger = protected_profit / (point_value * volume)
    trailing_price_distance = pontos_para_proteger * symbol_point

    sl_price = entry_price + trailing_price_distance

    print(f"   SL deveria ser: ${sl_price:.2f}")
    print(f"   Distancia do entry: ${sl_price - entry_price:.2f}")
    print()

    print("POSSIVEIS CAUSAS DA FALHA:")
    print("   1. Worker nao rodando?")
    print("      - Procurar log: [WORKER] Monitor de trailing iniciado")
    print()
    print("   2. Ticket nao nos dicionarios?")
    print("      - Procurar log: [BREAK-EVEN DEBUG] Ticket X sem entry_price")
    print()
    print("   3. Calculo de lucro errado?")
    print("      - Verificar formula: profit_dollars = profit_points * point_value * volume")
    print()
    print("   4. Worker nao checou a tempo?")
    print("      - Ordem fechou MUITO rapido antes de worker checar?")
    print("      - Worker roda a cada 20ms, se ordem durou <20ms nao checou")
    print()
    print("   5. Condicao de ativacao errada no codigo?")
    print("      - Verificar linha ~664: if profit_dollars >= self.trailing_activation_dollar")
    print()
else:
    print(f"   [X] NAO - Trailing NAO deveria ativar")

print()
print("=" * 60)
print("PROXIMOS PASSOS:")
print("=" * 60)
print()
print("1. Verificar logs do agente:")
print("   - Procurar '[WORKER] Monitor de trailing iniciado'")
print("   - Procurar '[TRAILING ATIVADO]' ou '[TRAILING ATUALIZADO]'")
print("   - Procurar '[BREAK-EVEN' logs")
print()
print("2. Se nao houver logs de trailing:")
print("   - Worker nao rodou OU")
print("   - Lucro nunca chegou a $3.50 OU")
print("   - Ticket nao estava nos dicionarios")
print()
print("3. Adicionar debug logging:")
print("   - Imprimir lucro SEMPRE no callback do worker")
print("   - Imprimir quando trailing checa mas nao ativa")
print()
print("=" * 60)
