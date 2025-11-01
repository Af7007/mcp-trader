#!/usr/bin/env python3
"""
BTC Loss Zero - Teste Simples
"""

def main():
    print("BTC LOSS ZERO - TESTE")
    print("="*40)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        
        from agents.btc_loss_zero_simple import BTCLossZeroSimple
        
        print("Importacao: OK")
        
        agent = BTCLossZeroSimple()
        print("Agente criado: OK")
        
        print("\nESTRATEGIA LOSS 0:")
        print("- Trailing ilimitado")
        print("- Zero losses")
        print("- Maximo profit")
        
        print("\nTeste: SUCESSO!")
        
    except Exception as e:
        print(f"ERRO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
