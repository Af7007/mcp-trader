#!/usr/bin/env python3
"""
Encerrar Todas as Posições via MCP
Conecta ao MCP Server e fecha todas as posições abertas
"""

import sys
import logging
from pathlib import Path
import MetaTrader5 as mt5

sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Encerrar todas as posições via MCP"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║     🔒 ENCERRANDO TODAS AS POSIÇÕES VIA MCP              ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return
    
    # 1. Verificar posições abertas
    logger.info("=" * 60)
    logger.info("1️⃣  VERIFICANDO POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = mt5.positions_get()
    if not positions:
        logger.info("✅ Nenhuma posição aberta")
        mt5.shutdown()
        return
    
    logger.info(f"📊 Encontradas {len(positions)} posição(ões):")
    for pos in positions:
        logger.info(f"   • #{pos.ticket}: {pos.symbol} {'BUY' if pos.type == 0 else 'SELL'} {pos.volume} @ {pos.price_open:.5f}")
    
    # 2. Fechar cada posição
    logger.info("\n" + "=" * 60)
    logger.info("2️⃣  ENCERRANDO POSIÇÕES")
    logger.info("=" * 60)
    logger.info("")
    
    closed_count = 0
    failed_count = 0
    
    for pos in positions:
        logger.info(f"Encerrando #{pos.ticket}...")
        
        try:
            # Determinar tipo de ordem para fechar
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            
            # Obter preço
            tick = mt5.symbol_info_tick(pos.symbol)
            if not tick:
                logger.error(f"   ❌ Não conseguiu obter preço")
                failed_count += 1
                continue
            
            close_price = tick.bid if pos.type == 0 else tick.ask
            
            # Criar requisição
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "price": close_price,
                "deviation": 100,
                "magic": 0,
                "comment": "Encerramento via MCP",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"   ✅ Encerrada! Novo ticket: {result.order}")
                closed_count += 1
            else:
                retcode = result.retcode if result else "None"
                logger.warning(f"   ⚠️  Retcode: {retcode}")
                # Tentar novamente com IOC
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result2 = mt5.order_send(request)
                if result2 and result2.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"   ✅ Encerrada (IOC)! Novo ticket: {result2.order}")
                    closed_count += 1
                else:
                    logger.error(f"   ❌ Falha ao encerrar")
                    failed_count += 1
        
        except Exception as e:
            logger.error(f"   ❌ Erro: {e}")
            failed_count += 1
    
    # 3. Verificar resultado
    logger.info("\n" + "=" * 60)
    logger.info("3️⃣  RESULTADO FINAL")
    logger.info("=" * 60)
    
    positions_after = mt5.positions_get()
    
    logger.info(f"\n📊 Resumo:")
    logger.info(f"   Total de posições: {len(positions)}")
    logger.info(f"   Encerrradas: {closed_count}")
    logger.info(f"   Falhadas: {failed_count}")
    logger.info(f"   Posições restantes: {len(positions_after) if positions_after else 0}")
    
    if positions_after:
        logger.warning(f"\n⚠️  Ainda há {len(positions_after)} posição(ões) abertas:")
        for pos in positions_after:
            logger.info(f"   • #{pos.ticket}: {pos.symbol}")
    else:
        logger.info("\n✅ TODAS AS POSIÇÕES FORAM ENCERRRADAS!")
    
    mt5.shutdown()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ OPERAÇÃO CONCLUÍDA")
    logger.info("=" * 60)
    logger.info("")


if __name__ == "__main__":
    main()
