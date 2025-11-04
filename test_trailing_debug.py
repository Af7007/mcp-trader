#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Trailing Stop - Game API
Verifica se o worker está funcionando e se o trailing está sendo aplicado
"""

import sys
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_worker_status():
    """Testa se o worker está rodando"""
    print("=== TESTE DO WORKER STATUS ===")
    
    try:
        response = requests.get('http://localhost:3000/api/game/worker-status')
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Worker rodando: {data['worker_running']}")
            print(f"✓ Magic Number: {data['magic_number']}")
            print(f"✓ Posições no estado: {len(data['positions_state'])}")
            print(f"✓ Posições no MT5: {len(data['mt5_positions'])}")
            
            debug = data['debug_info']
            print(f"✓ Worker existe: {debug['worker_exists']}")
            print(f"✓ Worker running: {debug['worker_running']}")
            print(f"✓ Check count: {debug.get('worker_check_count', 0)}")
            
            # Mostra detalhes das posições
            if data['mt5_positions']:
                print("\n=== POSIÇÕES MT5 ===")
                for pos in data['mt5_positions']:
                    print(f"Ticket: {pos['ticket']} | Type: {pos['type']} | Profit: ${pos['profit']:.2f} | SL: {pos['sl']:.5f} | Magic: {pos['magic']}")
            
            # Mostra estado do worker
            if debug.get('worker_positions_data'):
                print("\n=== ESTADO DO WORKER ===")
                for ticket, data in debug['worker_positions_data'].items():
                    print(f"Ticket: {ticket} | Trailing: {data['trailing_active']} | SL$: {data['sl_dollars']} | Level: {data['last_trailing_level']}")
            
            return True
        else:
            print(f"✗ Erro ao verificar status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return False

def test_open_position():
    """Testa abrir uma posição"""
    print("\n=== TESTE DE ABERTURA DE POSIÇÃO ===")
    
    try:
        response = requests.post('http://localhost:3000/api/game/open', json={
            'type': 'BUY',
            'volume': 0.02,
            'sl': 5.0
        })
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✓ Posição aberta: Ticket {data['ticket']}")
                return data['ticket']
            else:
                print(f"✗ Falha ao abrir: {data['error']}")
                return None
        else:
            print(f"✗ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Erro ao abrir posição: {e}")
        return None

def monitor_trailing(ticket, duration=60):
    """Monitora o trailing por X segundos"""
    print(f"\n=== MONITORANDO TRAILING (Ticket: {ticket}) ===")
    print(f"Monitorando por {duration} segundos...")
    
    start_time = time.time()
    last_profit = None
    last_sl = None
    
    while time.time() - start_time < duration:
        try:
            response = requests.get('http://localhost:3000/api/game/worker-status')
            if response.status_code == 200:
                data = response.json()
                
                # Encontra a posição
                position = None
                for pos in data['mt5_positions']:
                    if pos['ticket'] == ticket:
                        position = pos
                        break
                
                if position:
                    current_profit = position['profit']
                    current_sl = position['sl']
                    
                    # Verifica se mudou
                    if last_profit != current_profit or last_sl != current_sl:
                        print(f"[{time.strftime('%H:%M:%S')}] Profit: ${current_profit:.2f} | SL: {current_sl:.5f}")
                        
                        # Verifica se trailing está ativo
                        debug = data['debug_info']
                        worker_data = debug.get('worker_positions_data', {}).get(ticket, {})
                        trailing_active = worker_data.get('trailing_active', False)
                        
                        if trailing_active:
                            print(f"  >>> TRAILING ATIVO! Level: {worker_data.get('last_trailing_level', 0)}")
                        else:
                            print(f"  >>> Trailing inativo (aguardando lucro >= SL)")
                        
                        last_profit = current_profit
                        last_sl = current_sl
            
            time.sleep(2)  # Verifica a cada 2 segundos
            
        except KeyboardInterrupt:
            print("\nMonitoramento interrompido")
            break
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            time.sleep(2)

def main():
    print("TESTE DO TRAILING STOP - GAME API")
    print("=" * 50)
    
    # 1. Verifica se o worker está rodando
    if not test_worker_status():
        print("\n✗ Worker não está rodando! Inicie o servidor com:")
        print("   python run_game_server.py")
        return
    
    # 2. Abre uma posição de teste
    print("\nDeseja abrir uma posição de teste? (s/n): ", end="")
    if input().lower() != 's':
        print("Teste cancelado.")
        return
    
    ticket = test_open_position()
    if not ticket:
        print("\n✗ Não foi possível abrir posição de teste")
        return
    
    # 3. Monitora o trailing
    print(f"\nIniciando monitoramento do trailing para posição {ticket}...")
    print("Pressione Ctrl+C para parar")
    
    try:
        monitor_trailing(ticket, duration=120)  # 2 minutos
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    print("\n=== TESTE FINALIZADO ===")
    print("Verifique os logs do servidor para ver se o trailing está funcionando.")

if __name__ == '__main__':
    main()
