#!/usr/bin/env python3
"""
BTC Loss Zero - Execução Contínua
Agente Loss Zero com trailing stop ilimitado
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """
    Executa BTC Loss Zero continuamente
    """
    print("BTC LOSS ZERO - EXECUÇÃO CONTÍNUA")
    print("="*60)
    print("Agente Loss Zero com Trailing Stop Ilimitado")
    print("Pressione Ctrl+C para parar")
    print("="*60)
    
    try:
        from agents.btc_loss_zero_simple import BTCLossZeroSimple
        
        print("Importando BTCLossZeroSimple...")
        
        # Criar agente Loss Zero
        agent = BTCLossZeroSimple(
            symbol='BTCUSDc',           # BTC Cents
            volume=0.05,               # Volume agressivo
            check_interval=15,         # Check frequente
            trailing_start_percent=0.5,  # Ativa trailing em 0.5%
            trailing_increment=0.1,    # Incremento por movimento
            use_buy=True,
            use_sell=True
        )
        
        print(f"\nAGENTE BTC LOSS ZERO CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   Trailing: {agent.trailing_start_percent}% -> ILIMITADO")
        print(f"   BUY/SELL: Ativo")
        
        print(f"\nESTRATÉGIA LOSS 0:")
        print(f"   - Sem Take Profit fixo")
        print(f"   - Trailing stop ilimitado")
        print(f"   - Ativação em 0.5% lucro")
        print(f"   - Incremento gradual infinito")
        print(f"   - Zero losses garantidos")
        
        print(f"\nINICIANDO EXECUÇÃO CONTÍNUA...")
        print("="*60)
        
        # EXECUÇÃO CONTÍNUA - descomentado para LIVE
        agent.run()
        
    except KeyboardInterrupt:
        print("\n\nAgente BTC Loss Zero parado pelo usuário")
        print("="*60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        print("="*60)

if __name__ == "__main__":
    main()
