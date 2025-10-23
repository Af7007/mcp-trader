#!/usr/bin/env python3
"""
Exemplo de uso da integração Chatbot ↔ MT5
Demonstra como usar o MT5Connector e ChatbotMT5Integration
"""

import asyncio
import sys
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chatbot.mt5_integration import ChatbotMT5Integration
from core.mt5_connector import MT5Connector, MT5OperationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_1_basic_connection():
    """Exemplo 1: Conexão básica"""
    print("\n" + "=" * 60)
    print("EXEMPLO 1: Conexão Básica")
    print("=" * 60)

    integration = ChatbotMT5Integration()
    connected = await integration.verify_connection()

    if connected:
        print("✅ Conectado ao MT5 com sucesso!")
    else:
        print("❌ Falha ao conectar ao MT5")


async def example_2_account_info():
    """Exemplo 2: Obter informações da conta"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Informações da Conta")
    print("=" * 60)

    integration = ChatbotMT5Integration()
    account = await integration.get_account_summary()

    if account.get("status") == "success":
        print(f"✅ Conta: {account.get('login')}")
        print(f"   Saldo: ${account.get('balance'):.2f}")
        print(f"   Equity: ${account.get('equity'):.2f}")
        print(f"   Margem Livre: ${account.get('margin_free'):.2f}")
        print(f"   Lucro/Prejuízo: ${account.get('profit'):.2f}")
    else:
        print(f"❌ Erro: {account.get('message')}")


async def example_3_open_positions():
    """Exemplo 3: Verificar posições abertas"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Posições Abertas")
    print("=" * 60)

    integration = ChatbotMT5Integration()
    positions = await integration.get_open_positions_summary()

    if positions.get("status") == "success":
        count = positions.get("count", 0)
        print(f"✅ Total de posições: {count}")

        if count > 0:
            print("\nDetalhes:")
            for pos in positions.get("positions", []):
                print(f"\n   Ticket: {pos.get('ticket')}")
                print(f"   Símbolo: {pos.get('symbol')}")
                print(f"   Tipo: {pos.get('type')}")
                print(f"   Volume: {pos.get('volume')} lots")
                print(f"   Preço de Entrada: {pos.get('price_open'):.5f}")
                print(f"   Preço Atual: {pos.get('price_current'):.5f}")
                print(f"   Lucro/Prejuízo: ${pos.get('profit'):.2f}")
                if pos.get('sl'):
                    print(f"   Stop Loss: {pos.get('sl'):.5f}")
                if pos.get('tp'):
                    print(f"   Take Profit: {pos.get('tp'):.5f}")
        else:
            print("   Nenhuma posição aberta")
    else:
        print(f"❌ Erro: {positions.get('message')}")


async def example_4_symbol_prices():
    """Exemplo 4: Obter preços de símbolos"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Preços de Símbolos")
    print("=" * 60)

    integration = ChatbotMT5Integration()
    symbols = ["EURUSD", "GBPUSD", "XAUUSD"]

    for symbol in symbols:
        price_data = await integration.get_symbol_price(symbol)

        if price_data.get("status") == "success":
            bid = price_data.get("bid", 0)
            ask = price_data.get("ask", 0)
            spread = (ask - bid) * 10000  # em pips (para forex)
            print(f"\n✅ {symbol}")
            print(f"   Bid: {bid:.5f}")
            print(f"   Ask: {ask:.5f}")
            print(f"   Spread: {spread:.1f} pips")
        else:
            print(f"\n❌ {symbol}: {price_data.get('message')}")


async def example_5_market_data():
    """Exemplo 5: Obter dados de mercado (velas)"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Dados de Mercado (Velas)")
    print("=" * 60)

    integration = ChatbotMT5Integration()

    market_data = await integration.get_market_data(
        symbol="EURUSD",
        timeframe=60,  # H1
        count=5
    )

    if market_data.get("status") == "success":
        print(f"✅ Dados de EURUSD (H1)")
        print(f"   Total de velas: {market_data.get('count')}")

        candles = market_data.get("candles", [])
        if candles:
            print("\n   Últimas 5 velas:")
            print("   " + "-" * 55)
            print("   | Time                | O      | H      | L      | C      |")
            print("   " + "-" * 55)

            for candle in candles[-5:]:
                time_str = str(candle.get("time", ""))[:19]
                o = candle.get("open", 0)
                h = candle.get("high", 0)
                l = candle.get("low", 0)
                c = candle.get("close", 0)
                print(f"   | {time_str} | {o:.4f} | {h:.4f} | {l:.4f} | {c:.4f} |")

            print("   " + "-" * 55)
    else:
        print(f"❌ Erro: {market_data.get('message')}")


