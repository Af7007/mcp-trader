#!/usr/bin/env python3
"""
Teste diagnóstico completo do Gold Agent
Verifica: Conexão, indicadores, sinais, bloqueios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tentar importar o agent
try:
    from src.agents.btc_hedge_agent import BTCHedgeAgent
    logger.info("✅ Agent importado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao importar agent: {e}")
    sys.exit(1)

def test_connection():
    """Testa conexão com MT5"""
    logger.info("\n" + "="*80)
    logger.info("1️⃣  TESTE DE CONEXÃO MT5")
    logger.info("="*80)

    try:
        agent = BTCHedgeAgent(symbol='XAUUSDm')
        logger.info("✅ Agente criado com sucesso")
        logger.info(f"   Symbol: {agent.symbol}")
        logger.info(f"   Volume: {agent.volume}")
        logger.info(f"   Target Profit: ${agent.target_profit}")
        logger.info(f"   Mode: SELL-ONLY" if agent.only_sell else "   Mode: BUY/SELL")
        return agent
    except Exception as e:
        logger.error(f"❌ Erro ao criar agente: {e}")
        return None

def test_indicators(agent):
    """Testa cálculo de indicadores"""
    logger.info("\n" + "="*80)
    logger.info("2️⃣  TESTE DE INDICADORES")
    logger.info("="*80)

    try:
        indicators = agent.calculate_indicators()

        if not indicators:
            logger.error("❌ Não conseguiu calcular indicadores")
            return None

        logger.info("✅ Indicadores calculados com sucesso:")
        logger.info(f"   Preço: ${indicators.get('current_price', 0):.2f}")
        logger.info(f"   RSI: {indicators.get('rsi', 0):.1f}")
        logger.info(f"   MACD: {indicators.get('macd', 0):.4f}")
        logger.info(f"   MACD Histogram: {indicators.get('macd_histogram', 0):.4f}")
        logger.info(f"   Trend: {indicators.get('trend', 'N/A')}")
        logger.info(f"   ATR: {indicators.get('atr', 0):.2f}")
        logger.info(f"   BB Upper: ${indicators.get('bb_upper', 0):.2f}")
        logger.info(f"   BB Middle: ${indicators.get('bb_middle', 0):.2f}")
        logger.info(f"   BB Lower: ${indicators.get('bb_lower', 0):.2f}")
        logger.info(f"   SMA20: ${indicators.get('sma_20', 0):.2f}")
        logger.info(f"   SMA50: ${indicators.get('sma_50', 0):.2f}")

        return indicators
    except Exception as e:
        logger.error(f"❌ Erro ao calcular indicadores: {e}")
        return None

def analyze_signal(indicators):
    """Analisa se há sinal SELL baseado nos indicadores"""
    logger.info("\n" + "="*80)
    logger.info("3️⃣  ANÁLISE DE SINAL SELL (3+ sinais necessários)")
    logger.info("="*80)

    if not indicators:
        logger.error("❌ Sem indicadores para análise")
        return None

    rsi = indicators.get('rsi', 50)
    macd_histogram = indicators.get('macd_histogram', 0)
    current_price = indicators.get('current_price', 0)
    bb_upper = indicators.get('bb_upper', 0)
    trend = indicators.get('trend', 'NEUTRAL')

    sell_signals = 0
    details = []

    # RSI - mais exigente para SELL em Gold
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
    if macd_histogram is not None:
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

    # Mostrar detalhes
    for detail in details:
        logger.info(f"   {detail}")

    logger.info(f"\n   📊 TOTAL: {sell_signals} sinais (precisa de 3)")

    if sell_signals >= 3:
        logger.info(f"   ✅ SINAL GERADO: SELL ✅")
        return 'SELL'
    else:
        logger.info(f"   ❌ Sinal insuficiente ({3 - sell_signals} faltando)")
        return 'NEUTRAL'

def check_blockers(agent):
    """Verifica se há bloqueios para abrir posições"""
    logger.info("\n" + "="*80)
    logger.info("4️⃣  VERIFICAÇÃO DE BLOQUEIOS")
    logger.info("="*80)

    blockers = []

    try:
        # 1. Verificar posições abertas
        positions = agent.mt5.positions_get(symbol=agent.symbol)
        if positions:
            logger.warning(f"⚠️  Posições abertas: {len(positions)}")
            for pos in positions:
                logger.warning(f"   - Ticket {pos.get('ticket')}: {pos.get('type')} Volume {pos.get('volume')}")
            blockers.append(f"Posições abertas: {len(positions)}")
        else:
            logger.info("✅ Nenhuma posição aberta")

        # 2. Verificar limite diário
        if agent.daily_trades >= agent.max_daily_trades:
            logger.warning(f"⚠️  Limite diário atingido: {agent.daily_trades}/{agent.max_daily_trades}")
            blockers.append(f"Limite diário: {agent.daily_trades}/{agent.max_daily_trades}")
        else:
            logger.info(f"✅ Limite diário OK: {agent.daily_trades}/{agent.max_daily_trades}")

        # 3. Verificar hedge
        if agent.hedge_active:
            logger.warning(f"⚠️  Hedge ativo")
            blockers.append("Hedge ativo (mas deveria estar desativado!)")
        else:
            logger.info("✅ Hedge desativado (correto)")

        # 4. Verificar account info
        account_info = agent.mt5.get_account_info()
        if account_info:
            balance = account_info.get('balance', 0)
            margin_free = account_info.get('margin_free', 0)
            logger.info(f"✅ Conta conectada:")
            logger.info(f"   Balance: ${balance:,.2f}")
            logger.info(f"   Margin Livre: ${margin_free:,.2f}")

            if margin_free < 100:
                logger.warning(f"⚠️  Margem livre muito baixa!")
                blockers.append(f"Margem baixa: ${margin_free:.2f}")
        else:
            logger.warning("⚠️  Não conseguiu obter info da conta")
            blockers.append("Não conseguiu obter info da conta")

        # 5. Verificar símbolo
        symbol_info = agent.mt5.get_symbol_info(agent.symbol)
        if symbol_info:
            logger.info(f"✅ Símbolo encontrado: {agent.symbol}")
        else:
            logger.warning(f"⚠️  Símbolo não encontrado!")
            blockers.append(f"Símbolo {agent.symbol} não encontrado")

        if not blockers:
            logger.info("\n✅ Nenhum bloqueio detectado!")
        else:
            logger.warning(f"\n⚠️  {len(blockers)} bloqueio(s) detectado(s):")
            for i, blocker in enumerate(blockers, 1):
                logger.warning(f"   {i}. {blocker}")

        return blockers

    except Exception as e:
        logger.error(f"❌ Erro ao verificar bloqueios: {e}")
        return ['Erro ao verificar']

def simulate_trade_opening(agent, signal):
    """Simula abertura de trade"""
    logger.info("\n" + "="*80)
    logger.info("5️⃣  SIMULAÇÃO DE ABERTURA DE TRADE")
    logger.info("="*80)

    if signal == 'NEUTRAL':
        logger.info("❌ Sinal NEUTRAL - Não abriria trade")
        return False

    if signal != 'SELL':
        logger.warning(f"⚠️  Sinal é {signal}, não SELL")
        return False

    logger.info(f"✅ Sinal SELL detectado - Tentaria abrir:")
    logger.info(f"   Symbol: {agent.symbol}")
    logger.info(f"   Type: SELL")
    logger.info(f"   Volume: {agent.volume} lots")
    logger.info(f"   Target Profit: ${agent.target_profit}")
    logger.info(f"   SL: ATR × 1.5 (dinâmico)")
    logger.info(f"\n   ✅ Condições OK para abertura de trade!")
    return True

def main():
    """Teste diagnóstico principal"""
    logger.info("\n" + "="*80)
    logger.info("🔍 TESTE DIAGNÓSTICO COMPLETO - GOLD AGENT")
    logger.info("="*80)

    # 1. Teste de conexão
    agent = test_connection()
    if not agent:
        logger.error("❌ Falha fatal: Não conseguiu conectar ao MT5")
        return

    # 2. Teste de indicadores
    indicators = test_indicators(agent)
    if not indicators:
        logger.error("❌ Falha fatal: Não conseguiu calcular indicadores")
        return

    # 3. Análise de sinal
    signal = analyze_signal(indicators)

    # 4. Verificação de bloqueios
    blockers = check_blockers(agent)

    # 5. Simulação
    can_open = simulate_trade_opening(agent, signal)

    # RESUMO FINAL
    logger.info("\n" + "="*80)
    logger.info("📊 RESUMO FINAL")
    logger.info("="*80)

    logger.info(f"\n✅ CONEXÃO: OK")
    logger.info(f"✅ INDICADORES: OK")
    logger.info(f"{'✅' if signal == 'SELL' else '❌'} SINAL: {signal}")
    logger.info(f"{'✅' if not blockers else '⚠️'} BLOQUEIOS: {len(blockers)}")

    if signal == 'SELL' and not blockers:
        logger.info(f"\n🎯 DIAGNÓSTICO: PRONTO PARA ABRIR TRADE!")
        logger.info(f"   Agent pode abrir posição SELL agora")
    elif signal == 'NEUTRAL':
        logger.info(f"\n⏸️  DIAGNÓSTICO: Aguardando sinal SELL")
        logger.info(f"   Mercado não atende critérios (3+ sinais necessários)")
        logger.info(f"   RSI precisa estar > 70 ou outros indicadores alinhados")
    elif blockers:
        logger.info(f"\n🚫 DIAGNÓSTICO: Bloqueado")
        logger.info(f"   Razão(s):")
        for blocker in blockers:
            logger.info(f"   - {blocker}")

    logger.info("\n" + "="*80)

if __name__ == '__main__':
    main()
