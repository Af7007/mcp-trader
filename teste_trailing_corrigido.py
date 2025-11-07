#!/usr/bin/env python3
"""
Teste simples para verificar se o trailing stop está funcionando corretamente
após a correção da lógica de posicionamento do SL.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
import time

def main():
    print("="*60)
    print("TESTE TRAILING STOP CORRIGIDO")
    print("="*60)
    
    # Criar agente GOLD
    print("Iniciando agente GOLD Loss Zero...")
    agent = GoldLossZeroSimple(
        symbol="XAUUSDc",
        volume=0.1,  # Volume de teste
        check_interval=5  # Verificação mais frequente
    )
    
    print(f"\nStatus inicial:")
    print(f"  Symbol: {agent.symbol}")
    print(f"  Volume: {agent.volume}")
    print(f"  Point: {agent.symbol_point}")
    print(f"  Point Value: ${agent.point_value:.4f}")
    print(f"  Trailing Ativo: ${agent.trailing_activation_dollar:.2f}")
    print(f"  Trailing Protege: ${agent.trailing_distance_dollar:.2f}")
    
    # Verificar posição atual
    print(f"\nVerificando posições abertas...")
    positions = agent.mt5.positions_get(symbol=agent.symbol)
    
    if not positions:
        print("❌ Nenhuma posição aberta")
        print("   Execute primeiro o teste principal para abrir uma posição")
        return
    
    print(f"[OK] Encontradas {len(positions)} posicao(s):")
    
    for pos in positions:
        ticket = pos.get('ticket')
        pos_type = pos.get('type', 0)
        profit = pos.get('profit', 0.0)
        current_price = pos.get('price_current', 0)
        entry_price = pos.get('price_open', 0)
        sl_price = pos.get('sl', 0)
        
        print(f"\n  Posicao #{ticket}:")
        print(f"    Tipo: {'BUY' if pos_type == 0 else 'SELL'}")
        print(f"    Entry: ${entry_price:.2f}")
        print(f"    Atual: ${current_price:.2f}")
        print(f"    SL: ${sl_price:.2f}")
        print(f"    Lucro: ${profit:.2f}")
        
        # Teste do trailing stop
        print(f"\n  Testando trailing stop...")
        
        # Verificar se position está no dicionário
        if ticket in agent.positions_entry_price:
            print(f"    [OK] Posicao registrada nos dicionarios")
            print(f"    Entry (dict): ${agent.positions_entry_price[ticket]:.2f}")
            print(f"    Trailing ativo: {agent.positions_trailing_active.get(ticket, False)}")
        else:
            print(f"    [AVISO] Posicao NAO registrada nos dicionarios")
            # Adicionar ao dicionário
            agent.positions_entry_price[ticket] = entry_price
            agent.positions_trailing_active[ticket] = False
            agent.positions_trailing_stop[ticket] = 0.0
            print(f"    [OK] Adicionada aos dicionarios")
        
        # Simular ativação do trailing se lucro >= $1
        if profit >= agent.trailing_activation_dollar:
            print(f"    [ATIVO] Lucro >= ${agent.trailing_activation_dollar:.2f} - Testando ativacao do trailing")
            
            # Chamar método de gerenciamento de position trailing
            try:
                agent._manage_position_trailing(pos)
                print(f"    [OK] Metodo _manage_position_trailing executado com sucesso")
            except Exception as e:
                print(f"    [ERRO] Erro ao executar trailing: {e}")
        else:
            falta = agent.trailing_activation_dollar - profit
            print(f"    [AGUARDANDO] Aguardando ${falta:.2f} para ativar trailing")
    
    print(f"\n" + "="*60)
    print(f"TESTE CONCLUIDO")
    print(f"="*60)
    print(f"Proximo passo: Verifique se o teste principal esta executando")
    print(f"e se o trailing stop foi ativado com sucesso.")

if __name__ == "__main__":
    main()
