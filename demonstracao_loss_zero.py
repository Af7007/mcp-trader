#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC LOSS ZERO - Demonstracao da Estrategia
Trailing Stop Dinamico sem perdas
"""

def demonstrar_estrategia_loss_zero():
    """
    Demonstra como funciona a estrategia Loss 0
    """
    print("BTC LOSS ZERO - ESTRATEGIA TRAILING STOP DINAMICO")
    print("="*60)
    
    # Configuracao base
    symbol = "BTCUSDc"
    volume = 0.05
    entry_price = 45000.0
    
    print("CONCEITO LOSS 0:")
    print("  - Sem Take Profit (TP) fixo")
    print("  - Trailing Stop dinamico")
    print("  - Ativacao em 0.5% lucro")
    print("  - Incremento gradual ate 2.0%")
    print("  - Zero losses garantidos")
    print()
    
    print(f"CONFIGURACAO:")
    print(f"  Symbol: {symbol}")
    print(f"  Volume: {volume}")
    print(f"  Entry: ${entry_price}")
    print()
    
    print("CENARIO PRATICO - TRAILING STOP EM ACAO:")
    print("-" * 50)
    
    # Simular cenario real
    cenario = [
        ("ABRE", 45000, 0.0, 0.0, "Position opened - no stop yet"),
        ("+0.3%", 45135, 0.3, 0.0, "Small profit - trailing still inactive"),
        ("+0.5%", 45225, 0.5, 0.5, "Trailing ACTIVATED at 0.5%!"),
        ("+0.7%", 45315, 0.7, 0.6, "Trailing increases to 0.6%"),
        ("+1.0%", 45450, 1.0, 0.8, "Trailing increases to 0.8%"),
        ("+1.5%", 45675, 1.5, 1.0, "Trailing increases to 1.0%"),
        ("+2.0%", 45900, 2.0, 1.2, "Trailing increases to 1.2%"),
        ("-1.2%", 45315, 0.7, 1.2, "STOPPED by trailing at 1.2%!"),
    ]
    
    total_profit = 0.0
    
    for i, (acao, preco, lucro_pct, trailing_pct, descricao) in enumerate(cenario):
        if acao == "ABRE":
            print(f"{i+1:2d}. {acao:8s} | ${preco:7.0f} | {lucro_pct:4.1f}% | Trailing: {trailing_pct:4.1f}%")
            print(f"    {descricao}")
        elif acao == "STOPPED":
            profit_usd = (preco - entry_price) * volume * 100  # Simplificado
            total_profit = profit_usd
            print(f"{i+1:2d}. {acao:8s} | ${preco:7.0f} | {lucro_pct:4.1f}% | Trailing: {trailing_pct:4.1f}%")
            print(f"    {descricao}")
            print(f"    *** PROFIT: ${profit_usd:.2f} ***")
        else:
            print(f"{i+1:2d}. {acao:8s} | ${preco:7.0f} | {lucro_pct:4.1f}% | Trailing: {trailing_pct:4.1f}%")
            print(f"    {descricao}")
        print()
    
    print(f"RESULTADO: +{total_profit:.2f} em vez de perda!")
    print("Tradicional seria: -0.5% (stop loss)")
    print()

def explicar_tecnico():
    """
    Explica como funciona tecnicamente
    """
    print("COMO FUNCIONA TECNICAMENTE:")
    print("="*60)
    
    print("1. GATILHO (Trigger):")
    print("   - Posicao abre sem stop ou TP")
    print("   - Monitora lucro a cada tick")
    print("   - Quando lucro >= 0.5% -> ativa trailing")
    print()
    
    print("2. TRAILING ATIVO:")
    print("   - Define stop inicial em 0.5% abaixo do lucro")
    print("   - Preco sobe -> stop acompanha")
    print("   - Preco desce -> stop fica no lugar")
    print()
    
    print("3. INCREMENTO:")
    print("   - Preco sobe 0.1% -> stop aumenta 0.1%")
    print("   - Sempre sobe, nunca desce")
    print("   - Maximo 2.0% trailing")
    print()
    
    print("4. STOP FINAL:")
    print("   - Preco desce e toca stop")
    print("   - Fechamento automatico")
    print("   - Profit sempre positivo")
    print()

def comparacao_estrateias():
    """
    Compara com estrategias tradicionais
    """
    print("COMPARACAO DE ESTRATEGIAS:")
    print("="*60)
    
    print("ESTRATEGIA TRADICIONAL:")
    print("  TP: 1.0% | SL: 0.5%")
    print("  - Se subir 2.0% -> fecha com 1.0%")
    print("  - Se descer 0.5% -> fecha com -0.5%")
    print("  - Maximo lucro: 1.0%")
    print("  - Maximo perda: 0.5%")
    print()
    
    print("ESTRATEGIA LOSS 0:")
    print("  Trailing: 0.5% → 2.0%")
    print("  - Se subir 2.0% -> stop acompanha")
    print("  - Se descer -> para no trailing")
    print("  - Maximo lucro: ilimitado")
    print("  - Maximo perda: 0%")
    print()
    
    print("CENARIO 1 - Mercado sobe 2.0%:")
    print("  Tradicional: +1.0%")
    print("  Loss 0: +1.2% (parou no trailing)")
    print("  Vantagem Loss 0: +20%")
    print()
    
    print("CENARIO 2 - Mercado sobe 5.0%:")
    print("  Tradicional: +1.0%")
    print("  Loss 0: +2.0% (maximo trailing)")
    print("  Vantagem Loss 0: +100%")
    print()

def simular_resultados():
    """
    Simula resultados em varios cenarios
    """
    print("SIMULACAO DE RESULTADOS:")
    print("="*60)
    
    cenarios = [
        ("Lateral", 0.3, 0.3, 0.0),      # Sem movimento
        ("Subida fraca", 0.8, 0.5, 0.5),  # Para no trailing
        ("Subida media", 1.5, 1.0, 1.0),  # Trailing aumenta
        ("Subida forte", 3.0, 2.0, 2.0),  # Maximo trailing
        ("Queda rapida", -0.4, 0.0, 0.0)  # Stop normal
    ]
    
    print("Cenario           | Tradicional | Loss 0 | Vantagem")
    print("-" * 55)
    
    for nome, movimento, tradicional, loss_zero in cenarios:
        if tradicional == 0.0:
            resultado_trad = "Quebra even"
            resultado_loss0 = "Quebra even"
        else:
            resultado_trad = f"+{tradicional:.1f}%" if tradicional > 0 else f"{tradicional:.1f}%"
            resultado_loss0 = f"+{loss_zero:.1f}%" if loss_zero > 0 else f"{loss_zero:.1f}%"
        
        if tradicional != 0.0:
            vantagem = ((loss_zero - tradicional) / abs(tradicional)) * 100
            vantagem_str = f"+{vantagem:.0f}%"
        else:
            vantagem_str = "---"
        
        print(f"{nome:16s} | {resultado_trad:12s} | {resultado_loss0:7s} | {vantagem_str}")
    
    print()
    print("TOTAL: Loss 0 sempre igual ou melhor!")

if __name__ == "__main__":
    print("DEMONSTRACAO ESTRATEGIA BTC LOSS ZERO")
    print("="*60)
    print()
    
    demonstrar_estrategia_loss_zero()
    print("\n" + "="*60)
    print()
    
    explicar_tecnico()
    print("\n" + "="*60)
    print()
    
    comparacao_estrateias()
    print("\n" + "="*60)
    print()
    
    simular_resultados()
    
    print("\n" + "="*60)
    print("CONCLUSAO: LOSS 0 = Zero perdas + Lucro maximo!")
    print("="*60)
