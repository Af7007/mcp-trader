#!/usr/bin/env python3
"""
Teste para verificar indicadores atuais do Gold e se está gerando sinais
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.mt5_mcp_client import get_mt5_client
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_indicators(mt5_client, symbol, timeframe='M15'):
    """Calcula os indicadores para Gold"""

    # Obter dados de OHLC
    candles = mt5_client.get_candles(
        symbol=symbol,
        timeframe=timeframe,
        count=50
    )

    if not candles:
        logger.error(f"❌ Não conseguiu obter candles para {symbol}")
        return None

    closes = [c['close'] for c in candles]
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]
    current_price = closes[-1]

    # RSI (14 períodos)
    def calculate_rsi(closes, period=14):
        if len(closes) < period + 1:
            return 50

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        seed = deltas[:period]
        up = sum([x for x in seed if x > 0])
        down = sum([-x for x in seed if x < 0])
        rs = up / down if down != 0 else 100
        rsi = 100 - (100 / (1 + rs)) if rs else 50

        for i in range(period, len(deltas)):
            delta = deltas[i]
            if delta > 0:
                up = (up * (period - 1) + delta) / period
                down = down * (period - 1) / period
            else:
                up = up * (period - 1) / period
                down = (down * (period - 1) - delta) / period

            rs = up / down if down != 0 else 100
            rsi = 100 - (100 / (1 + rs)) if rs else 50

        return rsi

    # MACD (12, 26, 9)
    def calculate_macd(closes):
        if len(closes) < 26:
            return 0, 0, 0

        ema12 = closes[-1]
        ema26 = closes[-1]

        for i in range(len(closes) - 2, -1, -1):
            ema12 = closes[i] * (2 / 13) + ema12 * (11 / 13)
            ema26 = closes[i] * (2 / 27) + ema26 * (25 / 27)

        macd = ema12 - ema26
        signal = macd * 0.5
        histogram = macd - signal

        return macd, signal, histogram

    # Bollinger Bands (20, 2)
    def calculate_bb(closes, period=20, std_dev=2):
        if len(closes) < period:
            return current_price, current_price, current_price

        sma = sum(closes[-period:]) / period
        variance = sum((x - sma) ** 2 for x in closes[-period:]) / period
        std = variance ** 0.5

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)

        return upper, sma, lower

    # Calcular
    rsi = calculate_rsi(closes)
    macd, macd_signal, macd_histogram = calculate_macd(closes)
    bb_upper, bb_middle, bb_lower = calculate_bb(closes)

    # Trend simples
    sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
    if current_price > sma20:
        trend = 'UP'
    else:
        trend = 'DOWN'

    return {
        'current_price': current_price,
        'rsi': rsi,
        'macd': macd,
        'macd_histogram': macd_histogram,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'trend': trend,
        'sma20': sma20
    }

def analyze_gold_signal(indicators):
    """Analisa sinal SELL para Gold (cópia da lógica do agent)"""

    rsi = indicators['rsi']
    macd_histogram = indicators['macd_histogram']
    current_price = indicators['current_price']
    bb_upper = indicators['bb_upper']
    trend = indicators['trend']

    sell_signals = 0
    details = []

    # RSI
    if rsi > 70:
        sell_signals += 3
        details.append(f"✅ RSI > 70 ({rsi:.1f}) = +3 sinais (super overbought)")
    elif rsi > 65:
        sell_signals += 2
        details.append(f"✅ RSI > 65 ({rsi:.1f}) = +2 sinais (overbought)")
    elif rsi > 55:
        sell_signals += 1
        details.append(f"⚠️  RSI > 55 ({rsi:.1f}) = +1 sinal (leve)")
    else:
        details.append(f"❌ RSI {rsi:.1f} = 0 sinais (não overbought)")

    # MACD Histogram
    if macd_histogram < -0.05:
        sell_signals += 2
        details.append(f"✅ MACD histogram < -0.05 ({macd_histogram:.4f}) = +2 sinais")
    elif macd_histogram < 0:
        sell_signals += 1
        details.append(f"⚠️  MACD histogram < 0 ({macd_histogram:.4f}) = +1 sinal")
    else:
        details.append(f"❌ MACD histogram {macd_histogram:.4f} = 0 sinais")

    # Bollinger Bands
    if current_price > bb_upper:
        sell_signals += 2
        details.append(f"✅ Preço ({current_price:.2f}) > BB Upper ({bb_upper:.2f}) = +2 sinais")
    else:
        details.append(f"❌ Preço ({current_price:.2f}) ≤ BB Upper ({bb_upper:.2f}) = 0 sinais")

    # Trend
    if trend == 'DOWN':
        sell_signals += 2
        details.append(f"✅ Trend DOWN = +2 sinais")
    else:
        details.append(f"❌ Trend {trend} = 0 sinais")

    return sell_signals, details

def main():
    """Teste principal"""
    try:
        # Conectar ao MT5
        mt5_client = get_mt5_client()

        logger.info("=" * 80)
        logger.info("🔍 TESTE DE SINAIS GOLD (XAUUSDm)")
        logger.info("=" * 80)

        # Verificar símbolo
        symbol_info = mt5_client.get_symbol_info('XAUUSDm')
        if not symbol_info:
            logger.error("❌ Símbolo XAUUSDm não encontrado. Tentando XAUUSDc...")
            symbol_info = mt5_client.get_symbol_info('XAUUSDc')
            symbol = 'XAUUSDc'
        else:
            symbol = 'XAUUSDm'

        logger.info(f"✅ Símbolo encontrado: {symbol}")

        # Calcular indicadores
        logger.info("\n📊 Calculando indicadores...")
        indicators = calculate_indicators(mt5_client, symbol, 'M15')

        if not indicators:
            logger.error("❌ Não conseguiu calcular indicadores")
            return

        # Mostrar indicadores
        logger.info(f"\n📈 INDICADORES ATUAIS:")
        logger.info(f"   Preço: ${indicators['current_price']:.2f}")
        logger.info(f"   RSI(14): {indicators['rsi']:.1f}")
        logger.info(f"   MACD: {indicators['macd']:.4f}")
        logger.info(f"   MACD Histogram: {indicators['macd_histogram']:.4f}")
        logger.info(f"   BB Upper: ${indicators['bb_upper']:.2f}")
        logger.info(f"   BB Middle: ${indicators['bb_middle']:.2f}")
        logger.info(f"   BB Lower: ${indicators['bb_lower']:.2f}")
        logger.info(f"   SMA20: ${indicators['sma20']:.2f}")
        logger.info(f"   Trend: {indicators['trend']}")

        # Analisar sinal
        logger.info(f"\n🔍 ANÁLISE DE SINAL SELL (modo SELL-ONLY):")
        sell_signals, details = analyze_gold_signal(indicators)

        for detail in details:
            logger.info(f"   {detail}")

        logger.info(f"\n{'='*80}")
        logger.info(f"📊 TOTAL DE SINAIS SELL: {sell_signals}/3")

        if sell_signals >= 3:
            logger.info(f"✅ SINAL GERADO: SELL ✅")
            logger.info(f"   Agent vai abrir uma posição SELL!")
        else:
            logger.info(f"❌ SINAL NÃO ATINGIU LIMITE")
            logger.info(f"   Agent está esperando mais sinais (precisa de {3 - sell_signals} a mais)")
            logger.info(f"\n💡 SUGESTÕES:")

            if indicators['rsi'] < 55:
                logger.info(f"   1. RSI muito baixo ({indicators['rsi']:.1f}) - Esperar aumento")

            if indicators['macd_histogram'] >= -0.05:
                logger.info(f"   2. MACD histogram não tão negativo ({indicators['macd_histogram']:.4f}) - Esperar queda")

            if indicators['current_price'] <= indicators['bb_upper']:
                logger.info(f"   3. Preço não está no topo da banda - Esperar aproximação")

            logger.info(f"\n⚡ SOLUÇÃO RÁPIDA:")
            logger.info(f"   Para ver sinais com mais frequência, podemos:")
            logger.info(f"   A) Relaxar requisitos (ex: sell_signals >= 2)")
            logger.info(f"   B) Usar timeframe menor (ex: M5 em vez de M15)")
            logger.info(f"   C) Ajustar indicadores (ex: RSI > 65 em vez de > 70)")

        logger.info(f"{'='*80}")

    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)

if __name__ == '__main__':
    main()
