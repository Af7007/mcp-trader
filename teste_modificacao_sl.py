#!/usr/bin/env python3
"""
TESTE DO MÉTODO _safe_modify_sl CORRIGIDO
Verifica se as modificações do Stop Loss estão sendo executadas no MT5
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def test_safe_modify_sl():
    """
    Testa o método _safe_modify_sl com uma posição de teste
    """
    print("TESTANDO MÉTODO _safe_modify_sl CORRIGIDO")
    print("="*60)
    print("")
    
    # Criar agente
    agent = GoldLossZeroSimple(
        symbol='XAUUSDc',
        volume=0.01,
        check_interval=5,
        trailing_activation_atr_multiplier=0.025,
        trailing_distance_atr_multiplier=0.01,
        stop_loss_atr_multiplier=2.0,
        use_buy=True,
        use_sell=True
    )
    
    print("AGENTE CRIADO COM CONFIGURAÇÕES ULTRA-AGGRESSIVE")
    print(f"- Trailing ativa em: ${agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos):.2f}")
    print(f"- Trailing distância: ${agent._pontos_para_dinheiro(agent.current_trailing_distance_pontos):.2f}")
    print(f"- Volume: {agent.volume}")
    print(f"- Check interval: {agent.check_interval}s")
    print("")
    
    # Verificar se há posições abertas
    try:
        positions = agent.mt5.positions_get(symbol='XAUUSDc')
        if positions:
            print(f"POSIÇÕES ABERTAS ENCONTRADAS: {len(positions)}")
            for pos in positions:
                print(f"  Ticket: {pos.get('ticket')}")
                print(f"  Tipo: {'BUY' if pos.get('type') == 0 else 'SELL'}")
                print(f"  Preço: ${pos.get('price_open', 0):.3f}")
                print(f"  SL atual: ${pos.get('sl', 0):.3f}")
                print(f"  Profit: ${pos.get('profit', 0):.2f}")
                print("")
                
                # Testar modificação de SL
                ticket = pos.get('ticket')
                if ticket:
                    print(f"TESTANDO MODIFICAÇÃO DE SL PARA TICKET {ticket}")
                    
                    # Calcular novo SL (descer 1 ponto para teste)
                    current_price = pos.get('price_open', 0)
                    current_sl = pos.get('sl', 0)
                    
                    # Para BUY: tentar subir o SL em 0.5
                    # Para SELL: tentar descer o SL em 0.5
                    pos_type = pos.get('type', 0)
                    if pos_type == 0:  # BUY
                        new_sl_test = current_sl + 0.5 if current_sl > 0 else current_price - 0.5
                    else:  # SELL
                        new_sl_test = current_sl - 0.5 if current_sl > 0 else current_price + 0.5
                    
                    print(f"  SL atual: ${current_sl:.3f}")
                    print(f"  SL teste: ${new_sl_test:.3f}")
                    
                    # Testar o método corrigido
                    success = agent._safe_modify_sl(ticket, new_sl_test, "TESTE MODIFICAO")
                    
                    if success:
                        print("  ✅ MODIFICAÇÃO BEM-SUCEDIDA!")
                    else:
                        print("  ❌ MODIFICAÇÃO FALHOU!")
                    
                    print("")
        else:
            print("NENHUMA POSIÇÃO ABERTA - AGENTE PODERÁ TESTAR AO ABRIR UMA POSIÇÃO")
            print("")
            print("CONFIGURAÇÕES PARA TESTE FUTURO:")
            print(f"- Thresholds ultra-agressivos configurados")
            print(f"- Método _safe_modify_sl melhorado com múltiplas tentativas")
            print(f"- Debug detalhado ativado")
            print(f"- Agente pronto para operação")
            
    except Exception as e:
        print(f"ERRO NO TESTE: {e}")
    
    print("")
    print("="*60)
    print("RESUMO DA CORREÇÃO:")
    print("✅ Múltiplas tentativas de modificação (3x)")
    print("✅ Logs detalhados para debug")
    print("✅ Tratamento específico de erro 130 (invalid stops)")
    print("✅ Tentativa final com order_send se modify_position falhar")
    print("✅ Distância mínima mais permissiva")
    print("✅ Timeout entre tentativas para estabilidade")
    print("")
    print("PRÓXIMOS PASSOS:")
    print("1. Aguardar nova posição aberta pelo agente")
    print("2. Verificar se trailing ativa automaticamente")
    print("3. Confirmar se modificações são executadas no MT5")
    print("="*60)

if __name__ == "__main__":
    test_safe_modify_sl()
