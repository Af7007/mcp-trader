#!/usr/bin/env python3
"""
GOLD LOSS ZERO - CONFIGURAÇÃO FINAL
Volume: 0.02 lote
SL: $6.00
Trailing ativa: $1.00
Trailing sobe: $0.50
Worker: 0.5s
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO FIXA
VOLUME = 0.02
WORKER_INTERVAL = 0.5

# GOLD SPECS
POINT_VALUE_PER_LOT = 0.10          # $0.10 por lote por ponto
ATR_MEDIO = 60                       # ATR médio para Gold

# VALORES DESEJADOS EM $
SL_DOLLARS = 6.00
TRAILING_ACT_DOLLARS = 1.00
TRAILING_DIST_DOLLARS = 0.50

# CALCULAR
point_value_with_volume = VOLUME * POINT_VALUE_PER_LOT  # $0.002 por ponto

# Converter $ para pontos
sl_pontos = SL_DOLLARS / point_value_with_volume                    # 3000 pts
trailing_act_pontos = TRAILING_ACT_DOLLARS / point_value_with_volume  # 500 pts
trailing_dist_pontos = TRAILING_DIST_DOLLARS / point_value_with_volume # 250 pts

# Multiplicadores de ATR
sl_mult = sl_pontos / ATR_MEDIO                        # 50.0
trailing_act_mult = trailing_act_pontos / ATR_MEDIO    # 8.33
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO  # 4.17

print(f"\n{'='*60}")
print(f"GOLD LOSS ZERO - CONFIGURAÇÃO $6 SL")
print(f"{'='*60}\n")
print(f"Volume: {VOLUME} lote (FIXO)")
print(f"Point Value: ${POINT_VALUE_PER_LOT}/lote/pt")
print(f"Com {VOLUME} lote: 1 pt = ${point_value_with_volume:.4f}")
print(f"ATR Médio: {ATR_MEDIO} pts")
print(f"")
print(f"CONFIGURAÇÃO EM DÓLARES:")
print(f"  SL:               ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Sobe:    ${TRAILING_DIST_DOLLARS:.2f}")
print(f"  Worker:           {WORKER_INTERVAL}s")
print(f"")
print(f"CONVERSÃO PARA PONTOS:")
print(f"  SL:               {sl_pontos:.0f} pts (ATR × {sl_mult:.2f})")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts (ATR × {trailing_act_mult:.2f})")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts (ATR × {trailing_dist_mult:.2f})")
print(f"\n{'='*60}\n")


# Criar agente
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=VOLUME,
    check_interval=WORKER_INTERVAL,
    stop_loss_atr_multiplier=sl_mult,
    trailing_activation_atr_multiplier=trailing_act_mult,
    trailing_distance_atr_multiplier=trailing_dist_mult,
    use_buy=True,
    use_sell=True
)

print(f"\n{'='*60}")
print(f"AGENTE GOLD INICIADO!")
print(f"{'='*60}")
print(f"Volume: {VOLUME} lote")
print(f"SL: {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"Trailing Ativa: {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"Trailing Sobe: {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"Worker: {WORKER_INTERVAL}s (muito rápido!)")
print(f"\nCTRL+C para parar")
print(f"{'='*60}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD parado pelo usuário")
    agent.stop()
