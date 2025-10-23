#!/usr/bin/env python3
"""Test script para controlar agente"""

import requests

def test_agent_control(agent_id, operation):
    """Testar operação do agente"""
    try:
        url = f'http://localhost:3000/api/agents/{agent_id}/{operation}'
        response = requests.post(url, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"Operacao {operation} executada com sucesso")
                return True
            else:
                print(f"Erro na operacao: {data.get('message', data.get('error', 'Unknown error'))}")
                return False
        else:
            print(f"Erro HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"Erro na requisicao: {e}")
        return False

if __name__ == "__main__":
    agent_id = "6c22ab48"
    operations = ["pause", "resume", "stop"]

    for operation in operations:
        print(f"\nTestando {operation} do agente {agent_id}...")
        test_agent_control(agent_id, operation)

        # Aguardar um pouco entre operações
        import time
        time.sleep(1)
