#!/usr/bin/env python3
"""
Script para iniciar o Chatbot de Trading
Acesso via terminal interativo
"""

import sys
import asyncio
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Inicia o chatbot interativo"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║           🤖 TRADING CHATBOT - MODO INTERATIVO             ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    try:
        from chatbot.mt5_integration import ChatbotMT5Integration
        
        # Inicializar integração
        integration = ChatbotMT5Integration()
        
        logger.info("🔍 Verificando conexão com MT5...")
        connected = await integration.verify_connection()
        
        if not connected:
            logger.error("❌ Não foi possível conectar ao MT5")
            logger.info("   Certifique-se de que:")
            logger.info("   1. MT5 Terminal está rodando e logado")
            logger.info("   2. Execute: python test_mt5_direct.py")
            return 1
        
        logger.info("✅ Conectado ao MT5 com sucesso!")
        logger.info("")
        logger.info("=" * 60)
        logger.info("💬 COMANDOS DISPONÍVEIS:")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📊 Informações da Conta:")
        logger.info("  • 'saldo' ou 'account' - Ver saldo e informações")
        logger.info("  • 'posições' ou 'positions' - Ver posições abertas")
        logger.info("")
        logger.info("💹 Dados de Mercado:")
        logger.info("  • 'preço EURUSD' - Ver preço de um símbolo")
        logger.info("  • 'velas EURUSD' - Ver últimas velas")
        logger.info("")
        logger.info("🔄 Operações de Trading:")
        logger.info("  • 'comprar EURUSD 0.1' - Executar compra")
        logger.info("  • 'vender EURUSD 0.1' - Executar venda")
        logger.info("  • 'fechar 123456' - Fechar posição")
        logger.info("")
        logger.info("🛠️  Utilitários:")
        logger.info("  • 'ajuda' ou 'help' - Ver esta mensagem")
        logger.info("  • 'sair' ou 'exit' - Sair do chatbot")
        logger.info("")
        logger.info("=" * 60)
        logger.info("")
        
        # Loop interativo
        while True:
            try:
                user_input = input("💬 Você: ").strip().lower()
                
                if not user_input:
                    continue
                
                # Comandos de saída
                if user_input in ['sair', 'exit', 'quit']:
                    logger.info("👋 Até logo!")
                    break
                
                # Comandos de ajuda
                if user_input in ['ajuda', 'help']:
                    logger.info("")
                    logger.info("=" * 60)
                    logger.info("💬 COMANDOS DISPONÍVEIS:")
                    logger.info("=" * 60)
                    logger.info("  • 'saldo' - Ver saldo da conta")
                    logger.info("  • 'posições' - Ver posições abertas")
                    logger.info("  • 'preço EURUSD' - Ver preço")
                    logger.info("  • 'velas EURUSD' - Ver velas")
                    logger.info("  • 'comprar EURUSD 0.1' - Comprar")
                    logger.info("  • 'vender EURUSD 0.1' - Vender")
                    logger.info("  • 'fechar 123456' - Fechar posição")
                    logger.info("")
                    continue
                
                # Comando: Saldo
                if 'saldo' in user_input or 'account' in user_input:
                    logger.info("📊 Obtendo informações da conta...")
                    account = await integration.get_account_summary()
                    if account.get('status') == 'success':
                        logger.info(f"   ✅ Saldo: ${account.get('balance', 0):.2f}")
                        logger.info(f"   ✅ Equity: ${account.get('equity', 0):.2f}")
                        logger.info(f"   ✅ Margem Livre: ${account.get('margin_free', 0):.2f}")
                    else:
                        logger.error(f"   ❌ Erro: {account.get('message')}")
                    continue
                
                # Comando: Posições
                if 'posição' in user_input or 'position' in user_input:
                    logger.info("📋 Obtendo posições abertas...")
                    positions = await integration.get_open_positions_summary()
                    if positions.get('status') == 'success':
                        count = positions.get('count', 0)
                        if count > 0:
                            logger.info(f"   ✅ {count} posição(ões) aberta(s):")
                            for pos in positions.get('positions', []):
                                logger.info(f"      • {pos['symbol']}: {pos['volume']} lots @ {pos['price_open']:.5f}")
                        else:
                            logger.info("   ✅ Nenhuma posição aberta")
                    else:
                        logger.error(f"   ❌ Erro: {positions.get('message')}")
                    continue
                
                # Comando: Preço
                if 'preço' in user_input or 'price' in user_input:
                    parts = user_input.split()
                    if len(parts) >= 2:
                        symbol = parts[-1].upper() + 'c'  # Adicionar 'c' para cents
                        logger.info(f"💹 Obtendo preço de {symbol}...")
                        price = await integration.get_symbol_price(symbol)
                        if price.get('status') == 'success':
                            logger.info(f"   ✅ {symbol}:")
                            logger.info(f"      Bid: {price.get('bid'):.5f}")
                            logger.info(f"      Ask: {price.get('ask'):.5f}")
                        else:
                            logger.error(f"   ❌ Erro: {price.get('message')}")
                    else:
                        logger.warning("   ⚠️  Use: 'preço EURUSD'")
                    continue
                
                # Comando: Velas
                if 'vela' in user_input or 'candle' in user_input:
                    parts = user_input.split()
                    if len(parts) >= 2:
                        symbol = parts[-1].upper() + 'c'  # Adicionar 'c' para cents
                        logger.info(f"📊 Obtendo velas de {symbol}...")
                        data = await integration.get_market_data(symbol, timeframe=60, count=5)
                        if data.get('status') == 'success':
                            candles = data.get('candles', [])
                            if candles:
                                logger.info(f"   ✅ Últimas 3 velas de {symbol}:")
                                for i, candle in enumerate(candles[-3:]):
                                    logger.info(f"      {i+1}. O:{candle['open']:.5f} H:{candle['high']:.5f} L:{candle['low']:.5f} C:{candle['close']:.5f}")
                        else:
                            logger.error(f"   ❌ Erro: {data.get('message')}")
                    else:
                        logger.warning("   ⚠️  Use: 'velas EURUSD'")
                    continue
                
                # Comando: Comprar
                if 'comprar' in user_input or 'buy' in user_input:
                    parts = user_input.split()
                    if len(parts) >= 3:
                        symbol = parts[-2].upper() + 'c'  # Adicionar 'c' para cents
                        try:
                            volume = float(parts[-1])
                            logger.info(f"🟢 Executando compra de {volume} {symbol}...")
                            result = await integration.execute_buy_order(symbol, volume)
                            if result.get('status') == 'success':
                                logger.info(f"   ✅ Ordem executada!")
                                logger.info(f"      Preço: {result.get('price'):.5f}")
                                logger.info(f"      Order: {result.get('order')}")
                            else:
                                logger.error(f"   ❌ Erro: {result.get('message')}")
                        except ValueError:
                            logger.warning("   ⚠️  Volume inválido")
                    else:
                        logger.warning("   ⚠️  Use: 'comprar EURUSD 0.1'")
                    continue
                
                # Comando: Vender
                if 'vender' in user_input or 'sell' in user_input:
                    parts = user_input.split()
                    if len(parts) >= 3:
                        symbol = parts[-2].upper() + 'c'  # Adicionar 'c' para cents
                        try:
                            volume = float(parts[-1])
                            logger.info(f"🔴 Executando venda de {volume} {symbol}...")
                            result = await integration.execute_sell_order(symbol, volume)
                            if result.get('status') == 'success':
                                logger.info(f"   ✅ Ordem executada!")
                                logger.info(f"      Preço: {result.get('price'):.5f}")
                                logger.info(f"      Order: {result.get('order')}")
                            else:
                                logger.error(f"   ❌ Erro: {result.get('message')}")
                        except ValueError:
                            logger.warning("   ⚠️  Volume inválido")
                    else:
                        logger.warning("   ⚠️  Use: 'vender EURUSD 0.1'")
                    continue
                
                # Comando: Fechar
                if 'fechar' in user_input or 'close' in user_input:
                    parts = user_input.split()
                    if len(parts) >= 2:
                        try:
                            ticket = int(parts[-1])
                            logger.info(f"🔒 Fechando posição {ticket}...")
                            result = await integration.close_position(ticket)
                            if result.get('status') == 'success':
                                logger.info(f"   ✅ Posição fechada!")
                                logger.info(f"      Preço: {result.get('price'):.5f}")
                            else:
                                logger.error(f"   ❌ Erro: {result.get('message')}")
                        except ValueError:
                            logger.warning("   ⚠️  Ticket inválido")
                    else:
                        logger.warning("   ⚠️  Use: 'fechar 123456'")
                    continue
                
                # Comando não reconhecido
                logger.warning(f"   ❓ Comando não reconhecido: '{user_input}'")
                logger.info("   Digite 'ajuda' para ver comandos disponíveis")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Até logo!")
                break
            except Exception as e:
                logger.error(f"❌ Erro: {e}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar chatbot: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n👋 Até logo!")
        sys.exit(0)
