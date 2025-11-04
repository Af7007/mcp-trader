#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de operação BTC Loss Zero com configuração atual
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def exemplo_operacao():
    """
    Demonstra exemplo de operação com config atual
    """
    print("="*80)
    print("EXEMPLO DE OPERAÇÃO - BTC LOSS ZERO")
    print("="*80)
    print()

    # Configuração atual
    volume = 1.0
    sl_distance = 30.0
    tp_distance = 50.0
    trailing_distance = 10.0

    print("[CONFIGURAÇÃO ATUAL]")
    print(f"   Volume: {volume} lote")
    print(f"   Stop Loss: ${sl_distance}")
    print(f"   Take Profit: ${tp_distance} (para ativar trailing)")
    print(f"   Trailing: ${trailing_distance} de distância")
    print()

    # Obter preço atual
    mt5 = get_mt5_client()
    tick = mt5.get_symbol_info_tick("BTCUSDc")

    if not tick:
        print("ERRO: Não foi possível obter preço do BTCUSDc")
        return

    bid = tick['bid']
    ask = tick['ask']

    print("[PREÇO ATUAL DO BTCUSDc]")
    print(f"   Bid (venda): ${bid:,.2f}")
    print(f"   Ask (compra): ${ask:,.2f}")
    print()

    # Exemplo 1: Posição SELL
    print("="*80)
    print("EXEMPLO 1: POSIÇÃO SELL (Venda)")
    print("="*80)
    print()

    entry_sell = bid
    sl_sell = entry_sell + sl_distance
    tp_sell = entry_sell - tp_distance

    print("[PASSO 1] ABERTURA DA POSIÇÃO")
    print(f"   Sinal: SELL (RSI overbought)")
    print(f"   Entrada: ${entry_sell:,.2f} (preço Bid atual)")
    print(f"   Stop Loss: ${sl_sell:,.2f} (+${sl_distance})")
    print(f"   Take Profit: ${tp_sell:,.2f} (-${tp_distance})")
    print()
    print(f"   Risco: ${sl_distance} (se SL atingido)")
    print(f"   Recompensa: ${tp_distance} (se TP atingido)")
    print(f"   R:R = 1:{tp_distance/sl_distance:.2f}")
    print()

    print("[PASSO 2] AGUARDANDO LUCRO DE $50")
    print(f"   Posição aberta em ${entry_sell:,.2f}")
    print(f"   SL e TP ativos no MT5")
    print(f"   Trailing: INATIVO (aguardando ${tp_distance} de lucro)")
    print()

    # Simular atingir TP
    price_at_tp = entry_sell - tp_distance

    print("[PASSO 3] ATINGIU $50 DE LUCRO!")
    print(f"   Preço desceu para: ${price_at_tp:,.2f}")
    print(f"   Lucro atual: ${tp_distance} [OK]")
    print()
    print(f"   TRAILING ATIVADO!")
    print(f"   - Remove TP do MT5")
    print(f"   - Mantém SL inicial de ${sl_distance}")
    print(f"   - Trailing Stop: ${price_at_tp + trailing_distance:,.2f} (+${trailing_distance})")
    print()

    print("[PASSO 4] TRAILING EM AÇÃO")
    print(f"   Cenário A: Preço continua descendo (favorável)")
    price_a1 = price_at_tp - 5
    trailing_a1 = price_a1 + trailing_distance
    print(f"   - Preço vai para ${price_a1:,.2f}")
    print(f"   - Trailing atualiza: ${trailing_a1:,.2f}")
    print(f"   - Lucro protegido: ${entry_sell - trailing_a1:.2f}")
    print()

    price_a2 = price_a1 - 10
    trailing_a2 = price_a2 + trailing_distance
    print(f"   - Preço vai para ${price_a2:,.2f}")
    print(f"   - Trailing atualiza: ${trailing_a2:,.2f}")
    print(f"   - Lucro protegido: ${entry_sell - trailing_a2:.2f}")
    print()

    print(f"   Cenário B: Preço reverte ${trailing_distance}")
    price_b = trailing_a2 + 0.1  # Ligeiramente acima do trailing
    print(f"   - Preço sobe para ${price_b:,.2f}")
    print(f"   - TRAILING STOP ACIONADO!")
    print(f"   - Posição fechada com lucro de ${entry_sell - price_b:.2f}")
    print()

    print("[PASSO 5] APÓS FECHAMENTO")
    print(f"   Cooldown de 60 segundos ativado")
    print(f"   Agente aguarda antes de abrir nova posição")
    print(f"   Evita trades impulsivos")
    print()

    # Exemplo 2: Posição BUY
    print("="*80)
    print("EXEMPLO 2: POSIÇÃO BUY (Compra)")
    print("="*80)
    print()

    entry_buy = ask
    sl_buy = entry_buy - sl_distance
    tp_buy = entry_buy + tp_distance

    print("[PASSO 1] ABERTURA DA POSIÇÃO")
    print(f"   Sinal: BUY (RSI oversold)")
    print(f"   Entrada: ${entry_buy:,.2f} (preço Ask atual)")
    print(f"   Stop Loss: ${sl_buy:,.2f} (-${sl_distance})")
    print(f"   Take Profit: ${tp_buy:,.2f} (+${tp_distance})")
    print()

    print("[PASSO 2-5] Funcionamento idêntico ao SELL, mas invertido:")
    print(f"   - Aguarda preço subir ${tp_distance}")
    print(f"   - Ativa trailing em ${tp_buy:,.2f}")
    print(f"   - Trailing fica ${trailing_distance} ABAIXO do preço")
    print(f"   - Fecha se preço descer ${trailing_distance}")
    print()

    print("="*80)
    print("VANTAGENS DO SISTEMA LOSS ZERO")
    print("="*80)
    print()
    print("1. SL Fixo de $30: Risco sempre controlado")
    print("2. TP de $50: Garante lucro mínimo antes do trailing")
    print("3. Trailing de $10: Protege lucro com flexibilidade")
    print("4. Cooldown 60s: Evita trades consecutivos ruins")
    print("5. Sem TP no MT5 após trailing: Lucro ilimitado teoricamente")
    print()

    print("CENÁRIOS POSSÍVEIS:")
    print()
    print("Cenário 1 - SL Atingido (antes do trailing)")
    print(f"   Resultado: Prejuízo de ${sl_distance}")
    print()
    print("Cenário 2 - TP Atingido + Trailing Fecha")
    print(f"   Resultado: Lucro entre ${tp_distance} e ilimitado")
    print()
    print("Cenário 3 - Mercado Lateral")
    print(f"   Resultado: SL ou TP atingido eventualmente")
    print()

    print("="*80)
    print(f"Exemplo baseado em preço real: ${bid:,.2f}")
    print("="*80)

if __name__ == "__main__":
    exemplo_operacao()
