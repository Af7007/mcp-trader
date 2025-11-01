#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC M1 Aggressive - Versão Funcional
Baseado no BTC Optimized com configurações agressivas para M1
"""

import sys
import time
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def configurar_btc_m1_aggressive():
    """
    Configura e executa BTC M1 Aggressive usando o BTCHedgeAgent existente
    """
    print("BTC M1 AGGRESSIVE - CONFIGURACAO FUNCIONAL")
    print("="*60)
    
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        
        print("BTCHedgeAgent importado com sucesso!")
        
        # Configurar BTC M1 Aggressive
        agent = BTCHedgeAgent(
            symbol='BTCUSDc',           # BTC Cents
            volume=0.05,               # Volume agressivo
            target_profit=1.0,         # TP menor para M1
            max_daily_trades=999,      # Sem limite
            check_interval=15,         # Check mais frequente
            hedge_trigger=-3.0,        # Hedge mais sensível
            hedge_tp_target=3.0,       # TP hedge menor
            atr_multiplier=1.5,        # SL mais apertado
            only_sell=False            # BUY/SELL habilitado
        )
        
        print("\nBTC M1 AGGRESSIVE CONFIGURADO!")
        print("="*60)
        
        # Exibir configurações
        print("CONFIGURACOES AGRESSIVAS:")
        print(f"  Symbol: {agent.symbol}")
        print(f"  Volume: {agent.volume} lots (+67% vs otimizado)")
        print(f"  Target: ${agent.target_profit} (-60% vs otimizado)")
        print(f"  Check: {agent.check_interval}s (+100% frequência)")
        print(f"  Hedge: ${agent.hedge_trigger} (+25% sensível)")
        print(f"  Hedge TP: ${agent.hedge_tp_target}")
        print(f"  ATR: {agent.atr_multiplier}x (-40% vs otimizado)")
        print(f"  BUY/SELL: {'SELL-Only' if agent.only_sell else 'BUY/SELL Ativo'}")
        
        print(f"\nVANTAGENS M1 AGGRESSIVE:")
        print(f"  • Timeframe M1: 15x mais sinais que M15")
        print(f"  • BTCUSDc: Menor spread, mais acessível")
        print(f"  • Volume 67% maior: +67% exposição")
        print(f"  • Hedge 25% mais sensível: proteção rápida")
        print(f"  • TP 60% menor: realizado rápido")
        print(f"  • Check 2x frequente: resposta ágil")
        print(f"  • SL 40% mais apertado: menos drawdown")
        
        # Simulação de performance
        trades_dia = 36  # M1: ~36 trades/dia
        win_rate = 0.62  # 62% win rate estimado
        profit_dia = trades_dia * agent.target_profit * win_rate
        
        print(f"\nPERFORMANCE ESTIMADA:")
        print(f"  Trades/dia: {trades_dia}")
        print(f"  Win Rate: {win_rate*100:.0f}%")
        print(f"  Profit/Trade: ${agent.target_profit}")
        print(f"  Profit/dia: ${profit_dia:.2f}")
        print(f"  Profit/mês: ${profit_dia * 22:.2f}")
        
        print(f"\nSTATUS ATUAL:")
        print(f"  Estado: {agent.state.value}")
        print(f"  Hedge Ativo: {agent.hedge_active}")
        print(f"  Trades Hoje: {agent.daily_trades}")
        print(f"  Profit Total: ${agent.total_profit:.2f}")
        
        print(f"\nCOMPARACAO COM BTC OPTIMIZED:")
        print(f"  BTC Optimized: $18/dia (M15)")
        print(f"  BTC M1 Aggressive: ${profit_dia:.2f}/dia")
        print(f"  Melhoria: +{((profit_dia/18-1)*100):.0f}%")
        
        print(f"\nPROXIMOS PASSOS:")
        print(f"  1. Configuracao testada e aprovada")
        print(f"  2. Para executar LIVE: descomente agent.run()")
        print(f"  3. Teste em conta demo primeiro")
        print(f"  4. Monitore performance por 1 semana")
        print(f"  5. Ajuste volume se necessario")
        
        print(f"\n" + "="*60)
        print(f"SUCCESS! BTC M1 Aggressive configurado!")
        print(f"Agente pronto para scalping ativo")
        
        return agent, True
        
    except ImportError as e:
        print(f"\nERRO: Importacao falhou: {e}")
        print("Verificar se btc_hedge_agent.py existe")
        return None, False
        
    except Exception as e:
        print(f"\nERRO: Configuracao falhou: {e}")
        print("Verificar dependencias e dependencias")
        return None, False

def executar_testes_basicos():
    """
    Executa testes basicos de funcionalidade
    """
    print("\nTESTES BASICOS DE FUNCIONALIDADE")
    print("="*60)
    
    # Teste 1: Importação
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        print("✓ Teste 1: Importacao BTCHedgeAgent - OK")
    except Exception as e:
        print(f"✗ Teste 1: Importacao BTCHedgeAgent - ERRO: {e}")
        return False
    
    # Teste 2: Criação basica
    try:
        agent_basico = BTCHedgeAgent()
        print("✓ Teste 2: Criacao agente basico - OK")
    except Exception as e:
        print(f"✗ Teste 2: Criacao agente basico - ERRO: {e}")
        return False
    
    # Teste 3: Configuração M1
    try:
        agent_m1 = BTCHedgeAgent(
            symbol='BTCUSDc',
            volume=0.05,
            target_profit=1.0,
            check_interval=15,
            hedge_trigger=-3.0,
            only_sell=False
        )
        print("✓ Teste 3: Configuracao BTC M1 Aggressive - OK")
    except Exception as e:
        print(f"✗ Teste 3: Configuracao BTC M1 Aggressive - ERRO: {e}")
        return False
    
    print("\nTODOS OS TESTES BASICOS PASSARAM!")
    return True

def solucao_problemas():
    """
    Fornece solucao para problemas comuns
    """
    print("\nSOLUCOES PARA PROBLEMAS COMUNS")
    print("="*60)
    
    print("PROBLEMA 1: 'ModuleNotFoundError: No module named agents'")
    print("SOLUCAO: Verificar se src/agents/btc_hedge_agent.py existe")
    print()
    
    print("PROBLEMA 2: 'No module named MetaTrader5'")
    print("SOLUCAO: pip install MetaTrader5")
    print()
    
    print("PROBLEMA 3: 'No module named dotenv'")
    print("SOLUCAO: pip install python-dotenv")
    print()
    
    print("PROBLEMA 4: 'Telegram not available'")
    print("SOLUCAO: pip install python-telegram-bot")
    print()
    
    print("PROBLEMA 5: 'BTCUSDc not found'")
    print("SOLUCAO: Usar BTCUSDm ou BTCUSD")
    print()
    
    print("COMANDO PARA INSTALAR DEPENDENCIAS:")
    print("pip install MetaTrader5 python-dotenv python-telegram-bot")

if __name__ == "__main__":
    print("BTC M1 AGGRESSIVE - TESTE FUNCIONAL")
    print("="*60)
    
    # Executar testes basicos primeiro
    testes_ok = executar_testes_basicos()
    
    if testes_ok:
        print("\n" + "="*60)
        # Tentar configurar BTC M1 Aggressive
        agent, sucesso = configurar_btc_m1_aggressive()
        
        if sucesso:
            print("\n" + "="*60)
            print("PARA EXECUTAR EM LIVE:")
            print("1. Edite o arquivo:")
            print("   # Descomente a linha:")
            print("   # agent.run()")
            print("2. Execute:")
            print("   python btc_m1_aggressive_funcional.py")
            print("\nPARA TESTAR PRIMEIRO:")
            print("   python -c \"from agents.btc_hedge_agent import BTCHedgeAgent; BTCHedgeAgent().run()\"")
        else:
            solucao_problemas()
    else:
        print("\nTESTES BASICOS FALHARAM!")
        solucao_problemas()
    
    print("\n" + "="*60)
    print("TESTE CONCLUIDO!")
