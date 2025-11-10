"""
Script de validacao para BTC v2.0.0
Verifica se parametros estao corretos e equivalentes ao Gold
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.btc_loss_zero_v2 import BTCLossZeroV2

print("="*80)
print("VALIDACAO - BTC AGENT v2.0.0")
print("="*80)

# Criar instancia
agent = BTCLossZeroV2(
    symbol="BTCUSDc",
    volume=0.30,
    fixed_sl_dollars=5.0
)

print("\n[1] PARAMETROS PRINCIPAIS - BTC vs GOLD")
print("-"*80)
print(f"{'Parametro':<30} {'BTC (v2.0.0)':<20} {'Gold (v2.0.0)':<20}")
print("-"*80)
print(f"{'Symbol':<30} {agent.symbol:<20} {'XAUUSDc':<20}")
print(f"{'Volume':<30} {agent.volume:<20} {'0.03':<20}")
print(f"{'Fixed SL':<30} ${agent.fixed_sl_dollars:<19} {'$5.00':<20}")
print(f"{'TS Activation':<30} ${agent.trailing_activation_dollar:<19} {'$2.00':<20}")
print(f"{'TS Distance':<30} ${agent.trailing_distance_dollar:<19} {'$1.00':<20}")
print(f"{'Min Score M5':<30} {agent.min_score_m5:<20} {'4.0':<20}")
print(f"{'Max ATR M5':<30} ${agent.max_atr_m5_dollars:<19} {'$2.00':<20}")
print(f"{'Max Spread':<30} ${agent.max_spread_dollars:<19} {'$0.50':<20}")

print("\n[2] POINT VALUE EQUIVALENTE")
print("-"*80)
# Point value deveria ser $0.003 para ambos
expected_point_value = 0.003
actual_point_value = agent.point_value * agent.volume

print(f"BTC Point Value (com volume {agent.volume}): ${actual_point_value:.4f}")
print(f"Gold Point Value (com volume 0.03): ${expected_point_value:.4f}")
print(f"Equivalente: {'[OK]' if abs(actual_point_value - expected_point_value) < 0.0001 else '[FALHA]'}")

print("\n[3] VALIDACOES")
print("-"*80)

# Validacoes
checks = {
    "Volume BTC = 0.30": agent.volume == 0.30,
    "SL fixo = $5.00": agent.fixed_sl_dollars == 5.0,
    "TS Activation = $2.00": agent.trailing_activation_dollar == 2.0,
    "TS Distance = $1.00": agent.trailing_distance_dollar == 1.0,
    "Min Score M5 = 4.0": agent.min_score_m5 == 4.0,
    "Max ATR = $2.00": agent.max_atr_m5_dollars == 2.0,
    "Max Spread = $0.50": agent.max_spread_dollars == 0.5,
    "Point Value equivalente": abs(actual_point_value - expected_point_value) < 0.0001
}

all_ok = True
for check_name, result in checks.items():
    status = "[OK]" if result else "[FALHA]"
    print(f"{status} {check_name}")
    if not result:
        all_ok = False

print("\n[4] METODOS - VERIFICACAO")
print("-"*80)
has_analyze_m5 = hasattr(agent, '_analyze_m5_trend')
has_confirm_m1 = hasattr(agent, '_confirm_m1_timing')
has_m15_check = hasattr(agent, '_check_m15_trend')

print(f"{'[OK]' if has_analyze_m5 else '[FALHA]'} _analyze_m5_trend existe")
print(f"{'[OK]' if has_confirm_m1 else '[FALHA]'} _confirm_m1_timing existe")
print(f"{'[OK]' if not has_m15_check else '[FALHA]'} _check_m15_trend removido")

print("\n[5] COMPARACAO DETALHADA")
print("="*80)
print("""
GOLD v2.0.0:
- Volume: 0.03 lotes
- Point: $0.001
- Tick Value: $0.10/lote
- Point Value: $0.003/ponto (com 0.03 lotes)
- SL: $5.00 = 1667 pontos = $1.667 distancia preco

BTC v2.0.0:
- Volume: 0.30 lotes
- Point: $0.01
- Tick Value: $0.01/lote
- Point Value: $0.003/ponto (com 0.30 lotes)
- SL: $5.00 = 1667 pontos = $16.67 distancia preco

EXPECTATIVA EM DOLARES: IDENTICA
- SL: $5.00 para ambos
- TS Activation: $2.00 para ambos
- TS Distance: $1.00 para ambos
- Avg Win esperado: $1.50-2.00 para ambos
- Avg Loss: -$5.00 para ambos
""")

print("="*80)
print("RESUMO FINAL")
print("="*80)

if all_ok and has_analyze_m5 and has_confirm_m1 and not has_m15_check:
    print("[OK] BTC v2.0.0 VALIDADO COM SUCESSO!")
    print("\nParametros BTC equivalentes ao Gold:")
    print("  [OK] Volume: 0.30 (vs Gold 0.03)")
    print("  [OK] Point Value: $0.003/ponto (IGUAL)")
    print("  [OK] SL/TS em dolares: IGUAIS")
    print("  [OK] Filtros e score: IGUAIS")
    print("  [OK] Metodos v2.0.0: Implementados")
    print("\nAgente BTC v2.0.0 pronto para uso!")
    print("Expectativa: Mesmos resultados em $ que Gold")
else:
    print("[FALHA] ALGUNS PARAMETROS NAO ESTAO CORRETOS")
    print("Revise os itens marcados como [FALHA]")

print("\n" + "="*80)
print("Proximo passo: Executar agente com RUN_BTC_V2.bat")
print("="*80)
