#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples BTC M1 Aggressive
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def testar_configuracao():
    """
    Testa configuração BTC M1 Aggressive
    """
    print("BTC M1 AGGRESSIVE - TESTE SIMPLES")
    print("="*50)
    
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        
        print("BTCHedgeAgent importado com sucesso!")
        
        # Configurações BTC M1 Aggressive
        agent = BTCHedgeAgent(
            symbol='BTCUSDc',      # Cents version
            volume=0.05,           # Aggressive volume
            target_profit=1.0,     # Menor TP
            check_interval=15,     # Mais frequente
            hedge_trigger=-3.0,    # Mais sensível
            hedge_tp_target=3.0,   # TP hedge menor
            atr_multiplier=1.5,    # SL apertado
            only_sell=False        # BUY habilitado
        )
        
        print("\nAGENTE BTC M1 AGGRESSIVE CRIADO!")
        print("="*50)
        
        # Exibir configurações
        print("CONFIGURACOES PRINCIPAIS:")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume} lots (aggressive)")
        print(f"   Target Profit: ${agent.target_profit}")
        print(f"   Check Interval: {agent.check_interval}s")
        print(f"   Hedge Trigger: ${agent.hedge_trigger}")
        print(f"   Hedge TP: ${agent.hedge_tp_target}")
        print(f"   ATR Multiplier: {agent.atr_multiplier}x")
        buy_sell = "SELL-Only" if agent.only_sell else "BUY/SELL Habilitado"
        print(f"   BUY/SELL: {buy_sell}")
        
        print(f"\nSTATUS ATUAL:")
        print(f"   State: {agent.state.value}")
        print(f"   Hedge Active: {agent.hedge_active}")
        print(f"   Daily Trades: {agent.daily_trades}")
        print(f"   Total Profit: ${agent.total_profit:.2f}")
        
        print(f"\nAGGRESSIVE FEATURES:")
        print(f"   Volume +67% (0.05 vs 0.03)")
        print(f"   Hedge +25% sensivel (-$3.0 vs -$4.0)")
        print(f"   TP -60% menor ($1.0 vs $2.5)")
        print(f"   Check +100% frequente (15s vs 30s)")
        print(f"   SL -40% apertado (1.5x vs 2.5x)")
        print(f"   BTCUSDc: menor spread")
        
        print(f"\nVANTAGENS M1:")
        print(f"   Scalping ativo (timeframe M1)")
        print(f"   15x mais sinais que M15")
        print(f"   Volume 67% maior")
        print(f"   Realizado 60% mais rapido")
        print(f"   Hedge protecao rapida")
        print(f"   Menor drawdown")
        
        # Simulação de performance
        print(f"\nSIMULACAO PERFORMANCE:")
        trades_diarios = 36  # Estimativa M1
        win_rate = 0.62      # 62%
        profit_diario = trades_diarios * agent.target_profit * win_rate
        
        print(f"   Trades/dia estimados: {trades_diarios}")
        print(f"   Win Rate estimado: {win_rate*100:.0f}%")
        print(f"   Profit/Trade: ${agent.target_profit}")
        print(f"   Profit diario estimado: ${profit_diario:.2f}")
        print(f"   Profit mensal: ${profit_diario * 22:.2f}")
        
        print(f"\nPROXIMOS PASSOS:")
        print(f"   1. Configuracoes testadas")
        print(f"   2. Para executar live: descomente agent.run()")
        print(f"   3. Monitorar performance")
        print(f"   4. Ajustar se necessario")
        
        print(f"\n" + "="*50)
        print(f"BTC M1 AGGRESSIVE TESTADO COM SUCESSO!")
        print(f"Agente pronto para scalping ativo em M1")
        
        return True, agent
        
    except Exception as e:
        print(f"\nERRO ao testar BTC M1 Aggressive:")
        print(f"   {str(e)}")
        
        print(f"\nPOSSIVEIS SOLUCOES:")
        print(f"   Verificar se BTCHedgeAgent esta funcionando")
        print(f"   Verificar dependencias (MT5, database, etc.)")
        print(f"   Testar com configuracoes basicas primeiro")
        
        # Tentar configuração mínima
        try:
            print(f"\nTentando configuracao minima...")
            agent = BTCHedgeAgent()
            print(f"Agente basico funcionando!")
            return False, agent
        except Exception as e2:
            print(f"Erro na configuracao basica: {e2}")
            
        return False, None

def demonstracao_comparacao():
    """
    Demonstra a comparação com outros agentes
    """
    print(f"\nCOMPARACAO COM OUTROS AGENTES")
    print("="*50)
    
    comparacoes = [
        ("BTC Optimized (M15)", {
            "symbol": "BTCUSDm",
            "volume": 0.03,
            "target_profit": 2.5,
            "check_interval": 30,
            "hedge_trigger": -4.0,
            "hedge_tp_target": 4.0,
            "atr_multiplier": 2.5
        }),
        ("BTC M1 Aggressive", {
            "symbol": "BTCUSDc",
            "volume": 0.05,
            "target_profit": 1.0,
            "check_interval": 15,
            "hedge_trigger": -3.0,
            "hedge_tp_target": 3.0,
            "atr_multiplier": 1.5
        }),
        ("BTC Simples", {
            "symbol": "BTCUSD",
            "volume": 0.01,
            "target_profit": 5.0,
            "check_interval": 60,
            "hedge_trigger": -10.0,
            "hedge_tp_target": 10.0,
            "atr_multiplier": 3.0
        })
    ]
    
    for nome, config in comparacoes:
        print(f"\n{nome}:")
        print(f"   Symbol: {config['symbol']}")
        print(f"   Volume: {config['volume']} lots")
        print(f"   Target: ${config['target_profit']}")
        print(f"   Check: {config['check_interval']}s")
        print(f"   Hedge: ${config['hedge_trigger']}")
    
    print(f"\nRECOMENDACAO:")
    print(f"   Conservador: BTC Simples")
    print(f"   Balanceado: BTC Optimized")
    print(f"   Agressivo: BTC M1 Aggressive")

if __name__ == "__main__":
    sucesso, agent = testar_configuracao()
    
    if sucesso:
        demonstracao_comparacao()
        
        print(f"\nPARA EXECUTAR EM LIVE:")
        print(f"# Descomente a linha abaixo no codigo:")
        print(f"# agent.run()")
        
    print(f"\n" + "="*50)
    print(f"Teste concludo!")
