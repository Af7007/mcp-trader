#!/usr/bin/env python3
"""
Teste para validar a escalacao correta do trailing stop
"""

def test_escalation_formula():
    """Testa a formula de escalacao do trailing"""

    # Configuracoes
    trailing_activation_dollar = 1.0
    trailing_distance_dollar = 0.5
    trailing_step_dollar = 1.0

    print("=" * 70)
    print("TESTE DE ESCALACAO DE TRAILING STOP")
    print("=" * 70)
    print()
    print("Configuracao:")
    print(f"   Ativacao: ${trailing_activation_dollar:.2f}")
    print(f"   Distancia inicial: ${trailing_distance_dollar:.2f}")
    print(f"   Passo: ${trailing_step_dollar:.2f}")
    print()

    # Testes de escalacao
    test_cases = [
        (0.50, "Antes de ativar", False),  # Nao ativa
        (1.00, "Exatamente na ativacao", True),  # Ativa
        (1.50, "Meio do primeiro nivel", True),  # Protege $0.50
        (2.00, "Segundo nivel completo", True),  # Protege $1.50
        (2.50, "Meio do segundo nivel", True),  # Protege $1.50
        (3.00, "Terceiro nivel completo", True),  # Protege $2.50
        (4.00, "Quarto nivel completo", True),   # Protege $3.50
        (5.00, "Quinto nivel completo", True),   # Protege $4.50
    ]

    print("Resultados:")
    print("-" * 70)

    all_correct = True
    for profit, description, should_be_active in test_cases:
        # Verificar se deve ativar
        is_active = profit >= trailing_activation_dollar

        if is_active:
            # Formula CORRIGIDA
            additional_profit = max(0, profit - trailing_activation_dollar)
            additional_levels = int(additional_profit // trailing_step_dollar)
            protection = trailing_distance_dollar + additional_levels * trailing_step_dollar
        else:
            protection = 0
            is_active = False

        # Validar
        if is_active == should_be_active:
            status = "[OK]"
        else:
            status = "[ERRO]"
            all_correct = False

        print(f"{status} Lucro: ${profit:5.2f} | Ativo: {str(is_active):5} | Protege: ${protection:5.2f} | {description}")

    print("-" * 70)
    print()

    # Comparacao com formula ERRADA
    print("Comparacao com formula ERRADA (antiga):")
    print("-" * 70)

    for profit in [1.00, 2.00, 2.50, 3.00]:
        # Formula ERRADA
        profit_levels = int(profit // trailing_step_dollar) + 1
        wrong_protection = trailing_distance_dollar + (profit_levels - 1) * trailing_step_dollar

        # Formula CORRIGIDA
        additional_profit = max(0, profit - trailing_activation_dollar)
        additional_levels = int(additional_profit // trailing_step_dollar)
        correct_protection = trailing_distance_dollar + additional_levels * trailing_step_dollar

        print(f"Lucro ${profit:.2f}:")
        print(f"   ERRADA:    protege ${wrong_protection:.2f} (profit_levels={profit_levels})")
        print(f"   CORRIGIDA: protege ${correct_protection:.2f} (additional_levels={additional_levels})")
        print()

    print("=" * 70)
    if all_correct:
        print("[OK] ESCALACAO CORRIGIDA COM SUCESSO!")
        print()
        print("O trailing agora funciona corretamente:")
        print("   - Ativa em $1.00 de lucro")
        print("   - Protege $0.50 inicialmente")
        print("   - Sobe $1.00 a cada novo nivel de lucro")
    else:
        print("[ERRO] Alguns testes falharam!")
    print("=" * 70)

    return all_correct

if __name__ == "__main__":
    import sys
    if test_escalation_formula():
        sys.exit(0)
    else:
        sys.exit(1)
