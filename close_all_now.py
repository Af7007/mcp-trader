#!/usr/bin/env python3
"""
Fechar TODAS as posições - VERSÃO FINAL CORRIGIDA
Usa ORDER_FILLING_IOC para execução imediata
"""

import logging
import MetaTrader5 as mt5
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def close_all_positions():
    """Fechar todas as posições abertas"""
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                                                            ║")
    logger.info("║          🔒 FECHANDO TODAS AS POSIÇÕES ABERTAS            ║")
    logger.info("║                                                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        return False
    
    # Obter posições abertas
    positions = mt5.positions_get()
    
    if not positions:
        logger.info("✅ Nenhuma posição aberta")
        mt5.shutdown()
        return True
    
    logger.info(f"📊 Encontradas {len(positions)} posição(ões) aberta(s)")
    logger.info("")
    
    closed_count = 0
    failed_count = 0
    
    # Fechar cada posição
    for pos in positions:
        logger.info(f"Fechando posição #{pos.ticket}...")
        logger.info(f"  Símbolo: {pos.symbol}")
        logger.info(f"  Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
        logger.info(f"  Volume: {pos.volume}")
        logger.info(f"  Preço Atual: {pos.price_current:.5f}")
        
        try:
            # Obter preço atual
            tick = mt5.symbol_info_tick(pos.symbol)
            if not tick:
                logger.error(f"  ❌ Não conseguiu obter preço")
                failed_count += 1
                logger.info("")
                continue
            
            # Determinar tipo de ordem para fechar
            # Se é BUY (type=0), vender; se é SELL (type=1), comprar
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if pos.type == 0 else tick.ask
            
            logger.info(f"  Preço de fechamento: {close_price:.5f}")
            
            # Criar requisição de fechamento
            # IMPORTANTE: usar ORDER_FILLING_IOC para execução imediata
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "price": close_price,
                "deviation": 100,  # Aumentar desvio
                "magic": 0,
                "comment": f"Fechamento automático #{pos.ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,  # Execução imediata ou cancelamento
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result is None:
                logger.error(f"  ❌ order_send retornou None")
                failed_count += 1
            elif result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"  ✅ Posição fechada!")
                logger.info(f"     Novo ticket: {result.order}")
                closed_count += 1
            elif result.retcode == mt5.TRADE_RETCODE_PLACED:
                logger.warning(f"  ⚠️  Ordem colocada (pendente)")
                logger.info(f"     Ticket: {result.order}")
                # Tentar novamente com FOK
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result2 = mt5.order_send(request)
                if result2 and result2.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"  ✅ Posição fechada na segunda tentativa!")
                    closed_count += 1
                else:
                    failed_count += 1
            else:
                logger.error(f"  ❌ Falha: {result.comment}")
                logger.error(f"     Retcode: {result.retcode}")
                failed_count += 1
            
            # Pequeno delay entre ordens
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"  ❌ Exceção: {e}")
            failed_count += 1
        
        logger.info("")
    
    mt5.shutdown()
    
    # Resumo
    logger.info("=" * 60)
    logger.info("📊 RESUMO")
    logger.info("=" * 60)
    logger.info(f"Total de posições: {len(positions)}")
    logger.info(f"Fechadas com sucesso: {closed_count}")
    logger.info(f"Falhadas: {failed_count}")
    logger.info("")
    
    if failed_count == 0:
        logger.info("✅ Todas as posições foram fechadas!")
    else:
        logger.warning(f"⚠️  {failed_count} posição(ões) falharam")
        logger.info("")
        logger.info("💡 PRÓXIMAS AÇÕES:")
        logger.info("   1. Verifique saldo suficiente")
        logger.info("   2. Verifique horário de negociação")
        logger.info("   3. Feche manualmente no MT5")
        logger.info("   4. Verifique se há ordens pendentes")
    
    return failed_count == 0


if __name__ == "__main__":
    success = close_all_positions()
    exit(0 if success else 1)
