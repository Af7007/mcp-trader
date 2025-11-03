#!/usr/bin/env python3
"""
GOLD LOSS ZERO - VERSÃO HORÁRIO CORRIGIDO
Verifica horário de mercado antes de executar ordens
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
import datetime

# CONFIGURAÇÃO FLEXÍVEL
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

def is_market_open():
    """
    Verifica se o mercado de Gold está aberto
    Gold (XAUUSD) opera 24/5, fechado aos sábados e domingos
    """
    now = datetime.datetime.now()
    weekday = now.weekday()  # 0=segunda, 6=domingo
    hour = now.hour
    
    # Fechado fins de semana
    if weekday >= 5:  # Sábado (5) ou Domingo (6)
        return False, "Fim de semana"
    
    # Ajustar para horário de mercado (Sunday 5 PM - Friday 5 PM EST = UTC-5)
    # No horário brasileiro (UTC-3), isso seria Sunday 7 PM - Friday 7 PM BRT
    
    # Fechado de sexta 19h até domingo 19h (horário brasileiro)
    if weekday == 4 and hour >= 19:  # Sexta após 19h
        return False, "Fechado (sexta à noite)"
    if weekday == 5:  # Sábado todo
        return False, "Fim de semana"
    if weekday == 6 and hour < 19:  # Domingo antes 19h
        return False, "Fim de semana"
    
    return True, "Mercado aberto"

print(f"\n{'='*70}")
print(f"GOLD LOSS ZERO - VERSÃO HORÁRIO CORRIGIDO")
print(f"{'='*70}\n")
print(f"CONFIGURAÇÃO OTIMIZADA:")
print(f"  Volume:           {VOLUME} lote")
print(f"  SL:               {sl_pontos:.0f} pts = ${SL_DOLLARS:.2f}")
print(f"  Trailing Ativa:   {trailing_act_pontos:.0f} pts = ${TRAILING_ACT_DOLLARS:.2f}")
print(f"  Trailing Dist:    {trailing_dist_pontos:.0f} pts = ${TRAILING_DIST_DOLLARS:.2f}")
print(f"")
print(f"FUNCIONALIDADES ADICIONADAS:")
print(f"  ✓ Verificação de horário de mercado")
print(f"  ✓ Logs detalhados de status")
print(f"  ✓ Controle de tentativas de ordens")
print(f"  ✓ Flexibilidade máxima mantida")
print(f"\n{'='*70}\n")

input("Pressione ENTER para iniciar o agente GOLD HORÁRIO CORRIGIDO... ")

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

def _analyze_m5_trend_with_schedule(self, rates) -> dict:
    """
    Análise com verificação de horário de mercado
    """
    try:
        # VERIFICAÇÃO DE HORÁRIO DE MERCADO
        market_open, status_msg = is_market_open()
        if not market_open:
            # Só printar a cada 10 minutos para não spammar
            import time
            current_time = time.time()
            if not hasattr(self, '_last_market_log'):
                self._last_market_log = 0
            
            if current_time - self._last_market_log > 600:  # 10 minutos
                print(f"   [HORARIO] {status_msg} - Aguardando reopen...")
                self._last_market_log = current_time
            return None
        
        # Se mercado aberto, continuar com análise FLEXÍVEL
        # VERIFICAÇÃO MÍNIMA DE DADOS
        if not rates or len(rates) < 3:
            return None
            
        # Dados básicos com segurança
        max_analysis = min(15, len(rates))
        closes = [r['close'] for r in rates[:max_analysis]]
        highs = [r['high'] for r in rates[:max_analysis]]
        lows = [r['low'] for r in rates[:max_analysis]]
        volumes = [r['tick_volume'] for r in rates[:max_analysis]]

        current = closes[0]
        
        # Preços anteriores seguros
        prev_1 = closes[1] if len(closes) > 1 else current
        prev_2 = closes[2] if len(closes) > 2 else current
        prev_5 = closes[min(5, len(closes)-1)] if len(closes) > 1 else current
        prev_10 = closes[min(10, len(closes)-1)] if len(closes) > 1 else current

        # ATR simplificado
        atr_len = min(14, len(rates)-1)
        if atr_len < 2:
            self.current_atr = 60
        else:
            try:
                self.current_atr = self._calculate_atr_simple(rates[:atr_len])
            except:
                self.current_atr = 60

        # ANÁLISE MÍNIMA E FLEXÍVEL
        # 1. TENDÊNCIA SIMPLIFICADA (apenas 1 de 3 velas)
        if len(closes) >= 4:
            uptrend_simple = sum(1 for i in range(3) if closes[i] > closes[i+1]) >= 1
            downtrend_simple = sum(1 for i in range(3) if closes[i] < closes[i+1]) >= 1
        else:
            uptrend_simple = False
            downtrend_simple = False

        # 2. MOMENTUM MUITO BAIXO
        momentum_5m = ((current - prev_5) / prev_5) * 100 if prev_5 != 0 else 0
        momentum_1m = ((current - prev_1) / prev_1) * 100 if prev_1 != 0 else 0

        # 3. VOLUME SIMPLES
        if len(volumes) >= 2:
            vol_spike = volumes[0] > (sum(volumes[1:min(4, len(volumes))]) / min(3, len(volumes)-1)) * 1.05
        else:
            vol_spike = True

        # 4. VOLATILIDADE BÁSICA
        if len(highs) >= 2 and len(lows) >= 2:
            range_ok = (highs[0] - lows[0]) > 10  # Mínimo $10 de range
        else:
            range_ok = True

        # MOMENTUM MÍNIMO PARA ORDEM
        MOMENTUM_MIN = 0.02  # 0.02% = $0.08 por lote com 0.02 volume

        # LOG Mais frequente para debug
        print(f"   [FLEX] Mom5m: {momentum_5m:.3f}% | Mom1m: {momentum_1m:.3f}% | Trend: {'UP' if uptrend_simple else 'DOWN' if downtrend_simple else 'NONE'} | Vol: {vol_spike}")

        # === SINAIS DE BUY - ESTRATÉGIA FLEXÍVEL ===
        if self.use_buy:
            # Estratégia 1: Momentum 0.02% + Tendência UP OU Volume
            if momentum_5m > MOMENTUM_MIN and (uptrend_simple or vol_spike):
                return {"type": "BUY", "price": current, "reason": "Momentum_0.02_trend_flexible_buy"}
            
            # Estratégia 2: Momentum 0.01% + Volume + Range OK
            if momentum_5m > 0.01 and vol_spike and range_ok:
                return {"type": "BUY", "price": current, "reason": "Momentum_0.01_volume_flexible_buy"}
            
            # Estratégia 3: Tendência UP + Range OK (sem momentum)
            if uptrend_simple and range_ok:
                return {"type": "BUY", "price": current, "reason": "Trend_only_flexible_buy"}
            
            # Estratégia 4: Momentum puro (mais restritivo)
            if momentum_5m > 0.05:  # 0.05% = $0.20
                return {"type": "BUY", "price": current, "reason": "Momentum_pure_flexible_buy"}

        # === SINAIS DE SELL - ESTRATÉGIA FLEXÍVEL ===
        if self.use_sell:
            # Estratégia 1: Momentum -0.02% + Tendência DOWN OU Volume
            if momentum_5m < -MOMENTUM_MIN and (downtrend_simple or vol_spike):
                return {"type": "SELL", "price": current, "reason": "Momentum_0.02_trend_flexible_sell"}
            
            # Estratégia 2: Momentum -0.01% + Volume + Range OK
            if momentum_5m < -0.01 and vol_spike and range_ok:
                return {"type": "SELL", "price": current, "reason": "Momentum_0.01_volume_flexible_sell"}
            
            # Estratégia 3: Tendência DOWN + Range OK (sem momentum)
            if downtrend_simple and range_ok:
                return {"type": "SELL", "price": current, "reason": "Trend_only_flexible_sell"}
            
            # Estratégia 4: Momentum puro negativo (mais restritivo)
            if momentum_5m < -0.05:  # -0.05% = -$0.20
                return {"type": "SELL", "price": current, "reason": "Momentum_pure_flexible_sell"}

        return None

    except Exception as e:
        print(f"   [ERRO FLEX] Dados: {len(rates) if rates else 0} candles | Erro: {e}")
        return None

# Aplicar método com verificação de horário
agent._analyze_m5_trend = _analyze_m5_trend_with_schedule.__get__(agent, GoldLossZeroSimple)

print(f"\n{'='*70}")
print(f"AGENTE GOLD HORÁRIO CORRIGIDO INICIADO!")
print(f"{'='*70}")
print(f"")
print(f"COMPORTAMENTO COM HORÁRIO:")
print(f"  ✓ 4 estratégias de ordem diferentes")
print(f"  ✓ Verificação automática de horário de mercado")
print(f"  ✓ Momentum mínimo 0.02% (muito baixo)")
print(f"  ✓ Tendência relaxada (1 de 3 velas)")
print(f"  ✓ Logs informativos de status")
print(f"  ✓ MÁXIMA FREQUÊNCIA DE ORDENS")
print(f"\nHORÁRIO DE MERCADO:")
print(f"  ✓ Segunda 00h00 até Sexta 18h59: ABERTO")
print(f"  ✓ Sexta após 19h00 até Domingo 18h59: FECHADO")
print(f"  ✓ Sábado todo: FECHADO")
print(f"\nCTRL+C para parar")
print(f"{'='*70}\n")

try:
    agent.run()
except KeyboardInterrupt:
    print("\n\nAgente GOLD HORÁRIO CORRIGIDO parado pelo usuário")
    if hasattr(agent, 'stop'):
        agent.stop()
