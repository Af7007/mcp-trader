#!/usr/bin/env python3
"""
Teste direto de MT5 sem HTTP
Chama MetaTrader5 Python API diretamente
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Testa conexão com MT5"""
    logger.info("=" * 60)
    logger.info("🔍 TESTE 1: Verificando conexão com MT5")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            logger.info("✅ MT5 inicializado com sucesso")
            account = mt5.account_info()
            if account:
                logger.info(f"✅ Conectado à conta: {account.login}")
                logger.info(f"   Servidor: {account.server}")
                logger.info(f"   Saldo: ${account.balance:.2f}")
                mt5.shutdown()
                return True
            else:
                logger.error("❌ Não conseguiu obter informações da conta")
                mt5.shutdown()
                return False
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def test_account_info():
    """Testa obtenção de informações da conta"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 2: Obtendo informações da conta")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            account = mt5.account_info()
            if account:
                logger.info("✅ Informações da conta obtidas:")
                logger.info(f"   Login: {account.login}")
                logger.info(f"   Servidor: {account.server}")
                logger.info(f"   Saldo: ${account.balance:.2f}")
                logger.info(f"   Equity: ${account.equity:.2f}")
                logger.info(f"   Margem Livre: ${account.margin_free:.2f}")
                logger.info(f"   Nível de Margem: {account.margin_level:.2f}%")
                mt5.shutdown()
                return True
            else:
                logger.error("❌ Não conseguiu obter informações")
                mt5.shutdown()
                return False
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def test_positions():
    """Testa obtenção de posições"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 3: Verificando posições abertas")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            positions = mt5.positions_get()
            if positions:
                logger.info(f"✅ Posições obtidas: {len(positions)} aberta(s)")
                for pos in positions:
                    logger.info(f"   • {pos.symbol}: {pos.volume} lots @ {pos.price_open:.5f}")
            else:
                logger.info("✅ Nenhuma posição aberta")
            mt5.shutdown()
            return True
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def test_symbols():
    """Testa validação de símbolos"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 4: Validando símbolos")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            symbols_to_test = ["EURUSDc", "GBPUSDc", "XAUUSDc"]
            
            for symbol in symbols_to_test:
                # Tentar adicionar ao Market Watch
                if not mt5.symbol_select(symbol, True):
                    logger.warning(f"   ⚠️  Não conseguiu adicionar {symbol} ao Market Watch")
                
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    logger.info(f"   ✅ {symbol}: Válido")
                else:
                    logger.info(f"   ⚠️  {symbol}: Não visível (adicionando...)")
                    # Tentar novamente
                    mt5.symbol_select(symbol, True)
            
            mt5.shutdown()
            return True
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def test_prices():
    """Testa obtenção de preços"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 5: Obtendo preços de símbolos")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        
        if mt5.initialize():
            symbols = ["EURUSDc", "GBPUSDc", "XAUUSDc"]
            
            for symbol in symbols:
                # Adicionar ao Market Watch
                mt5.symbol_select(symbol, True)
                
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    logger.info(f"   ✅ {symbol}:")
                    logger.info(f"      Bid: {tick.bid:.5f}")
                    logger.info(f"      Ask: {tick.ask:.5f}")
                else:
                    logger.warning(f"   ⚠️  {symbol}: Não conseguiu obter preço")
            
            mt5.shutdown()
            return True
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def test_candles():
    """Testa obtenção de velas"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 TESTE 6: Obtendo dados de mercado (velas)")
    logger.info("=" * 60)

    try:
        import MetaTrader5 as mt5
        from datetime import datetime, timedelta
        
        if mt5.initialize():
            symbol = "EURUSDc"
            timeframe = mt5.TIMEFRAME_H1
            
            # Adicionar ao Market Watch
            mt5.symbol_select(symbol, True)
            
            # Obter últimas 5 velas
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 5)
            
            if rates is not None and len(rates) > 0:
                logger.info(f"✅ Velas obtidas para {symbol} (H1):")
                logger.info(f"   Total de velas: {len(rates)}")
                logger.info("   Últimas 3 velas:")
                
                for i, rate in enumerate(rates[-3:]):
                    time_str = datetime.fromtimestamp(rate['time']).strftime('%Y-%m-%d %H:%M')
                    logger.info(f"      {i+1}. {time_str} - O:{rate['open']:.5f} H:{rate['high']:.5f} L:{rate['low']:.5f} C:{rate['close']:.5f}")
                
                mt5.shutdown()
                return True
            else:
                logger.error("❌ Não conseguiu obter velas")
                logger.info("   Dica: Adicione EURUSDc ao Market Watch no MT5")
                mt5.shutdown()
                return False
        else:
            logger.error("❌ Falha ao inicializar MT5")
            return False
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False


def main():
    """Executa todos os testes"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  TESTE DIRETO DE MT5 (SEM HTTP)".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")

    results = {
        "Conexão": test_connection(),
        "Informações da Conta": test_account_info(),
        "Posições Abertas": test_positions(),
        "Validação de Símbolos": test_symbols(),
        "Preços de Símbolos": test_prices(),
        "Dados de Mercado": test_candles(),
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
        logger.info("🎉 Todos os testes passaram! MT5 funcionando perfeitamente!")
    else:
        logger.warning(f"⚠️  {total - passed} teste(s) falharam.")

    logger.info("=" * 60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
