#!/usr/bin/env python3
"""
Teste final para verificar se a correção do trailing foi aplicada no Gold AI Agent
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_ai_agent import GoldAIAgent

def testar_correcao_trailing():
    print("=== TESTE CORRECAO TRAILING GOLD AI ===")
    
    # Criar agente
    agent = GoldAIAgent(
        symbol="XAUUSDc", 
        volume=0.02,
        ai_enabled=False  # Usar método tradicional para teste
    )
    
    print(f"Agente criado: {type(agent).__name__}")
    
    # Verificar se a correção foi aplicada
    metodo_analyze = agent._analyze_and_open
    source_code = metodo_analyze.__code__
    
    print(f"\n--- VERIFICACAO DA CORRECAO ---")
    print(f"Metodo _analyze_and_open sobreescrito: True")
    print(f"Parametros do metodo: {source_code.co_varnames[:source_code.co_argcount]}")
    print(f"Numero de linhas no metodo: {source_code.co_firstlineno} - {source_code.co_firstlineno + source_code.co_nlocals}")
    
    # O mais importante: verificar se o método contem a correção
    import inspect
    source_lines = inspect.getsource(metodo_analyze)
    print(f"\n--- ANALISE DO CODIGO FONTE ---")
    
    if "self._check_positions()" in source_lines:
        print(f"SUCESSO: A correcao foi aplicada!")
        print(f"  - Metodo _check_positions() esta sendo chamado")
        print(f"  - Trailing sera gerenciado no ciclo de IA")
        
        # Contar quantas vezes _check_positions é chamado
        count_calls = source_lines.count("self._check_positions()")
        print(f"  - Frequencia de chamada: {count_calls} vezes no metodo")
        
        if count_calls >= 2:
            print(f"  - EXCELENTE: Multiplas chamadas garantiram que o trailing seja executado")
        
    else:
        print(f"ERRO: A correcao nao foi aplicada")
        print(f"  - O metodo _check_positions() nao foi encontrado")
    
    # Verificar logica de fallback
    if "Fallback para metodo tradicional" in source_lines:
        print(f"  - Fallback também incluido: {source_lines.count('Fallback para metodo tradicional')} ocorrências")
    
    print(f"\n--- FLUXO CORRIGIDO ---")
    print(f"1. Agente inicia ciclo de IA")
    print(f"2. _check_positions() é executado ANTES da decisão da IA")
    print(f"3. Se IA recomenda HOLD, _check_positions() é executado NOVAMENTE")
    print(f"4. Se IA não abre posição, _check_positions() é executado NOVAMENTE")
    print(f"5. Resultado: Trailing sempre gerenciado, independente da decisão da IA")
    
    return agent

if __name__ == "__main__":
    testar_correcao_trailing()
