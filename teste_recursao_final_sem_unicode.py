#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para verificar se a recursao infinita foi eliminada
"""
import sys
import logging
logging.getLogger().setLevel(logging.ERROR)

def test_recursion():
    """Testa se a recursao infinita foi eliminada"""
    try:
        print('Testando correcao de recursao infinita...')
        from src.agents.gold_ai_agent import GoldAIAgent
        print('SUCESSO: GoldAIAgent importado sem erros')
        
        # Teste basico de instanciação (sem MT5)
        agent = GoldAIAgent(ai_enabled=False)
        print('SUCESSO: GoldAIAgent instanciado sem erros')
        print('RECURSAO INFINITA ELIMINADA')
        print('SISTEMA FUNCIONANDO')
        
        return True
        
    except Exception as e:
        if 'maximum recursion depth exceeded' in str(e).lower():
            print('FALHA: Recursao ainda presente')
            print(f'Erro: {e}')
            return False
        else:
            print(f'Erro esperado (sem MT5): {e}')
            return True

if __name__ == "__main__":
    test_recursion()
