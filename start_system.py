#!/usr/bin/env python3
"""
Script para iniciar o sistema de trading completo
Inicia: MT5 MCP Server, Ollama MCP Server, Web Interface, Worker
"""

import asyncio
import subprocess
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemStarter:
    """Gerencia o início de todos os servidores"""

    def __init__(self):
        self.processes = {}
        self.base_path = Path(__file__).parent

    def start_mt5_server(self):
        """Inicia o servidor MT5 MCP"""
        logger.info("🚀 Iniciando MT5 MCP Server (porta 8000)...")
        
        try:
            cmd = [sys.executable, "src/mcp_mt5/main.py"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['mt5'] = process
            time.sleep(2)  # Aguardar inicialização
            
            if process.poll() is None:
                logger.info("✅ MT5 MCP Server iniciado com sucesso")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ MT5 MCP Server falhou: {stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar MT5 MCP Server: {e}")
            return False

    def start_ollama_server(self):
        """Inicia o servidor Ollama MCP"""
        logger.info("🚀 Iniciando Ollama MCP Server (porta 8001)...")
        
        try:
            cmd = [sys.executable, "src/mcp_ollama/main.py"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['ollama'] = process
            time.sleep(3)  # Aguardar inicialização
            
            if process.poll() is None:
                logger.info("✅ Ollama MCP Server iniciado com sucesso")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Ollama MCP Server falhou: {stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Ollama MCP Server: {e}")
            return False

    def start_web_server(self):
        """Inicia o servidor Web"""
        logger.info("🚀 Iniciando Web Interface (porta 3000)...")
        
        try:
            cmd = [sys.executable, "src/web/app.py"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['web'] = process
            time.sleep(2)  # Aguardar inicialização
            
            if process.poll() is None:
                logger.info("✅ Web Interface iniciada com sucesso")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Web Interface falhou: {stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Web Interface: {e}")
            return False

    def start_worker(self):
        """Inicia o Worker em segundo plano"""
        logger.info("🚀 Iniciando Worker em segundo plano...")
        
        try:
            cmd = [sys.executable, "src/core/main.py"]
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['worker'] = process
            time.sleep(1)  # Aguardar inicialização
            
            if process.poll() is None:
                logger.info("✅ Worker iniciado com sucesso")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Worker falhou: {stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Worker: {e}")
            return False

    def start_all(self):
        """Inicia todos os servidores"""
        logger.info("\n" + "=" * 70)
        logger.info("🚀 INICIANDO SISTEMA DE TRADING COMPLETO")
        logger.info("=" * 70 + "\n")

        results = {
            "MT5 MCP Server": self.start_mt5_server(),
            "Ollama MCP Server": self.start_ollama_server(),
            "Web Interface": self.start_web_server(),
            "Worker": self.start_worker(),
        }

        logger.info("\n" + "=" * 70)
        logger.info("📊 STATUS DOS SERVIDORES")
        logger.info("=" * 70)

        all_ok = True
        for name, status in results.items():
            status_str = "✅ OK" if status else "❌ FALHOU"
            logger.info(f"{status_str}: {name}")
            if not status:
                all_ok = False

        if all_ok:
            logger.info("\n" + "=" * 70)
            logger.info("✅ TODOS OS SERVIDORES INICIADOS COM SUCESSO!")
            logger.info("=" * 70)
            logger.info("\n📍 Acessos:")
            logger.info("   • Web Interface:      http://localhost:3000")
            logger.info("   • MT5 MCP Server:     http://localhost:8000")
            logger.info("   • Ollama MCP Server:  http://localhost:8001")
            logger.info("\n🔧 Próximos passos:")
            logger.info("   1. Abra http://localhost:3000 no navegador")
            logger.info("   2. Execute: python test_chatbot_mt5_integration.py")
            logger.info("   3. Execute: python example_chatbot_mt5_usage.py")
            logger.info("\n" + "=" * 70 + "\n")
            return True
        else:
            logger.info("\n" + "=" * 70)
            logger.info("❌ ALGUNS SERVIDORES FALHARAM")
            logger.info("=" * 70)
            logger.info("\n🔍 Troubleshooting:")
            logger.info("   • Verifique se MT5 está rodando e logado")
            logger.info("   • Verifique se Ollama está instalado")
            logger.info("   • Verifique os logs acima para mais detalhes")
            logger.info("\n" + "=" * 70 + "\n")
            return False

    def stop_all(self):
        """Para todos os servidores"""
        logger.info("\n🛑 Parando todos os servidores...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"   Parando {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.warning(f"   {name} foi forçadamente encerrado")

        logger.info("✅ Todos os servidores foram parados\n")


def main():
    """Função principal"""
    starter = SystemStarter()
    
    try:
        success = starter.start_all()
        
        if success:
            logger.info("💡 Dica: Pressione Ctrl+C para parar todos os servidores")
            
            # Manter os processos rodando
            try:
                while True:
                    time.sleep(1)
                    
                    # Verificar se algum processo morreu
                    for name, process in starter.processes.items():
                        if process and process.poll() is not None:
                            logger.warning(f"⚠️  {name} foi encerrado inesperadamente")
                            
            except KeyboardInterrupt:
                logger.info("\n⏹️  Interrupção do usuário detectada")
                starter.stop_all()
                return 0
        else:
            logger.error("Falha ao iniciar sistema")
            starter.stop_all()
            return 1
            
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        starter.stop_all()
        return 1


if __name__ == "__main__":
    sys.exit(main())
