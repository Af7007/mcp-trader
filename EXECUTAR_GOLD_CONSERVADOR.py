#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO CONSERVADORA
Foco na QUALIDADE das ordens, não quantidade
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
import datetime

# CONFIGURAÇÃO CONSERVADORA
VOLUME = 0.02
WORKER_INTERVAL = 0.5

# GOLD SPECS
POINT_VALUE_PER_LOT = 1.0
ATR_MEDIO = 60

# VALORES EM $ (ajustados para qualidade)
SL_DOLLARS = 8.00  # Aumentado de $6 para $8 (menos restritivo)
TRAILING_ACT_DOLLARS = 1.50  # Aumentado de $1 para $1.50
TRAILING_DIST_DOLLARS = 0.75  # Aumentado de $0.50 para $0.75

point_value_with_volume = VOLUME * POINT_VALUE_PER_LOT
sl_pontos = SL_DOLLARS / point_value_with_volume
trailing_act_pontos = TRAILING_ACT_DOLLARS / point_value_with_volume
trailing_dist_pontos = TRAILING_DIST_DOLLARS / point_value_with_volume

sl_mult = sl_pontos / ATR_MEDIO
trailing_act_mult = trailing_act_pontos / ATR_MEDIO
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO

def is_market_open():
    """
    Verifica se o mercado de Gold está aberto
    """
    now = datetime.datetime.now()
    weekday = now.weekday()
    hour = now.hour
    
    # Fechado fins de semana
    if weekday >= 5:
        return False, "Fim de semana"
    
    # Fechado de sexta 19h até domingo 19h (horário brasileiro)
    if weekday == 4 and hour >= 19:
        return False, "Fechado (sexta à noite)"
    if weekday == 5:
        return False, "Fim de semana"
    if weekday == 6 and hour < 19:
        return False, "Fim de semana"
    
    # Verificar horários ideais (evitar alta volatilidade)
    # Evitar 8h-10h e 14h-16h (horários de news de alta volatilidade)
    if hour in [8, 9, 14, 15]:
        return False, f"Alta volatilidade (horário news)"
    
    return True, "Mercado aberto"

print(f"\n{'='*70}")
print(f"GOLD LOSS ZERO - VERSÃO CONSERVADORA (QUALIDADE)")
print(f"{'='*70}\n")
print(f"CONFIGURAÇÃO QUALITATIVA:")
print(f"  Volume:           {VOLUME} lote")
print(f"  SL:               {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f} (MAIS FLEXÍVEL)")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"FOCO NA QUALIDADE:")
print(f"  ✓ Momentum alto (0.15% vs 0.02%)")
print(f"  ✓ 5 confirmações obrigatórias")
print(f"  ✓ Filtros de alta volatilidade")
print(f"  ✓ Evitar horários de news")
print(f"  ✓ SL mais flexível ($8 vs $6)")
print(f"  ✓ ATR dinâmico em tempo real")
print(f"\n{'='*70}\n")

input("Pressione ENTER para iniciar o agente GOLD CONSERVADOR... ")

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

def _analyze_m5_trend_conservative(self, rates) -> dict:
    """
    Análise CONSERVADORA - Foco na QUALIDADE das ordens
    """
    try:
        # VERIFICAÇÃO DE HORÁRIO DE MERCADO
        market_open, status_msg = is_market_open()
        if not market_open:
            import time
            current_time = time.time()
            if not hasattr(self, '_last_market_log'):
                self._last_market_log = 0
            
            if current_time - self._last_market_log > 600:
                print(f"   [CONS] {status_msg} - Aguardando...")
                self._last_market_log = current_time
            return None
        
        # VERIFICAÇÃO ROBUSTA DE DADOS
        if not rates or len(rates) < 20:  # Mínimo 20 candles para análise robusta
            return None
            
        # Dados com análise estendida
        max_analysis = min(20, len(rates))
        closes = [r['close'] for r in rates[:max_analysis]]
        highs = [r['high'] for r in rates[:max_analysis]]
        lows = [r['low'] for r in rates[:max_analysis]]
        volumes = [r['tick_volume'] for r in rates[:max_analysis]]

        current = closes[0]
        
        # Preços anteriores múltiplos
        prev_1 = closes[1] if len(closes) > 1 else current
        prev_3 = closes[3] if len(closes) > 3 else current
        prev_5 = closes[5] if len(closes) > 5 else current
        prev_10 = closes[10] if len(closes) > 10 else current
        prev_15 = closes[15] if len(closes) > 15 else current

        # ATR dinâmico em tempo real
        atr_len = min(14, len(rates)-1)
        if atr_len >= 2:
            self.current_atr = self._calculate_atr_simple(rates[:atr_len])
        else:
            self.current_atr = ATR_MEDIO

        # ANÁLISE CONSERVADORA - 5 CONFIRMAÇÕES OBRIGATÓRIAS
        
        # 1. TENDÊNCIA FORTE (últimas 15 velas)
        uptrend_strong = sum(1 for i in range(14) if closes[i] > closes[i+1]) >= 9  # 60% up
        downtrend_strong = sum(1 for i in range(14) if closes[i] < closes[i+1]) >= 9  # 60% down

        # 2. MOMENTUM ALTO (0.15% = $0.30 por lote)
        momentum_15m = ((current - prev_15) / prev_15) * 100 if prev_15 != 0 else 0
        momentum_10m = ((current - prev_10) / prev_10) * 100 if prev_10 != 0 else 0
        momentum_5m = ((current - prev_5) / prev_5) * 100 if prev_5 != 0 else 0

        # 3. VOLUME SIGNIFICATIVO
        vol_avg = sum(volumes[5:15]) / 10
        vol_spike = volumes[0] > vol_avg * 1.5  # Volume 50% acima da média
        high_volume = volumes[0] > vol_avg * 2.0  # Volume 100% acima da média

        # 4. VOLATILIDADE ADEQUADA
        current_range = highs[0] - lows[0]
        avg_range = sum([highs[i] - lows[i] for i in range(5, 15)]) / 10
        adequate_volatility = current_range > avg_range * 0.8
        high_volatility = current_range > avg_range * 1.5

        # 5. BREAKOUT REAL
        breakout_up = current > max(highs[1:6])  # Breakout acima dos últimos 5 highs
        breakout_down = current < min(lows[1:6])  # Breakout abaixo dos últimos 5 lows
        
        # 6. ATR ADEQUADO (não muito baixo, não muito alto)
        atr_ok = 40 <= self.current_atr <= 80  # ATR entre 40-80 pts
        
        # 7. POSIÇÃO EM RELAÇÃO A MÉDIAS
        sma_5 = sum(closes[0:5]) / 5
        sma_10 = sum(closes[0:10]) / 10
        above_sma_5 = current > sma_5
        above_sma_10 = current > sma_10

        # MOMENTUM THRESHOLDS ALTOS
        MOMENTUM_HIGH_BUY = 0.15   # 0.15% = $0.30 por lote
        MOMENTUM_HIGH_SELL = -0.15
        MOMENTUM_VERY_HIGH = 0.25  # 0.25% = $0.50 por lote

        # LOG DETALHADO
        print(f"   [CONS] ATR:{self.current_atr:.0f} | Mom15m:{momentum_15m:.3f}% | Trend:{'UP' if uptrend_strong else 'DOWN' if downtrend_strong else 'NEUTRAL'} | Vol:{vol_spike}")

        # === SINAIS DE BUY - 5 CONFIRMAÇÕES OBRIGATÓRIAS ===
        if self.use_buy:
            confirmations = 0
