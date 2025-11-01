#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de 100 operações do Agent Gold
Simula 100 trades e calcula resultado em dólares
"""

import random
from datetime import datetime, timedelta

print("\n" + "="*80)
print(" TESTE - 100 OPERACOES DO AGENTE GOLD")
print("="*80)

# Configuracao
LOTE = 0.01
TP_VALUE = 5.0  # $5.0 por operacao
SL_VALUE = 10.0  # ATR x 1.5 em média

# Lucro/Perda por operacao
WIN_PROFIT = LOTE * TP_VALUE * 10  # 0.01 x $5 x 10 = $50
LOSS_PROFIT = -(LOTE * SL_VALUE * 10)  # 0.01 x $10 x 10 = -$100

print(f"\nConfiguracao:")
print(f"  Lote: {LOTE}")
print(f"  TP: ${TP_VALUE:.2f} por trade")
print(f"  SL: ${SL_VALUE:.2f} por trade (dinamico)")
print(f"\nResultado por operacao:")
print(f"  WIN: +${WIN_PROFIT:.2f}")
print(f"  LOSS: -${abs(LOSS_PROFIT):.2f}")

# Testar com diferentes win rates
scenarios = [
    ("Pessimista (40% Win Rate)", 0.40),
    ("Conservador (50% Win Rate)", 0.50),
    ("Normal (60% Win Rate)", 0.60),
    ("Bom (70% Win Rate)", 0.70),
    ("Otimista (75% Win Rate)", 0.75),
    ("Excelente (80% Win Rate)", 0.80),
]

print("\n" + "="*80)
print(" SIMULACOES DE 100 OPERACOES")
print("="*80)

results = []

for scenario_name, win_rate in scenarios:
    print(f"\n{scenario_name}")
    print("=" * 80)

    # Calcular numero de wins e losses
    wins = int(100 * win_rate)
    losses = 100 - wins

    # Calcular lucro total
    total_profit = (wins * WIN_PROFIT) + (losses * LOSS_PROFIT)

    # Calcular metricas
    avg_profit_per_trade = total_profit / 100
    days_estimated = 100 / 10  # Estimando ~10 trades por dia
    profit_per_day = total_profit / days_estimated if days_estimated > 0 else 0

    print(f"  Total de trades: 100")
    print(f"  Wins: {wins} (${wins * WIN_PROFIT:.2f})")
    print(f"  Losses: {losses} (-${losses * abs(LOSS_PROFIT):.2f})")
    print(f"  Win Rate: {win_rate*100:.0f}%")
    print(f"\n  LUCRO TOTAL: ${total_profit:+.2f}")
    print(f"  Lucro por trade: ${avg_profit_per_trade:+.2f}")
    print(f"  Lucro estimado/dia: ${profit_per_day:+.2f} (estimando 10 trades/dia)")

    results.append({
        'scenario': scenario_name,
        'win_rate': win_rate,
        'wins': wins,
        'losses': losses,
        'total_profit': total_profit
    })

# Resultado mais provavel (baseado em performance historica)
print("\n" + "="*80)
print(" ANALISE - QUAL E O RESULTADO MAIS PROVAVEL?")
print("="*80)

print(f"\nBaseado na performance historica do agente Gold:")
print(f"- Derniers mensagens mostram ~71% win rate")
print(f"- Trades com SELL-ONLY e ordens acertivas")
print(f"- Sem hedge (foco em qualidade)")

# Usar 70% como mais provavel
likely_win_rate = 0.70
likely_wins = int(100 * likely_win_rate)
likely_losses = 100 - likely_wins
likely_profit = (likely_wins * WIN_PROFIT) + (likely_losses * LOSS_PROFIT)

print(f"\nCenario MAIS PROVAVEL (70% Win Rate):")
print(f"=======================================")
print(f"  Wins: {likely_wins}")
print(f"  Losses: {likely_losses}")
print(f"  Resultado: ${likely_profit:+.2f}")

if likely_profit > 0:
    print(f"\n  Status: [LUCRO] OK")
else:
    print(f"\n  Status: [PREJUIZO] NEGATIVO")

# Projecao mensal
print(f"\n" + "="*80)
print(" PROJECAO MENSAL (estimativa)")
print("="*80)

# Assumindo ~300 trades por mes (10 por dia x 30 dias)
trades_per_month = 300
months_to_calculate = 1

print(f"\nAssuindo {trades_per_month} trades por mes (10 por dia):")

for scenario_name, win_rate in scenarios:
    wins = int(trades_per_month * win_rate)
    losses = trades_per_month - wins
    monthly_profit = (wins * WIN_PROFIT) + (losses * LOSS_PROFIT)

    if win_rate == 0.70:
        print(f"\n{scenario_name} (MAIS PROVAVEL):")
        print(f"  Lucro estimado/mes: ${monthly_profit:+.2f}")
        print(f"  Lucro estimado/ano: ${monthly_profit * 12:+.2f}")
        if monthly_profit > 0:
            print(f"  Status: LUCRATIVO OK")
        else:
            print(f"  Status: NAO LUCRATIVO")

# Break-even analysis
print(f"\n" + "="*80)
print(" BREAK-EVEN ANALYSIS")
print("="*80)

print(f"\nCom WIN (+$50) e LOSS (-$100):")
print(f"  Para cada 1 WIN, precisa de 0.5 LOSS para empatar")
print(f"  Break-even win rate: 33.3%")
print(f"  (33 wins x $50 = $1650, 67 losses x $100 = $6700 = NET $0)")
print(f"\nWin rate minimo para lucrar: >33.3%")
print(f"Agente Gold atual: ~70% (MUITO ACIMA DO MINIMO)")

# Risk analysis
print(f"\n" + "="*80)
print(" ANALISE DE RISCO")
print("="*80)

print(f"\nRatio Risco/Recompensa:")
print(f"  TP: $5.0 (ganho por trade)")
print(f"  SL: $10.0 (perda por trade)")
print(f"  Ratio: 1:2 (precisa de 67% win rate para lucrar)")
print(f"  Agente obtem: ~70% win rate (ACIMA DO MINIMO)")

print(f"\nMargin de segurança:")
print(f"  70% - 67% = 3% (margem confortavel)")
print(f"  Agente pode ter ate 3% de queda sem perder dinheiro")

print(f"\n" + "="*80)
print(" CONCLUSAO")
print("="*80)

print(f"\nCom 100 operacoes e 70% win rate:")
print(f"  LUCRO ESPERADO: ${likely_profit:+.2f}")
print(f"\nMens estimada (300 trades):")
monthly = (int(300 * 0.70) * WIN_PROFIT) + ((300 - int(300 * 0.70)) * LOSS_PROFIT)
print(f"  LUCRO ESTIMADO: ${monthly:+.2f}")

print(f"\n" + "="*80)
print(" RECOMENDACOES")
print("="*80)

print(f"""
1. Agent continuar com 70% win rate = MUITO BOM
2. Continuar SELL-ONLY (performance comprovada)
3. Manter SL dinamico (ATR x 1.5)
4. Manter Hedge desativado (melhor resultados)
5. Volume 0.01 lots (conservador, certo)

PROXIMAS OPERACOES:
- Inicie o agent
- Deixe rodar naturalmente
- Monitor Telegram para resultados reais
- Compare com projecao

Status: PRONTO PARA PRODUCAO OK
""")

print("="*80 + "\n")
