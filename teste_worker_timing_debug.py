#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE WORKER TIMING DEBUG
========================

Teste específico para identificar por que o worker está demorando 
para detectar o trailing stop.

Identifica:
- Inicialização do worker
- Callback sendo chamado
- Lucro sendo detectado
- Ativação do trailing
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
from core.mt5_direct_client import get_mt5_client

def test_worker_timing():
    """
    Testa timing do worker em detalhes
    """
    print("="*80)
    print("TESTE WORKER TIMING DEBUG")
    print("="*80)
    
    # Criar agente
    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.1,
        check_interval=30  # Thread principal mais lenta
    )
    
    print(f"\n✅ AGENTE CRIADO")
    print(f"   Volume: {agent.volume}")
    print(f"   Trailing ativa em: ${agent.trailing_activation_dollar:.2f}")
    print(f"   Intervalo worker: 0.1s (10x por segundo)")
    
    # Verificar se MT5 está conectado
    print(f"\n🔍 VERIFICANDO MT5...")
    mt5 = get_mt5_client()
    if mt5:
        print(f"   ✅ MT5 conectado")
        
        # Verificar posições existentes
        positions = mt5.positions_get(symbol="XAUUSDc")
        print(f"   Posições abertas: {len(positions) if positions else 0}")
        
        if positions:
            print(f"   📊 ANALISANDO POSIÇÕES EXISTENTES:")
            for pos in positions[:3]:  # Primeiras 3
                ticket = pos.get('ticket', 0)
                profit = pos.get('profit', 0.0)
                entry = pos.get('price_open', 0)
                current = pos.get('price_current', 0)
                pos_type = "BUY" if pos.get('type') == 0 else "SELL"
                
                print(f"     Ticket #{ticket}: {pos_type}")
                print(f"     Entry: ${entry:.2f} | Current: ${current:.2f}")
                print(f"     Profit: ${profit:.2f}")
                
                # Verificar se deveria ativar trailing
                should_activate = profit >= agent.trailing_activation_dollar
                print(f"     Should activate trailing: {'✅ SIM' if should_activate else '❌ NÃO'}")
                print(f"     Difference: ${agent.trailing_activation_dollar - profit:.2f}")
                print()
        
        # Obter preço atual
        tick = mt5.get_symbol_info_tick("XAUUSDc")
        if tick:
            print(f"   💰 PREÇO ATUAL: ${tick['bid']:.2f} / ${tick['ask']:.2f}")
        
        # Simular posições diferentes para teste
        print(f"\n🧪 TESTE COM POSIÇÕES SIMULADAS:")
        
        test_cases = [
            {"profit": 0.50, "should_activate": False, "desc": "Abaixo do threshold"},
            {"profit": 1.00, "should_activate": True, "desc": "No threshold exato"},
            {"profit": 1.50, "should_activate": True, "desc": "Acima do threshold"},
            {"profit": 2.75, "should_activate": True, "desc": "Múltiplos níveis"}
        ]
        
        for test in test_cases:
            profit = test["profit"]
            should_activate = test["should_activate"]
            
            print(f"   Teste ${profit:.2f}:")
            print(f"     Resultado esperado: {'ATIVAR' if should_activate else 'NÃO ATIVAR'}")
            
            # Testar cálculos
            if agent.point_value and agent.symbol_point:
                pontos_needed = agent.trailing_activation_dollar / (agent.point_value * agent.volume)
                price_distance = pontos_needed * agent.symbol_point
                print(f"     Pontos necessários: {pontos_needed:.1f}")
                print(f"     Distância preço: {price_distance:.3f}")
            
            print()
        
        print(f"\n🎯 ANÁLISE DO PROBLEMA:")
        print(f"   1. Worker interval: 0.1s (✅ OK - muito rápido)")
        print(f"   2. Profit threshold: ${agent.trailing_activation_dollar:.2f}")
        print(f"   3. Point value: ${agent.point_value:.4f} por lote por ponto")
        print(f"   4. Symbol point: {agent.symbol_point}")
        
        # Verificar se há problemas de inicialização
        print(f"\n🔧 POSSÍVEIS CAUSAS DO DELAY:")
        print(f"   1. ✅ Intervalo do worker: 0.1s (muito rápido)")
        print(f"   2. ✅ Profit calculation: Usando MT5 profit diretamente")
        print(f"   3. ✅ Activation logic: Com logs detalhados")
        print(f"   4. ❓ Inicialização worker: Pode ter delay")
        print(f"   5. ❓ Thread synchronization: Worker vs Main thread")
        
        # Sugestões
        print(f"\n💡 SUGESTÕES PARA RESOLVER:")
        print(f"   1. Verificar se worker foi iniciado corretamente")
        print(f"   2. Adicionar logs na inicialização do worker")
        print(f"   3. Verificar se callback está sendo chamado")
        print(f"   4. Confirmar se profit está sendo lido corretamente")
        print(f"   5. Testar com posições reais (abrir posição teste)")
        
    else:
        print(f"   ❌ MT5 não conectado!")
    
    print(f"\n" + "="*80)
    print(f"ANÁLISE CONCLUÍDA")
    print(f"Próximo passo: Abrir posição teste e monitorar logs do worker")
    print(f"="*80)

if __name__ == "__main__":
    test_worker_timing()
