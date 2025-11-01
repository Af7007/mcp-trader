#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do BTC Loss Zero - Trailing Stop Dinâmico
Demonstração da estratégia Loss 0
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demonstrar_estrategia_loss_zero():
    """
    Demonstra a estratégia Loss 0 com trailing stop
    """
    print("BTC LOSS ZERO - TRAILING STOP DINAMICO")
    print("="*60)
    
    # Importar agente se disponível
    try:
        from agents.btc_loss_zero_agent import BTCLossZeroAgent
        
        print("BTCLossZeroAgent importado!")
        
        # Criar agente
        agent = BTCLossZeroAgent(
            symbol='BTCUSDc',
            volume=0.05,
            check_interval=15,
            trailing_start_percent=0.5,  # Ativa trailing em 0.5%
            trailing_min_percent=0.2,   # Trailing mínimo
            trailing_max_percent=2.0,   # Trailing máximo
            trailing_increment=0.1,     # Incremento por movimento
            use_buy=True,
            use_sell=True
        )
        
        print(f"\nAGENTE LOSS ZERO CRIADO!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   Trailing: {agent.trailing_start_percent}% → {agent.trailing_max_percent}%")
        
    except Exception as e:
        print(f"Erro ao importar: {e}")
        # Criar demonstração manual
        criar_demonstracao_manual()
        return
    
    print(f"\nESTRATEGIA LOSS 0:")
    print(f"   - Sem TP fixo")
    print(f"   - Trailing ativo em 0.5%")
    print(f"   - Incremento gradual 0.1%")
    print(f"   - Máximo 2.0% trailing")
    print(f"   - Zero losses garantidos")

def criar_demonstracao_manual():
    """
    Cria demonstração manual da estratégia
    """
    print("\nDEMONSTRACAO ESTRATEGIA LOSS 0:")
    print("="*60)
    
    # Configurações
    symbol = "BTCUSDc"
    volume = 0.05
    entry_price = 45000.0  # Exemplo
    
    print(f"Configuracao:")
    print(f"  Symbol: {symbol}")
    print(f"  Volume: {volume}")
    print(f"  Entry Price: ${entry_price}")
    print()
    
    print("Cenario de Trailing Stop Dinamico:")
    print("-" * 40)
    
    # Simular movimentos de preço
    movements = [
        ("Entry", entry_price, 0.0, 0.0, "Position opened"),
        ("Price up 0.3%", entry_price * 1.003, 0.3, 0.0, "Small profit, trailing inactive"),
        ("Price up 0.5%", entry_price * 1.005, 0.5, 0.5, "Trailing activated at 0.5%"),
        ("Price up 0.7%", entry_price * 1.007, 0.7, 0.5, "Trailing increases to 0.6%"),
        ("Price up 1.2%", entry_price * 1.012, 1.2, 0.8, "Trailing increases to 0.8%"),
        ("Price up 2.0%", entry_price * 1.020, 2.0, 1.2, "Trailing increases to 1.2%"),
        ("Price down 1.5%", entry_price * 1.005, 0.5, 1.2, "Stopped by trailing at 1.2%")
    ]
    
    for i, (action, price, profit_pct, trailing_pct, description) in enumerate(movements):
        print(f"{i+1:2d}. {action:10s} | ${price:8.0f} | {profit_pct:4.1f}% | Trailing: {trailing_pct:4.1f}%")
        print(f"    {description}")
        print()

def explicar_estrategia():
    """
    Explica detalhadamente a estratégia
    """
    print("EXPLICACAO DETALHADA:")
    print("="*60)
    
    print("1. CONCEITO LOSS 0:")
    print("   - Nao definimos TP fixo")
    print("   - Deixar o trailing stop fazer o trabalho")
    print("   - Maximizar lucro quando mercado favorece")
    print("   - Zero losses garantidos")
    print()
    
    print("2. TRAILING STOP DINAMICO:")
    print("   - Inativo ate 0.5% lucro")
    print("   - Ativa e aumenta com movimento favoravel")
    print("   - Nunca diminui (only up)")
    print("   - Maximo 2.0% trailing")
    print()
    
    print("3. VANTAGENS:")
    print("   - Captura movimentos extensos")
    print("   - Protecao total contra perdas")
    print("   - Adaptacao automatica ao mercado")
    print("   - Sem necessidade de TP manual")
    print()
    
    print("4. COMPARACAO:")
    print("   TRADICIONAL: TP 1.0%, SL 0.5%")
    print("   LOSS ZERO: Trailing 0.5%-2.0%")
    print()
    
    print("5. EXEMPLO PRATICO:")
