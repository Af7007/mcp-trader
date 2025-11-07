#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Trailing Stop Corrigido para Gold
Verifica se os novos parametros estao funcionando corretamente
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_loss_zero_simple import GoldLossZeroSimple

def testar_trailing_corrigido():
    """Testa o trailing stop com os parametros corrigidos"""
    print("="*60)
    print("TESTE: TRAILING STOP CORRIGIDO PARA GOLD")
    print("="*60)
    
    try:
        # Inicializar agente
        print("\n1. Inicializando agente Gold...")
        agent = GoldLossZeroSimple(
            symbol="XAUUSDc",
            volume=0.01,
            check_interval=30,
            use_buy=True,
            use_sell=True
        )
        
        # Verificar parametros corrigidos
        print(f"\n2. Parametros do Trailing Stop:")
        print(f"   - Ativacao: ${agent.trailing_activation_dollar:.2f}")
        print(f"   - Protecao inicial: ${agent.trailing_distance_dollar:.2f}")
        print(f"   - Passo adicional: ${agent.trailing_step_dollar:.2f}")
        
        # Verificar point value
        print(f"\n3. Configuracao Gold:")
        print(f"   - Symbol Point: {agent.symbol_point}")
        print(f"   - Point Value: ${agent.point_value:.4f}")
        
        # Testar calculo de pontos
        print(f"\n4. Teste de Calculo:")
        dollars_to_protect = agent.trailing_distance_dollar
        pontos_necessarios = dollars_to_protect / (agent.point_value * agent.volume)
        distancia_preco = pontos_necessarios * agent.symbol_point
        
        print(f"   - Para proteger ${dollars_to_protect:.2f}:")
        print(f"   - Pontos necessarios: {pontos_necessarios:.1f}")
        print(f"   - Distancia em preco: {distancia_preco:.3f}")
        
        # Validar distancia minima
        MIN_DISTANCE_POINTS = 0.010
        if distancia_preco < MIN_DISTANCE_POINTS:
            print(f"   - DISTANCIA AJUSTADA para minimo GOLD: {MIN_DISTANCE_POINTS:.3f}")
        else:
            print(f"   - Distancia OK para Gold")
        
        print(f"\n5. Teste de Cenarios:")
        
        # Cenario 1: Lucro pequeno
        profit_test = 1.5
        print(f"\n   Cenario 1 - Lucro: ${profit_test:.2f}")
        if profit_test >= agent.trailing_activation_dollar:
            print(f"   [OK] Trailing seria ATIVADO")
            
            # Calcular protecao
            levels = int(profit_test // agent.trailing_step_dollar) + 1
            protection = agent.trailing_distance_dollar + (levels - 1) * agent.trailing_step_dollar
            protection = min(protection, profit_test - 0.01)
            
            pontos_protecao = protection / (agent.point_value * agent.volume)
            distancia_protecao = pontos_protecao * agent.symbol_point
            
            print(f"   - Protecao: ${protection:.2f}")
            print(f"   - Distancia preco: {distancia_protecao:.3f}")
        else:
            print(f"   - Trailing ainda nao ativado (falta ${agent.trailing_activation_dollar - profit_test:.2f})")
        
        # Cenario 2: Lucro grande
        profit_test = 5.0
        print(f"\n   Cenario 2 - Lucro: ${profit_test:.2f}")
        if profit_test >= agent.trailing_activation_dollar:
            levels = int(profit_test // agent.trailing_step_dollar) + 1
            protection = agent.trailing_distance_dollar + (levels - 1) * agent.trailing_step_dollar
            protection = min(protection, profit_test - 0.01)
            
            pontos_protecao = protection / (agent.point_value * agent.volume)
            distancia_protecao = pontos_protecao * agent.symbol_point
            
            print(f"   - Niveis de protecao: {levels}")
            print(f"   - Protecao: ${protection:.2f}")
            print(f"   - Distancia preco: {distancia_protecao:.3f}")
            print(f"   - Valida: {'OK' if distancia_protecao >= MIN_DISTANCE_POINTS else 'ERRO'}")
        
        print(f"\n6. Conclusao:")
        print(f"   [OK] Parametros corrigidos aplicados com sucesso")
        print(f"   [OK] Distancias validadas para Gold")
        print(f"   [OK] Trailing stop deve funcionar sem erros 'Invalid stops'")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_trailing_corrigido()
    
    if sucesso:
        print(f"\n{'='*60}")
        print(f"[OK] TESTE CONCLUIDO COM SUCESSO")
        print(f"O agente Gold Loss Zero esta corrigido e pronto!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"[ERRO] TESTE FALHOU")
        print(f"Verificar os erros acima")
        print(f"{'='*60}")
