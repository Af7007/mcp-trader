#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do BTC Logger
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.btc_logger import BTCLogger

def testar_logger():
    """
    Testa se o BTC Logger está funcionando
    """
    print("TESTE DO BTC LOGGER")
    print("=" * 50)
    
    try:
        # Criar logger
        logger = BTCLogger()
        print("OK BTC Logger criado com sucesso!")
        
        # Testar log de ciclo
        print("\n1. Testando log de ciclo...")
        cycle_data = {
            'cycle_number': 999,
            'symbol': "BTCUSDc",
            'price': 110000.0,
            'bb_upper': 110100.0,
            'bb_middle': 110000.0,
            'bb_lower': 109900.0,
            'bb_position': "MIDDLE",
            'rsi': 50.0,
            'rsi_overbought': 70.0,
            'rsi_oversold': 30.0,
            'volume_current': 1000.0,
            'volume_avg': 800.0,
            'volume_multiplier': 1.25,
            'trend': "NEUTRAL",
            'momentum': 0.0,
            'signal_type': "BUY",
            'signal_strength': "3",
            'signal_reason': "Teste manual",
            'signal_price': 110000.0,
            'sl_price': 109970.0,
            'tp_price': 110050.0,
            'order_result': "10009",
            'order_error': "",
            'agent_version': "1.0.0"
        }
        logger.log_cycle(cycle_data)
        print("OK Ciclo logado com sucesso!")
        
        # Testar log de trade
        print("\n2. Testando log de trade...")
        trade_data = {
            'trade_type': "BUY",
            'entry_price': 110000.0,
            'sl_price': 109970.0,
            'tp_price': 110050.0,
            'volume': 0.05,
            'symbol': "BTCUSDc",
            'agent_version': "1.0.0",
            'reason': "Teste manual",
            'status': "OPEN"
        }
        logger.log_trade(trade_data)
        print("OK Trade logado com sucesso!")
        
        # Testar update de performance
        print("\n3. Testando update de performance...")
        logger.update_strategy_performance(
            strategy_name="Teste",
            signal_type="BUY",
            signal_strength="3",
            success=True,
            profit_loss=50.0
        )
        print("OK Performance atualizada com sucesso!")
        
        print("\n" + "=" * 50)
        print("TODOS OS TESTES PASSARAM!")
        print("O BTC Logger está funcionando corretamente!")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_logger()
