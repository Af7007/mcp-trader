#!/usr/bin/env python3
"""
Teste para verificar se os atributos da IA foram inicializados corretamente
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_ai_attributes():
    """Verifica se todos os atributos da IA foram inicializados"""
    try:
        from src.agents.gold_ai_agent import GoldAIAgent

        agent = GoldAIAgent(
            symbol="XAUUSDc",
            volume=0.02,
            ai_enabled=False
        )

        # Verificar atributos críticos
        required_attrs = [
            'ai_consecutive_errors',
            'ai_max_consecutive_errors',
            'ai_error_cooldown',
            'ai_error_cooldown_until',
            'ai_decisions',
            'ai_response_times',
            'last_ai_decision_time',
            'last_ai_action'
        ]

        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(agent, attr):
                missing_attrs.append(attr)
                print(f"[ERRO] Atributo ausente: {attr}")
            else:
                value = getattr(agent, attr)
                print(f"[OK] {attr} = {value}")

        if missing_attrs:
            print(f"\n[ERRO] Atributos faltando: {missing_attrs}")
            return False

        return True

    except Exception as e:
        print(f"[ERRO] Excecao: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE ATRIBUTOS DA IA")
    print("=" * 60)
    print()

    if test_ai_attributes():
        print()
        print("=" * 60)
        print("[OK] TODOS OS ATRIBUTOS INICIALIZADOS!")
        print("=" * 60)
        sys.exit(0)
    else:
        sys.exit(1)
