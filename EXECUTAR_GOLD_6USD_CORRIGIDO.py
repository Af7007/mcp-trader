#!/usr/bin/env python3
"""
GOLD LOSS ZERO - CONFIGURAÇÃO CORRIGIDA
Volume: 0.02 lote
SL: $6.00 (5.0 × ATR)
Trailing ativa: $1.00 (0.83 × ATR)
Trailing distancia: $0.50 (0.42 × ATR)
Worker: 0.5s
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO FIXA
VOLUME = 0.02
WORKER_INTERVAL = 0.5

# GOLD SPECS CORRETAS PARA CONTA CENTS
POINT_VALUE_PER_LOT = 1.0           # $1.00 por lote por ponto (XAUUSDc)
ATR_MEDIO = 60                       # ATR médio para Gold em pontos

# VALORES DESEJADOS EM $ (convertidos diretamente para ATR)
SL_DOLLARS = 6.00
TRAILING_ACT_DOLLARS = 1.00
TRAILING_DIST_DOLLARS = 0.50

# Calcular o valor do ponto COM VOLUME
point_value_with_volume = VOLUME * POINT_VALUE_PER_LOT  # $0.02 por ponto

# Converter $ para pontos (considerando volume)
sl_pontos = SL_DOLLARS / point_value_with_volume                    # 300 pts
trailing_act_pontos = TRAILING_ACT_DOLLARS / point_value_with_volume  # 50 pts
trailing_dist_pontos = TRAILING_DIST_DOLLARS / point_value_with_volume # 25 pts

# CORREÇÃO: Multiplicadores de ATR REALISTAS para Gold
# GOLD tem ATR ~60pts, então para conseguir os $ desejados:
sl_mult = sl_pontos / ATR_MEDIO                        # 5.0
trailing_act_mult = trailing_act_pontos / ATR_MEDIO    # 0.83
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO  # 0.42

print(f"\n{'='*60}")
print(f"GOLD LOSS ZERO - CONFIGURAÇÃO $6 SL (CORRIGIDO)")
print(f"{'='*60}\n")
print(f"Volume: {VOLUME} lote (FIXO - Conta Cents)")
print(f"Point Value: ${POINT_VALUE_PER_LOT}/lote/pt")
print(f"Com {VOLUME} lote: 1 pt = ${point_value_with_volume:.4f}")
print(f"ATR Médio: {ATR_MEDIO} pts")
print(f"")
print(f"CONFIGURAÇÃO EM DÓLARES:")
print(f"  SL:               ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Distância: ${TRAILING_DIST_DOLLARS:.2f}")
print(f"  Worker:           {WORKER_INTERVAL}s")
print(f"")
print(f"CONVERSÃO PARA PONTOS (COM VOLUME 0.02):")
print(f"  SL:               {sl_pontos:.0f} pts (ATR × {sl_mult:.2f})")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts (ATR × {trailing_act_mult:.2f})")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts (ATR × {trailing_dist_mult:.2f})")
print(f"")
print(f"CORREÇÕES APLICADAS:")
print(f"  - Point Value: $1.00/lote/pt (conta cents)")
print(f"  - Volume considera multiplicador")
print(f"  - Multiplicadores ATR realistas")
print(f"  - Trailing será ativado em $1.00 lucro")
print(f"  - Trailing protege $0.50 adicional")
print(f"\n{'='*60}\n")

input("Pressione ENTER para iniciar o agente GOLD... ")

# Criar agente com multiplicadores CORRIGIDOS
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=VOLUME,
    check_interval=WORKER_INTERVAL,
    stop_loss_atr_multiplier=sl_mult,              # CORRIGIDO: 5.0
    trailing_activation_atr_multiplier=trailing_act_mult,  # CORRIGIDO: 0.83
    trailing_distance_atr_multiplier=trailing_dist_mult,    # CORRIGIDO: 0.42
    use_buy=True,
    use_sell=True
)

print(f"\n{'='*60}")
print(f"AGENTE GOLD INICIADO! (TRAILING CORRIGIDO)")
print(f"{'='*60}")
print(f"Volume: {VOLUME} lote")
print(f"SL: {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"Trailing Ativa: {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"Trailing Dist: {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"COMPORTAMENTO CORRIGIDO:")
print(f"  - SL: $6.00 (perda máxima)")
print(f"  - Trailing ativa com $1.00 lucro")
print(f"  - Trailing sobe/desce $0.50")
print(f"  - Lucro mínimo protegido: $0.50")
print(f"  - Worker: {WORKER_INTERVAL}s (monitoramento contínuo)")
print(f"\nCTRL+C para parar")
print(f"{'='*60}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD parado pelo usuário")
    agent.stop()
