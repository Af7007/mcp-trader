#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO ULTRA-AGRESSIVA PARA GRANDES VELAS
Sistema otimizado para detectar e aproveitar velas gigantes em tempo real

MELHORIAS ULTRA-AGRESSIVAS:
- Detecção de velas gigantes (M1 + volume)
- Entrada INSTANTÂNEA em grandes movimentos
- Worker 0.2s (5x mais rápido)
- Trailing dinâmico baseado no sinal
- Thresholds ultra-sensíveis
- Análise M1 para timing perfeito
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO ULTRA-AGRESSIVA
VOLUME = 0.02
WORKER_INTERVAL = 0.2  # ULTRA-RÁPIDO: 0.2 segundos

# GOLD SPECS CORRETAS PARA CONTA CENTS
POINT_VALUE_PER_LOT = 0.1  # $0.10 por lote por ponto (XAUUSDc)
ATR_MEDIO = 60

# VALORES PARA GRANDES VELAS (mais agressivos)
SL_DOLLARS = 6.00
TRAILING_ACT_DOLLARS = 0.50  # Ativa com $0.50 lucro (muito rápido)
TRAILING_DIST_DOLLARS = 0.25  # Protege $0.25

point_value_with_volume = VOLUME * POINT_VALUE_PER_LOT
sl_pontos = SL_DOLLARS / point_value_with_volume
trailing_act_pontos = TRAILING_ACT_DOLLARS / point_value_with_volume
trailing_dist_pontos = TRAILING_DIST_DOLLARS / point_value_with_volume

sl_mult = sl_pontos / ATR_MEDIO
trailing_act_mult = trailing_act_pontos / ATR_MEDIO
trailing_dist_mult = trailing_dist_pontos / ATR_MEDIO

