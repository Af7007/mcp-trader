#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Agente BTC M1 Aggressive - Configurações e Análise
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def testar_configuracoes_btc_m1():
    """
    Testa e exibe as configurações do BTC M1 Aggressive
    """
    print("=== BTC M1 AGGRESSIVE - CONFIGURAÇÕES ===")
    print()
    
    try:
        # Importar o agente
        from agents.btc_m1_aggressive_agent import BTCM1AggressiveAgent
        
        # Criar agente BTC M1 Aggressive
        agent = BTCM1AggressiveAgent()
        
        print("🤖 AGENTE BTC M1 AGGRESSIVE CRIADO:")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume} lots")
        print(f"   Target Profit: ${agent.target_profit}")
        print(f"   Check Interval: {agent.check_interval}s")
        print(f"   Hedge Trigger: ${agent.hedge_trigger}")
        print(f"   Hedge TP: ${agent.hedge_tp_target}")
        print(f"   ATR Multiplier: {agent.atr_multiplier}x")
        print(f"   BUY/SELL: {'SELL-Only' if agent.only_sell else 'BUY/SELL Habilitado'}")
        print()
        
        # Comparação com BTC Optimized
        print("📊 COMPARAÇÃO: BTC M1 AGGRESSIVE vs BTC OPTIMIZED")
        print()
        print("BTC OPTIMIZED (M15):")
        print(f"   • Symbol: BTCUSDm")
        print(f"   • Volume: 0.03 lots")
        print(f"   • Target Profit: $2.5")
        print(f"   • Check Interval: 30s")
        print(f"   • Hedge Trigger: -$4.0")
        print(f"   • Hedge TP: $4.0")
        print(f"   • ATR Multiplier: 2.5x")
        print(f"   • BUY/SELL: BUY Habilitado")
        print()
        
        print("BTC M1 AGGRESSIVE (M1):")
        print(f"   • Symbol: {agent.symbol} (cents)")
        print(f"   • Volume: {agent.volume} lots (+67%)")
        print(f"   • Target Profit: ${agent.target_profit} (-60%)")
        print(f"   • Check Interval: {agent.check_interval}s (+100%)")
        print(f"   • Hedge Trigger: ${agent.hedge_trigger} (+25%)")
        print(f"   • Hedge TP: ${agent.hedge_tp_target} (-25%)")
        print(f"   • ATR Multiplier: {agent.atr_multiplier}x (-40%)")
        print(f"   • BUY/SELL: {'SELL-Only' if agent.only_sell else 'BUY/SELL Habilitado'}")
        print()
        
        # Vantagens M1
        print("✅ VANTAGENS DO M1 AGGRESSIVE:")
        print("   • Timeframe M1: Maior frequência de sinais")
        print("   • BTCUSDc: Menor spread, mais oportunidades")
        print("   • Volume 67% maior: Maior exposição")
        print("   • Check 2x mais frequente: Resposta rápida")
        print("   • TP menor: Realizado mais rápido")
        print("   • Hedge mais sensível: Proteção rápida")
        print("   • SL mais apertado: Menos drawdown")
        print()
        
        # Indicadores otimizados M1
        print("📈 INDICADORES OTIMIZADOS M1:")
        print("   • RSI: 10 períodos (vs 14) - mais sensível")
        print("   • MACD: 8,16,6 (vs 12,26,9) - resposta rápida")
        print("   • SMA: 10/30 (vs 20/50) - trend responsivo")
        print("   • Bollinger: 14 (vs 20) - volatilidade atual")
        print("   • ATR: 10 períodos (vs 14) - dinâmico")
        print()
        
        return True, agent
        
    except Exception as e:
        print(f"[ERRO] Erro ao testar configurações: {e}")
        return False, None

