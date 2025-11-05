#!/usr/bin/env python3
"""
Testa se GoldAdaptiveAgent esta gerando sinais
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_adaptive_agent import GoldAdaptiveAgent

print("="*70)
print("TESTE DE GERACAO DE SINAIS - GOLD ADAPTIVE AGENT")
print("="*70)

# Criar agente
agent = GoldAdaptiveAgent(
    symbol="XAUUSDc",
    volume=0.02,
    auto_tuning_enabled=False,  # Desabilitar para teste
    use_buy=True,
    use_sell=True
)

print("\n[1] TESTANDO GERACAO DE SINAIS")
print("-"*70)

# Tentar gerar sinal 5 vezes
for i in range(5):
    print(f"\nTentativa {i+1}:")
    
    signal = agent._get_simple_signal()
    
    if signal:
        print(f"  SINAL GERADO!")
        print(f"    Type: {signal['type']}")
        print(f"    Price: ${signal['price']:.2f}")
        print(f"    Reason: {signal['reason']}")
        break
    else:
        print(f"  Nenhum sinal (normal - condicoes nao atendidas)")
        
        # Mostrar estado do mercado
        try:
            tick = agent.mt5.get_symbol_info_tick(agent.symbol)
            if tick:
                price = tick.get('bid', 0)
                print(f"    Preco atual: ${price:.2f}")
        except:
            pass
        
        if i < 4:
            import time
            time.sleep(10)  # Esperar 10s antes de tentar novamente

print("\n" + "="*70)
print("ANALISE:")
print("="*70)

print("""
Se nenhum sinal foi gerado em 5 tentativas:
  - E NORMAL! O agente e conservador
  - Requer 2-3 confirmacoes de indicadores
  - M5 + M15 devem concordar
  - Momentum minimo de 0.03%

Condicoes para SELL (Gold):
  1. Downtrend em M5 (3 de 4 velas)
  2. Momentum < -0.03%
  3. Volume spike OU alta volatilidade
  4. M15 confirma downtrend
  
Com mercado calmo/lateral, pode levar 30-60 min para gerar sinal.
Isto e BOM - evita trades ruins!

Para testar rapidamente:
  - Aguarde movimento forte no mercado
  - Ou reduza thresholds temporariamente
""")

print("\n" + "="*70)
