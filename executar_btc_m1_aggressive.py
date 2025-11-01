#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC M1 Aggressive - Execução Simples
Script direto para executar o agente BTC M1 Aggressive
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def executar_btc_m1_aggressive():
    """
    Executa BTC M1 Aggressive
    """
    print("BTC M1 AGGRESSIVE - EXECUÇÃO")
    print("="*50)
    
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        
        print("Criando agente BTC M1 Aggressive...")
        
        # Configurações M1 Aggressive
        agent = BTCHedgeAgent(
            symbol='BTCUSDc',      # Cents version
            volume=0.05,           # Volume agressivo
            target_profit=1.0,     # TP menor
            check_interval=15,     # Check frequente
            hedge_trigger=-3.0,    # Hedge sensível
            hedge_tp_target=3.0,   # TP hedge
            atr_multiplier=1.5,    # SL apertado
            only_sell=False        # BUY/SELL ativo
        )
        
        print("Agente criado com sucesso!")
        print()
        print("CONFIGURAÇÕES:")
        print(f"  Symbol: {agent.symbol}")
        print(f"  Volume: {agent.volume}")
        print(f"  Target: ${agent.target_profit}")
        print(f"  Hedge: ${agent.hedge_trigger}")
        print(f"  BUY/SELL: {'Ativo' if not agent.only_sell else 'SELL-Only'}")
        print()
        
        print("Para executar em LIVE mode:")
        print("Descomente a linha 'agent.run()' abaixo")
        print()
        
        # IMPORTANTE: Descomente para executar
        agent.run()
        
        print("Configuração completa!")
        print("Agente pronto para execução.")
        
    except Exception as e:
        print(f"Erro: {e}")
        print()
        print("Soluções:")
        print("1. Verificar se BTCHedgeAgent existe")
        print("2. Instalar dependências: pip install MetaTrader5 python-dotenv")

if __name__ == "__main__":
    executar_btc_m1_aggressive()
    
    print()
    print("="*50)
    print("Para executar LIVE:")
    print("Edite este arquivo e descomente: agent.run()")
    print("="*50)
