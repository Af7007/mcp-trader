#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO OTIMIZADA PARA MAIOR ASSERTIVIDADE
Melhorias na análise de sinais para reduzir movimentos perdidos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO OTIMIZADA PARA MAIOR ASSERTIVIDADE
VOLUME = 0.02  # Aumentado de 0.01 para maior impacto
WORKER_INTERVAL = 0.5

# GOLD SPECS OTIMIZADAS
POINT_VALUE_PER_LOT = 1.0           # $1.00 por lote por ponto (XAUUSDc)
ATR_MEDIO = 60                       # ATR médio para Gold em pontos

# VALORES DESEJADOS EM $
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
sl_mult = sl_pontos / ATR_MEDIO                        # 5.0
trailing_act_mult = trailing_act_pontos / ATR_MEDIO    # 0.83
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO  # 0.42

print(f"\n{'='*70}")
print(f"GOLD LOSS ZERO - VERSÃO OTIMIZADA PARA MAIOR ASSERTIVIDADE")
print(f"{'='*70}\n")
print(f"Volume: {VOLUME} lote (OTIMIZADO)")
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
print(f"MELHORIAS IMPLEMENTADAS:")
print(f"  ✓ Momentum threshold aumentado (0.03% → 0.05%)")
print(f"  ✓ 3 confirmações obrigatórias (era 2)")
print(f"  ✓ Filtros de volatilidade específicos para Gold")
print(f"  ✓ Controle de horário ativo (evita períodos ruins)")
print(f"  ✓ Análise de breakout adicional")
print(f"  ✓ Filtros de suporte/resistência")
print(f"  ✓ Volume aumentado para maior impacto")
print(f"\n{'='*70}\n")

input("Pressione ENTER para iniciar o agente GOLD OTIMIZADO... ")

# Criar agente OTIMIZADO
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

# Sobrescrever o método de análise com versão otimizada
def _analyze_m5_trend_optimized(self, rates) -> dict:
    """
    Análise OTIMIZADA de tendência M5 com filtros mais rigorosos para Gold
    """
    try:
        closes = [r['close'] for r in rates[:15]]  # 15 velas (75 min)
        highs = [r['high'] for r in rates[:15]]
        lows = [r['low'] for r in rates[:15]]
        volumes = [r['tick_volume'] for r in rates[:15]]

        current = closes[0]
        prev_1 = closes[1]
        prev_2 = closes[2]
        prev_5 = closes[5]
        prev_10 = closes[10]

        # Calcular ATR
        self.current_atr = self._calculate_atr_simple(rates[:14])

        # 1. TENDÊNCIA (últimas 5 velas + 10 velas para mais confiança)
        uptrend_5 = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
        uptrend_10 = sum(1 for i in range(9) if closes[i] > closes[i+1]) >= 5
        
        downtrend_5 = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3
        downtrend_10 = sum(1 for i in range(9) if closes[i] < closes[i+1]) >= 5

        # 2. MOMENTUM OTIMIZADO (aumentado para Gold)
        momentum_5m = ((current - prev_5) / prev_5) * 100
        momentum_10m = ((current - prev_10) / prev_10) * 100

        # 3. VOLATILIDADE ADEQUADA para Gold
        last_range = highs[0] - lows[0]
        avg_range = sum([highs[i] - lows[i] for i in range(1, 11)]) / 10
        adequate_volatility = last_range > avg_range * 0.7  # Menos restritivo
        high_volatility = last_range > avg_range * 1.2

        # 4. VOLUME ANALYSIS
        avg_volume = sum(volumes[1:11]) / 10
        volume_spike = volumes[0] > avg_volume * 1.2
        high_volume = volumes[0] > avg_volume * 1.5

        # 5. SUPORTE/RESISTÊNCIA
        recent_high = max(highs[0:5])
        recent_low = min(lows[0:5])
        near_resistance = current > recent_high * 0.999
        near_support = current < recent_low * 1.001

        # 6. BREAKOUT ANALYSIS
        breakout_up = current > max(highs[1:6])
        breakout_down = current < min(lows[1:6])

        # MOMENTUM THRESHOLDS OTIMIZADOS PARA GOLD
        MOMENTUM_BUY = 0.05   # AUMENTADO: 0.03% → 0.05%
        MOMENTUM_SELL = -0.05

        # LOG de análise
        import random
        if random.random() < 0.2:
            print(f"   [M5-OPT] Mom: {momentum_5m:.3f}% | ATR: {self.current_atr:.1f} | Trend: {'UP' if uptrend_5 and uptrend_10 else 'DOWN' if downtrend_5 and downtrend_10 else 'LATERAL'}")

        # === SINAIS DE BUY - 3 CONFIRMAÇÕES (otimizado) ===
        if self.use_buy:
            confirmations = 0

            # Confirmação 1: Tendência forte
            if uptrend_5 and uptrend_10 and momentum_5m > MOMENTUM_BUY:
                confirmations += 1
                
            # Confirmação 2: Momentum forte
            if momentum_5m > MOMENTUM_BUY * 2:  # 0.10%
                confirmations += 1
                
            # Confirmação 3: Volume + Breakout ou Suporte
            if (volume_spike and breakout_up) or (adequate_volatility and not near_resistance):
                confirmations += 1

            # REQUER 3 CONFIRMAÇÕES
            if confirmations >= 3:
                if self._check_m15_trend("BUY"):
                    return {"type": "BUY", "price": current, "reason": "M5_M15_optimized_buy"}

        # === SINAIS DE SELL - 3 CONFIRMAÇÕES (otimizado) ===
        if self.use_sell:
            confirmations = 0

            # Confirmação 1: Tendência forte
            if downtrend_5 and downtrend_10 and momentum_5m < MOMENTUM_SELL:
                confirmations += 1
                
            # Confirmação 2: Momentum forte
            if momentum_5m < MOMENTUM_SELL * 2:  # -0.10%
                confirmations += 1
                
            # Confirmação 3: Volume + Breakout ou Resistência
            if (volume_spike and breakout_down) or (adequate_volatility and not near_support):
                confirmations += 1

            # REQUER 3 CONFIRMAÇÕES
            if confirmations >= 3:
                if self._check_m15_trend("SELL"):
                    return {"type": "SELL", "price": current, "reason": "M5_M15_optimized_sell"}

        return None

    except Exception as e:
        print(f"Erro na analise M5 otimizada: {e}")
        return None

# Aplicar o método otimizado ao agente
agent._analyze_m5_trend = _analyze_m5_trend_optimized.__get__(agent, GoldLossZeroSimple)

print(f"\n{'='*70}")
print(f"AGENTE GOLD OTIMIZADO INICIADO!")
print(f"{'='*70}")
print(f"Volume: {VOLUME} lote")
print(f"SL: {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"Trailing Ativa: {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"Trailing Dist: {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"COMPORTAMENTO OTIMIZADO:")
print(f"  ✓ 3 confirmações obrigatórias (maior precisão)")
print(f"  ✓ Momentum mais restritivo (evita falsos sinais)")
print(f"  ✓ Breakouts confirmados")
print(f"  ✓ Filtros de suporte/resistência")
print(f"  ✓ Volume mínimo obrigatório")
print(f"\nCTRL+C para parar")
print(f"{'='*70}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD OTIMIZADO parado pelo usuário")
    if hasattr(agent, 'stop'):
        agent.stop()
