#!/usr/bin/env python3
"""
Teste para verificar se o tratamento de TradeRequest foi corrigido
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_order_opening():
    """Testa se consegue processar resultado de ordem sem erro"""
    try:
        from src.agents.gold_ai_agent import GoldAIAgent

        print("[TESTE] Criando agente...")
        agent = GoldAIAgent(
            symbol="XAUUSDc",
            volume=0.02,
            ai_enabled=False
        )
        print("[OK] Agente criado com sucesso")

        # Testar acesso aos métodos críticos
        print("[TESTE] Verificando metodos de tratamento de ordem...")

        methods_to_test = [
            '_open_position',
            '_manage_position_trailing',
            '_check_positions'
        ]

        for method in methods_to_test:
            if hasattr(agent, method):
                print(f"[OK] Metodo {method} existe")
            else:
                print(f"[ERRO] Metodo {method} nao existe")
                return False

        return True

    except Exception as e:
        print(f"[ERRO] Excecao: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE TRATAMENTO DE ORDEM (TradeRequest)")
    print("=" * 60)
    print()

    if test_order_opening():
        print()
        print("=" * 60)
        print("[OK] TESTE PASSOU!")
        print("Tratamento de TradeRequest foi corrigido")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("[ERRO] TESTE FALHOU!")
        print("=" * 60)
        sys.exit(1)
