#!/usr/bin/env python3
"""Test script para operações do agente"""

import requests

def test_agent_operations(agent_id):
    """Testar operações do agente"""
    operations = [
        ("resume", "POST", f"/api/agents/{agent_id}/resume"),
        ("pause", "POST", f"/api/agents/{agent_id}/pause"),
        ("stop", "POST", f"/api/agents/{agent_id}/stop")
    ]

    for operation_name, method, endpoint in operations:
        try:
            print(f"\nTestando {operation_name}...")
            response = requests.post(f"http://localhost:3000{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")

            # Verificar status atual
            agents_response = requests.get("http://localhost:3000/api/agents", timeout=5)
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                if agents_data.get('agents'):
                    agent = agents_data['agents'][0]
                    print(f"Status atual do agente: {agent.get('status')}")

        except Exception as e:
            print(f"Erro em {operation_name}: {e}")

if __name__ == "__main__":
    print("Testando operações do agente a76fcb06...")
    test_agent_operations("a76fcb06")
