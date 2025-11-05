#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTAR AGENTE ADAPTIVE COM LÓGICA DO GAME
==========================================

Agente corrigido que aplica a lógica simples e eficaz do Game
que tem trailing stop funcionando corretamente.
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """
    Execução principal do agente com lógica do Game
    """
    print("="*70)
    print("🚀 EXECUTANDO AGENTE ADAPTIVE COM LÓGICA DO GAME")
    print("="*70)
    print("🎯 PROBLEMA RESOLVIDO:")
    print("   • Agente adaptive era muito conservador")
    print("   • Trailing ativava apenas com $1.65+ lucro")
    print("   • Game funciona com $0.10 lucro (16x mais sensível)")
    print("\n🔧 SOLUÇÃO APLICADA:")
    print("   • Sinais do Adaptive + Trailing do Game")
    print("   • Worker 15x mais ativo (1s vs 15s)")
    print("   • Lógica ultra-simples (3 linhas vs 30+)")
    print("   • Trailing com $0.50 lucro (vs $1.65+)")
    print("="*70)
    
    try:
        # Importar agente com lógica do Game
        from src.agents.gold_adaptive_agent_GAME_LOGIC import create_adaptive_agent_game_logic
        
        print("📦 Carregando agente...")
        
        # Criar agente
        agent = create_adaptive_agent_game_logic()
        
        print("✅ Agente carregado com sucesso!")
        print("\n⏱️ RESULTADO ESPERADO:")
        print("   • Primeira operação em 2-5 minutos")
        print("   • 15-30 operações/hora (vs 0-2 anterior)")
        print("   • Trailing ativa com $0.50 lucro")
        print("   • Logs mostram atividade constante")
        print("\n⏹️ Para parar: Ctrl+C")
        print("="*70)
        
        # Executar agente
        print(f"\n[{agent._get_time()}] Iniciando...")
        agent.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n📋 AÇÃO NECESSÁRIA:")
        print("   1. Execute primeiro: python testar_game_logic_agent.py")
        print("   2. Verificar se arquivo existe")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Agente parado pelo usuário")
        print("✅ Finalização correta!")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"\n📋 SOLUÇÕES:")
        print("   1. Verificar se MT5 está conectado")
        print("   2. Confirmar símbolo XAUUSDc disponível")
        print("   3. Execute validação: python testar_game_logic_agent.py")

if __name__ == "__main__":
    main()
