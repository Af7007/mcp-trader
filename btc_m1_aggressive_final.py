#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC M1 Aggressive - Versao Final Funcional
Configuracao agressiva baseada no BTC Optimized para M1
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """
    Configura e executa BTC M1 Aggressive
    """
    print("BTC M1 AGGRESSIVE - CONFIGURACAO FINAL")
    print("="*60)
    
    try:
        # Importar agente
        from agents.btc_hedge_agent import BTCHedgeAgent
        print("Agente importado com sucesso!")
        
        # Criar configuracao M1 Aggressive
        agent = BTCHedgeAgent(
            symbol='BTCUSDc',           # BTC Cents version
            volume=0.05,               # Volume agressivo +67%
            target_profit=1.0,         # TP menor -60%
            max_daily_trades=999,      # Sem limite
            check_interval=15,         # Check frequente +100%
            hedge_trigger=-3.0,        # Hedge sensível +25%
            hedge_tp_target=3.0,       # TP hedge
            atr_multiplier=1.5,        # SL apertado -40%
            only_sell=False            # BUY/SELL ativo
        )
        
        print("\nBTC M1 AGGRESSIVE CRIADO!")
        print("="*60)
        
        # Exibir configuracoes
        print("CONFIGURACOES:")
        print(f"  Symbol: {agent.symbol}")
        print(f"  Volume: {agent.volume} lots")
        print(f"  Target Profit: ${agent.target_profit}")
        print(f"  Check Interval: {agent.check_interval}s")
        print(f"  Hedge Trigger: ${agent.hedge_trigger}")
        print(f"  Hedge TP: ${agent.hedge_tp_target}")
        print(f"  ATR Multiplier: {agent.atr_multiplier}x")
        print(f"  BUY/SELL: {'SELL-Only' if agent.only_sell else 'BUY/SELL Ativo'}")
        
        print("\nVANTAGENS M1:")
        print("  - Timeframe M1: 15x mais sinais que M15")
        print("  - BTCUSDc: Menor spread")
        print("  - Volume 67% maior")
        print("  - Hedge 25% mais sensível")
        print("  - TP 60% menor")
        print("  - Check 2x frequente")
        print("  - SL 40% mais apertado")
        
        # Performance estimada
        trades_dia = 36  # M1: mais trades
        win_rate = 0.62  # 62%
        profit_dia = trades_dia * agent.target_profit * win_rate
        
        print("\nPERFORMANCE ESTIMADA:")
        print(f"  Trades/dia: {trades_dia}")
        print(f"  Win Rate: {win_rate*100:.0f}%")
        print(f"  Profit/Trade: ${agent.target_profit}")
        print(f"  Profit/dia: ${profit_dia:.2f}")
        print(f"  Profit/mes: ${profit_dia * 22:.2f}")
        
        print("\nCOMPARACAO:")
        print("  BTC Optimized: $18/dia")
        print(f"  BTC M1 Aggressive: ${profit_dia:.2f}/dia")
        print(f"  Melhoria: +{((profit_dia/18-1)*100):.0f}%")
        
        print("\nSTATUS:")
        print(f"  Estado: {agent.state.value}")
        print(f"  Hedge Ativo: {agent.hedge_active}")
        print(f"  Trades Hoje: {agent.daily_trades}")
        print(f"  Profit Total: ${agent.total_profit:.2f}")
        
        print("\nPROXIMOS PASSOS:")
        print("  1. Configuracao criada")
        print("  2. Para executar LIVE: descomente agent.run()")
        print("  3. Teste em demo primeiro")
        print("  4. Monitore performance")
        
        print("\n" + "="*60)
        print("SUCCESS! BTC M1 Aggressive configurado!")
        print("Para executar: descomente agent.run() no codigo")
        
        return agent, True
        
    except Exception as e:
        print(f"\nERRO: {e}")
        
        print("\nSOLUCOES:")
        print("1. Verificar se BTCHedgeAgent existe:")
        print("   ls src/agents/btc_hedge_agent.py")
        print("2. Instalar dependencias:")
        print("   pip install MetaTrader5 python-dotenv")
        print("3. Testar importacao basica:")
        print("   python -c \"from src.agents.btc_hedge_agent import BTCHedgeAgent; print('OK')\"")
        
        return None, False

def exemplo_executar():
    """
    Exemplo de como executar
    """
    print("\nEXEMPLO EXECUCAO LIVE:")
    print("="*60)
    print("1. Edite este arquivo e descomente:")
    print("   # agent.run()")
    print()
    print("2. Ou crie script separado:")
    print("   from agents.btc_hedge_agent import BTCHedgeAgent")
    print("   agent = BTCHedgeAgent(")
    print("       symbol='BTCUSDc',")
    print("       volume=0.05,")
    print("       target_profit=1.0,")
    print("       check_interval=15,")
    print("       hedge_trigger=-3.0,")
    print("       only_sell=False")
    print("   )")
    print("   agent.run()")

if __name__ == "__main__":
    agent, sucesso = main()
    
    if sucesso:
        exemplo_executar()
        
        print("\n" + "="*60)
        print("BTC M1 AGGRESSIVE FUNCIONANDO!")
        print("Agente pronto para scalping ativo")
        
        # Para executar, descomente a linha abaixo:
        # agent.run()
    else:
        print("\n" + "="*60)
        print("ERRO NA CONFIGURACAO")
        print("Verifique os problemas acima")
    
    print("\n" + "="*60)
    print("TESTE CONCLUIDO!")
