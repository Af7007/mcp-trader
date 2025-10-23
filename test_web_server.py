#!/usr/bin/env python3
import requests
import time
from src.web.app import create_app

def test_flask_app():
    print("TESTANDO FLASK APP...")

    try:
        # Criar app
        app = create_app()
        print("✅ App criada")

        # Testar alguns endpoints basicos
        with app.test_client() as client:
            print("\nTESTANDO ENDPOINTS:")

            # Teste /api/health
            response = client.get('/api/health')
            print(f"Health check: {response.status_code}")

            # Teste /api/agents
            response = client.get('/api/agents')
            print(f"Agents API: {response.status_code}")

            # Teste /
            response = client.get('/')
            print(f"Index page: {response.status_code}")

        print("\n✅ TESTE DO FLASK - OK")

    except Exception as e:
        print(f"❌ ERRO NO FLASK: {e}")

def start_simple_server():
    print("\nINICIANDO SERVIDOR SIMPLES...")

    try:
        app = create_app()

        # Iniciar apenas web server sem os agentes complexos
        from werkzeug.serving import make_server
        import threading

        def run_server():
            server = make_server('0.0.0.0', 3000, app, threaded=True)
            server.serve_forever()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        print("✅ Servidor iniciando na porta 3000...")
        time.sleep(2)

        # Testar conexão
        try:
            response = requests.get('http://localhost:3000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Servidor respondendo!")
                print("Acesse: http://localhost:3000")
                print("Admin: http://localhost:3000/admin")
                return True
            else:
                print(f"❌ Servidor com erro: {response.status_code}")
        except:
            print("❌ Erro ao conectar com o servidor")

        # Seguir funcionando
        server_thread.join()

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    test_flask_app()
    start_simple_server()
