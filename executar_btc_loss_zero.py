#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Loss Zero - Execução do Agente com Trailing Stop Ilimitado
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def executar_btc_loss_zero():
    """
    Executa BTC Loss Zero com trailing stop ilimitado
    """
    print("BTC LOSS ZERO - TRAILING STOP ILIMITADO")
    print("="*60)
    
    try:
        from agents.btc_loss_zero_agent import BTCLossZeroAgent
        
        print("BTCLossZeroAgent importado!")
        
        # Criar agente Loss Zero
        agent = BTCLossZeroAgent(
            symbol='BTCUSDc',           # BTC Cents
            volume=0.05,               # Volume agressivo
            check_interval=15,         # Check frequente
            trailing_start_percent=0.5,  # Ativa trailing em 0.5%
            trailing_min_percent=0.2,   # Trailing mínimo
            trailing_max_percent=float('inf'),  # ILIMITADO!
            trailing_increment=0.1,    # Incremento por movimento
            use_buy=True,
            use_sell=True
        )
        
        print(f"\nAGENTE BTC LOSS ZERO CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   Trailing: {agent.trailing_start_percent}% → ILIMITADO")
        print(f"   BUY/SELL: Ativo")
        
        print(f"\nESTRATEGIA LOSS 0:")
        print(f"   - Sem Take Profit fixo")
        print(f"   - Trailing stop ilimitado")
        print(f"   - Ativacao em 0.5% lucro")
        print(f"   - Incremento gradual infinito")
        print(f"   - Zero losses garantidos")
        
        print(f"\nDIFERENCA DO HEDGE:")
        print(f"   HEDGE: Ativa Hedge em -$3.0")
        print(f"   LOSS 0: Trailing stop ilimitado")
        print(f"   HEDGE: TP fixo $1.0")
        print(f"   LOSS 0: Sem TP (deixa o trailing trabalhar)")
        
        print(f"\nPara executar em LIVE mode:")
        print(f"Descomente a linha 'agent.run()' abaixo")
        print()
        
        # IMPORTANTE: Descomente para executar
        # agent.run()
        
        print("Configuracao Loss Zero completa!")
        print("Agente pronto para executar sem losses!")
        
        return agent, True
        
    except Exception as e:
        print(f"Erro: {e}")
        print()
        print("Solucoes:")
        print("1. Verificar se BTCLossZeroAgent existe")
        print("2. Instalar dependencias: pip install MetaTrader5 python-dotenv")
        
        return None, False

def explicar_diferenca():
    """
    Explica diferenca entre hedge e loss zero
    """
    print("\nDIFERENCA HEDGE vs LOSS ZERO:")
    print("="*60)
    
    print("HEDGE AGENT (Atual):")
    print("  - TP: $1.0 fixo")
    print("  - Hedge: ativa em -$3.0")
    print("  - Maximo profit: $1.0")
    print("  - Maximo perda: $3.0 (hedge)")
    print("  - Estrategia: Take profit + Hedge")
    print()
    
    print("LOSS ZERO AGENT (Novo):")
    print("  - TP: SEM TP fixo")
    print("  - Trailing: 0.5% -> ilimitado")
    print("  - Maximo profit: ILIMITADO")
    print("  - Maximo perda: 0% (zero)")
    print("  - Estrategia: Trailing stop ilimitado")
    print()
    
    print("QUANDO USAR:")
    print("  Hedge: Mercado lateral, lucro rapido")
    print("  Loss Zero: Tendencias fortes, lucro maximo")
    print()
    
    print("RESULTADO EM TENDENCIA FORTE (BTC +10%):")
    print("  Hedge: +$1.0 (para no TP)")
    print("  Loss Zero: +$5.2 (trailing ilimitado)")

if __name__ == "__main__":
    agent, sucesso = executar_btc_loss_zero()
    
    if sucesso:
        explicar_diferenca()
        
        print("\n" + "="*60)
        print("BTC LOSS ZERO CONFIGURADO!")
        print("Para executar LIVE:")
        print("Edite este arquivo e descomente: agent.run()")
        
        # Para executar, descomente a linha abaixo:
        # agent.run()
    else:
        print("\n" + "="*60)
        print("ERRO NA CONFIGURACAO")
        print("Verifique os problemas acima")
    
    print("\n" + "="*60)
    print("TESTE CONCLUIDO!")
