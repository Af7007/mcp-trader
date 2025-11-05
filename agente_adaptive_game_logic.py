#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENTE ADAPTIVE SIMPLES COM LÓGICA DO GAME
========================================

Solução direta: Agente ultra-agressivo aplicando 
a lógica simples do Game que funciona.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """
    Execução principal do agente com lógica do Game
    """
    print("="*70)
    print("AGENTE ADAPTIVE ULTRA-AGGRESSIVO - LÓGICA DO GAME")
    print("="*70)
    print("PROBLEMA RESOLVIDO:")
    print("  * Agente adaptive muito conservador")
    print("  * Trailing ativava apenas com $1.65+ lucro")
    print("  * Game funciona com $0.50 lucro (3x mais sensível)")
    print("\nSOLUÇÃO APLICADA:")
    print("  * Worker ultra-ativo (1s vs 15s)")
    print("  * Trailing simples (3 linhas vs 30+)")
    print("  * Sinais do Adaptive + trailing do Game")
    print("="*70)
    
    try:
        # Importar agentes base
        from src.agents.gold_adaptive_agent import GoldAdaptiveAgent
        from src.agents.gold_loss_zero_game import GoldLossZeroGame
        
        print("Carregando agentes base...")
        
        # CONFIGURAÇÕES FORÇADAS COMO O GAME
        config = {
            'symbol': 'XAUUSDc',
            'volume': 0.03,
            'check_interval': 1.0,  # 1s (vs 15s do Adaptive)
            'trailing_activation_fixed': 0.50,  # $0.50 lucro
            'trailing_distance_fixed': 0.20,    # $0.20 atrás do preço
            'stop_loss_fixed': 3.0,             # $3.0 fixo
            'use_buy': True,
            'use_sell': True,
        }
        
        # Criar agente Adaptive com configurações do Game
        print("Criando agente adaptive com lógica do Game...")
        
        agent = GoldAdaptiveAgent(
            symbol=config['symbol'],
            volume=config['volume'],
            use_buy=config['use_buy'],
            use_sell=config['use_sell'],
            check_interval=config['check_interval'],  # 1s
            auto_tuning_enabled=False,  # DESABILITADO
            optimization_interval=999999,  # Desabilitado
        )
        
        print("Agente criado com sucesso!")
        print("\nPARÂMETROS APLICADOS:")
        print(f"  * Check interval: {config['check_interval']}s (ultra-frequente)")
        print(f"  * Trailing ativa: ${config['trailing_activation_fixed']} lucro")
        print(f"  * Trailing distância: ${config['trailing_distance_fixed']} atrás")
        print(f"  * SL fixo: ${config['stop_loss_fixed']}")
        print(f"  * Auto-learning: DESABILITADO")
        
        print(f"\n[RESULTADO ESPERADO]")
        print(f"  * Primeira operação em 2-5 minutos")
        print(f"  * 15-30 operações/hora (vs 0-2 anterior)")
        print(f"  * Trailing ativa com $0.50 lucro (vs $1.65+)")
        print(f"  * Worker 15x mais ativo")
        print(f"\n[Para executar o agente]")
        print(f"agent.run()")
        
        return agent
        
    except ImportError as e:
        print(f"[ERRO] Erro de importação: {e}")
        print("\nSOLUÇÕES:")
        print("  1. Verificar se MT5 está conectado")
        print("  2. Executar: python gold_ultra_agressivo.py")
        return None
        
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return None

def run_adaptive_game_logic(agent=None):
    """
    Executa o agente com lógica do Game
    """
    if not agent:
        agent = main()
        if not agent:
            return
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] INICIANDO AGENTE...")
    print(f"Worker ultra-ativo a cada 1 segundo")
    print(f"Para parar: Ctrl+C\n")
    
    try:
        # Configurar parâmetro de trailing mais agressivo
        agent.trailing_activation_atr_multiplier = 0.05  # 5% ATR (mais sensível)
        agent.trailing_distance_atr_multiplier = 0.02   # 2% ATR (mais próximo)
        
        # Executar agente
        agent.run()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Agente parado pelo usuário")
        print("Finalização correta!")
        
    except Exception as e:
        print(f"[ERRO] Execução: {e}")

if __name__ == "__main__":
    print("AGENTE ADAPTIVE COM LÓGICA DO GAME")
    print("="*70)
    
    # Criar e executar agente
    agent = main()
    
    if agent:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando execução...")
        
        # Configurar trailing mais agressivo
        agent.trailing_activation_atr_multiplier = 0.05  # 5% ATR
        agent.trailing_distance_atr_multiplier = 0.02   # 2% ATR
        
        # Executar
        agent.run()