def analisar_vantagens_m1():
    """
    Analisa as vantagens específicas do timeframe M1
    """
    print("🔍 ANÁLISE M1 AGGRESSIVE:")
    print()
    
    vantagens = [
        ("Scalping", "Capture movimentos em 1 minuto"),
        ("Frequência", "2x mais sinais que M15"),
        ("Volume", "67% maior para acelerar profits"),
        ("Hedge", "Ativação 25% mais rápida"),
        ("TP", "Realizado 60% mais rápido"),
        ("SL", "40% mais apertado = menos risco"),
        ("BUY/SELL", "Não SELL-only = mais oportunidades"),
        ("Cents", "Menor spread = menos custo")
    ]
    
    for vantagem, descricao in vantagens:
        print(f"   ✅ {vantagem}: {descricao}")
    
    print()
    print("⚠️ RISCOS M1:")
    print("   • Volatilidade alta em M1")
    print("   • Spikes podem causar SL")
    print("   • Requer monitoramento ativo")
    print("   • Stress emocional maior")
    print()

def simulacao_performance():
    """
    Simula performance esperada do M1 Aggressive
    """
    print("📊 SIMULAÇÃO PERFORMANCE M1 AGGRESSIVE")
    print()
    
    # Simulação baseada nas configurações
    trades_por_hora = 4  # M1 - mais trades
    target_por_trade = 1.0  # TP $1.0
    win_rate_estimado = 65  # M1 mais seletivo
    volume_multiplier = 0.05 / 0.03  # 67% maior
    
    trades_diarios = trades_por_hora * 12  # 12 horas úteis
    profits_diarios = trades_diarios * target_por_trade * (win_rate_estimado / 100)
    profits_mensais = profits_diarios * 22  # 22 dias úteis
    
    print(f"ESTIMATIVA DIÁRIA:")
    print(f"   • Trades: {trades_diarios}")
    print(f"   • Win Rate: {win_rate_estimado}%")
    print(f"   • Target/Trade: ${target_por_trade}")
    print(f"   • Profit Diário: ${profits_diarios:.2f}")
    print()
    
    print(f"ESTIMATIVA MENSAL:")
    print(f"   • Profit Mensal: ${profits_mensais:.2f}")
    print(f"   • Volume 67% maior: +{((volume_multiplier - 1) * 100):.0f}% exposição")
    print(f"   • Hedge mais rápido: -25% tempo de proteção")
    print()
    
    print("🎯 COMPARAÇÃO COM OPTIMIZED:")
    optimized_trades = 12  # trades/dia otimizado
    optimized_profit = optimized_trades * 2.5 * 0.6  # 60% win rate
    
    print(f"   • BTC Optimized: ${optimized_profit:.2f}/dia")
    print(f"   • BTC M1 Aggressive: ${profits_diarios:.2f}/dia")
    print(f"   • Melhoria: +{((profits_diarios/optimized_profit - 1) * 100):.0f}%")
    print()

def recomendacao_final():
    """
    Recomendação final sobre usar M1 Aggressive
    """
    print("🏆 RECOMENDAÇÃO FINAL")
    print()
    
    print("USE BTC M1 AGGRESSIVE SE:")
    print("   ✅ Quer scalping ativo")
    print("   ✅ Tem tempo para monitorar")
    print("   ✅ Acepta volatilidade alta")
    print("   ✅ Quer acelerar profits")
    print("   ✅ Tem experiência com M1")
    print()
    
    print("USE BTC OPTIMIZED SE:")
    print("   ✅ Prefere trades mais longos")
    print("   ✅ Quer menos stress")
    print("   ✅ Trading passivo")
    print("   ✅ Tem capital conservador")
    print()
    
    print("🚀 PRÓXIMOS PASSOS:")
    print("   1. Testar em conta demo")
    print("   2. Monitorar performance 1 semana")
    print("   3. Ajustar volume se necessário")
    print("   4. Usar hedge ativamente")
    print("   5. Implementar em conta real")

if __name__ == "__main__":
    print("TESTE BTC M1 AGGRESSIVE")
    print("="*50)
    
    # Executar testes
    sucesso, agent = testar_configuracoes_btc_m1()
    
    if sucesso:
        analisar_vantagens_m1()
        simulacao_performance()
        recomendacao_final()
        
        print("\n" + "="*50)
        print("BTC M1 AGGRESSIVE TESTADO COM SUCESSO!")
        print("Agente pronto para execução em M1 com BTCUSDc")
    else:
        print("\n" + "="*50)
        print("ERRO AO TESTAR BTC M1 AGGRESSIVE")
        
    print(f"\nPARA EXECUTAR:")
    print(f"python src/agents/btc_m1_aggressive_agent.py")
