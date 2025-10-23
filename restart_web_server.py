#!/usr/bin/env python3
"""
Script para reiniciar o servidor web com as novas funcionalidades do Agent Manager
"""

import os
import sys
import time
import subprocess
import signal
import requests
from pathlib import Path

def kill_existing_servers():
    """Matar servidores existentes na porta 3000"""
    print("Verificando servidores existentes...")

    try:
        # Verificar processos na porta 3000
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        pids = []

        for line in result.stdout.split('\n'):
            if ':3000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[4]
                    if pid.isdigit():
                        pids.append(int(pid))

        # Matar processos encontrados
        for pid in pids:
            try:
                print(f"Matando processo {pid}...")
                subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
                print(f"Processo {pid} finalizado")
            except subprocess.CalledProcessError:
                print(f"Nao foi possivel finalizar processo {pid}")

        time.sleep(2)  # Aguardar processos serem finalizados

    except Exception as e:
        print(f"Erro ao verificar processos: {e}")

def clear_browser_cache():
    """Limpar cache do navegador (simulado)"""
    print("Limpando cache do navegador...")
    print("Dica: Pressione Ctrl+F5 no navegador para forcar recarregamento")
    time.sleep(1)

def start_web_server():
    """Iniciar o servidor web com as novas funcionalidades"""
    print("Iniciando servidor web com Agent Manager...")

    # Mudar para o diretório do projeto
    os.chdir(str(Path(__file__).parent))

    # Iniciar servidor em background
    try:
        print("Iniciando servidor na porta 3000...")
        server_process = subprocess.Popen([
            sys.executable, "src/web/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print(f"Servidor iniciado (PID: {server_process.pid})")
        print("Acesse: http://localhost:3000")
        print("Agent Manager disponível na sidebar direita!")

        # Aguardar servidor responder
        print("Aguardando servidor responder...")
        for i in range(30):  # 30 segundos timeout
            try:
                response = requests.get("http://localhost:3000/api/health", timeout=1)
                if response.status_code == 200:
                    print("Servidor respondendo!")
                    print("Agent Manager Web Integration funcionando!")
                    break
            except requests.exceptions.RequestException:
                pass

            time.sleep(1)
        else:
            print("Servidor nao respondeu no tempo esperado")

        return server_process

    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        return None

def test_new_functionality():
    """Testar as novas funcionalidades"""
    print("\nTestando novas funcionalidades...")

    try:
        # Testar health check
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            print("Health check: OK")
        else:
            print("Health check: Falhou")
            return False

        # Testar inicialização do chatbot
        response = requests.post("http://localhost:3000/api/chatbot/initialize", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("Chatbot initialization: OK")
            else:
                print(f"Chatbot initialization: {data.get('error')}")
                return False
        else:
            print("Chatbot initialization: HTTP error")
            return False

        # Testar listagem de agentes
        response = requests.get("http://localhost:3000/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                agents_count = len(data.get('agents', []))
                print(f"Agents list: {agents_count} agents found")
            else:
                print(f"Agents list: {data.get('error')}")
        else:
            print("Agents list: HTTP error")

        # Testar worker status
        response = requests.get("http://localhost:3000/api/agents/worker/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                worker_status = "rodando" if data.get('worker_running') else "parado"
                print(f"Worker status: {worker_status}")
            else:
                print(f"Worker status: {data.get('error')}")
        else:
            print("Worker status: HTTP error")

        print("Testes basicos concluidos!")
        return True

    except Exception as e:
        print(f"Erro nos testes: {e}")
        return False

def main():
    """Função principal"""
    print("Reiniciando servidor web com Agent Manager...")
    print("=" * 60)

    # Parar servidores existentes
    kill_existing_servers()

    # Limpar cache
    clear_browser_cache()

    # Iniciar novo servidor
    server_process = start_web_server()

    if server_process:
        # Testar funcionalidades
        test_new_functionality()

        print("\n" + "=" * 60)
        print("FUNCIONALIDADES DISPONIVEIS:")
        print("=" * 60)
        print("Agent Manager na sidebar direita:")
        print("   • Criar novos agentes")
        print("   • Pausar/Retomar/Parar agentes")
        print("   • Ver histórico de eventos")
        print("   • Operações em lote")
        print("   • Estatísticas detalhadas")
        print("   • Controle do worker")
        print("")
        print("API Endpoints:")
        print("   • /api/agents - Listar agentes")
        print("   • /api/agents/create - Criar agente")
        print("   • /api/agents/{id}/pause - Pausar agente")
        print("   • /api/agents/{id}/resume - Retomar agente")
        print("   • /api/agents/{id}/stop - Parar agente")
        print("   • /api/agents/{id}/delete - Deletar agente")
        print("   • /api/agents/{id}/history - Histórico")
        print("   • /api/agents/{id}/stats - Estatísticas")
        print("   • /api/agents/worker/* - Controle do worker")
        print("   • /api/agents/bulk/* - Operações em lote")
        print("")
        print("DICAS:")
        print("   • Use Ctrl+F5 para forçar recarregamento")
        print("   • Verifique o console do navegador (F12)")
        print("   • Teste com: python test_agent_manager_web.py")

        print("\nServidor reiniciado com sucesso!")
        print("Acesse: http://localhost:3000")
        print("Agent Manager disponível na sidebar!")

        # Manter servidor rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            if server_process:
                server_process.terminate()
                server_process.wait()
            print("Ate logo!")

    else:
        print("❌ Falha ao iniciar servidor")
        sys.exit(1)

if __name__ == "__main__":
    main()
