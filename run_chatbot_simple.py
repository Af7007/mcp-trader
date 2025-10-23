#!/usr/bin/env python3
"""
Chatbot de Trading Simples - Acesso Direto ao MT5
Sem HTTP, sem FastMCP - Direto com MetaTrader5 Python API
"""

import sys
import asyncio
import logging
from pathlib import Path
import MetaTrader5 as mt5

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from agents.generator import AgentGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleTradingChatbot:
    """Chatbot simples para trading"""
    
    def __init__(self):
        self.connected = False
        self.agent_generator = AgentGenerator()
    
    async def connect(self):
        """Conectar ao MT5"""
        if mt5.initialize():
            account = mt5.account_info()
            if account:
                self.connected = True
                logger.info(f"✅ Conectado à conta: {account.login}")
                logger.info(f"   Servidor: {account.server}")
                logger.info(f"   Saldo: ${account.balance:.2f}")
                return True
        
        logger.error("❌ Falha ao conectar ao MT5")
        return False
    
    async def get_account_info(self):
        """Obter informações da conta"""
        if not self.connected:
            return None
        
        account = mt5.account_info()
        if account:
            return {
                'login': account.login,
                'balance': account.balance,
                'equity': account.equity,
                'margin_free': account.margin_free,
                'margin_level': account.margin_level,
                'profit': account.profit
            }
        return None
    
    async def get_positions(self):
        """Obter posições abertas"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get()
        if positions:
            return [
                {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'sl': pos.sl,
                    'tp': pos.tp
                }
                for pos in positions
            ]
        return []
    
    async def get_price(self, symbol):
        """Obter preço de um símbolo"""
        if not self.connected:
            return None
        
        # Adicionar 'c' se não tiver
        if not symbol.endswith('c'):
            symbol = symbol + 'c'
        
        # Selecionar símbolo
        mt5.symbol_select(symbol, True)
        
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask
            }
        return None
    
    async def buy(self, symbol, volume, sl=None, tp=None):
        """Executar compra"""
        if not self.connected:
            return None
        
        # Adicionar 'c' se não tiver
        if not symbol.endswith('c'):
            symbol = symbol + 'c'
        
        # Selecionar símbolo
        mt5.symbol_select(symbol, True)
        
        # Obter preço
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return None
        
        # Preparar requisição
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 10,
            "magic": 234000,
            "comment": "Chatbot BUY",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        # Enviar ordem
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {
                'status': 'success',
                'order': result.order,
                'price': tick.ask,
                'symbol': symbol,
                'volume': volume
            }
        else:
            logger.error(f"   Erro na ordem: {result.comment}")
        
        return None
    
    async def sell(self, symbol, volume, sl=None, tp=None):
        """Executar venda"""
        if not self.connected:
            return None
        
        # Adicionar 'c' se não tiver
        if not symbol.endswith('c'):
            symbol = symbol + 'c'
        
        # Selecionar símbolo
        mt5.symbol_select(symbol, True)
        
        # Obter preço
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return None
        
        # Preparar requisição
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "deviation": 10,
            "magic": 234000,
            "comment": "Chatbot SELL",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        # Enviar ordem
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {
                'status': 'success',
                'order': result.order,
                'price': tick.bid,
                'symbol': symbol,
                'volume': volume
            }
        else:
            logger.error(f"   Erro na ordem: {result.comment}")
        
        return None
    
    async def close_position(self, ticket):
        """Fechar posição"""
        if not self.connected:
            return None
        
        # Obter posição
        positions = mt5.positions_get()
        position = None
        for pos in positions:
            if pos.ticket == ticket:
                position = pos
                break
        
        if not position:
            return None
        
        symbol = position.symbol
        volume = position.volume
        is_buy = position.type == 0
        
        # Obter preço
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return None
        
        # Preparar requisição
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY,
            "price": tick.bid if is_buy else tick.ask,
            "deviation": 10,
            "magic": 234000,
            "comment": f"Close {ticket}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Enviar ordem
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {
                'status': 'success',
                'order': result.order,
                'price': tick.bid if is_buy else tick.ask
            }
        
        return None
    
    def disconnect(self):
        """Desconectar do MT5"""
        mt5.shutdown()
        self.connected = False


async def main():
    """Função principal"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║           🤖 TRADING CHATBOT - MODO INTERATIVO             ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # Inicializar chatbot
    chatbot = SimpleTradingChatbot()
    
    logger.info("🔍 Conectando ao MT5...")
    if not await chatbot.connect():
        logger.error("❌ Falha ao conectar")
        return 1
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("💬 COMANDOS DISPONÍVEIS:")
    logger.info("=" * 60)
    logger.info("  • 'saldo' - Ver saldo da conta")
    logger.info("  • 'posições' - Ver posições abertas")
    logger.info("  • 'preço EURUSD' - Ver preço")
    logger.info("  • 'comprar EURUSD 0.1' - Comprar")
    logger.info("  • 'vender EURUSD 0.1' - Vender")
    logger.info("  • 'fechar 123456' - Fechar")
    logger.info("  • 'criar agente EURUSD com RSI' - Criar agente")
    logger.info("  • 'listar agentes' - Ver agentes")
    logger.info("  • 'ajuda' - Ver comandos")
    logger.info("  • 'sair' - Sair")
    logger.info("=" * 60)
    logger.info("")
    
    # Loop interativo
    try:
        while True:
            user_input = input("💬 Você: ").strip().lower()
            # Remover acentos para comparação
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
                logger.info("  • 'fechar 123456' - Fechar")
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
            if 'posicao' in user_input_clean or 'posição' in user_input or 'position' in user_input:
                positions = await chatbot.get_positions()
                if positions:
                    logger.info(f"   ✅ {len(positions)} posição(ões):")
                    for pos in positions:
                        logger.info(f"      • {pos['symbol']}: {pos['volume']} @ {pos['price_open']:.5f}")
                else:
                    logger.info("   ✅ Nenhuma posição aberta")
                continue
            
            # Preço
            if 'preco' in user_input_clean or 'preço' in user_input or 'price' in user_input:
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
            
            # Comprar
            if 'comprar' in user_input_clean or 'buy' in user_input:
                parts = user_input.split()
                if len(parts) >= 3:
                    symbol = parts[-2].upper()
                    try:
                        volume = float(parts[-1])
                        result = await chatbot.buy(symbol, volume)
                        if result:
                            logger.info(f"   ✅ Ordem executada!")
                            logger.info(f"      Order: {result['order']}")
                            logger.info(f"      Preço: {result['price']:.5f}")
                        else:
                            logger.error("   ❌ Erro ao executar ordem")
                            logger.info("   💡 Dica: Verifique volume mínimo (0.01) e saldo")
                    except ValueError:
                        logger.warning("   ⚠️  Volume inválido")
                else:
                    logger.warning("   ⚠️  Use: 'comprar EURUSD 0.1'")
                continue
            
            # Vender
            if 'vender' in user_input_clean or 'sell' in user_input:
                parts = user_input.split()
                if len(parts) >= 3:
                    symbol = parts[-2].upper()
                    try:
                        volume = float(parts[-1])
                        result = await chatbot.sell(symbol, volume)
                        if result:
                            logger.info(f"   ✅ Ordem executada!")
                            logger.info(f"      Order: {result['order']}")
                            logger.info(f"      Preço: {result['price']:.5f}")
                        else:
                            logger.error("   ❌ Erro ao executar ordem")
                            logger.info("   💡 Dica: Verifique volume mínimo (0.01) e saldo")
                    except ValueError:
                        logger.warning("   ⚠️  Volume inválido")
                else:
                    logger.warning("   ⚠️  Use: 'vender EURUSD 0.1'")
                continue
            
            # Fechar
            if 'fechar' in user_input_clean or 'close' in user_input:
                parts = user_input.split()
                if len(parts) >= 2:
                    try:
                        ticket = int(parts[-1])
                        result = await chatbot.close_position(ticket)
                        if result:
                            logger.info(f"   ✅ Posição fechada!")
                            logger.info(f"      Preço: {result['price']:.5f}")
                        else:
                            logger.error("   ❌ Erro ao fechar posição")
                            logger.info("   💡 Dica: Verifique se o ticket existe")
                    except ValueError:
                        logger.warning("   ⚠️  Ticket inválido")
                else:
                    logger.warning("   ⚠️  Use: 'fechar 123456'")
                continue
            
            # Comando: Criar agente
            if 'criar agente' in user_input_clean or 'create agent' in user_input:
                logger.info(f"🤖 Criando agente...")
                agent = chatbot.agent_generator.create_agent(user_input)
                if agent:
                    logger.info(f"   ✅ Agente criado com sucesso!")
                    logger.info(f"      Nome: {agent.name}")
                    logger.info(f"      ID: {agent.id}")
                    logger.info(f"      Símbolo: {agent.symbol}")
                    logger.info(f"      Volume: {agent.volume}")
                    logger.info(f"      TP: ${agent.take_profit}, SL: ${agent.stop_loss}")
                    logger.info(f"      Indicadores: {[ind.type.value for ind in agent.indicators]}")
                else:
                    logger.error("   ❌ Erro ao criar agente")
                continue
            
            # Comando: Listar agentes
            if 'listar agente' in user_input_clean or 'list agent' in user_input:
                agents = chatbot.agent_generator.list_agents()
                if agents:
                    logger.info(f"   ✅ {len(agents)} agente(s) criado(s):")
                    for agent in agents:
                        logger.info(f"      • {agent.name} ({agent.id})")
                else:
                    logger.info("   ✅ Nenhum agente criado ainda")
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
