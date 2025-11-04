#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Game API - Testar endpoint /api/game/history
"""

import requests
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_game_api():
    """Testa a API do game diretamente"""
    try:
        # Teste da API local
        url = "http://localhost:3000/api/game/history"
        
        print("=== TESTANDO API GAME HISTORY ===")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n=== RESPOSTA DA API ===")
            print(f"History items: {len(data.get('history', []))}")
            print(f"Stats: {data.get('stats', {})}")
            
            if data.get('history'):
                print("\n=== PRIMEIROS 3 ITENS DO HISTÓRICO ===")
                for i, item in enumerate(data['history'][:3]):
                    print(f"Item {i+1}:")
                    print(f"  Ticket: {item.get('ticket')}")
                    print(f"  Type: {item.get('type')}")
                    print(f"  Profit: {item.get('profit')}")
                    print(f"  Close Time: {item.get('close_time')}")
                    print(f"  Volume: {item.get('volume')}")
                    print()
                
                print("=== ANÁLISE DOS DADOS ===")
                profits = [item.get('profit', 0) for item in data['history']]
                close_times = [item.get('close_time') for item in data['history']]
                
                print(f"Profits: {profits[:5]}...")  # Primeiros 5
                print(f"Close times: {close_times[:3]}...")  # Primeiros 3
                
                # Verificar se há timestamps inválidos
                invalid_dates = 0
                zero_profits = 0
                
                for item in data['history']:
                    # Testar timestamp
                    try:
                        close_time = item.get('close_time')
                        if close_time:
                            from datetime import datetime
                            datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                    except:
                        invalid_dates += 1
                    
                    # Testar profit
                    if item.get('profit', 0) == 0:
                        zero_profits += 1
                
                print(f"\nPROBLEMAS ENCONTRADOS:")
                print(f"  Timestamps inválidos: {invalid_dates}")
                print(f"  Profits zerados: {zero_profits}/{len(data['history'])}")
                
            return True
        else:
            print(f"ERRO: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERRO: Não foi possível conectar ao servidor Flask")
        print("Certifique-se de que o servidor está rodando na porta 3000")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    test_game_api()
