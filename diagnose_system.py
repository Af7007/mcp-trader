#!/usr/bin/env python3
"""
Script de diagnóstico do sistema de trading
Verifica status de todos os componentes
"""

import requests
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemDiagnostics:
    """Diagnóstico do sistema"""

    def __init__(self):
        self.results = {}

    def check_mt5_server(self):
        """Verifica se o servidor MT5 MCP está rodando"""
        logger.info("\n🔍 Verificando MT5 MCP Server (porta 8000)...")
        
        try:
            response = requests.get("http://localhost:8000/mcp", timeout=5)
            if response.status_code in [200, 404]:  # 404 é ok, significa que o servidor está rodando
                logger.info("   ✅ MT5 MCP Server está RODANDO")
                self.results['mt5_server'] = True
                return True
            else:
                logger.warning(f"   ⚠️  MT5 MCP Server respondeu com status {response.status_code}")
                self.results['mt5_server'] = False
                return False
        except requests.exceptions.ConnectionError:
            logger.error("   ❌ MT5 MCP Server NÃO ESTÁ RODANDO")
            logger.info("      Inicie com: python src/mcp_mt5/main.py")
            self.results['mt5_server'] = False
            return False
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar: {e}")
            self.results['mt5_server'] = False
            return False

    def check_ollama_server(self):
        """Verifica se o servidor Ollama MCP está rodando"""
        logger.info("\n🔍 Verificando Ollama MCP Server (porta 8001)...")
        
        try:
            response = requests.get("http://localhost:8001/mcp", timeout=5)
            if response.status_code in [200, 404]:
                logger.info("   ✅ Ollama MCP Server está RODANDO")
                self.results['ollama_server'] = True
                return True
            else:
                logger.warning(f"   ⚠️  Ollama MCP Server respondeu com status {response.status_code}")
                self.results['ollama_server'] = False
                return False
        except requests.exceptions.ConnectionError:
            logger.error("   ❌ Ollama MCP Server NÃO ESTÁ RODANDO")
            logger.info("      Inicie com: python src/mcp_ollama/main.py")
            self.results['ollama_server'] = False
            return False
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar: {e}")
            self.results['ollama_server'] = False
            return False

    def check_web_server(self):
        """Verifica se o servidor Web está rodando"""
        logger.info("\n🔍 Verificando Web Interface (porta 3000)...")
        
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                logger.info("   ✅ Web Interface está RODANDO")
                self.results['web_server'] = True
                return True
            else:
                logger.warning(f"   ⚠️  Web Interface respondeu com status {response.status_code}")
                self.results['web_server'] = False
                return False
        except requests.exceptions.ConnectionError:
            logger.error("   ❌ Web Interface NÃO ESTÁ RODANDO")
            logger.info("      Inicie com: python src/web/app.py")
            self.results['web_server'] = False
            return False
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar: {e}")
            self.results['web_server'] = False
            return False

    def check_mt5_terminal(self):
        """Verifica se MT5 Terminal está rodando"""
        logger.info("\n🔍 Verificando MetaTrader 5 Terminal...")
        
        try:
            import MetaTrader5 as mt5
            
            if mt5.initialize():
                account = mt5.account_info()
                if account:
                    logger.info(f"   ✅ MT5 Terminal está RODANDO e LOGADO")
                    logger.info(f"      Conta: {account.login}")
                    logger.info(f"      Servidor: {account.server}")
                    logger.info(f"      Saldo: ${account.balance:.2f}")
                    self.results['mt5_terminal'] = True
                    mt5.shutdown()
                    return True
                else:
                    logger.error("   ❌ MT5 Terminal não está LOGADO")
                    logger.info("      Faça login no MT5 e tente novamente")
                    self.results['mt5_terminal'] = False
                    mt5.shutdown()
                    return False
            else:
                logger.error("   ❌ MT5 Terminal NÃO ESTÁ RODANDO")
                logger.info("      Inicie o MetaTrader 5 e faça login")
                self.results['mt5_terminal'] = False
                return False
        except ImportError:
            logger.error("   ❌ MetaTrader5 Python API não está instalada")
            logger.info("      Instale com: pip install MetaTrader5")
            self.results['mt5_terminal'] = False
            return False
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar: {e}")
            self.results['mt5_terminal'] = False
            return False

    def check_ollama_service(self):
        """Verifica se o serviço Ollama está rodando"""
        logger.info("\n🔍 Verificando Ollama Service (porta 11434)...")
        
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                logger.info("   ✅ Ollama Service está RODANDO")
                self.results['ollama_service'] = True
                return True
            else:
                logger.warning(f"   ⚠️  Ollama Service respondeu com status {response.status_code}")
                self.results['ollama_service'] = False
                return False
        except requests.exceptions.ConnectionError:
            logger.error("   ❌ Ollama Service NÃO ESTÁ RODANDO")
            logger.info("      Inicie com: ollama serve")
            self.results['ollama_service'] = False
            return False
        except Exception as e:
            logger.error(f"   ❌ Erro ao verificar: {e}")
            self.results['ollama_service'] = False
            return False

    def check_database(self):
        """Verifica se o banco de dados existe"""
        logger.info("\n🔍 Verificando Banco de Dados...")
        
        db_path = Path("trading_bot.db")
        if db_path.exists():
            logger.info(f"   ✅ Banco de dados existe: {db_path}")
            self.results['database'] = True
            return True
        else:
            logger.warning(f"   ⚠️  Banco de dados não encontrado: {db_path}")
            logger.info("      Será criado automaticamente na primeira execução")
            self.results['database'] = False
            return False

    def check_python_packages(self):
        """Verifica se os pacotes Python necessários estão instalados"""
        logger.info("\n🔍 Verificando Pacotes Python...")
        
        packages = {
            'MetaTrader5': 'MetaTrader5',
            'requests': 'requests',
            'aiohttp': 'aiohttp',
            'pydantic': 'pydantic',
            'pandas': 'pandas',
        }
        
        all_ok = True
        for import_name, package_name in packages.items():
            try:
                __import__(import_name)
                logger.info(f"   ✅ {package_name}")
            except ImportError:
                logger.error(f"   ❌ {package_name} NÃO INSTALADO")
                logger.info(f"      Instale com: pip install {package_name}")
                all_ok = False
        
        self.results['python_packages'] = all_ok
        return all_ok

    def run_all_checks(self):
        """Executa todos os diagnósticos"""
        logger.info("\n" + "=" * 70)
        logger.info("🔍 DIAGNÓSTICO DO SISTEMA DE TRADING")
        logger.info("=" * 70)

        self.check_python_packages()
        self.check_mt5_terminal()
        self.check_ollama_service()
        self.check_mt5_server()
        self.check_ollama_server()
        self.check_web_server()
        self.check_database()

        # Resumo
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESUMO DO DIAGNÓSTICO")
        logger.info("=" * 70)

        for component, status in self.results.items():
            status_str = "✅" if status else "❌"
            component_name = component.replace('_', ' ').title()
            logger.info(f"{status_str} {component_name}")

        # Recomendações
        logger.info("\n" + "=" * 70)
        logger.info("💡 RECOMENDAÇÕES")
        logger.info("=" * 70)

        if not self.results.get('mt5_terminal'):
            logger.info("1. ⚠️  MT5 Terminal não está rodando")
            logger.info("   → Inicie o MetaTrader 5 e faça login")

        if not self.results.get('ollama_service'):
            logger.info("2. ⚠️  Ollama Service não está rodando")
            logger.info("   → Execute: ollama serve")

        if not self.results.get('mt5_server'):
            logger.info("3. ⚠️  MT5 MCP Server não está rodando")
            logger.info("   → Execute: python src/mcp_mt5/main.py")

        if not self.results.get('ollama_server'):
            logger.info("4. ⚠️  Ollama MCP Server não está rodando")
            logger.info("   → Execute: python src/mcp_ollama/main.py")

        if not self.results.get('web_server'):
            logger.info("5. ⚠️  Web Interface não está rodando")
            logger.info("   → Execute: python src/web/app.py")

        # Status geral
        all_ok = all(self.results.values())
        
        logger.info("\n" + "=" * 70)
        if all_ok:
            logger.info("✅ SISTEMA PRONTO PARA USAR!")
            logger.info("=" * 70)
            logger.info("\n🚀 Próximos passos:")
            logger.info("   1. Execute: python test_chatbot_mt5_integration.py")
            logger.info("   2. Execute: python example_chatbot_mt5_usage.py")
            logger.info("   3. Acesse: http://localhost:3000")
        else:
            logger.info("❌ SISTEMA NÃO ESTÁ COMPLETAMENTE PRONTO")
            logger.info("=" * 70)
            logger.info("\n🔧 Corrija os problemas acima e tente novamente")

        logger.info("=" * 70 + "\n")
        
        return all_ok


def main():
    """Função principal"""
    diagnostics = SystemDiagnostics()
    all_ok = diagnostics.run_all_checks()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
