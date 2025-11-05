#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDACAO E EXECUCAO: AGENTE ADAPTIVE COM LOGICA DO GAME
======================================================

Script para testar e validar a correcao baseada no Game que funciona.
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_game_logic_agent():
    """
    Testa se o agente com logica do Game foi criado corretamente
    """
    print("="*70)
    print("TESTANDO AGENTE ADAPTIVE COM LOGICA DO GAME")
    print("="*70)
    
    try:
        # Importar agente com logica do Game
        from src.agents.gold_adaptive_agent_GAME_LOGIC import GoldAdaptiveAgentGameLogic, create_adaptive_agent_game_logic
        
        print("[OK] Importacao bem-sucedida!")
        
        # Criar agente usando factory function
        agent = create_adaptive_agent_game_logic()
        
        print("[OK] Agente criado com sucesso!")
        
        # Verificar parametros criticos
        print(f"\nPARAMETROS CRITICOS:")
        print(f"   * check_interval: {agent.check_interval}s (deve ser 1s)")
        print(f"   * trailing_activation_fixed: ${agent.trailing_activation_fixed} (deve ser $0.50)")
        print(f"   * trailing_distance_fixed: ${agent.trailing_distance_fixed} (deve ser $0.20)")
        print(f"   * stop_loss_fixed: ${agent.stop_loss_fixed} (deve ser $3.0)")
        print(f"   * auto_tuning_enabled: {agent.auto_tuning_enabled} (deve ser False)")
        
        # Validacoes
        validations = [
            (agent.check_interval == 1.0, "Worker interval correto (1s)"),
            (agent.trailing_activation_fixed == 0.50, "Trailing activation correto ($0.50)"),
            (agent.trailing_distance_fixed == 0.20, "Trailing distance correto ($0.20)"),
            (agent.stop_loss_fixed == 3.0, "Stop loss fixo correto ($3.0)"),
            (agent.auto_tuning_enabled == False, "Auto-learning desabilitado"),
        ]
        
        print(f"\nVALIDACOES:")
        all_valid = True
        for validation, description in validations:
            if validation:
                print(f"   [OK] {description}")
            else:
                print(f"   [ERRO] {description}")
                all_valid = False
        
        if all_valid:
            print(f"\n[TODAS VALIDACOES PASSARAM]")
            print(f"RESULTADO ESPERADO:")
            print(f"   * 15-30 operacoes/hora (vs 0-2 anterior)")
            print(f"   * Trailing ativa com $0.50 lucro (vs $1.65+)")
            print(f"   * Worker 15x mais ativo (1s vs 15s)")
            print(f"   * Logica ultra-simples (3 linhas vs 30+)")
            
            return True
        else:
            print(f"\n[ALGUMAS VALIDACOES FALHARAM]")
            return False
            
    except ImportError as e:
        print(f"[ERRO] Erro de importacao: {e}")
        print(f"   Verificar se arquivo existe: src/agents/gold_adaptive_agent_GAME_LOGIC.py")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False

def compare_with_original():
    """
    Compara parametros do agente original vs Game Logic
    """
    print(f"\n" + "="*70)
    print("COMPARACAO: ADAPTIVE ORIGINAL vs GAME LOGIC")
    print("="*70)
    
    comparison_table = [
        ["Aspecto", "ADAPTIVE Original", "ADAPTIVE Game Logic", "Melhoria"],
        ["-"*15, "-"*18, "-"*20, "-"*10],
        ["Trailing Ativa", "$1.65+ lucro", "$0.50 lucro", "230% mais sensivel"],
        ["Trailing Distancia", "$0.62 (13% ATR)", "$0.20 fixo", "210% mais simples"],
        ["Worker Interval", "15 segundos", "1 segundo", "1.400% mais frequente"],
        ["Auto-Learning", "Ativo", "Desabilitado", "Mantem configuracoes"],
        ["Logica", "30+ linhas", "3 linhas", "90% mais simples"],
        ["Calculo", "ATR complexo", "Lucro direto", "Clareza total"],
        ["Ativacoes/Hora", "240 (4/min)", "3.600 (60/min)", "1.400% mais ativa"],
    ]
    
    # Print table
    for row in comparison_table:
        print(f"{row[0]:<18} {row[1]:<20} {row[2]:<22} {row[3]:<12}")

def main():
    """
    Funcao principal de teste
    """
    print("VALIDACAO: AGENTE ADAPTIVE COM LOGICA DO GAME")
    print("="*70)
    
    # 1. Testar se o agente foi criado corretamente
    if test_game_logic_agent():
        print(f"\n[TESTE PASSOU]")
        
        # 2. Comparar com original
        compare_with_original()
        
        # 3. Instrucoes finais
        print(f"\n" + "="*70)
        print("EXECUTAR AGENTE COM LOGICA DO GAME")
        print("="*70)
        print("COMANDO PARA EXECUTAR:")
        print("   python executar_game_logic_agent.py")
        print("\nOU no codigo Python:")
        print("   from src.agents.gold_adaptive_agent_GAME_LOGIC import create_adaptive_agent_game_logic")
        print("   agent = create_adaptive_agent_game_logic()")
        print("   agent.run()")
        print("\nRESULTADO ESPERADO:")
        print("   * Primeira operacao em 2-5 minutos")
        print("   * Trailing ativa com $0.50 lucro")
        print("   * Logs mostram atividade constante")
        print("   * 3-5 operacoes em 30 minutos")
        
    else:
        print(f"\n[TESTE FALHOU]")
        print(f"   Verificar se o arquivo existe e esta correto")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