async def example_6_validate_symbols():
    """Exemplo 6: Validar símbolos"""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Validação de Símbolos")
    print("=" * 60)

    integration = ChatbotMT5Integration()
    symbols_to_test = ["EURUSD", "GBPUSD", "XAUUSD", "INVALID_SYMBOL"]

    print("\nValidando símbolos...")
    for symbol in symbols_to_test:
        is_valid = await integration.validate_symbol(symbol)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {symbol}: {'Válido' if is_valid else 'Inválido'}")


async def example_7_execute_order():
    """Exemplo 7: Executar ordem (CUIDADO: Operação Real!)"""
    print("\n" + "=" * 60)
    print("EXEMPLO 7: Executar Ordem (SIMULADO)")
    print("=" * 60)
    print("\n⚠️  ESTE EXEMPLO NÃO EXECUTA ORDENS REAIS")
    print("   Para testar, descomente o código abaixo\n")

    # DESCOMENTE PARA EXECUTAR ORDEM REAL (CUIDADO!)
    """
    integration = ChatbotMT5Integration()

    # Executar compra
    result = await integration.execute_buy_order(
        symbol="EURUSD",
        volume=0.01,  # 0.01 lots = 1000 units
        sl=1.0800,    # Stop loss
        tp=1.0950     # Take profit
    )

    if result.get("status") == "success":
        print(f"✅ Ordem BUY executada!")
        print(f"   Símbolo: {result.get('symbol')}")
        print(f"   Volume: {result.get('volume')} lots")
        print(f"   Preço: {result.get('price'):.5f}")
        print(f"   Order: {result.get('order')}")
    else:
        print(f"❌ Erro: {result.get('message')}")
    """

    print("   Exemplo de código:")
    print("""
    result = await integration.execute_buy_order(
        symbol="EURUSD",
        volume=0.01,
        sl=1.0800,
        tp=1.0950
    )
    """)


async def example_8_close_position():
    """Exemplo 8: Fechar posição (CUIDADO: Operação Real!)"""
    print("\n" + "=" * 60)
    print("EXEMPLO 8: Fechar Posição (SIMULADO)")
    print("=" * 60)
    print("\n⚠️  ESTE EXEMPLO NÃO FECHA POSIÇÕES REAIS")
    print("   Para testar, descomente o código abaixo\n")

    # DESCOMENTE PARA FECHAR POSIÇÃO REAL (CUIDADO!)
    """
    integration = ChatbotMT5Integration()

    # Obter posições abertas
    positions = await integration.get_open_positions_summary()

    if positions.get("count", 0) > 0:
        # Fechar primeira posição
        ticket = positions.get("positions")[0].get("ticket")

        result = await integration.close_position(ticket)

        if result.get("status") == "success":
            print(f"✅ Posição {ticket} fechada!")
            print(f"   Preço: {result.get('price'):.5f}")
        else:
            print(f"❌ Erro: {result.get('message')}")
    else:
        print("   Nenhuma posição aberta para fechar")
    """

    print("   Exemplo de código:")
    print("""
    result = await integration.close_position(ticket=123456)
    """)


async def example_9_direct_connector():
    """Exemplo 9: Usar MT5Connector diretamente"""
    print("\n" + "=" * 60)
    print("EXEMPLO 9: Usar MT5Connector Diretamente")
    print("=" * 60)

    connector = MT5Connector(
        server_url="http://localhost:8000",
        timeout=30,
        max_retries=3,
        retry_delay=1.0
    )

    try:
        # Verificar conexão
        if connector.check_connection():
            print("✅ Conectado ao MT5")

            # Obter informações da conta
            account = connector.get_account_info()
            print(f"\n   Saldo: ${account.get('balance', 0):.2f}")

            # Obter posições
            positions = connector.get_positions()
            print(f"   Posições abertas: {len(positions)}")

            # Obter preço
            tick = connector.get_symbol_tick("EURUSD")
            print(f"   EURUSD: {tick.get('bid'):.5f} / {tick.get('ask'):.5f}")

    except MT5OperationError as e:
        print(f"❌ Erro: {e}")


async def main():
    """Executa todos os exemplos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  EXEMPLOS DE USO: CHATBOT ↔ MT5".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    try:
        await example_1_basic_connection()
        await example_2_account_info()
        await example_3_open_positions()
        await example_4_symbol_prices()
        await example_5_market_data()
        await example_6_validate_symbols()
        await example_7_execute_order()
        await example_8_close_position()
        await example_9_direct_connector()

        print("\n" + "=" * 60)
        print("✅ Todos os exemplos executados com sucesso!")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Erro ao executar exemplos: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
