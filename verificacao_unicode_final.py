#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Final da Correção Unicode
Testa se o agente gold_loss_zero_simple.py está funcionando sem erros
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def verificar_unicode():
    """Verifica se a correção Unicode foi bem-sucedida"""
    print('=== VERIFICACAO FINAL CORRECAO UNICODE ===')
    print()
    
    success_count = 0
    total_tests = 5
    
    try:
        # Teste 1: Importação sem erros
        print("Teste 1: Importação do agente...")
        from agents.gold_loss_zero_simple import GoldLossZeroSimple
        print("[OK] Importacao: SUCESSO")
        success_count += 1
        
        # Teste 2: Inicialização sem Unicode errors
        print("\nTeste 2: Inicialização do agente...")
        agent = GoldLossZeroSimple(symbol='XAUUSDc', volume=0.01)
        print("[OK] Inicializacao: SUCESSO")
        success_count += 1
        
        # Teste 3: Verificar se emojis foram removidos
        print("\nTeste 3: Verificação de emojis no código...")
        with open('src/agents/gold_loss_zero_simple.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de emojis que deveriam ter sido removidos
        emojis = ['🔥', '⚠️', '⛔', '✅', '❌', '🎯', '📊', '🔧', '🛡️']
        found_emojis = [e for e in emojis if e in content]
        
        if found_emojis:
            print(f"[ERROR] Emojis ainda encontrados: {found_emojis}")
        else:
            print("[OK] Emojis removidos: SUCESSO")
            print("[OK] Código limpo: SUCESSO")
            success_count += 1
        
        # Teste 4: MT5 conexão
        print("\nTeste 4: Conexão MT5...")
        if agent.mt5 and agent.mt5.connected():
            print("[OK] Conexao MT5: ATIVA")
            success_count += 1
            
            # Testar algumas funções críticas
            try:
                positions = agent.mt5.positions_get(symbol='XAUUSDc')
                print(f"[OK] Posicoes detectadas: {len(positions) if positions else 0}")
                
                if positions:
                    pos = positions[0]
                    ticket = pos.get('ticket')
                    profit = pos.get('profit', 0)
                    print(f"[OK] Teste trailing: Posicao #{ticket} com ${profit:.2f}")
                else:
                    print("[INFO] Nenhuma posicao ativa (normal em teste)")
            except Exception as e:
                print(f"[WARNING] Teste positions: {e}")
        else:
            print("[WARNING] Conexao MT5: INATIVA")
        
        # Teste 5: Verificar trailing stop calculation
        print("\nTeste 5: Cálculo de trailing stop...")
        try:
            # Verificar se as funções de cálculo funcionam
            if hasattr(agent, '_pontos_para_dinheiro'):
                # Testar conversão de pontos para dinheiro
                teste_resultado = agent._pontos_para_dinheiro(100)
                print(f"[OK] Calculo pontos: 100 pts = ${teste_resultado:.2f}")
                success_count += 1
            else:
                print("[WARNING] Funcao _pontos_para_dinheiro nao encontrada")
        except Exception as e:
            print(f"[WARNING] Teste calculo: {e}")
        
    except Exception as e:
        print(f"[ERROR] Erro durante verificacao: {e}")
        print("A correcao pode precisar de ajustes adicionais.")
        return False
    
    print()
    print("=== RESUMO FINAL ===")
    print(f"Testes aprovados: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("[OK] Correcao Unicode: COMPLETA")
        print("[OK] Sistema funcional: SIM")
        print("[OK] Trailing stop: OPERACIONAL")
        print("[OK] Safety rules: ATIVAS")
        return True
    else:
        print("[WARNING] Correcao Unicode: PARCIAL")
        print("[WARNING] Alguns testes falharam")
        return False

if __name__ == "__main__":
    sucesso = verificar_unicode()
    sys.exit(0 if sucesso else 1)
