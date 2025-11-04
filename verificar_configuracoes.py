#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica configurações do agente corrigido
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.btc_loss_zero_simple import BTCLossZeroSimple

def main():
    print("="*70)
    print("VERIFICACAO DE CONFIGURACOES - BTC LOSS ZERO v1.1")
    print("="*70)
    print()

    # Criar agente SEM executar
    print("Criando agente com configuracoes padrao...")
    print()

    agent = BTCLossZeroSimple(symbol="BTCUSDc")

    print()
    print("="*70)
    print("CONFIGURACOES ATUAIS")
    print("="*70)
    print()

    print(f"1. VOLUME:")
    print(f"   Configurado: {agent.volume} lotes")
    print(f"   Esperado: 0.01 lotes")
    print(f"   Status: {'OK' if agent.volume == 0.01 else 'ERRO!'}")
    print()

    print(f"2. MULTIPLICADORES SL/TRAILING:")
    print(f"   SL multiplier: {agent.sl_atr_mult}")
    print(f"   Esperado: 2.0")
    print(f"   Status: {'OK' if agent.sl_atr_mult == 2.0 else 'ERRO!'}")
    print()
    print(f"   Trailing activation: {agent.trailing_activation_mult}")
    print(f"   Esperado: 0.6")
    print(f"   Status: {'OK' if agent.trailing_activation_mult == 0.6 else 'ERRO!'}")
    print()
    print(f"   Trailing distance: {agent.trailing_distance_mult}")
    print(f"   Esperado: 0.4")
    print(f"   Status: {'OK' if agent.trailing_distance_mult == 0.4 else 'ERRO!'}")
    print()

    print(f"3. ATR:")
    print(f"   ATR atual: {agent.current_atr} pontos")
    print(f"   Minimo esperado: 150-180 pontos")
    # Simular calculo de ATR
    try:
        from core.mt5_direct_client import get_mt5_client
        mt5 = get_mt5_client()
        rates = mt5.copy_rates_from_pos(symbol="BTCUSDc", timeframe="M5", start_pos=0, count=14)
        if rates:
            atr = agent._calculate_atr_simple(rates)
            print(f"   ATR calculado: {atr} pontos")
            print(f"   Status: {'OK' if atr >= 150 else 'ALERTA: Muito baixo!'}")
        else:
            print(f"   Nao foi possivel calcular ATR (MT5 offline?)")
    except Exception as e:
        print(f"   Erro ao calcular ATR: {e}")
    print()

    print(f"4. CIRCUIT BREAKER:")
    print(f"   Max perdas consecutivas: {agent.max_consecutive_losses}")
    print(f"   Cooldown: {agent.circuit_breaker_cooldown}s = {agent.circuit_breaker_cooldown/60:.0f} min")
    print()

    print(f"5. HORARIOS BLOQUEADOS:")
    print(f"   Total de periodos: {len(agent.blacklisted_hours)}")
    for start, end in agent.blacklisted_hours:
        print(f"   - {start:02d}:00 - {end:02d}:00 UTC")
    print()

    print(f"6. COOLDOWN ENTRE TRADES:")
    print(f"   Cooldown: {agent.cooldown_seconds}s")
    print()

    # Testar validacao de volume
    print("="*70)
    print("TESTE DE VALIDACAO DE VOLUME")
    print("="*70)
    print()

    test_volumes = [0.005, 0.01, 0.05, 0.1, 0.3, 1.0, 2.0]
    for vol in test_volumes:
        agent_test = BTCLossZeroSimple(symbol="BTCUSDc", volume=vol)
        result = "OK" if agent_test.volume <= 0.1 else "ERRO"
        print(f"   Volume {vol} -> {agent_test.volume} [{result}]")

    print()
    print("="*70)
    print("VERIFICACAO COMPLETA")
    print("="*70)
    print()

    # Verificar se tudo esta OK
    checks = [
        ("Volume padrao", agent.volume == 0.01),
        ("SL multiplier", agent.sl_atr_mult == 2.0),
        ("Trailing activation", agent.trailing_activation_mult == 0.6),
        ("Trailing distance", agent.trailing_distance_mult == 0.4),
    ]

    all_ok = all([check[1] for check in checks])

    for check_name, check_result in checks:
        status = "OK" if check_result else "FALHOU"
        print(f"   [{status}] {check_name}")

    print()
    if all_ok:
        print("Status geral: TODAS AS CONFIGURACOES CORRETAS!")
        print()
        print("O agente esta pronto para testes.")
    else:
        print("Status geral: ALGUMAS CONFIGURACOES INCORRETAS!")
        print()
        print("Verifique o codigo antes de executar.")

    print()


if __name__ == "__main__":
    main()
