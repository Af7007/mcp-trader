#!/usr/bin/env python3
"""Test script para criar um agente via API"""

import requests
import json

def test_create_agent():
    """Testar criação de agente"""
    try:
        response = requests.post(
            'http://localhost:3000/api/agents/create',
            json={'message': 'criar agente EURUSD com RSI'},
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                agent = data.get('agent', {})
                print(f"Agente criado com sucesso: {agent.get('name')}")
                print(f"ID: {agent.get('id')}")
                return agent.get('id')
            else:
                print(f"Erro na criação: {data.get('error')}")
                return None
        else:
            print(f"Erro HTTP: {response.status_code}")
            return None

    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

if __name__ == "__main__":
    print("Testando criação de agente...")
    agent_id = test_create_agent()

    if agent_id:
        print(f"Agente criado com ID: {agent_id}")
    else:
        print("Falha na criação do agente")
