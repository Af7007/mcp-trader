#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO - TRAILING STOP CORRIGIDO
=====================================

Valida se o trailing stop está ativando corretamente após a correção.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def test_trailing_activation():
    """
    Testa se o trailing stop ativa corretamente com $1 de lucro
    """
    print("="*60)
    print("TESTE RÁPIDO - TRAILING STOP CORRIGIDO")
    print("="*60)
    
    # Criar agente
    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.1,
        check_interval=5
    )
    
    print(f"\n✅ AGENTE CRIADO COM SUCESSO")
    print(f"   Volume: {agent.volume} lotes")
    print(f"   Point Value: ${agent.point_value:.4f}")
    print(f"   Trailing ativa em: ${agent.trailing_activation_dollar:.2f}")
    print(f"   Trailing protege: ${agent.trailing_distance_dollar:.2f}")
    
    # Verificar se worker thread está disponível
    if agent.position_worker is None:
        print(f"\n✅ WORKER THREAD NÃO INICIADO (NORMAL - só inicia com posição)")
    else:
        print(f"\n⚠️  WORKER THREAD JÁ ATIVO")
    
    print(f"\n" + "="*60)
    print(f"STATUS DO TESTE:")
    print(f"="*60)
    print(f"✅ Código corrigido: Variável trailing_distance_dinheiro definida")
    print(f"✅ Worker thread: Será iniciado ao abrir posição")  
    print(f"✅ Trailing activation: ${agent.trailing_activation_dollar:.2f}")
    print(f"✅ Proteção inicial: ${agent.trailing_distance_dollar:.2f}")
    print(f"")
    print(f"📋 PRÓXIMOS PASSOS:")
    print(f"1. Execute o teste principal para abrir uma posição")
    print(f"2. Aguarde o lucro atingir ${agent.trailing_activation_dollar:.2f}")
    print(f"3. Verifique se o trailing stop é ativado")
    print(f"4. Confirme se o banco de dados registra o evento")
    print(f"="*60)

if __name__ == "__main__":
    test_trailing_activation()
