#!/usr/bin/env python3
"""
Diagnóstico detalhado do MT5
Verifica configurações, símbolos, e possibilidades de fechar
"""

import logging
import MetaTrader5 as mt5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose():
    """Diagnóstico detalhado"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🔍 DIAGNÓSTICO DETALHADO DO MT5                 ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # 1. Informações da Conta
    logger.info("=" * 60)
    logger.info("1️⃣  INFORMAÇÕES DA CONTA")
    logger.info("=" * 60)
    
    account = mt5.account_info()
    logger.info(f"Login: {account.login}")
    logger.info(f"Servidor: {account.server}")
    logger.info(f"Saldo: ${account.balance:.2f}")
    logger.info(f"Equity: ${account.equity:.2f}")
    logger.info(f"Margem Livre: ${account.margin_free:.2f}")
    logger.info(f"Nível de Margem: {account.margin_level:.2f}%")
    logger.info(f"Lucro: ${account.profit:.2f}")
    
    # 2. Posições Abertas
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = mt5.positions_get()
    if positions:
        logger.info(f"Total: {len(positions)}")
        for pos in positions:
            logger.info(f"\n  Ticket: {pos.ticket}")
            logger.info(f"  Símbolo: {pos.symbol}")
            logger.info(f"  Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
            logger.info(f"  Volume: {pos.volume}")
            logger.info(f"  Preço de Abertura: {pos.price_open:.5f}")
            logger.info(f"  Preço Atual: {pos.price_current:.5f}")
            logger.info(f"  SL: {pos.sl}")
            logger.info(f"  TP: {pos.tp}")
            logger.info(f"  Lucro/Prejuízo: ${pos.profit:.2f}")
    else:
        logger.info("Nenhuma posição aberta")
    
    # 3. Verificar Símbolos
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  VERIFICAR SÍMBOLOS")
    logger.info("=" * 60)
    
    symbols_to_check = ["XAUUSDm", "EURUSDc", "GBPUSDc"]
    for symbol in symbols_to_check:
        info = mt5.symbol_info(symbol)
        if info:
            logger.info(f"\n  {symbol}:")
            logger.info(f"    Visível: {info.visible}")
            logger.info(f"    Negociável: {info.trade_mode}")
            logger.info(f"    Volume Mínimo: {info.volume_min}")
            logger.info(f"    Volume Máximo: {info.volume_max}")
            logger.info(f"    Volume Passo: {info.volume_step}")
            
            # Obter tick
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                logger.info(f"    Bid: {tick.bid:.5f}")
                logger.info(f"    Ask: {tick.ask:.5f}")
            else:
                logger.warning(f"    ⚠️  Não conseguiu obter tick")
        else:
            logger.warning(f"  ❌ {symbol} não encontrado")
    
    # 4. Verificar Horário
    logger.info("\n" + "=" * 60)
    logger.info("4️⃣  VERIFICAR HORÁRIO DE NEGOCIAÇÃO")
    logger.info("=" * 60)
    
    import datetime
    now = datetime.datetime.now()
    logger.info(f"Hora Local: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Dia da Semana: {now.strftime('%A')}")
    
    # Verificar se é horário de negociação
    # Ouro (XAU) negocia 24/5
    weekday = now.weekday()
    hour = now.hour
    
    if weekday >= 5:  # Sábado ou domingo
        logger.warning("⚠️  Fim de semana - mercado fechado")
    elif 0 <= hour < 5:
        logger.warning("⚠️️  Madrugada - mercado pode estar fechado")
    else:
        logger.info("✅ Horário de negociação ativo")
    
    # 5. Testar Ordem
    logger.info("\n" + "=" * 60)
    logger.info("5️⃣  TESTAR ORDEM (SEM EXECUTAR)")
    logger.info("=" * 60)
    
    if positions:
        pos = positions[0]
        logger.info(f"\nTestando fechamento da posição #{pos.ticket}...")
        
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if pos.type == 0 else tick.ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "price": close_price,
                "deviation": 50,
                "magic": 0,
                "comment": "Teste",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            logger.info(f"Requisição:")
            for key, value in request.items():
                logger.info(f"  {key}: {value}")
            
            # Tentar enviar
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("❌ order_send retornou None")
                logger.info("\n💡 Possíveis causas:")
                logger.info("   1. Símbolo não está selecionado")
                logger.info("   2. Preço fora do intervalo permitido")
                logger.info("   3. Volume inválido")
                logger.info("   4. Horário de negociação fechado")
                logger.info("   5. Conta sem permissão de trading")
            else:
                logger.info(f"\nResultado:")
                logger.info(f"  Retcode: {result.retcode}")
                logger.info(f"  Comment: {result.comment}")
                logger.info(f"  Order: {result.order}")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ DIAGNÓSTICO CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    diagnose()
