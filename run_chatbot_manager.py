#!/usr/bin/env python3
"""
Chatbot de Trading com Agent Manager
Gerencia agentes, monitora, pausa, retoma, deleta
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from chatbot.client import send_message_sync, TradingChatbot, ChatbotConfig  # MCP-ONLY CHATBOT
from agents.manager import AgentManager, AgentStatus
from core.database import setup_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)





class TradingChatbotWithManager:
    """Chatbot com Agent Manager integrado - MCP ONLY"""

    def __init__(self):
        self.connected = False
        self.manager = AgentManager()
        self.worker_running = False

        # Inicializar database
        setup_database()

    async def connect(self):
        """Testar conexão MCP"""
        try:
            # Testar se MCP MT5 server está rodando
            result = send_message_sync("teste")
            if "CONEXAO OK" in result.get("response", "") or "OK" in result.get("response", "").upper():
                self.connected = True
                logger.info("✅ Conectado via MCP:")
                logger.info("   Sistema: MT5 + Ollama MCP")
                return True
            else:
                logger.error("❌ Falha na conexão MCP")
                logger.info("💡 PARA FUNCIONAR:")
                logger.info("   1. Inicie o servidor MT5 MCP: python src/mcp_mt5/main.py")
                logger.info("   2. Inicie o servidor Ollama MCP: python src/mcp_ollama/main.py")
                logger.info("   3. OU use: python main.py (inicia tudo automaticamente)")
                return False
        except Exception as e:
            logger.error(f"❌ Erro de conexão MCP: {e}")
            logger.info("💡 Os servidores MCP precisam estar rodando primeiro!")
            return False

    async def get_account_info(self):
        """Obter informações da conta via MCP"""
        if not self.connected:
            logger.error("❌ MCP não conectado")
            return None

        try:
            result = send_message_sync("saldo")
            if result.get("response"):
                # Extrair números da resposta
                response = result["response"]
                import re
                balance_match = re.search(r'Saldo:\s*\$([0-9.]+)', response)
                equity_match = re.search(r'Equity:\s*\$([0-9.]+)', response)

                return {
                    'balance': float(balance_match.group(1)) if balance_match else 0,
                    'equity': float(equity_match.group(1)) if equity_match else 0,
                    'login': 'MCP-Connected'
                }
        except Exception as e:
            logger.error(f"Erro ao obter saldo via MCP: {e}")
        return None

    async def get_positions(self):
        """Obter posições abertas via MCP"""
        if not self.connected:
            logger.error("❌ MCP não conectado")
            return []

        try:
            result = send_message_sync("posições")
            if result.get("result", {}).get("positions"):
                return result["result"]["positions"]
        except Exception as e:
            logger.error(f"Erro ao obter posições via MCP: {e}")
        return []

    async def get_price(self, symbol):
        """Obter preço de um símbolo via MCP"""
        if not self.connected:
            logger.error("❌ MCP não conectado")
            return None

        try:
            result = send_message_sync(f"preço {symbol}")
            return {
                'symbol': symbol,
                'bid': 0.0,  # MCP processará realmente
                'ask': 0.0   # MCP processará realmente
            }
        except Exception as e:
            logger.error(f"Erro ao obter preço via MCP: {e}")
        return None

    def disconnect(self):
        """Não precisa desconectar MCP"""
        pass


async def main():
    """Função principal"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🤖 TRADING CHATBOT COM AGENT MANAGER                  ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # Inicializar chatbot
    chatbot = TradingChatbotWithManager()
    
    logger.info("🔍 Conectando ao Sistema MCP...")
    if not await chatbot.connect():
        logger.error("❌ SERVIDORES MCP NÃO DISPONÍVEIS - SISTEMA INOPERANTE")
        logger.error("💡 INSTRUÇÕES PARA FUNCIONAR:")
        logger.error("   1. Inicie o servidor MT5 MCP: uv run python src/mcp_mt5/main.py")
        logger.error("   2. Inicie o servidor Ollama MCP: uv run python src/mcp_ollama/main.py")
        logger.error("   3. OU use: uv run python main.py (inicia tudo)")
        logger.error("   4. Execute este comando novamente")
        return 1  # Exit with error
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("💬 COMANDOS DISPONÍVEIS:")
    logger.info("=" * 60)
    logger.info("  • 'saldo' - Ver saldo da conta")
    logger.info("  • 'posições' - Ver posições abertas")
    logger.info("  • 'preço EURUSD' - Ver preço")
    logger.info("  • 'comprar EURUSD 0.1' - Comprar")
    logger.info("  • 'vender EURUSD 0.1' - Vender")
    logger.info("  • 'criar agente EURUSD com RSI' - Criar agente")
    logger.info("  • 'listar agentes' - Ver agentes")
    logger.info("  • 'iniciar worker' - Iniciar monitoramento")
    logger.info("  • 'parar worker' - Parar monitoramento")
    logger.info("  • 'pausar agente <ID>' - Pausar agente")
    logger.info("  • 'retomar agente <ID>' - Retomar agente")
    logger.info("  • 'parar agente <ID>' - Parar agente")
    logger.info("  • 'deletar agente <ID>' - Deletar agente")
    logger.info("  • 'stats agente <ID>' - Ver estatísticas")
    logger.info("  • 'resumo' - Ver resumo do sistema")
    logger.info("  • 'fechar <TICKET>' - Fechar posição")
    logger.info("  • 'fechar tudo' - Fechar todas as posições")
    logger.info("  • 'ajuda' - Ver comandos")
    logger.info("  • 'sair' - Sair")
    logger.info("=" * 60)
    logger.info("")
    
    # Loop interativo
    try:
        while True:
            user_input = input("💬 Você: ").strip().lower()
            user_input_clean = user_input.replace('ã', 'a').replace('é', 'e').replace('ç', 'c')
            
            if not user_input:
                continue
            
            # Sair
            if user_input in ['sair', 'exit', 'quit']:
                logger.info("👋 Até logo!")
                break
            
            # Ajuda
            if user_input in ['ajuda', 'help']:
                logger.info("  • 'saldo' - Ver saldo")
                logger.info("  • 'posições' - Ver posições")
                logger.info("  • 'preço EURUSD' - Ver preço")
                logger.info("  • 'comprar EURUSD 0.1' - Comprar")
                logger.info("  • 'vender EURUSD 0.1' - Vender")
                logger.info("  • 'criar agente EURUSD com RSI' - Criar agente")
                logger.info("  • 'listar agentes' - Ver agentes")
                logger.info("  • 'iniciar worker' - Iniciar monitoramento")
                logger.info("  • 'parar worker' - Parar monitoramento")
                logger.info("  • 'pausar agente <ID>' - Pausar agente")
                logger.info("  • 'retomar agente <ID>' - Retomar agente")
                logger.info("  • 'parar agente <ID>' - Parar agente")
                logger.info("  • 'deletar agente <ID>' - Deletar agente")
                logger.info("  • 'stats agente <ID>' - Ver estatísticas")
                logger.info("  • 'resumo' - Ver resumo do sistema")
                logger.info("  • 'fechar <TICKET>' - Fechar posição")
                logger.info("  • 'fechar tudo' - Fechar todas as posições")
                continue
            
            # Saldo
            if 'saldo' in user_input or 'account' in user_input:
                account = await chatbot.get_account_info()
                if account:
                    logger.info(f"   ✅ Saldo: ${account['balance']:.2f}")
                    logger.info(f"   ✅ Equity: ${account['equity']:.2f}")
                    logger.info(f"   ✅ Margem Livre: ${account['margin_free']:.2f}")
                else:
                    logger.error("   ❌ Erro ao obter saldo")
                continue
            
            # Posições
            if 'posicao' in user_input_clean or 'posi' in user_input_clean:
                positions = await chatbot.get_positions()
                if positions:
                    logger.info(f"   ✅ {len(positions)} posição(ões):")
                    for pos in positions:
                        logger.info(f"      • {pos['symbol']}: {pos['volume']} @ {pos['price_open']:.5f}")
                else:
                    logger.info("   ✅ Nenhuma posição aberta")
                continue
            
            # Preço
            if 'preco' in user_input_clean or 'price' in user_input:
                parts = user_input.split()
                if len(parts) >= 2:
                    symbol = parts[-1].upper()
                    price = await chatbot.get_price(symbol)
                    if price:
                        logger.info(f"   ✅ {price['symbol']}:")
                        logger.info(f"      Bid: {price['bid']:.5f}")
                        logger.info(f"      Ask: {price['ask']:.5f}")
                    else:
                        logger.error("   ❌ Erro ao obter preço")
                else:
                    logger.warning("   ⚠️  Use: 'preço EURUSD'")
                continue
            
            # COMPRAR (AGORA MCP-ONLY COM AUTO-FECHAMENTO E TP/SL)
            if 'comprar' in user_input_clean:
                if not chatbot.connected:
                    logger.error("   ❌ MCP não conectado - execute os servidores MCP primeiro")
                    continue
                logger.info(f"🟢 Processando via MCP: {user_input}")
                result = send_message_sync(user_input)
                if result and result.get('response'):
                    logger.info(f"   {result['response']}")
                else:
                    logger.error("   ❌ Erro na comunicação MCP")
                continue

            # VENDER (AGORA MCP-ONLY COM AUTO-FECHAMENTO E TP/SL)
            if 'vender' in user_input_clean:
                if not chatbot.connected:
                    logger.error("   ❌ MCP não conectado - execute os servidores MCP primeiro")
                    continue
                logger.info(f"🔴 Processando via MCP: {user_input}")
                result = send_message_sync(user_input)
                if result and result.get('response'):
                    logger.info(f"   {result['response']}")
                else:
                    logger.error("   ❌ Erro na comunicação MCP")
                continue
            
            # Criar agente
            if 'criar agente' in user_input_clean:
                logger.info("🤖 Criando agente...")
                agent = chatbot.manager.create_agent(user_input)
                if agent:
                    logger.info(f"   ✅ Agente criado com sucesso!")
                    logger.info(f"      Nome: {agent.config.name}")
                    logger.info(f"      ID: {agent.config.id}")
                    logger.info(f"      Símbolo: {agent.config.symbol}")
                    logger.info(f"      Volume: {agent.config.volume}")
                    logger.info(f"      TP: ${agent.config.take_profit}, SL: ${agent.config.stop_loss}")
                    logger.info(f"      Indicadores: {[ind.type.value for ind in agent.config.indicators]}")
                else:
                    logger.error("   ❌ Erro ao criar agente")
                continue
            
            # Listar agentes
            if 'listar agente' in user_input_clean:
                agents = chatbot.manager.list_agents()
                if agents:
                    logger.info(f"   ✅ {len(agents)} agente(s) criado(s):")
                    for agent in agents:
                        logger.info(f"      • {agent.config.name} ({agent.config.id})")
                        logger.info(f"        Status: {agent.status.value}")
                else:
                    logger.info("   ✅ Nenhum agente criado")
                continue
            
            # Iniciar worker
            if 'iniciar worker' in user_input_clean:
                if not chatbot.worker_running:
                    chatbot.manager.start_worker(check_interval=30)
                    chatbot.worker_running = True
                    logger.info("   ✅ Worker iniciado")
                else:
                    logger.warning("   ⚠️  Worker já está rodando")
                continue
            
            # Parar worker
            if 'parar worker' in user_input_clean:
                if chatbot.worker_running:
                    chatbot.manager.stop_worker()
                    chatbot.worker_running = False
                    logger.info("   ✅ Worker parado")
                else:
                    logger.warning("   ⚠️  Worker não está rodando")
                continue
            
            # Pausar agente
            if 'pausar agente' in user_input_clean:
                parts = user_input.split()
                if len(parts) >= 3:
                    agent_id = parts[-1]
                    if chatbot.manager.pause_agent(agent_id):
                        logger.info(f"   ✅ Agente {agent_id} pausado")
                    else:
                        logger.error(f"   ❌ Agente {agent_id} não encontrado")
                else:
                    logger.warning("   ⚠️  Use: 'pausar agente <ID>'")
                continue
            
            # Retomar agente
            if 'retomar agente' in user_input_clean:
                parts = user_input.split()
                if len(parts) >= 3:
                    agent_id = parts[-1]
                    if chatbot.manager.resume_agent(agent_id):
                        logger.info(f"   ✅ Agente {agent_id} retomado")
                    else:
                        logger.error(f"   ❌ Agente {agent_id} não encontrado")
                else:
                    logger.warning("   ⚠️  Use: 'retomar agente <ID>'")
                continue
            
            # Parar agente
            if 'parar agente' in user_input_clean:
                parts = user_input.split()
                if len(parts) >= 3:
                    agent_id = parts[-1]
                    if chatbot.manager.stop_agent(agent_id):
                        logger.info(f"   ✅ Agente {agent_id} parado")
                    else:
                        logger.error(f"   ❌ Agente {agent_id} não encontrado")
                else:
                    logger.warning("   ⚠️  Use: 'parar agente <ID>'")
                continue
            
            # Deletar agente
            if 'deletar agente' in user_input_clean:
                parts = user_input.split()
                if len(parts) >= 3:
                    agent_id = parts[-1]
                    if chatbot.manager.delete_agent(agent_id):
                        logger.info(f"   ✅ Agente {agent_id} deletado")
                    else:
                        logger.error(f"   ❌ Agente {agent_id} não encontrado")
                else:
                    logger.warning("   ⚠️  Use: 'deletar agente <ID>'")
                continue
            
            # Stats agente
            if 'stats agente' in user_input_clean:
                parts = user_input.split()
                if len(parts) >= 3:
                    agent_id = parts[-1]
                    stats = chatbot.manager.get_agent_stats(agent_id)
                    if stats:
                        logger.info(f"   ✅ Estatísticas de {agent_id}:")
                        logger.info(f"      Status: {stats['status']}")
                        logger.info(f"      Trades abertos: {stats['trades_opened']}")
                        logger.info(f"      Trades fechados: {stats['trades_closed']}")
                        logger.info(f"      Lucro total: ${stats['total_profit']:.2f}")
                        logger.info(f"      Uptime: {stats['uptime_seconds']:.0f}s")
                    else:
                        logger.error(f"   ❌ Agente {agent_id} não encontrado")
                else:
                    logger.warning("   ⚠️  Use: 'stats agente <ID>'")
                continue
            
            # Resumo
            if 'resumo' in user_input_clean:
                summary = chatbot.manager.get_summary()
                logger.info("   ✅ Resumo do Sistema:")
                logger.info(f"      Total de agentes: {summary['total_agents']}")
                logger.info(f"      Ativos: {summary['active']}")
                logger.info(f"      Pausados: {summary['paused']}")
                logger.info(f"      Parados: {summary['stopped']}")
                logger.info(f"      Total de trades: {summary['total_trades']}")
                logger.info(f"      Lucro total: ${summary['total_profit']:.2f}")
                logger.info(f"      Worker: {'Rodando' if summary['worker_running'] else 'Parado'}")
                continue
            
            # Fechar posição específica (VIA MCP)
            if 'fechar' in user_input_clean and 'tudo' not in user_input_clean:
                logger.info(f"🔒 Processando: {user_input}")
                result = send_message_sync(user_input)
                if result and result.get('response'):
                    logger.info(f"   {result['response']}")
                else:
                    logger.error("   ❌ Erro na comunicação MCP")
                continue

            # Fechar todas as posições (VIA MCP)
            if 'fechar tudo' in user_input_clean:
                logger.info(f"🔒 Processando: {user_input}")
                result = send_message_sync(user_input)
                if result and result.get('response'):
                    logger.info(f"   {result['response']}")
                else:
                    logger.error("   ❌ Erro na comunicação MCP")
                continue
            
            # Comando não reconhecido
            logger.warning(f"   ❓ Comando não reconhecido: '{user_input}'")
            logger.info("   Digite 'ajuda' para ver comandos")
    
    except KeyboardInterrupt:
        logger.info("\n👋 Até logo!")
    finally:
        chatbot.disconnect()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n👋 Até logo!")
        sys.exit(0)
