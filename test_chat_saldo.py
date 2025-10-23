#!/usr/bin/env python3
"""Test script para verificar saldo via chat"""

import requests

def test_chat_saldo():
    """Testar comando de saldo no chat"""
    try:
        response = requests.post(
            'http://localhost:3000/api/chat',
            json={'message': 'quanto tenho de saldo?'},
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("Chat respondeu com sucesso!")
                print(f"Resposta: {data.get('response', '')[:200]}...")
                return True
            else:
                print(f"Erro no chat: {data.get('error')}")
                return False
        else:
            print(f"Erro HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"Erro na requisicao: {e}")
        return False

if __name__ == "__main__":
    print("Testando comando de saldo no chat...")
    success = test_chat_saldo()

    if success:
        print("Chat funcionando corretamente!")
    else:
        print("Problema no chat")
