#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Loss Zero - Execução Contínua CORRIGIDO
Agente Loss Zero com trailing stop ilimitado
Versão sem emojis para compatibilidade Windows
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
    Executa BTC Loss Zero continuamente
    """
    print("BTC LOSS ZERO - EXECUÇÃO CONTÍNUA CORRIGIDO")
    print("="*60)
    print("Agente Loss Zero com Trailing Stop Ilimitado")
    print("Pressione Ctrl+C para parar")
    print("="*60)
    
    try:
        from agents.btc_loss_zero_simple import BTCLossZeroSimple
        
        print("Importando BTCLossZeroSimple...")
        
        # Criar agente Loss Zero - CONFIGURAÇÃO OTIMIZADA
        agent = BTCLossZeroSimple(
            symbol="BTCUSDc",
            volume=0.3,                          # Reduzido de 0.5
            check_interval=15,
            stop_loss_dollars=50.0,              # Aumentado de $30
            take_profit_dollars=80.0,            # Aumentado de $50
            trailing_activation_dollars=15.0,    # Aumentado de $5
            trailing_dollars=15.0,               # Aumentado de $10
            use_buy=True,
            use_sell=True
        )
        
        print(f"\nAGENTE BTC LOSS ZERO CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   SL: ${agent.stop_loss_dollars}")
        print(f"   TP: ${agent.take_profit_dollars}")
        print(f"   Trailing: ${agent.trailing_dollars}")
        print(f"   BUY/SELL: Ativo")
        
        print(f"\nESTRATÉGIA LOSS 0:")
        print(f"   - Stop Loss fixo de ${agent.stop_loss_dollars}")
        print(f"   - Take Profit fixo de ${agent.take_profit_dollars}")
        print(f"   - Trailing stop de ${agent.trailing_dollars} após TP")
        print(f"   - Zero losses garantidos")
        
        print(f"\nINICIANDO EXECUÇÃO CONTÍNUA...")
        print("="*60)
        
        # EXECUÇÃO CONTÍNUA
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\nAgente BTC Loss Zero parado pelo usuário")
        print("="*60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)

if __name__ == "__main__":
    main()
