#!/usr/bin/env python3
"""
INICIAR SISTEMA WEB FINAL
Versão limpa sem emojis para resolver problemas de encoding
"""

from src.web.app import create_app
from flask import Flask
import requests
import time
import threading

def iniciar_servidor_web():
    """Inicia apenas o servidor web"""
    print("INICIANDO SERVIDOR WEB...")

    try:
        # Importar app
        app = create_app()
        print("App criado com sucesso")

        # Iniciar em thread
        def run_server():
            app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        print("Servidor iniciando na porta 3000...")
        time.sleep(3)  # Aguardar inicialização

        # Testar endpoints
        urls_to_test = [
            'http://localhost:3000/api/health',
            'http://localhost:3000/api/agents',
            'http://localhost:3000/',
            'http://localhost:3000/admin'
        ]

        print("\nTESTANDO ENDPOINTS:")

        for url in urls_to_test:
            try:
                response = requests.get(url, timeout=10)
                status = "OK" if response.status_code in [200, 201] else f"ERRO {response.status_code}"
                print(f"  {url}: {status}")
            except Exception as e:
                print(f"  {url}: FALHA - {str(e)[:50]}")

        print("\nSERVIDOR ATIVO!")
        print("Url: http://localhost:3000")
        print("Admin: http://localhost:3000/admin")

        # Aguardar comandos
        server_thread.join()

    except Exception as e:
        print(f"ERRO AO INICIAR SERVIDOR: {e}")
        import traceback
        traceback.print_exc()

def testar_app_sozinha():
    """Testa apenas a criação da app"""
    print("TESTANDO SOMENTE A APP...")

    try:
        app = create_app()
        print("App criada com sucesso")

        # Teste básico com test client
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"Test client - health: {response.status_code}")

            response = client.get('/')
            print(f"Test client - index: {response.status_code}")

    except Exception as e:
        print(f"ERRO NA APP: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "teste":
        testar_app_sozinha()
    else:
        iniciar_servidor_web()
