#!/usr/bin/env python3
"""Verifica informacoes reais do simbolo XAUUSDc no MT5"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

def check_gold_info():
    print("="*60)
    print("VERIFICANDO INFORMACOES XAUUSDc NO MT5")
    print("="*60)
    
    try:
        mt5 = get_mt5_client()
        
        # Informacoes do simbolo
        print("\n[SYMBOL INFO - XAUUSDc]")
        info = mt5.get_symbol_info('XAUUSDc')
        
        if info:
            print(f"Point: {info.get('point')}")
            print(f"Trade Tick Value: ${info.get('trade_tick_value')}")
            print(f"Trade Tick Size: {info.get('trade_tick_size')}")
            print(f"Trade Contract Size: {info.get('trade_contract_size')}")
            print(f"Volume Min: {info.get('volume_min')}")
            print(f"Volume Max: {info.get('volume_max')}")
            print(f"Volume Step: {info.get('volume_step')}")
            print(f"Digits: {info.get('digits')}")
            
            # Calcular point value
            point = info.get('point', 0.001)
            tick_value = info.get('trade_tick_value', 0)
            tick_size = info.get('trade_tick_size', 0)
            
            print("\n[CALCULOS]")
            print(f"Point: {point}")
            print(f"Tick Value: ${tick_value}")
            print(f"Tick Size: {tick_size}")
            
            if tick_size > 0:
                point_value_per_lot = tick_value / tick_size * point
                print(f"Point Value por lote: ${point_value_per_lot:.4f}")
                
                # Teste com volume 0.02
                test_volume = 0.02
                point_value_for_volume = point_value_per_lot * test_volume
                print(f"\nCom volume {test_volume}:")
                print(f"  1 ponto = ${point_value_for_volume:.4f}")
                
                # Exemplo: 3000 pontos (SL tipico)
                test_pontos = 3000
                test_dinheiro = test_pontos * point_value_for_volume
                print(f"  {test_pontos} pontos = ${test_dinheiro:.2f}")
                
        else:
            print("ERRO: Simbolo XAUUSDc nao encontrado!")
            
        # Informacoes da conta
        print("\n[ACCOUNT INFO]")
        account = mt5.get_account_info()
        if account:
            print(f"Currency: {account.get('currency')}")
            print(f"Balance: ${account.get('balance'):.2f}")
            print(f"Equity: ${account.get('equity'):.2f}")
            print(f"Leverage: 1:{account.get('leverage')}")
            print(f"Margin Free: ${account.get('margin_free'):.2f}")
            
            # Verificar se eh conta cents
            currency = account.get('currency', '')
            if 'cent' in currency.lower() or 'usd' in currency.lower():
                print(f"\nTipo de conta: CENTS (currency: {currency})")
            else:
                print(f"\nTipo de conta: STANDARD (currency: {currency})")
                
        # Verificar preco atual
        print("\n[PRECO ATUAL]")
        tick = mt5.get_symbol_info_tick('XAUUSDc')
        if tick:
            print(f"Bid: ${tick.get('bid'):.3f}")
            print(f"Ask: ${tick.get('ask'):.3f}")
            print(f"Spread: {(tick.get('ask', 0) - tick.get('bid', 0)) / point:.0f} pontos")
            
        print("\n" + "="*60)
        print("VERIFICACAO CONCLUIDA")
        print("="*60)
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_gold_info()
