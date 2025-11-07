#!/usr/bin/env python3
"""
Teste rápido para verificar se a recursão foi corrigida no gold_ai_agent
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Testa se consegue importar o módulo sem erro"""
    try:
        from src.agents.gold_ai_agent import GoldAIAgent
        print("[OK] Importacao bem-sucedida")
        return True
    except RecursionError as e:
        print(f"[ERRO] Erro de recursao durante importacao: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro durante importacao: {e}")
        return False

def test_class_init():
    """Testa se consegue criar instância sem erro de recursão"""
    try:
        from src.agents.gold_ai_agent import GoldAIAgent

        # Desabilitar IA para teste mais rápido
        agent = GoldAIAgent(
            symbol="XAUUSDc",
            volume=0.02,
            ai_enabled=False
        )
        print("[OK] Instancia criada com sucesso")
        return True
    except RecursionError as e:
        print(f"[ERRO] Erro de recursao ao criar instancia: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao criar instancia: {type(e).__name__}: {e}")
        return False

def test_method_exists():
    """Verifica se os métodos principais existem"""
    try:
        from src.agents.gold_ai_agent import GoldAIAgent

        agent = GoldAIAgent(ai_enabled=False)

        # Verificar métodos críticos
        methods = [
            '_analyze_and_open',
            '_check_positions',
            '_analyze_traditional_fallback',
            '_get_simple_signal',
            '_open_position'
        ]

        for method in methods:
            if not hasattr(agent, method):
                print(f"[ERRO] Metodo {method} nao encontrado")
                return False
            print(f"  [OK] Metodo {method} existe")

        return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar metodos: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CORRECAO - RECURSAO INFINITA")
    print("=" * 60)
    print()

    print("1. Testando importacao...")
    if not test_import():
        sys.exit(1)
    print()

    print("2. Testando criacao de instancia...")
    if not test_class_init():
        sys.exit(1)
    print()

    print("3. Testando existencia de metodos...")
    if not test_method_exists():
        sys.exit(1)
    print()

    print("=" * 60)
    print("[OK] TODOS OS TESTES PASSARAM!")
    print("A recursao foi corrigida com sucesso!")
    print("=" * 60)
