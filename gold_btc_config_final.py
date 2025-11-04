#!/usr/bin/env python3
"""
CONFIGURAÇÃO FINAL - GOLD E BTC
Volume: 0.02 lote
SL: $6.00
Trailing ativa: $1.00
Trailing sobe: $0.50
Worker: 0.5s
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
from agents.btc_loss_zero_simple import BTCLossZeroSimple

def calcular_configuracao(symbol, point_value_per_lot, atr_medio):
    """Calcula pontos necessários para atingir valores em $"""
    volume = 0.02

    # Valor de 1 ponto com o volume configurado
    point_value_with_volume = volume * point_value_per_lot

    # Converter $ para pontos
    sl_dollars = 6.00
    trailing_act_dollars = 1.00
    trailing_dist_dollars = 0.50

    sl_pontos = sl_dollars / point_value_with_volume
    trailing_act_pontos = trailing_act_dollars / point_value_with_volume
    trailing_dist_pontos = trailing_dist_dollars / point_value_with_volume

    # Calcular multiplicadores de ATR
    sl_mult = sl_pontos / atr_medio
    trailing_act_mult = trailing_act_pontos / atr_medio
    trailing_dist_mult = trailing_dist_pontos / atr_medio

    return {
        'volume': volume,
        'point_value': point_value_per_lot,
        'point_value_with_volume': point_value_with_volume,
        'atr_medio': atr_medio,
        'sl_pontos': sl_pontos,
        'sl_dollars': sl_dollars,
        'sl_mult': sl_mult,
        'trailing_act_pontos': trailing_act_pontos,
        'trailing_act_dollars': trailing_act_dollars,
        'trailing_act_mult': trailing_act_mult,
        'trailing_dist_pontos': trailing_dist_pontos,
        'trailing_dist_dollars': trailing_dist_dollars,
        'trailing_dist_mult': trailing_dist_mult
    }

# GOLD
print(f"\n{'='*70}")
print(f"CONFIGURAÇÃO GOLD E BTC - VALORES EM DÓLARES FIXOS")
print(f"{'='*70}\n")

gold_config = calcular_configuracao('XAUUSDc', 0.10, 60)
btc_config = calcular_configuracao('BTCUSDc', 0.01, 100)

print(f"GOLD (XAUUSDc):")
print(f"  Volume: {gold_config['volume']} lote")
print(f"  Point Value: ${gold_config['point_value']}/lote/pt")
print(f"  Com {gold_config['volume']} lote: 1 pt = ${gold_config['point_value_with_volume']:.4f}")
print(f"  ATR Médio: {gold_config['atr_medio']} pts")
print(f"")
print(f"  SL: {gold_config['sl_pontos']:.0f} pts = ${gold_config['sl_dollars']:.2f}")
print(f"    Multiplicador ATR: {gold_config['sl_mult']:.2f}")
print(f"  Trailing Ativa: {gold_config['trailing_act_pontos']:.0f} pts = ${gold_config['trailing_act_dollars']:.2f}")
print(f"    Multiplicador ATR: {gold_config['trailing_act_mult']:.2f}")
print(f"  Trailing Dist: {gold_config['trailing_dist_pontos']:.0f} pts = ${gold_config['trailing_dist_dollars']:.2f}")
print(f"    Multiplicador ATR: {gold_config['trailing_dist_mult']:.2f}")
print(f"")

print(f"BTC (BTCUSDc):")
print(f"  Volume: {btc_config['volume']} lote")
print(f"  Point Value: ${btc_config['point_value']}/lote/pt")
print(f"  Com {btc_config['volume']} lote: 1 pt = ${btc_config['point_value_with_volume']:.4f}")
print(f"  ATR Médio: {btc_config['atr_medio']} pts")
print(f"")
print(f"  SL: {btc_config['sl_pontos']:.0f} pts = ${btc_config['sl_dollars']:.2f}")
print(f"    Multiplicador ATR: {btc_config['sl_mult']:.2f}")
print(f"  Trailing Ativa: {btc_config['trailing_act_pontos']:.0f} pts = ${btc_config['trailing_act_dollars']:.2f}")
print(f"    Multiplicador ATR: {btc_config['trailing_act_mult']:.2f}")
print(f"  Trailing Dist: {btc_config['trailing_dist_pontos']:.0f} pts = ${btc_config['trailing_dist_dollars']:.2f}")
print(f"    Multiplicador ATR: {btc_config['trailing_dist_mult']:.2f}")
print(f"")
print(f"Worker: 0.5s (para ambos)")
print(f"\n{'='*70}\n")

# Escolher qual executar
print("Escolha qual agente executar:")
print("  1 - GOLD (XAUUSDc)")
print("  2 - BTC (BTCUSDc)")
print("  3 - AMBOS (paralelo)")
print()

escolha = input("Digite 1, 2 ou 3: ").strip()

if escolha == '1':
    print(f"\n{'='*70}")
    print(f"INICIANDO GOLD...")
    print(f"{'='*70}\n")

    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=gold_config['volume'],
        check_interval=0.5,
        stop_loss_atr_multiplier=gold_config['sl_mult'],
        trailing_activation_atr_multiplier=gold_config['trailing_act_mult'],
        trailing_distance_atr_multiplier=gold_config['trailing_dist_mult'],
        use_buy=True,
        use_sell=True
    )

    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nAgente GOLD parado pelo usuário")
        agent.stop()

elif escolha == '2':
    print(f"\n{'='*70}")
    print(f"INICIANDO BTC...")
    print(f"{'='*70}\n")

    agent = BTCLossZeroSimple(
        symbol="BTCUSDc",
        volume=btc_config['volume'],
        check_interval=0.5,
        stop_loss_atr_multiplier=btc_config['sl_mult'],
        trailing_activation_atr_multiplier=btc_config['trailing_act_mult'],
        trailing_distance_atr_multiplier=btc_config['trailing_dist_mult'],
        use_buy=True,
        use_sell=True
    )

    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nAgente BTC parado pelo usuário")
        agent.stop()

elif escolha == '3':
    print(f"\n{'='*70}")
    print(f"INICIANDO AMBOS...")
    print(f"{'='*70}\n")
    print("ERRO: Modo paralelo ainda não implementado.")
    print("Execute em 2 terminais separados:")
    print("  Terminal 1: python gold_btc_config_final.py (escolha 1)")
    print("  Terminal 2: python gold_btc_config_final.py (escolha 2)")
else:
    print("Opção inválida!")
