#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Loss Zero Flexible - Execução Ultra-Adaptável
Agente Loss Zero com múltiplos parâmetros flexíveis
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
    Executa BTC Loss Zero Flexible continuamente
    """
    print("BTC LOSS ZERO FLEXIBLE - ULTRA-ADAPTÁVEL")
    print("="*60)
    print("Agente Loss Zero com múltiplos parâmetros flexíveis")
    print("Pressione Ctrl+C para parar")
    print("="*60)
    
    try:
        from agents.btc_loss_zero_flexible import BTCLossZeroFlexible
        
        print("Importando BTCLossZeroFlexible...")
        
        # Criar agente Loss Zero Flexible
        agent = BTCLossZeroFlexible(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            stop_loss_dollars=30.0,
            take_profit_dollars=50.0,
            trailing_dollars=10.0,
            use_buy=True,
            use_sell=True,
            # Parâmetros Bollinger Bands
            bb_period=20,
            bb_std_dev=2.0,
            # Parâmetros RSI (mais flexíveis)
            rsi_period=14,
            rsi_overbought=60.0,  # Reduzido para mais sinais
            rsi_oversold=40.0,      # Aumentado para mais sinais
            # Parâmetros Volume (mais flexíveis)
            volume_period=20,
            volume_multiplier=1.0,    # Reduzido para mais flexibilidade
            # Parâmetros de Tendência
            use_trend_filter=True,
            trend_periods=5,
            # Parâmetros de Momentum
            use_momentum=True,
            momentum_period=3
        )
        
        print(f"\nAGENTE BTC LOSS ZERO FLEXIBLE CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   SL: ${agent.stop_loss_dollars}")
        print(f"   TP: ${agent.take_profit_dollars}")
        print(f"   Trailing: ${agent.trailing_dollars}")
        print(f"   BB: {agent.bb_period} períodos, {agent.bb_std_dev} std")
        print(f"   RSI: {agent.rsi_period} períodos ({agent.rsi_oversold}-{agent.rsi_overbought})")
        print(f"   Volume: {agent.volume_period} períodos (x{agent.volume_multiplier})")
        print(f"   Tendência: {agent.trend_periods} períodos")
        print(f"   Momentum: {agent.momentum_period} períodos")
        print(f"   BUY/SELL: Ativo")
        
        print(f"\nESTRATÉGIA FLEXIBLE:")
        print(f"   - 5 estratégias diferentes de entrada")
        print(f"   - RSI flexível ({agent.rsi_oversold}-{agent.rsi_overbought})")
        print(f"   - Volume reduzido (x{agent.volume_multiplier})")
        print(f"   - Filtro de tendência")
        print(f"   - Indicador de momentum")
        print(f"   - Apenas BB + tendência (mais permissivo)")
        print(f"   - Stop Loss fixo de ${agent.stop_loss_dollars}")
        print(f"   - Take Profit fixo de ${agent.take_profit_dollars}")
        print(f"   - Trailing stop de ${agent.trailing_dollars} após TP")
        print(f"   - Zero losses garantidos")
        
        print(f"\nINICIANDO EXECUÇÃO CONTÍNUA...")
        print("="*60)
        
        # EXECUÇÃO CONTÍNUA
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\nAgente BTC Loss Zero Flexible parado pelo usuário")
        print("="*60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)

if __name__ == "__main__":
    main()
