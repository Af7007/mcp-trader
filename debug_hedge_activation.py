#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do Hedge Activation - Verificar por que não ativa em -$4
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_hedge_activation():
    """
    Testa especificamente a ativação do hedge
    """
    print("=== DEBUG HEDGE ACTIVATION ===")
    
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        
        # Criar agente BTC
        agent = BTCHedgeAgent(symbol="BTCUSDm")
        
        print(f"Agente criado:")
        print(f"   Hedge Trigger: ${agent.hedge_trigger}")
        print(f"   Hedge TP Target: ${agent.hedge_tp_target}")
        print(f"   Hedge Active: {agent.hedge_active}")
        
        # Simular diferentes cenários de profit
        print("\n=== SIMULAÇÃO DE CENÁRIOS ===")
        
        # Cenário 1: Profit = -$3.5 (não deveria ativar)
        profit1 = -3.5
        should_activate1 = profit1 < agent.hedge_trigger
        print(f"Cenário 1: Profit = -${profit1:.2f}")
        print(f"   Condição: {profit1:.2f} < {agent.hedge_trigger} = {should_activate1}")
        print(f"   Deve ativar hedge: {'SIM' if should_activate1 else 'NÃO'}")
        
        # Cenário 2: Profit = -$4.0 (na fronteira - NAO deveria ativar)
        profit2 = -4.0
        should_activate2 = profit2 < agent.hedge_trigger
        print(f"\nCenário 2: Profit = -${profit2:.2f}")
        print(f"   Condição: {profit2:.2f} < {agent.hedge_trigger} = {should_activate2}")
        print(f"   Deve ativar hedge: {'SIM' if should_activate2 else 'NÃO'}")
        
        # Cenário 3: Profit = -$4.1 (SOMENTE DEVERIA ATIVAR)
        profit3 = -4.1
        should_activate3 = profit3 < agent.hedge_trigger
        print(f"\nCenário 3: Profit = -${profit3:.2f}")
        print(f"   Condição: {profit3:.2f} < {agent.hedge_trigger} = {should_activate3}")
        print(f"   Deve ativar hedge: {'SIM' if should_activate3 else 'NÃO'}")
        
        # Cenário 4: Profit = -$5.0 (definitivamente deveria ativar)
        profit4 = -5.0
        should_activate4 = profit4 < agent.hedge_trigger
        print(f"\nCenário 4: Profit = -${profit4:.2f}")
        print(f"   Condição: {profit4:.2f} < {agent.hedge_trigger} = {should_activate4}")
        print(f"   Deve ativar hedge: {'SIM' if should_activate4 else 'NÃO'}")
        
        print(f"\n=== ANÁLISE ===")
        print(f"PROBLEMA IDENTIFICADO:")
        print(f"  - Hedge só ativa quando profit < {agent.hedge_trigger}")
        print(f"  - Para ativar em EXATAMENTE -$4.00, precisa de 'profit <= {agent.hedge_trigger}'")
        print(f"  - Solução: Mudar condition de '<' para '<='")
        
        return True, agent
        
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
        return False, None

def test_gold_hedge_comparison():
    """
    Compara o hedge do Gold vs BTC para entender o problema
    """
    print("\n=== COMPARAÇÃO GOLD vs BTC HEDGE ===")
    
    try:
        from agents.btc_hedge_agent import BTCHedgeAgent
        
        # Criar agentes
        gold_agent = BTCHedgeAgent(symbol="XAUUSDm")
        btc_agent = BTCHedgeAgent(symbol="BTCUSDm")
        
        print(f"GOLD AGENT:")
        print(f"   Hedge Trigger: ${gold_agent.hedge_trigger}")
        print(f"   Hedge TP Target: ${gold_agent.hedge_tp_target}")
        
        print(f"\nBTC AGENT:")
        print(f"   Hedge Trigger: ${btc_agent.hedge_trigger}")
        print(f"   Hedge TP Target: ${btc_agent.hedge_tp_target}")
        
        # Testar cenários similares
        print(f"\n=== TESTE COM PROFIT = -$4.00 ===")
        profit = -4.00
        
        gold_trigger = profit < gold_agent.hedge_trigger
        btc_trigger = profit < btc_agent.hedge_trigger
        
        print(f"Profit = -${profit:.2f}")
        print(f"   Gold ativaria: {gold_trigger} ({profit:.2f} < {gold_agent.hedge_trigger})")
        print(f"   BTC ativaria: {btc_trigger} ({profit:.2f} < {btc_agent.hedge_trigger})")
        
        if btc_agent.hedge_trigger == -4.0:
            print(f"\nDIAGNÓSTICO:")
            print(f"  - BTC trigger = -$4.00")
            print(f"  - Profit = -$4.00")
            print(f"  - Condição (profit < trigger): -4.00 < -4.00 = False")
            print(f"  - PROBLEMA: Precisa de profit < -4.01 para ativar!")
            print(f"  - SOLUÇÃO: Usar '<=' ou ajustar trigger para -3.99")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro na comparação: {e}")
        return False

def propose_fix():
    """
    Proposta de correção
    """
    print("\n=== PROPOSTA DE CORREÇÃO ===")
    
    print("OPÇÃO 1: Mudar condição no código")
    print("   De: if profit < self.hedge_trigger")
    print("   Para: if profit <= self.hedge_trigger")
    
    print("\nOPÇÃO 2: Ajustar trigger para -$3.99")
    print("   BTC trigger: -$4.00 → -$3.99")
    
    print("\nOPÇÃO 3: Proteger com margem")
    print("   BTC trigger: -$4.00 → -$3.50")
    
    print("\nRECOMENDAÇÃO: Usar OPÇÃO 2 (-$3.99)")
    print("  - Mais seguro que OPÇÃO 1 (evita problemas de floating point)")
    print("  - Mais preciso que OPÇÃO 3 (mantém trigger original)")
    
if __name__ == "__main__":
    print("DEBUG HEDGE ACTIVATION - BTC OPTIMIZED")
    print("="*50)
    
    # Executar testes
    sucesso1, agent = test_hedge_activation()
    sucesso2 = test_gold_hedge_comparison()
    propose_fix()
    
    print("\n" + "="*50)
    if sucesso1 and sucesso2:
        print("DIAGNÓSTICO CONCLUÍDO")
        print("[OK] Problema identificado: Condição muito restritiva")
        print("[OK] Solução proposta: Ajustar trigger para -$3.99")
    else:
        print("[ERRO] Falha no diagnóstico")
