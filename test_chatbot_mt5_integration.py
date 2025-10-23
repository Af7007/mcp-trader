#!/usr/bin/env python3
"""
Teste de integração Chatbot ↔ MT5
Valida a conexão e operações básicas
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chatbot.mt5_integration import ChatbotMT5Integration
from core.mt5_connector import MT5Connector, MT5OperationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_connection():
    """Testa conexão básica com MT5"""
    logger.info("=" * 60)
    logger.info("🔍 TESTE 1: Verificando conexão com MT5")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()
    connected = await integration.verify_connection()

    if connected:
        logger.info("✅ Conexão com MT5 estabelecida com sucesso!")
        return True
    else:
        logger.error("❌ Falha ao conectar com MT5")
        logger.info("   Certifique-se de que:")
        logger.info("   1. MT5 está rodando e logado")
        logger.info("   2. O servidor MCP MT5 está iniciado (porta 8000)")
        return False


async def test_account_info():
    """Testa obtenção de informações da conta"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 2: Obtendo informações da conta")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()

    try:
        account = await integration.get_account_summary()

        if account.get("status") == "success":
            logger.info("✅ Informações da conta obtidas:")
            logger.info(f"   Balance: ${account.get('balance', 0):.2f}")
            logger.info(f"   Equity: ${account.get('equity', 0):.2f}")
            logger.info(f"   Margem Livre: ${account.get('margin_free', 0):.2f}")
            logger.info(f"   Nível de Margem: {account.get('margin_level', 0):.2f}%")
            logger.info(f"   Servidor: {account.get('server')}")
            return True
        else:
            logger.error(f"❌ Erro: {account.get('message')}")
            return False
    except Exception as e:
        logger.error(f"❌ Exceção: {e}")
        return False


async def test_positions():
    """Testa obtenção de posições abertas"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 3: Verificando posições abertas")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()

    try:
        positions = await integration.get_open_positions_summary()

        if positions.get("status") == "success":
            count = positions.get("count", 0)
            logger.info(f"✅ Posições obtidas: {count} aberta(s)")

            if count > 0:
                for pos in positions.get("positions", []):
                    logger.info(f"   • {pos.get('symbol')} {pos.get('type')} "
                              f"{pos.get('volume')} lots @ {pos.get('price_open'):.5f} "
                              f"(Profit: ${pos.get('profit'):.2f})")
            else:
                logger.info("   Nenhuma posição aberta no momento")

            return True
        else:
            logger.error(f"❌ Erro: {positions.get('message')}")
            return False
    except Exception as e:
        logger.error(f"❌ Exceção: {e}")
        return False


async def test_symbol_validation():
    """Testa validação de símbolos"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 4: Validando símbolos")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()
    symbols_to_test = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "INVALID123"]

    for symbol in symbols_to_test:
        try:
            is_valid = await integration.validate_symbol(symbol)
            status = "✅" if is_valid else "❌"
            logger.info(f"   {status} {symbol}: {'Válido' if is_valid else 'Inválido'}")
        except Exception as e:
            logger.error(f"   ❌ {symbol}: Erro - {e}")

    return True


async def test_symbol_price():
    """Testa obtenção de preços"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 5: Obtendo preços de símbolos")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()
    symbols = ["EURUSD", "GBPUSD", "XAUUSD"]

    for symbol in symbols:
        try:
            price_data = await integration.get_symbol_price(symbol)

            if price_data.get("status") == "success":
                logger.info(f"   ✅ {symbol}:")
                logger.info(f"      Bid: {price_data.get('bid'):.5f}")
                logger.info(f"      Ask: {price_data.get('ask'):.5f}")
            else:
                logger.warning(f"   ⚠️  {symbol}: {price_data.get('message')}")
        except Exception as e:
            logger.error(f"   ❌ {symbol}: {e}")

    return True


async def test_market_data():
    """Testa obtenção de dados de mercado"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 6: Obtendo dados de mercado (velas)")
    logger.info("=" * 60)

    integration = ChatbotMT5Integration()

    try:
        market_data = await integration.get_market_data(
            symbol="EURUSD",
            timeframe=60,  # H1
            count=5
        )

        if market_data.get("status") == "success":
            logger.info(f"✅ Dados obtidos para EURUSD (H1):")
            logger.info(f"   Total de velas: {market_data.get('count')}")

            candles = market_data.get("candles", [])
            if candles:
                logger.info("   Últimas 3 velas:")
                for i, candle in enumerate(candles[-3:]):
                    logger.info(f"      {i+1}. O:{candle.get('open'):.5f} "
                              f"H:{candle.get('high'):.5f} "
                              f"L:{candle.get('low'):.5f} "
                              f"C:{candle.get('close'):.5f}")
            return True
        else:
            logger.error(f"❌ Erro: {market_data.get('message')}")
            return False
    except Exception as e:
        logger.error(f"❌ Exceção: {e}")
        return False


async def main():
    """Executa todos os testes"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  TESTE DE INTEGRAÇÃO CHATBOT ↔ MT5".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")

    results = {
        "Conexão": await test_connection(),
        "Informações da Conta": await test_account_info(),
        "Posições Abertas": await test_positions(),
        "Validação de Símbolos": await test_symbol_validation(),
        "Preços de Símbolos": await test_symbol_price(),
        "Dados de Mercado": await test_market_data(),
    }

    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 60)
    logger.info(f"Resultado: {passed}/{total} testes passaram")

    if passed == total:
        logger.info("🎉 Todos os testes passaram! Integração funcionando!")
    else:
        logger.warning(f"⚠️  {total - passed} teste(s) falharam. Verifique os erros acima.")

    logger.info("=" * 60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