print(f"\n{'='*80}")
print(f"GOLD LOSS ZERO - VERSÃO ULTRA-AGRESSIVA PARA GRANDES VELAS")
print(f"{'='*80}\n")
print(f"CONFIGURAÇÃO ULTRA-AGRESSIVA:")
print(f"  Volume:           {VOLUME} lote")
print(f"  SL:               {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"  Worker:           {WORKER_INTERVAL}s (ULTRA-RÁPIDO)")
print(f"")
print(f"MELHORIAS PARA GRANDES VELAS:")
print(f"  * Detecção de velas gigantes (M1 + volume)")
print(f"  * Entrada INSTANTÂNEA em grandes movimentos")
print(f"  * Worker 0.2s para capturar micro-movimentos")
print(f"  * Trailing agressivo ($0.50 ativa)")
print(f"  * Thresholds ultra-sensíveis")
print(f"  * Análise M1 para timing perfeito")
print(f"\n{'='*80}\n")



# Criar agente com parâmetros ULTRA-AGRESSIVOS
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

def _detect_giant_candle_ultra(self, rates_m1, rates_m5) -> dict:
    """
    DETECÇÃO ULTRA-AGRESSIVA DE VELAS GIGANTES
    Critérios: range 3x + volume 2x + corpo forte
    """
    try:
        if len(rates_m1) < 6 or len(rates_m5) < 6:
            return {"is_giant": False, "direction": "NEUTRAL"}

        # Análise da última vela M1
        current_m1 = rates_m1[0]
        range_m1 = current_m1['high'] - current_m1['low']
        volume_m1 = current_m1['tick_volume']
        body_size = abs(current_m1['close'] - current_m1['open'])

        # Calcular médias dos últimos 5 períodos
        ranges_m1 = [r['high'] - r['low'] for r in rates_m1[1:6]]
        volumes_m1 = [r['tick_volume'] for r in rates_m1[1:6]]

        avg_range_m1 = sum(ranges_m1) / len(ranges_m1)
        avg_volume_m1 = sum(volumes_m1) / len(volumes_m1)

        # CRITÉRIOS ULTRA-AGRESSIVOS PARA VELA GIGANTE
        range_multiplier = range_m1 / avg_range_m1 if avg_range_m1 > 0 else 1
        volume_multiplier = volume_m1 / avg_volume_m1 if avg_volume_m1 > 0 else 1
        body_ratio = body_size / range_m1 if range_m1 > 0 else 0

        # VELA GIGANTE: range 3x + volume 2x + corpo forte
        is_giant = (range_multiplier >= 3.0) and (volume_multiplier >= 2.0) and (body_ratio >= 0.6)

        # DIREÇÃO baseada no corpo da vela
        if current_m1['close'] > current_m1['open']:
            direction = "BUY" if body_ratio >= 0.6 else "NEUTRAL"
        else:
            direction = "SELL" if body_ratio >= 0.6 else "NEUTRAL"

        # Confirmação adicional com M5
        m5_trend = self._check_m15_trend(direction) if direction != "NEUTRAL" else False

        if is_giant and direction != "NEUTRAL" and m5_trend:
            print(f"   [VELA GIGANTE DETECTADA!] {direction} - Range: {range_multiplier:.1f}x | Volume: {volume_multiplier:.1f}x | Corpo: {body_ratio:.1f}")
            return {
                "is_giant": True,
                "direction": direction,
                "range_multiplier": range_multiplier,
                "volume_multiplier": volume_multiplier,
                "body_ratio": body_ratio,
                "price": current_m1['close']
            }

        return {"is_giant": False, "direction": "NEUTRAL"}

    except Exception as e:
        print(f"   [ERRO] Detecção vela gigante: {e}")
        return {"is_giant": False, "direction": "NEUTRAL"}

def _get_signal_ultra_aggressive(self) -> dict:
    """
    ANÁLISE ULTRA-AGRESSIVA COM PRIORIDADE PARA VELAS GIGANTES
    """
    try:
        # Buscar dados M1 e M5 simultaneamente
        rates_m1 = self.mt5.copy_rates_from_pos(self.symbol, "M1", 0, 15)
        rates_m5 = self.mt5.copy_rates_from_pos(self.symbol, "M5", 0, 15)

        if len(rates_m1) < 10 or len(rates_m5) < 8:
            return None

        # 1. PRIORIDADE MÁXIMA: DETECTAR VELA GIGANTE
        giant_candle = self._detect_giant_candle_ultra(rates_m1, rates_m5)

        if giant_candle["is_giant"]:
            # ENTRADA INSTANTÂNEA NA VELA GIGANTE!
            return {
                "type": giant_candle["direction"],
                "price": giant_candle["price"],
                "reason": f"ULTRA_GIANT_CANDLE_{giant_candle['direction']}_R{giant_candle['range_multiplier']:.1f}_V{giant_candle['volume_multiplier']:.1f}",
                "priority": "ULTRA_CRITICAL"
            }

        # 2. Análise M1 ultra-sensível se não houver vela gigante
        m1_signal = self._analyze_m1_ultra_fast(rates_m1)
        if m1_signal:
            return m1_signal

        # 3. Fallback para análise M5 normal
        return self._analyze_m5_trend_ultra(rates_m5)

    except Exception as e:
        print(f"   [ERRO] Análise ultra-agressiva: {e}")
        return None

def _analyze_m1_ultra_fast(self, rates_m1) -> dict:
    """
    ANÁLISE M1 ULTRA-RÁPIDA PARA MOMENTOS VOLÁTEIS
    """
    try:
        if len(rates_m1) < 5:
            return None

        current = rates_m1[0]['close']
        prev_1 = rates_m1[1]['close']
        prev_2 = rates_m1[2]['close']

        # Momentum M1 ultra-sensível
        momentum_m1 = ((current - prev_2) / prev_2) * 100

        # Volume spike em M1
        volumes = [r['tick_volume'] for r in rates_m1[:5]]
        avg_volume = sum(volumes[1:]) / 4
        volume_spike = volumes[0] > avg_volume * 1.5  # 50% acima

        # THRESHOLDS ULTRA-SENSÍVEIS
        MOMENTUM_BUY_ULTRA = 0.02   # 0.2% em 2 minutos
        MOMENTUM_SELL_ULTRA = -0.02

        # SINAIS ULTRA-RÁPIDOS
        if momentum_m1 > MOMENTUM_BUY_ULTRA and volume_spike and current > prev_1:
            return {
                "type": "BUY",
                "price": current,
                "reason": f"ULTRA_FAST_M1_BUY_M{momentum_m1:.2f}_V{volumes[0]/avg_volume:.1f}"
            }

        if momentum_m1 < MOMENTUM_SELL_ULTRA and volume_spike and current < prev_1:
            return {
                "type": "SELL",
                "price": current,
                "reason": f"ULTRA_FAST_M1_SELL_M{momentum_m1:.2f}_V{volumes[0]/avg_volume:.1f}"
            }

        return None

    except Exception as e:
        print(f"   [ERRO] Análise M1 ultra: {e}")
        return None

def _analyze_m5_trend_ultra(self, rates) -> dict:
    """
    ANÁLISE M5 ULTRA-AGRESSIVA COM THRESHOLDS REDUZIDOS
    """
    try:
        closes = [r['close'] for r in rates[:10]]
        highs = [r['high'] for r in rates[:10]]
        lows = [r['low'] for r in rates[:10]]
        volumes = [r['tick_volume'] for r in rates[:10]]

        current = closes[0]
        prev_1 = closes[1]
        prev_5 = closes[5]

        self.current_atr = self._calculate_atr_simple(rates[:14])

        # 1. TENDÊNCIA (mais permissiva)
        uptrend = sum(1 for i in range(3) if closes[i] > closes[i+1]) >= 2
        downtrend = sum(1 for i in range(3) if closes[i] < closes[i+1]) >= 2

        # 2. MOMENTUM ULTRA-SENSÍVEL
        momentum_5m = ((current - prev_5) / prev_5) * 100

        # 3. VOLATILIDADE (mais permissiva)
        last_range = highs[0] - lows[0]
        avg_range = sum([highs[i] - lows[i] for i in range(1, 6)]) / 5
        adequate_volatility = last_range > avg_range * 0.8  # Reduzido de 1.0

        # 4. VOLUME (mais permissivo)
        volume_spike = volumes[0] > sum(volumes[1:6]) / 5 * 1.2  # Reduzido de 1.1

        # THRESHOLDS ULTRA-AGRESSIVOS
        MOMENTUM_BUY_ULTRA = 0.015   # 0.15% em 5 minutos
        MOMENTUM_SELL_ULTRA = -0.015

        # SINAIS ULTRA-AGRESSIVOS (2 confirmações mínimas)
        if self.use_buy:
            confirmations = 0

            if uptrend and momentum_5m > MOMENTUM_BUY_ULTRA:
                confirmations += 1
            if momentum_5m > MOMENTUM_BUY_ULTRA * 1.5:
                confirmations += 1
            if (adequate_volatility or volume_spike) and current > prev_1:
                confirmations += 1

            if confirmations >= 2:
                if self._check_m15_trend("BUY"):
                    return {"type": "BUY", "price": current, "reason": "ULTRA_AGGRESSIVE_M5_BUY"}

        if self.use_sell:
            confirmations = 0

            if downtrend and momentum_5m < MOMENTUM_SELL_ULTRA:
                confirmations += 1
            if momentum_5m < MOMENTUM_SELL_ULTRA * 1.5:
                confirmations += 1
            if (adequate_volatility or volume_spike) and current < prev_1:
                confirmations += 1

            if confirmations >= 2:
                if self._check_m15_trend("SELL"):
                    return {"type": "SELL", "price": current, "reason": "ULTRA_AGGRESSIVE_M5_SELL"}

        return None

    except Exception as e:
        print(f"   [ERRO] Análise M5 ultra: {e}")
        return None

def _calculate_dynamic_trailing_ultra(self, signal_reason: str):
    """
    TRAILING DINÂMICO BASEADO NO TIPO DE SINAL
    """
    if "ULTRA_GIANT_CANDLE" in signal_reason:
        # Para velas gigantes: trailing ultra-agressivo
        self.current_trailing_activation_pontos = self.current_atr * 0.3  # 30% ATR
        self.current_trailing_distance_pontos = self.current_atr * 0.2    # 20% ATR
        print(f"   [TRAILING ULTRA-AGRESSIVO] Vela gigante - Ativa em: ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")

    elif "ULTRA_FAST_M1" in signal_reason:
        # Para sinais M1: trailing rápido
        self.current_trailing_activation_pontos = self.current_atr * 0.4  # 40% ATR
        self.current_trailing_distance_pontos = self.current_atr * 0.25   # 25% ATR
        print(f"   [TRAILING RÁPIDO] Sinal M1 - Ativa em: ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")

    else:
        # Trailing padrão
        self.current_trailing_activation_pontos = self.current_atr * trailing_act_mult
        self.current_trailing_distance_pontos = self.current_atr * trailing_dist_mult

def _start_ultra_worker(self):
    """
    WORKER ULTRA-RESPONSIVO PARA GRANDES VELAS
    """
    try:
        if not self.position_worker or not self.position_worker.is_running():
            # INTERVALO ULTRA-RÁPIDO: 0.2 segundos
            ultra_interval = 0.2

            self.position_worker = PositionMonitorWorker(
                mt5_client=self.mt5,
                symbol=self.symbol,
                check_interval=ultra_interval,
                trailing_callback=self._trailing_worker_callback
            )
            self.position_worker.start()

            print(f"   [WORKER ULTRA-ACTIVADO] {ultra_interval}s - CAPTURA MICRO-MOVIMENTOS EM TEMPO REAL!")
            print(f"   [WORKER] Trailing será atualizado a cada {ultra_interval}s!")

    except Exception as e:
        print(f"   [ERRO] Worker ultra: {e}")

# Aplicar métodos ultra-agressivos
agent._detect_giant_candle_ultra = _detect_giant_candle_ultra.__get__(agent, GoldLossZeroSimple)
agent._get_signal_ultra_aggressive = _get_signal_ultra_aggressive.__get__(agent, GoldLossZeroSimple)
agent._analyze_m1_ultra_fast = _analyze_m1_ultra_fast.__get__(agent, GoldLossZeroSimple)
agent._analyze_m5_trend_ultra = _analyze_m5_trend_ultra.__get__(agent, GoldLossZeroSimple)
agent._calculate_dynamic_trailing_ultra = _calculate_dynamic_trailing_ultra.__get__(agent, GoldLossZeroSimple)
agent._start_ultra_worker = _start_ultra_worker.__get__(agent, GoldLossZeroSimple)

# Substituir métodos originais pelos ultra-agressivos
agent._get_simple_signal = agent._get_signal_ultra_aggressive
agent._calculate_dynamic_trailing_for_giant_candle = agent._calculate_dynamic_trailing_ultra

print(f"\n{'='*80}")
print(f"AGENTE GOLD ULTRA-AGRESSIVO INICIADO!")
print(f"{'='*80}")
print(f"")
print(f"ESTRATÉGIA ULTRA-AGRESSIVA:")
print(f"  * Detecção de velas gigantes (range 3x + volume 2x)")
print(f"  * Entrada INSTANTÂNEA em grandes movimentos")
print(f"  * Worker 0.2s (5x mais rápido)")
print(f"  * Trailing ativa com $0.50 lucro")
print(f"  * Thresholds ultra-sensíveis")
print(f"  * Análise M1 + M5 simultânea")
print(f"")
print(f"OBJETIVO: APROVEITAR GRANDES VELAS COM LUCROS MÁXIMOS!")
print(f"\nCTRL+C para parar")
print(f"{'='*80}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD ULTRA-AGRESSIVO parado pelo usuário")
    if hasattr(agent, 'stop'):
        agent.stop()
