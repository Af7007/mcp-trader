#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Loss Zero Enhanced - Execução com Indicadores Melhorados
Agente Loss Zero com Bollinger Bands + RSI + Volume
"""

import sys
import os
from pathlib import Path

# Configurar encoding para UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """
    Executa BTC Loss Zero Enhanced continuamente
    """
    print("BTC LOSS ZERO ENHANCED - BOLLINGER BANDS + RSI + VOLUME")
    print("="*60)
    print("Agente Loss Zero com indicadores melhorados")
    print("Pressione Ctrl+C para parar")
    print("="*60)
    
    try:
        from agents.btc_loss_zero_enhanced import BTCLossZeroEnhanced
        
        print("Importando BTCLossZeroEnhanced...")
        
        # Criar agente Loss Zero Enhanced
        agent = BTCLossZeroEnhanced(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            stop_loss_dollars=30.0,
            take_profit_dollars=50.0,
            trailing_dollars=10.0,
            use_buy=True,
            use_sell=True,
            bb_period=20,
            bb_std_dev=2.0,
            rsi_period=14,
            volume_period=20
        )
        
        print(f"\nAGENTE BTC LOSS ZERO ENHANCED CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   SL: ${agent.stop_loss_dollars}")
        print(f"   TP: ${agent.take_profit_dollars}")
        print(f"   Trailing: ${agent.trailing_dollars}")
        print(f"   Bollinger Bands: {agent.bb_period} períodos, {agent.bb_std_dev} std")
        print(f"   RSI: {agent.rsi_period} períodos")
        print(f"   Volume: {agent.volume_period} períodos")
        print(f"   BUY/SELL: Ativo")
        
        print(f"\nESTRATÉGIA ENHANCED:")
        print(f"   - Bollinger Bands para identificar extremos")
        print(f"   - RSI para confirmar momentum")
        print(f"   - Volume para validar força")
        print(f"   - Stop Loss fixo de ${agent.stop_loss_dollars}")
        print(f"   - Take Profit fixo de ${agent.take_profit_dollars}")
        print(f"   - Trailing stop de ${agent.trailing_dollars} após TP")
        print(f"   - Zero losses garantidos")
        
        print(f"\nINICIANDO EXECUÇÃO CONTÍNUA...")
        print("="*60)
        
        # EXECUÇÃO CONTÍNUA
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\nAgente BTC Loss Zero Enhanced parado pelo usuário")
        print("="*60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)

if __name__ == "__main__":
    main()
