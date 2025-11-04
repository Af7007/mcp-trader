#!/usr/bin/env python3
"""
Gold Loss Zero - VALORES EM DÓLARES FIXOS
Configuração:
- SL: $9.00
- Trailing ativa: $1.00
- Trailing sobe: $0.50
- Worker: 0.5s
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def calculate_volume_for_sl(sl_dollars: float, sl_points: int, point_value_per_lot: float) -> float:
    """
    Calcula o volume necessário para atingir um SL em dólares.

    sl_dollars: Valor desejado em $ (ex: 9.00)
    sl_points: Distância em pontos (ex: 90)
    point_value_per_lot: Valor de 1 ponto para 1 lote (ex: 0.1 para Gold)

    Retorna: Volume em lotes
    """
    # sl_dollars = volume × sl_points × point_value_per_lot
    # volume = sl_dollars / (sl_points × point_value_per_lot)
    volume = sl_dollars / (sl_points * point_value_per_lot)
    return volume


# PARÂMETROS DESEJADOS
SL_DOLLARS = 9.00                    # $9.00 de stop loss
TRAILING_ACTIVATION_DOLLARS = 1.00   # Ativa trailing em $1.00 lucro
TRAILING_DISTANCE_DOLLARS = 0.50     # Mantém trailing a $0.50 do preço
WORKER_INTERVAL = 0.5                # Monitora a cada 0.5s

# GOLD SPECS (do MT5)
GOLD_POINT_VALUE = 0.1               # $0.10 por lote por ponto
GOLD_POINT_SIZE = 0.001              # Tick size

# CALCULAR PONTOS E VOLUME
# Usando ATR médio de 60 pontos para Gold
ATR_MEDIO = 60

# SL em pontos (1.5 × ATR = 90 pontos)
SL_POINTS = int(ATR_MEDIO * 1.5)  # 90 pontos

# Volume necessário para SL de $9.00 com 90 pontos
# $9.00 = volume × 90 × $0.1
# volume = $9.00 / (90 × $0.1) = $9.00 / $9.00 = 1.0 lote
VOLUME = calculate_volume_for_sl(SL_DOLLARS, SL_POINTS, GOLD_POINT_VALUE)
print(f"\n{'='*60}")
print(f"GOLD LOSS ZERO - CONFIGURAÇÃO EM DÓLARES")
print(f"{'='*60}\n")
print(f"SL Desejado: ${SL_DOLLARS:.2f}")
print(f"SL Pontos: {SL_POINTS} pts (1.5 × ATR {ATR_MEDIO})")
print(f"Volume Calculado: {VOLUME:.2f} lotes")
print(f"")
print(f"Verificação:")
print(f"  {SL_POINTS} pts × {VOLUME:.2f} lotes × ${GOLD_POINT_VALUE:.2f}/pt = ${SL_POINTS * VOLUME * GOLD_POINT_VALUE:.2f}")
print(f"")

# Calcular multiplicadores baseados em $ ao invés de ATR
# Trailing ativa: $1.00 / ($0.1 × volume) = pontos
trailing_activation_points = TRAILING_ACTIVATION_DOLLARS / (GOLD_POINT_VALUE * VOLUME)
trailing_activation_mult = trailing_activation_points / ATR_MEDIO

# Trailing distance: $0.50 / ($0.1 × volume) = pontos
trailing_distance_points = TRAILING_DISTANCE_DOLLARS / (GOLD_POINT_VALUE * VOLUME)
trailing_distance_mult = trailing_distance_points / ATR_MEDIO

print(f"Trailing Ativa em: ${TRAILING_ACTIVATION_DOLLARS:.2f} = {trailing_activation_points:.0f} pts (ATR × {trailing_activation_mult:.2f})")
print(f"Trailing Distância: ${TRAILING_DISTANCE_DOLLARS:.2f} = {trailing_distance_points:.0f} pts (ATR × {trailing_distance_mult:.2f})")
print(f"Worker Monitora: {WORKER_INTERVAL}s")
print(f"\n{'='*60}\n")

# CONFIRMAÇÃO
input("Pressione ENTER para iniciar o agente com estas configurações... ")

# Criar agente
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=VOLUME,
    check_interval=WORKER_INTERVAL,
    stop_loss_atr_multiplier=1.5,  # 90 pontos com ATR 60
    trailing_activation_atr_multiplier=trailing_activation_mult,
    trailing_distance_atr_multiplier=trailing_distance_mult,
    use_buy=True,
    use_sell=True
)

print(f"\n{'='*60}")
print(f"AGENTE INICIADO!")
print(f"{'='*60}")
print(f"")
print(f"Configuração Ativa:")
print(f"  SL: ${SL_DOLLARS:.2f} ({SL_POINTS} pontos)")
print(f"  Trailing Ativa: ${TRAILING_ACTIVATION_DOLLARS:.2f}")
print(f"  Trailing Distância: ${TRAILING_DISTANCE_DOLLARS:.2f}")
print(f"  Volume: {VOLUME:.2f} lotes")
print(f"  Worker: {WORKER_INTERVAL}s (muito rápido!)")
print(f"")
print(f"CTRL+C para parar")
print(f"{'='*60}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente parado pelo usuário")
    agent.stop()
