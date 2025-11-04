#!/usr/bin/env python3
"""
Gold Loss Zero - VOLUME FIXO 0.02 LOTE
Configuração:
- Volume: 0.02 lote (FIXO)
- Worker: 0.5s
- Valores em $ calculados automaticamente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO
VOLUME = 0.02                        # Volume fixo
WORKER_INTERVAL = 0.5                # Monitora a cada 0.5s

# GOLD SPECS
GOLD_POINT_VALUE = 0.10              # $0.10 por lote por ponto
ATR_MEDIO = 60                       # ATR médio para Gold

# MULTIPLICADORES (padrão do agente)
SL_MULT = 1.5                        # SL = ATR × 1.5 = 90 pontos
TRAILING_ACT_MULT = 0.4              # Trailing ativa = ATR × 0.4 = 24 pontos
TRAILING_DIST_MULT = 0.3             # Trailing dist = ATR × 0.3 = 18 pontos

# CALCULAR VALORES EM $
# Com 0.02 lote: 1 ponto = 0.02 × $0.10 = $0.002
point_value_with_volume = VOLUME * GOLD_POINT_VALUE

sl_pontos = ATR_MEDIO * SL_MULT
sl_dollars = sl_pontos * point_value_with_volume

trailing_act_pontos = ATR_MEDIO * TRAILING_ACT_MULT
trailing_act_dollars = trailing_act_pontos * point_value_with_volume

trailing_dist_pontos = ATR_MEDIO * TRAILING_DIST_MULT
trailing_dist_dollars = trailing_dist_pontos * point_value_with_volume

print(f"\n{'='*60}")
print(f"GOLD LOSS ZERO - VOLUME FIXO 0.02 LOTE")
print(f"{'='*60}\n")
print(f"Volume: {VOLUME} lote (FIXO)")
print(f"Point Value: ${GOLD_POINT_VALUE}/lote/pt")
print(f"Com {VOLUME} lote: 1 ponto = ${point_value_with_volume:.4f}")
print(f"")
print(f"ATR Médio: {ATR_MEDIO} pontos")
print(f"")
print(f"VALORES CALCULADOS:")
print(f"  SL:               {sl_pontos:.0f} pts = ${sl_dollars:.2f}")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${trailing_act_dollars:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${trailing_dist_dollars:.2f}")
print(f"  Worker:           {WORKER_INTERVAL}s (muito rápido!)")
print(f"\n{'='*60}\n")

# CONFIRMAÇÃO
input("Pressione ENTER para iniciar o agente... ")

# Criar agente
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=VOLUME,
    check_interval=WORKER_INTERVAL,
    stop_loss_atr_multiplier=SL_MULT,
    trailing_activation_atr_multiplier=TRAILING_ACT_MULT,
    trailing_distance_atr_multiplier=TRAILING_DIST_MULT,
    use_buy=True,
    use_sell=True
)

print(f"\n{'='*60}")
print(f"AGENTE GOLD INICIADO!")
print(f"{'='*60}")
print(f"")
print(f"Volume: {VOLUME} lote")
print(f"SL: {sl_pontos:.0f} pts = ${sl_dollars:.2f}")
print(f"Trailing Ativa: {trailing_act_pontos:.0f} pts = ${trailing_act_dollars:.2f}")
print(f"Trailing Dist: {trailing_dist_pontos:.0f} pts = ${trailing_dist_dollars:.2f}")
print(f"Worker: {WORKER_INTERVAL}s")
print(f"")
print(f"CTRL+C para parar")
print(f"{'='*60}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente parado pelo usuário")
    agent.stop()
