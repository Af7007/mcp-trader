#!/usr/bin/env python3
"""
Teste real do sinal usando a função do agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.btc_hedge_agent import BTCHedgeAgent
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("="*80)
    logger.info("🧪 TESTE REAL DE SINAL - GOLD AGENT")
    logger.info("="*80)

    try:
        # Criar agent
        agent = BTCHedgeAgent(symbol='XAUUSDm')
        logger.info("\n✅ Agent criado")

        # Calcular indicadores
        indicators = agent.calculate_indicators()
        logger.info("\n✅ Indicadores calculados:")
        logger.info(f"   Preço: ${indicators.get('current_price', 0):.2f}")
        logger.info(f"   RSI: {indicators.get('rsi', 0):.1f}")
        logger.info(f"   MACD: {indicators.get('macd', 0):.4f}")
        logger.info(f"   MACD Histogram: {indicators.get('macd_histogram', 0):.4f}")
        logger.info(f"   Trend: {indicators.get('trend', 'N/A')}")
        logger.info(f"   ATR: {indicators.get('atr', 0):.2f}")
        logger.info(f"   BB Upper: ${indicators.get('bb_upper', 0):.2f}")
        logger.info(f"   BB Middle: ${indicators.get('bb_middle', 0):.2f}")

        # Analisar sinal usando função real do agent
        signal = agent.analyze_signal(indicators)

        logger.info(f"\n📊 RESULTADO:")
        logger.info(f"   {'='*60}")

        if signal == 'SELL':
            logger.info(f"   ✅✅✅ SINAL SELL GERADO ✅✅✅")
            logger.info(f"   Agent ABRIRÁ uma posição SELL agora!")
        elif signal == 'BUY':
            logger.info(f"   🔵 SINAL BUY (mas mode=SELL-ONLY, será rejeitado)")
        else:
            logger.info(f"   ❌ Sinal NEUTRAL (aguardando)")

        logger.info(f"   {'='*60}")

        # Verificar bloqueios
        positions = agent.mt5.positions_get(symbol=agent.symbol)
        if positions:
            logger.warning(f"\n⚠️  BLOQUEIO: Posições abertas ({len(positions)})")
        else:
            logger.info(f"\n✅ Nenhuma posição aberta")

        if agent.daily_trades >= agent.max_daily_trades:
            logger.warning(f"\n⚠️  BLOQUEIO: Limite diário atingido")
        else:
            logger.info(f"✅ Limite diário OK ({agent.daily_trades}/{agent.max_daily_trades})")

        logger.info(f"\n{'='*80}")

    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)

if __name__ == '__main__':
    main()
