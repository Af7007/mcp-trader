#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO BALANCEADA CORRIGIDA
Ajustando filtros para equilíbrio entre precisão e frequência
Com verificações de segurança para evitar erros de índice
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

# CONFIGURAÇÃO BALANCEADA
VOLUME = 0.02
WORKER_INTERVAL = 0.5

# GOLD SPECS
POINT_VALUE_PER_LOT = 1.0
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
print(f"GOLD LOSS ZERO - VERSÃO BALANCEADA CORRIGIDA")
print(f"{'='*70}\n")
print(f"CONFIGURAÇÃO OTIMIZADA:")
print(f"  Volume:           {VOLUME} lote")
print(f"  SL:               {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"CORREÇÕES APLICADAS:")
print(f"  ✓ Verificações de segurança para dados insuficientes")
print(f"  ✓ Momentum ajustado (0.05% → 0.04%)")
print(f"  ✓ Confirmações balanceadas (3 → 2+ volume)")
print(f"  ✓ Filtros de breakout mais flexíveis")
print(f"  ✓ Volume analysis mais permissivo")
print(f"  ✓ Tratamento robusto de erros")
print(f"\n{'='*70}\n")

input("Pressione ENTER para iniciar o agente GOLD BALANCEADO CORRIGIDO... ")

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

def _analyze_m5_trend_balanced_safe(self, rates) -> dict:
    """
    Análise BALANCEADA com verificações de segurança
    """
    try:
        # VERIFICAÇÃO DE DADOS SUFICIENTES
        if not rates or len(rates) < 5:  # Mínimo 5 candles para análise
            return None
            
        # Limitar análise ao número de dados disponíveis
        max_analysis = min(15, len(rates))
        
        # Extrair dados com verificações de segurança
        closes = [r['close'] for r in rates[:max_analysis]]
        highs = [r['high'] for r in rates[:max_analysis]]
        lows = [r['low'] for r in rates[:max_analysis]]
        volumes = [r['tick_volume'] for r in rates[:max_analysis]]

        current = closes[0]
        
        # Valores seguros para preços anteriores
        prev_1 = closes[1] if len(closes) > 1 else current
        prev_2 = closes[2] if len(closes) > 2 else current
        prev_5 = closes[min(5, len(closes)-1)]
        prev_10 = closes[min(10, len(closes)-1)]

        # Calcular ATR com dados disponíveis
        atr_len = min(14, len(rates)-1)
        if atr_len < 2:
            return None
        self.current_atr = self._calculate_atr_simple(rates[:atr_len])

        # Definir ranges seguros para análise
        trend_5_len = min(4, len(closes)-2)
        trend_10_len = min(9, len(closes)-2)
        vol_avg_len = min(10, len(volumes)-1)
        
        if trend_5_len < 1 or vol_avg_len < 1:
            return None

        # 1. TENDÊNCIA (verificações de segurança)
        uptrend_5 = sum(1 for i in range(trend_5_len) if closes[i] > closes[i+1]) >= max(1, trend_5_len // 2)
        uptrend_10 = sum(1 for i in range(min(trend_10_len, len(closes)-2)) if closes[i] > closes[i+1]) >= max(1, min(trend_10_len, len(closes)-2) // 2)
        
        downtrend_5 = sum(1 for i in range(trend_5_len) if closes[i] < closes[i+1]) >= max(1, trend_5_len // 2)
        downtrend_10 = sum(1 for i in range(min(trend_10_len, len(closes)-2)) if closes[i] < closes[i+1]) >= max(1, min(trend_10_len, len(closes)-2) // 2)

        # 2. MOMENTUM BALANCEADO
        momentum_5m = ((current - prev_5) / prev_5) * 100 if prev_5 != 0 else 0
        momentum_10m = ((current - prev_10) / prev_10) * 100 if prev_10 != 0 else 0

        # 3. VOLATILIDADE FLEXÍVEL com verificações
        if len(highs) < 2 or len(lows) < 2:
            return None
            
        last_range = highs[0] - lows[0]
        vol_ranges = [highs[i] - lows[i] for i in range(1, min(11, len(highs)))]
        
        if not vol_ranges:
            adequate_volatility = True  # Se não há dados suficientes, assumir volatilidade adequada
        else:
            avg_range = sum(vol_ranges) / len(vol_ranges)
            adequate_volatility = last_range > avg_range * 0.5 if avg_range > 0 else True

        # 4. VOLUME ANALYSIS FLEXÍVEL com verificações
        if len(volumes) < 2:
            volume_spike = True  # Se não há dados suficientes, assumir volume adequado
        else:
            vol_data = volumes[1:min(11, len(volumes))]
            if not vol_data:
                volume_spike = True
            else:
                avg_volume = sum(vol_data) / len(vol_data)
                volume_spike = volumes[0] > avg_volume * 1.1 if avg_volume > 0 else True
        high_volume = False  # Simplificado

        # 5. SUPORTE/RESISTÊNCIA FLEXÍVEL
        recent_high_len = min(5, len(highs))
        recent_low_len = min(5, len(lows))
        recent_high = max(highs[:recent_high_len])
        recent_low = min(lows[:recent_low_len])
        
        near_resistance = current > recent_high * 0.998
        near_support = current < recent_low * 1.002

        # 6. BREAKOUT FLEXÍVEL
        if len(highs) < 6 or len(lows) < 6:
            breakout_up = False
            breakout_down = False
        else:
            breakout_up = current > max(highs[1:6]) * 0.999
            breakout_down = current < min(lows[1:6]) * 1.001

        # MOMENTUM THRESHOLDS BALANCEADOS
        MOMENTUM_BUY = 0.04
        MOMENTUM_SELL = -0.04

        # LOG (reduzido para evitar spam)
        import random
        if random.random() < 0.05:  # 5% de chance de log
            print(f"   [M5-SAFE] Data: {len(rates)} candles | Vol: {volume_spike} | Trend: {'UP' if uptrend_5 and uptrend_10 else 'DOWN' if downtrend_5 and downtrend_10 else 'LATERAL'}")

        # === SINAIS DE BUY - 2 CONFIRMAÇÕES ===
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

            # SINAL se tiver 2 confirmações
            if confirmations >= 2:
                try:
                    if self._check_m15_trend("BUY"):
                        return {"type": "BUY", "price": current, "reason": "M5_M15_balanced_safe_buy"}
                except:
                    # Se falhar M15, ainda assim executar com filtro mínimo
                    if momentum_5m > MOMENTUM_BUY and (volume_spike or adequate_volatility):
                        return {"type": "BUY", "price": current, "reason": "M5_only_balanced_safe_buy"}

        # === SINAIS DE SELL - 2 CONFIRMAÇÕES ===
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

            # SINAL se tiver 2 confirmações
            if confirmations >= 2:
                try:
                    if self._check_m15_trend("SELL"):
                        return {"type": "SELL", "price": current, "reason": "M5_M15_balanced_safe_sell"}
                except:
                    # Se falhar M15, ainda assim executar com filtro mínimo
                    if momentum_5m < MOMENTUM_SELL and (volume_spike or adequate_volatility):
                        return {"type": "SELL", "price": current, "reason": "M5_only_balanced_safe_sell"}

        return None

    except Exception as e:
        # Log detalhado para debug
        print(f"   [ERRO] Dados: {len(rates) if rates else 0} candles | Erro: {e}")
        return None

# Aplicar método corrigido
agent._analyze_m5_trend = _analyze_m5_trend_balanced_safe.__get__(agent, GoldLossZeroSimple)

print(f"\n{'='*70}")
print(f"AGENTE GOLD BALANCEADO CORRIGIDO INICIADO!")
print(f"{'='*70}")
print(f"")
print(f"COMPORTAMENTO CORRIGIDO:")
print(f"  ✓ Verificações robustas de dados")
print(f"  ✓ 2 confirmações obrigatórias + 1 opcional")
print(f"  ✓ Momentum moderado (0.04%)")
print(f"  ✓ Volume flexível (1.1x)")
print(f"  ✓ Tratamento de erros aprimorado")
print(f"  ✓ Frequência aumentada, precisão mantida")
print(f"\nCTRL+C para parar")
print(f"{'='*70}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD BALANCEADO CORRIGIDO parado pelo usuário")
    if hasattr(agent, 'stop'):
        agent.stop()
