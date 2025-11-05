#!/usr/bin/env python3
"""
TESTE DA CORREÇÃO DE TRADE_ID NO TRAILING
Valida se o trade_id está sendo salvo corretamente no banco
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.btc_logger import BTCLogger

def test_trade_id_retrieval():
    """
    Testa se o método get_trade_id_by_ticket existe e funciona
    """
    print("TESTANDO RECUPERAÇÃO DE TRADE_ID")
    print("="*50)
    
    try:
        btc_logger = BTCLogger()
        
        # Verificar se o método existe
        if hasattr(btc_logger, 'get_trade_id_by_ticket'):
            print("[OK] Metodo get_trade_id_by_ticket existe")
            
            # Testar com ticket ficticio
            test_ticket = 112891439  # Ticket do exemplo do usuario
            trade_id = btc_logger.get_trade_id_by_ticket(test_ticket)
            
            if trade_id:
                print(f"[OK] Trade ID encontrado para ticket {test_ticket}: {trade_id}")
            else:
                print(f"[INFO] Trade ID nao encontrado para ticket {test_ticket}")
                print("   Possiveis razoes:")
                print("   - Ticket nao existe no banco")
                print("   - Trade ainda nao foi salvo no banco")
                print("   - Metodo retorna None quando nao encontra")
        else:
            print("[ERRO] Metodo get_trade_id_by_ticket NAO existe!")
            print("   Precisa implementar este metodo no BTCLogger")
            
            # Mostrar metodos disponiveis
            methods = [method for method in dir(btc_logger) if not method.startswith('_')]
            print(f"   Metodos disponiveis: {methods}")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar: {e}")
    
    print("")
    print("SOLUÇÕES POSSÍVEIS:")
    print("1. Implementar get_trade_id_by_ticket no BTCLogger")
    print("2. Usar query SQL direta para buscar por ticket")
    print("3. Manter current_trade_id atualizado sempre")
    print("4. Criar mapping ticket -> trade_id na memória")

def suggest_implementation():
    """
    Sugere implementação do método get_trade_id_by_ticket
    """
    print("")
    print("IMPLEMENTAÇÃO SUGERIDA PARA BTCLogger:")
    print("="*50)
    
    code = '''
def get_trade_id_by_ticket(self, ticket: int) -> int:
    """
    Busca trade_id pelo ticket no banco de dados
    
    Args:
        ticket: Ticket da posição no MT5
        
    Returns:
        trade_id se encontrado, None caso contrário
    """
    try:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar trade_id na tabela trades pelo ticket
        cursor.execute("""
            SELECT id FROM trades 
            WHERE ticket = ? AND status = 'OPEN'
        """, (ticket,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]  # Retornar o trade_id
        else:
            return None
            
    except Exception as e:
        print(f"Erro ao buscar trade_id: {e}")
        return None
'''
    
    print(code)

if __name__ == "__main__":
    test_trade_id_retrieval()
    suggest_implementation()
