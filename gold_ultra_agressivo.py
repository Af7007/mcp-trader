#!/usr/bin/env python3
"""
GOLD ULTRA-AGGRESSIVE - Script simples
Modifica configuracoes para ser 78% mais responsivo
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Importar agente existente
from agents.gold_loss_zero_simple import GoldLossZeroSimple


def main():
    print("="*70)
    print("GOLD ULTRA-AGGRESSIVE - CONFIGURACAO ATUALIZADA")
    print("="*70)
    print("MODIFICACOES APLICADAS:")
    print("- Trailing ativa: 78% menor (era 0.35 -> agora 0.075)")
    print("- Trailing distancia: 88% menor (era 0.35 -> agora 0.04)") 
    print("- Volume: 5x maior (era 0.01 -> agora 0.05)")
    print("- Check interval: 3x mais rapido (era 15s -> agora 5s)")
    print("- Cooldown: 24x mais rapido (era 120s -> agora 5s)")
    print("- SEM auto-learning (configuracoes fixas)")
    print("="*70)
    print("")
    
    # Criar agente com configuracoes ultra-agressivas
    agent = GoldLossZeroSimple(
        symbol='XAUUSDc',
        volume=0.05,  # 5x maior
        check_interval=5,  # 3x mais rapido
        stop_loss_atr_multiplier=3.0,  # 40% menor
        trailing_activation_atr_multiplier=0.075,  # 78% menor!
        trailing_distance_atr_multiplier=0.04,  # 88% menor!
        use_buy=True,
        use_sell=True
    )
    
    # Forcar cooldown ultra-rapido
    agent.cooldown_seconds = 5
    agent.cooldown_same_direction = 1
    
    print("CONFIGURACOES ULTRA-AGGRESSIVES:")
    print(f"- Trailing ativa em: ${agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos):.2f}")
    print(f"- Volume: {agent.volume}")
    print(f"- Check a cada: {agent.check_interval}s")
    print(f"- Cooldown: {agent.cooldown_seconds}s")
    print("")
    print("OBJETIVO: Abrir 3-5 posicoes em 15-20 minutos")
    print("PARA PARAR: Ctrl+C")
    print("")
    
    # Executar agente
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n[STOP] Agente parado pelo usuario")


if __name__ == "__main__":
    main()
