#!/usr/bin/env python3
"""
MT5 Position Closer - Fechar posições de forma robusta
Implementa o método correto para fechar posições no MT5
"""

import logging
import MetaTrader5 as mt5
import time
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MT5PositionCloser:
    """Gerenciador robusto de fechamento de posições"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 0.5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def close_position(self, ticket: int, comment: str = "Fechamento automático") -> Dict:
        """
        Fechar posição específica pelo ticket
        
        Args:
            ticket: Número do ticket da posição
            comment: Comentário da ordem
        
        Returns:
            Dict com resultado: {'success': bool, 'message': str, 'order': int}
        """
        
        logger.info(f"🔒 Fechando posição #{ticket}...")
        
        # Obter posição
        position = self._get_position_by_ticket(ticket)
        if not position:
            logger.error(f"❌ Posição #{ticket} não encontrada")
            return {'success': False, 'message': f'Posição {ticket} não encontrada', 'order': None}
        
        logger.info(f"   Símbolo: {position.symbol}")
        logger.info(f"   Tipo: {'BUY' if position.type == 0 else 'SELL'}")
        logger.info(f"   Volume: {position.volume}")
        logger.info(f"   Preço Atual: {position.price_current:.5f}")
        
        # Tentar fechar com retry
        for attempt in range(self.max_retries):
            logger.info(f"   Tentativa {attempt + 1}/{self.max_retries}...")
            
            result = self._attempt_close(position, comment)
            
            if result['success']:
                logger.info(f"   ✅ Posição fechada!")
                logger.info(f"      Novo ticket: {result['order']}")
                return result
            else:
                logger.warning(f"   ⚠️  Falha: {result['message']}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ Falha ao fechar posição após {self.max_retries} tentativas")
        return {'success': False, 'message': 'Falha após múltiplas tentativas', 'order': None}
    
    def close_all_positions(self, comment: str = "Fechamento automático") -> Dict:
        """
        Fechar todas as posições abertas
        
        Returns:
            Dict com resultado: {'total': int, 'closed': int, 'failed': int}
        """
        
        logger.info("🔒 Fechando TODAS as posições...")
        
        positions = mt5.positions_get()
        if not positions:
            logger.info("✅ Nenhuma posição aberta")
            return {'total': 0, 'closed': 0, 'failed': 0}
        
        logger.info(f"📊 Encontradas {len(positions)} posição(ões)")
        
        closed_count = 0
        failed_count = 0
        
        for pos in positions:
            result = self.close_position(pos.ticket, comment)
            if result['success']:
                closed_count += 1
            else:
                failed_count += 1
            
            time.sleep(0.2)  # Pequeno delay entre posições
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 RESUMO")
        logger.info("=" * 60)
        logger.info(f"Total de posições: {len(positions)}")
        logger.info(f"Fechadas com sucesso: {closed_count}")
        logger.info(f"Falhadas: {failed_count}")
        
        return {'total': len(positions), 'closed': closed_count, 'failed': failed_count}
    
    def _get_position_by_ticket(self, ticket: int) -> Optional:
        """Obter posição pelo ticket"""
        positions = mt5.positions_get()
        if positions:
            for pos in positions:
                if pos.ticket == ticket:
                    return pos
        return None
    
    def _attempt_close(self, position, comment: str) -> Dict:
        """Tentar fechar posição uma vez"""
        
        try:
            # Obter preço atual
            tick = mt5.symbol_info_tick(position.symbol)
            if not tick:
                return {'success': False, 'message': 'Não conseguiu obter preço', 'order': None}
            
            # Determinar tipo de ordem para fechar
            # Se é BUY (type=0), vender; se é SELL (type=1), comprar
            close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if position.type == 0 else tick.ask
            
            # Criar requisição de fechamento
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "price": close_price,
                "deviation": 100,
                "magic": 0,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result is None:
                return {'success': False, 'message': 'order_send retornou None', 'order': None}
            
            # Verificar resultado
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return {'success': True, 'message': 'Posição fechada', 'order': result.order}
            
            elif result.retcode == mt5.TRADE_RETCODE_PLACED:
                # Ordem foi colocada mas não executada, tentar novamente com FOK
                logger.warning(f"   ⚠️  Ordem colocada, tentando FOK...")
                request["type_filling"] = mt5.ORDER_FILLING_FOK
                result2 = mt5.order_send(request)
                
                if result2 and result2.retcode == mt5.TRADE_RETCODE_DONE:
                    return {'success': True, 'message': 'Posição fechada (FOK)', 'order': result2.order}
                else:
                    return {'success': False, 'message': f'Retcode: {result.retcode}', 'order': None}
            
            else:
                return {'success': False, 'message': f'{result.comment} (retcode: {result.retcode})', 'order': None}
        
        except Exception as e:
            return {'success': False, 'message': f'Exceção: {str(e)}', 'order': None}


# Exemplos de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        exit(1)
    
    closer = MT5PositionCloser()
    
    # Fechar todas as posições
    result = closer.close_all_positions()
    
    logger.info("")
    if result['failed'] == 0:
        logger.info("✅ Todas as posições foram fechadas!")
    else:
        logger.warning(f"⚠️  {result['failed']} posição(ões) falharam")
    
    mt5.shutdown()
