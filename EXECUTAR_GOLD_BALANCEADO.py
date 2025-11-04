#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO BALANCEADA 
Ajustando filtros para equilíbrio entre precisão e frequência
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO BALANCEADA
VOLUME = 0.02
WORKER_INTERVAL = 0.5

# GOLD SPECS
POINT_VALUE_PER_LOT = 0.1  # CORRIGIDO: $0.10 por lote por ponto (XAUUSDc)
ATR_MEDIO = 60

# VALORES EM $ (mantendo os mesmos)
SL_DOLLARS = 6.00
TRAILING_ACT_DOLLARS = 1.00
TRAILING_DIST_DOLLARS = 0.50

point_value_with_volume = VOLUME * POINT_VALUE_PER_LOT
sl_pontos = SL_DOLLARS / point_value_with_volume
trailing_act_pontos = TRAILING_ACT_DOLLARS / point_value_with_volume
trailing_dist_pontos = TRAILING_DIST_DOLLARS / point_value_with_volume

sl_mult = sl_pontos / ATR_MEDIO
trailing_act_mult = trailing_act_pontos / ATR_MEDIO
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO

print(f"\n{'='*70}")
print(f"GOLD LOSS ZERO - VERSÃO BALANCEADA (Frequência + Precisão)")
print(f"{'='*70}\n")
print(f"CONFIGURAÇÃO OTIMIZADA:")
print(f"  Volume:           {VOLUME} lote")
print(f"  SL:               {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"AJUSTES FEITOS PARA MAIOR FREQUÊNCIA:")
print(f"  ✓ Momentum ajustado (0.05% → 0.04%)")
print(f"  ✓ Confirmações balanceadas (3 obrigatórias → 2+ volume)")
print(f"  ✓ Filtros de breakout mais flexíveis")
print(f"  ✓ Volume analysis mais permissivo")
print(f"  ✓ Suporte/resistência flexível")
print(f"\n{'='*70}\n")


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

def _analyze_m5_trend_balanced(self, rates) -> dict:
    """
    Análise BALANCEADA - precisão sem perder frequência
    """
    try:
        closes = [r['close'] for r in rates[:15]]
        highs = [r['high'] for r in rates[:15]]
        lows = [r['low'] for r in rates[:15]]
        volumes = [r['tick_volume'] for r in rates[:15]]

        current = closes[0]
        prev_1 = closes[1]
        prev_2 = closes[2]
        prev_5 = closes[5]
        prev_10 = closes[10]

        self.current_atr = self._calculate_atr_simple(rates[:14])

        # 1. TENDÊNCIA (simplificada para mais sinais)
        uptrend_5 = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 2  # Menos restritivo
        uptrend_10 = sum(1 for i in range(9) if closes[i] > closes[i+1]) >= 4  # Menos restritivo
        
        downtrend_5 = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 2
        downtrend_10 = sum(1 for i in range(9) if closes[i] < closes[i+1]) >= 4

        # 2. MOMENTUM BALANCEADO (reduzido para mais sinais)
        momentum_5m = ((current - prev_5) / prev_5) * 100
        momentum_10m = ((current - prev_10) / prev_10) * 100

        # 3. VOLATILIDADE FLEXÍVEL
        last_range = highs[0] - lows[0]
        avg_range = sum([highs[i] - lows[i] for i in range(1, 11)]) / 10
        adequate_volatility = last_range > avg_range * 0.5  # Mais flexível
        high_volatility = last_range > avg_range * 1.0

        # 4. VOLUME ANALYSIS FLEXÍVEL
        avg_volume = sum(volumes[1:11]) / 10
        volume_spike = volumes[0] > avg_volume * 1.1  # Menos restritivo
        high_volume = volumes[0] > avg_volume * 1.3

        # 5. SUPORTE/RESISTÊNCIA FLEXÍVEL
        recent_high = max(highs[0:5])
        recent_low = min(lows[0:5])
        near_resistance = current > recent_high * 0.998  # Mais flexível
        near_support = current < recent_low * 1.002

        # 6. BREAKOUT FLEXÍVEL
        breakout_up = current > max(highs[1:6]) * 0.999  # Menos restritivo
        breakout_down = current < min(lows[1:6]) * 1.001

        # MOMENTUM THRESHOLDS BALANCEADOS
        MOMENTUM_BUY = 0.04   # Reduzido de 0.05% para 0.04%
        MOMENTUM_SELL = -0.04

        # LOG
        import random
        if random.random() < 0.1:  # Menos logs
            print(f"   [M5-BAL] Mom: {momentum_5m:.3f}% | Vol: {volume_spike} | Breakout: {breakout_up}")

        # === SINAIS DE BUY - 2 CONFIRMAÇÕES + VOLUME ===
        if self.use_buy:
            confirmations = 0

            # Confirmação 1: Tendência forte OU momentum forte
            if (uptrend_5 and uptrend_10) or momentum_5m > MOMENTUM_BUY * 1.5:
                confirmations += 1
                
            # Confirmação 2: Volume OU volatilidade adequada
            if volume_spike or adequate_volatility:
                confirmations += 1
                
            # BÔNUS: Breakout OU momentum extra
            if breakout_up or momentum_5m > MOMENTUM_BUY * 2:
                confirmations += 1

            # SINAL se tiver 2 confirmações (mais permissivo)
            if confirmations >= 2:
                if self._check_m15_trend("BUY"):
                    return {"type": "BUY", "price": current, "reason": "M5_M15_balanced_buy"}

        # === SINAIS DE SELL - 2 CONFIRMAÇÕES + VOLUME ===
        if self.use_sell:
            confirmations = 0

            # Confirmação 1: Tendência forte OU momentum forte
            if (downtrend_5 and downtrend_10) or momentum_5m < MOMENTUM_SELL * 1.5:
                confirmations += 1
                
            # Confirmação 2: Volume OU volatilidade adequada
            if volume_spike or adequate_volatility:
                confirmations += 1
                
            # BÔNUS: Breakout OU momentum extra
            if breakout_down or momentum_5m < MOMENTUM_SELL * 2:
                confirmations += 1

            # SINAL se tiver 2 confirmações (mais permissivo)
            if confirmations >= 2:
                if self._check_m15_trend("SELL"):
                    return {"type": "SELL", "price": current, "reason": "M5_M15_balanced_sell"}

        return None

    except Exception as e:
        print(f"Erro na analise M5 balanceada: {e}")
        return None

# Aplicar método balanceado
agent._analyze_m5_trend = _analyze_m5_trend_balanced.__get__(agent, GoldLossZeroSimple)

print(f"\n{'='*70}")
print(f"AGENTE GOLD BALANCEADO INICIADO!")
print(f"{'='*70}")
print(f"")
print(f"COMPORTAMENTO BALANCEADO:")
print(f"  ✓ 2 confirmações obrigatórias + 1 opcional")
print(f"  ✓ Momentum moderado (0.04%)")
print(f"  ✓ Volume flexível (1.1x)")
print(f"  ✓ Breakout menos restritivo")
print(f"  ✓ Suporte/resistência flexível")
print(f"  ✓ Frequência aumentada, precisão mantida")
print(f"\nCTRL+C para parar")
print(f"{'='*70}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD BALANCEADO parado pelo usuário")
    if hasattr(agent, 'stop'):
        agent.stop()
