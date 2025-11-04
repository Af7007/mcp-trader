#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from core.mt5_direct_client import get_mt5_client

mt5 = get_mt5_client()
if mt5:
    info = mt5.get_symbol_info('XAUUSDc')
    if info:
        print('XAUUSDc Symbol Info:')
        print(f'  Point: {info.get("point")}')
        print(f'  Trade contract size: {info.get("trade_contract_size")}')
        print(f'  Trade tick value: {info.get("trade_tick_value")}')
        print(f'  Trade tick size: {info.get("trade_tick_size")}')

        # Calcular point value correto
        contract_size = info.get('trade_contract_size', 1.0)
        point = info.get('point', 0.001)
        tick_value = info.get('trade_tick_value')

        if tick_value:
            print(f'  Point value per lot: ${tick_value:.4f}')
            print(f'  Point value per 0.01 lot: ${tick_value * 0.01:.6f}')
        else:
            point_value = contract_size * point
            print(f'  Calculated point value per lot: ${point_value:.4f}')
            print(f'  For cents account (divide by 100): ${point_value/100:.6f}')
            print(f'  Point value per 0.01 lot: ${(point_value/100) * 0.01:.8f}')
    else:
        print('Could not get symbol info')
else:
    print('MT5 not connected')
