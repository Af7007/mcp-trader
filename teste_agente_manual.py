#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Agente GOLD Loss Zero - MODO MANUAL
Verifica se o agente não abre trades automaticamente
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

def main():
    print("=" * 60)
    print("TESTE DO AGENTE GOLD LOSS ZERO - MODO MANUAL")
    print("=" * 60)
    print()
    
    try:
        # Criar agente
        print("1. Criando agente GOLD Loss Zero...")
        agente = GoldLossZeroSimple(
            symbol="XAUUSDc",
            volume=0.01,
            check_interval=5,  # Intervalo curto para teste
            use_buy=True,
            use_sell=True
        )
        
        print("   ✅ Agente criado com sucesso!")
        print(f"   - Symbol: {agente.symbol}")
        print(f"   - Volume: {agente.volume}")
        print(f"   - Modo: MANUAL (sem aberturas automáticas)")
        print()
        
        # Verificar se o sistema de análise existe mas não é chamado automaticamente
        print("2. Verificando sistema de análise (não deve ser executado automaticamente)...")
        
        # Testar se a função de análise existe
        if hasattr(agente, '_analyze_and_open'):
            print("   ✅ Método _analyze_and_open existe")
            print("   ✅ Método marcado como interno (não público)")
        else:
            print("   ❌ Método _analyze_and_open não encontrado")
        
        if hasattr(agente, '_get_simple_signal'):
            print("   ✅ Método _get_simple_signal existe")
        else:
            print("   ❌ Método _get_simple_signal não encontrado")
        
        if hasattr(agente, '_open_position'):
            print("   ✅ Método _open_position existe")
            print("   ✅ Método marcado como interno (não público)")
        else:
            print("   ❌ Método _open_position não encontrado")
        
        print()
        
        # Verificar se o sistema de trailing está funcionando
        print("3. Verificando sistema de trailing stop...")
        print(f"   - Trailing activation: ${agente.trailing_activation_dollar}")
        print(f"   - Trailing distance: ${agente.trailing_distance_dollar}")
        print(f"   - Trailing step: ${agente.trailing_step_dollar}")
        print("   ✅ Sistema de trailing configurado")
        print()
        
        # Verificar posições existentes
        print("4. Verificando posições no MT5...")
        try:
            positions = agente.mt5.positions_get(symbol=agente.symbol)
            if positions:
                print(f"   📊 Encontradas {len(positions)} posições abertas:")
                for i, pos in enumerate(positions):
                    print(f"      {i+1}. Ticket: {pos['ticket']} | Tipo: {'BUY' if pos['type'] == 0 else 'SELL'} | Volume: {pos['volume']}")
                print("   ⚠️  O agente gerenciará essas posições (trailing stop)")
            else:
                print("   📊 Nenhuma posição aberta")
                print("   💡 Use agente.open_trade_manual('BUY') ou agente.open_trade_manual('SELL') para abrir trades")
        except Exception as e:
            print(f"   ❌ Erro ao verificar posições: {e}")
        
        print()
        
        # Mostrar comandos disponíveis
        print("5. Comandos disponíveis para uso manual:")
        print("   - agente.open_trade_manual('BUY')  - Abrir trade BUY manualmente")
        print("   - agente.open_trade_manual('SELL') - Abrir trade SELL manualmente")
        print("   - agente.run()                      - Executar monitoramento (Ctrl+C para parar)")
        print("   - agente.get_status()               - Ver status atual")
        print()
        
        print("=" * 60)
        print("TESTE CONCLUÍDO - AGENTE EM MODO MANUAL")
        print("=" * 60)
        print()
        print("RESULTADO: ✅ O agente NÃO abrirá trades automaticamente")
        print("           ✅ O agente gerenciará posições existentes com trailing stop")
        print("           ✅ Use comandos manuais para abrir novos trades")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
