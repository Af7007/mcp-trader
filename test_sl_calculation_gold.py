#!/usr/bin/env python3
"""Testa calculo de SL para Gold"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def test_sl_calculation():
    print("="*60)
    print("TESTE DE CALCULO DE SL - GOLD XAUUSDc")
    print("="*60)
    
    try:
        mt5 = get_mt5_client()
        
        # Obter info do simbolo
        print("\n[1] OBTER SYMBOL INFO")
        info = mt5.get_symbol_info('XAUUSDc')
        if not info:
            print("ERRO: Simbolo nao encontrado!")
            return
        
        symbol_point = info.get('point', 0.001)
        print(f"Symbol Point: {symbol_point}")
        
        # Obter preco atual
        print("\n[2] OBTER PRECO ATUAL")
        tick = mt5.get_symbol_info_tick('XAUUSDc')
        if not tick:
            print("ERRO: Tick nao encontrado!")
            return
        
        bid = tick.get('bid')
        ask = tick.get('ask')
        print(f"Bid: ${bid:.3f}")
        print(f"Ask: ${ask:.3f}")
        
        # Simular calculo de SL (SELL position)
        print("\n[3] SIMULAR CALCULO DE SL (SELL)")
        market_price = bid
        sl_pontos = 3000
        
        print(f"\nParametros:")
        print(f"  Market Price (BID): ${market_price:.3f}")
        print(f"  SL Pontos: {sl_pontos}")
        print(f"  Symbol Point: {symbol_point}")
        
        print(f"\nCalculo CORRETO:")
        sl_price_distance = sl_pontos * symbol_point
        sl_price_correto = market_price + sl_price_distance
        print(f"  sl_price_distance = {sl_pontos} * {symbol_point} = ${sl_price_distance:.3f}")
        print(f"  sl_price = ${market_price:.3f} + ${sl_price_distance:.3f} = ${sl_price_correto:.3f}")
        
        print(f"\nCalculo ERRADO (sem multiplicar por symbol_point):")
        sl_price_errado = market_price + sl_pontos
        print(f"  sl_price = ${market_price:.3f} + {sl_pontos} = ${sl_price_errado:.3f}")
        
        print(f"\nDIFERENCA:")
        diferenca = abs(sl_price_correto - sl_price_errado)
        print(f"  Correto: ${sl_price_correto:.3f}")
        print(f"  Errado:  ${sl_price_errado:.3f}")
        print(f"  Diff:    ${diferenca:.3f}")
        
        # Verificar se SL seria valido
        print(f"\n[4] VALIDACAO")
        risco_dinheiro = sl_price_distance * 0.02  # volume 0.02
        print(f"Risco com volume 0.02: ${risco_dinheiro:.2f}")
        
        if abs(risco_dinheiro - 6.0) < 0.1:
            print("VALIDACAO: CORRETO! Risco = $6.00")
        else:
            print(f"VALIDACAO: INCORRETO! Esperado $6.00, obtido ${risco_dinheiro:.2f}")
        
        print("\n" + "="*60)
        print("TESTE CONCLUIDO")
        print("="*60)
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sl_calculation()
