#!/usr/bin/env python3
"""
INICIAR INTERFACE ATUALIZADA DO SISTEMA DE HEDGE
Esta versão carrega a nova interface profissional sem erros
"""

import subprocess
import sys
import time
import os

def parar_processos_existentes():
    """Tenta parar processos Python existentes"""
    print("Parando processos existentes...")

    # Tentar comandos de parada
    comandos = [
        'taskkill /F /FI "IMAGENAME eq python.exe"',
        'pkill -f "operacional"',
        'pkill -f "iniciar"'
    ]

    for cmd in comandos:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        except:
            pass

    time.sleep(2)

def limpar_pid_arquivos():
    """Limpa arquivos de PID antigos"""
    for arquivo in ['agent_hedge_pid.txt']:
        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
                print(f"Arquivo {arquivo} removido")
        except:
            pass

def testar_conexao():
    """Testa se o servidor já está respondendo"""
    try:
        import requests
        response = requests.get('http://localhost:3000', timeout=2)
        if 'Trading Bot - Agent Manager' in response.text:
            print("✅ Nova interface já está rodando!")
            return True
    except:
        pass
    return False

def iniciar_servidor_novo():
    """Inicia o servidor com a nova interface"""
    from src.web.app import create_app

    print("Iniciando servidor Flask com nova interface...")
    app = create_app()

    try:
        app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

def main():
    print("INICIANDO INTERFACE ATUALIZADA DO SISTEMA DE HEDGE")

    # Verificar se já está funcionando com a nova versão
    if testar_conexao():
        print("Sistema ja esta funcionando com a nova interface!")
        return

    # Parar processos antigos e limpar
    parar_processos_existentes()
    limpar_pid_arquivos()

    print("Iniciando nova interface...")

    # Verificar versão do código
    print("Verificando codigo atualizado...")

    try:
        with open('src/web/app.py', 'r') as f:
            conteudo = f.read()
            if 'Trading Bot - Agent Manager' in conteudo:
                print("Codigo com nova interface encontrado")
            else:
                print("Codigo antigo ainda presente")
    except:
        print("Erro ao verificar codigo")

    # Iniciar servidor
    iniciar_servidor_novo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupcao do usuario")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
