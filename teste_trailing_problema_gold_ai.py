#!/usr/bin/env python3
"""
Teste para verificar por que o trailing não ativa no Gold AI Agent
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_ai_agent import GoldAIAgent

def testar_trailing_gold_ai():
    print("=== TESTE TRAILING GOLD AI AGENT ===")
    
    # Criar agente
    agent = GoldAIAgent(
        symbol="XAUUSDc",
        volume=0.02,
        ai_enabled=False  # Desabilitar IA para teste tradicional
    )
    
    print(f"Agente criado: {type(agent).__name__}")
    print(f"Herda de: {type(agent).__bases__[0].__name__}")
    
    # Verificar se herda métodos de trailing
    print(f"\n--- METODOS HERDADOS ---")
    print(f"Tem _check_positions: {hasattr(agent, '_check_positions')}")
    print(f"Tem _manage_trailing: {hasattr(agent, '_manage_trailing')}")
    print(f"Tem _manage_position_trailing: {hasattr(agent, '_manage_position_trailing')}")
    print(f"Tem _open_position: {hasattr(agent, '_open_position')}")
    
    # Verificar se o método não foi sobreescrito
    metodo_heranca = agent.__class__.__bases__[0].__dict__.get('_check_positions')
    metodo_atual = agent.__class__.__dict__.get('_check_positions')
    
    print(f"\n--- ANALISE DE OVERRIDE ---")
    print(f"_check_positions está sobreescrito: {metodo_heranca is not None and metodo_atual is not None and metodo_heranca != metodo_atual}")
    print(f"ID do método herdado: {id(metodo_heranca) if metodo_heranca else 'N/A'}")
    print(f"ID do método atual: {id(metodo_atual) if metodo_atual else 'N/A'}")
    
    # Verificar variáveis de trailing
    print(f"\n--- VARIAVEIS DE TRAILING ---")
    print(f"trailing_active: {getattr(agent, 'trailing_active', 'N/A')}")
    print(f"trailing_activation_dollar: {getattr(agent, 'trailing_activation_dollar', 'N/A')}")
    print(f"trailing_distance_dollar: {getattr(agent, 'trailing_distance_dollar', 'N/A')}")
    print(f"position_worker: {getattr(agent, 'position_worker', 'N/A')}")
    
    # Verificar se método _check_positions da classe pai é chamado corretamente
    print(f"\n--- FLUXO DE EXECUCAO ---")
    print(f"run() está sobreescrito: {'_run' in agent.__class__.__dict__}")
    print(f" Métodos que agent pode chamar:")
    for attr in sorted(dir(agent)):
        if not attr.startswith('_') or attr in ['_check_positions', '_analyze_and_open', '_manage_trailing']:
            print(f"   {attr}")
    
    print(f"\n--- PROBLEMA IDENTIFICADO ---")
    print(f"O GoldAI sobreescreve _analyze_and_open() para usar IA")
    print(f"Quando abre posição via IA, herda _open_position() corretamente")
    print(f"Mas o método _check_positions() que gerencia trailing pode não estar sendo chamado")
    print(f"no ciclo correto quando há posições abertas via IA")
    
    return agent

if __name__ == "__main__":
    testar_trailing_gold_ai()
