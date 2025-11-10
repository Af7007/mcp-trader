"""
Script de teste para validar melhorias da versao 2.0.0 do agente Gold
Verifica se todas as mudancas foram aplicadas corretamente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

print("="*80)
print("TESTE DE VALIDACAO - GOLD AGENT v2.0.0")
print("="*80)

# Criar instancia do agente
agent = GoldLossZeroSimple(
    symbol="XAUUSDc",
    volume=0.03,
    fixed_sl_dollars=5.0
)

print("\n[1] PARAMETROS PRINCIPAIS")
print("-"*80)
print(f"Symbol: {agent.symbol}")
print(f"Volume: {agent.volume}")
print(f"Fixed SL: ${agent.fixed_sl_dollars}")
print(f"SL ATR Multiplier (deprecated): {agent.sl_atr_mult}")

print("\n[2] TRAILING STOP - OTIMIZADO PARA SCALPING")
print("-"*80)
print(f"Activation: ${agent.trailing_activation_dollar} (esperado: $2.00)")
print(f"Distance: ${agent.trailing_distance_dollar} (esperado: $1.00)")
print(f"Profit Step: ${agent.profit_step_for_increment_dollar} (esperado: $1.50)")
print(f"Protection Increment: ${agent.protection_increment_dollar} (esperado: $1.00)")

# Validacoes
ts_ok = agent.trailing_activation_dollar == 2.0
print(f"\n[VALIDACAO TS] {'[OK]' if ts_ok else '[FALHA]'} - Activation = $2.00")

print("\n[3] FILTROS DE QUALIDADE - NOVOS")
print("-"*80)
print(f"Min Score M5: {agent.min_score_m5} (esperado: 4.0)")
print(f"Max ATR M5: ${agent.max_atr_m5_dollars} (esperado: $2.00)")
print(f"Max Spread: ${agent.max_spread_dollars} (esperado: $0.50)")

# Validacoes
score_ok = agent.min_score_m5 == 4.0
atr_ok = agent.max_atr_m5_dollars == 2.0
spread_ok = agent.max_spread_dollars == 0.5

print(f"\n[VALIDACAO FILTROS]")
print(f"  Min Score M5: {'[OK]' if score_ok else '[FALHA]'}")
print(f"  Max ATR M5: {'[OK]' if atr_ok else '[FALHA]'}")
print(f"  Max Spread: {'[OK]' if spread_ok else '[FALHA]'}")

print("\n[4] METODOS - VERIFICACAO DE EXISTENCIA")
print("-"*80)

# Verificar se metodos novos existem
has_analyze_m5 = hasattr(agent, '_analyze_m5_trend')
has_confirm_m1 = hasattr(agent, '_confirm_m1_timing')
has_m15_check = hasattr(agent, '_check_m15_trend')  # Deve ser False

print(f"_analyze_m5_trend: {'[OK] Existe' if has_analyze_m5 else '[FALHA] Nao encontrado'}")
print(f"_confirm_m1_timing: {'[OK] Existe' if has_confirm_m1 else '[FALHA] Nao encontrado'}")
print(f"_check_m15_trend: {'[OK] Removido' if not has_m15_check else '[FALHA] Ainda existe'}")

print("\n[5] RESUMO DA VALIDACAO")
print("="*80)

all_ok = ts_ok and score_ok and atr_ok and spread_ok and has_analyze_m5 and has_confirm_m1 and not has_m15_check

if all_ok:
    print("[OK] TODAS AS MELHORIAS FORAM APLICADAS COM SUCESSO!")
    print("\nMelhorias implementadas:")
    print("  [OK] Trailing Stop ativa com $2.00")
    print("  [OK] Score minimo M5 = 4.0")
    print("  [OK] Filtro ATR M5 (max $2.00)")
    print("  [OK] Filtro Spread (max $0.50)")
    print("  [OK] Metodo _analyze_m5_trend criado")
    print("  [OK] Metodo _confirm_m1_timing criado")
    print("  [OK] Metodo _check_m15_trend removido")
    print("\nAgente Gold v2.0.0 pronto para uso!")
else:
    print("[FALHA] ALGUMAS MELHORIAS NAO FORAM APLICADAS")
    print("\nVerifique os itens marcados como [FALHA] acima")

print("\n" + "="*80)
print("Proximos passos:")
print("1. Executar agente em modo de teste")
print("2. Monitorar 10-20 trades")
print("3. Analisar win rate e resultados")
print("4. Comparar com versao anterior (v1.3.0)")
print("="*80)
