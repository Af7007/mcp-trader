#!/usr/bin/env python3
"""
Trading Operations - Wrapper para operações de trading
Integra MT5, Database e Position Closer
"""

import logging
import MetaTrader5 as mt5
from typing import Dict, Optional
from .database import create_trade, update_trade_status
from .mt5_position_closer import MT5PositionCloser

logger = logging.getLogger(__name__)


class TradingOperations:
    """Gerenciador de operações de trading com persistência em BD"""
    
    def __init__(self):
        self.position_closer = MT5PositionCloser()
    
    def open_buy_order(self, symbol: str, volume: float, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict:
        """
        Abrir ordem de compra
        
        Args:
            symbol: Símbolo (ex: EURUSDc)
            volume: Volume em lots
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
        
        Returns:
            Dict com resultado: {'success': bool, 'message': str, 'ticket': int, 'price': float}
        """
        
        logger.info(f"🟢 Abrindo BUY: {symbol} {volume} lots")
        
        try:
            # Garantir que símbolo está selecionado
            mt5.symbol_select(symbol, True)
            
            # Obter preço atual
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"❌ Não conseguiu obter preço de {symbol}")
                return {'success': False, 'message': f'Não conseguiu obter preço de {symbol}', 'ticket': None, 'price': None}
            
            # Criar requisição
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "deviation": 50,
                "magic": 0,
                "comment": "Aberto via chatbot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if sl:
                request["sl"] = sl
            if tp:
                request["tp"] = tp
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("❌ order_send retornou None")
                return {'success': False, 'message': 'Erro ao enviar ordem', 'ticket': None, 'price': None}
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ BUY executada! Ticket: {result.order}, Preço: {tick.ask:.5f}")
                
                # Registrar no BD
                create_trade(result.order, symbol, volume, tick.ask, sl, tp)
                
                return {
                    'success': True,
                    'message': 'Ordem de compra executada',
                    'ticket': result.order,
                    'price': tick.ask
                }
            else:
                logger.error(f"❌ Falha: {result.comment} (retcode: {result.retcode})")
                return {'success': False, 'message': result.comment, 'ticket': None, 'price': None}
        
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            return {'success': False, 'message': str(e), 'ticket': None, 'price': None}
    
    def open_sell_order(self, symbol: str, volume: float, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict:
        """
        Abrir ordem de venda
        
        Args:
            symbol: Símbolo (ex: EURUSDc)
            volume: Volume em lots
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
        
        Returns:
            Dict com resultado: {'success': bool, 'message': str, 'ticket': int, 'price': float}
        """
        
        logger.info(f"🔴 Abrindo SELL: {symbol} {volume} lots")
        
        try:
            # Garantir que símbolo está selecionado
            mt5.symbol_select(symbol, True)
            
            # Obter preço atual
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"❌ Não conseguiu obter preço de {symbol}")
                return {'success': False, 'message': f'Não conseguiu obter preço de {symbol}', 'ticket': None, 'price': None}
            
            # Criar requisição
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": tick.bid,
                "deviation": 50,
                "magic": 0,
                "comment": "Aberto via chatbot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if sl:
                request["sl"] = sl
            if tp:
                request["tp"] = tp
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("❌ order_send retornou None")
                return {'success': False, 'message': 'Erro ao enviar ordem', 'ticket': None, 'price': None}
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ SELL executada! Ticket: {result.order}, Preço: {tick.bid:.5f}")
                
                # Registrar no BD
                create_trade(result.order, symbol, volume, tick.bid, sl, tp)
                
                return {
                    'success': True,
                    'message': 'Ordem de venda executada',
                    'ticket': result.order,
                    'price': tick.bid
                }
            else:
                logger.error(f"❌ Falha: {result.comment} (retcode: {result.retcode})")
                return {'success': False, 'message': result.comment, 'ticket': None, 'price': None}
        
        except Exception as e:
            logger.error(f"❌ Exceção: {e}")
            return {'success': False, 'message': str(e), 'ticket': None, 'price': None}
    
    def close_position(self, ticket: int) -> Dict:
        """
        Fechar posição
        
        Args:
            ticket: Número do ticket
        
        Returns:
            Dict com resultado: {'success': bool, 'message': str, 'order': int}
        """
        
        logger.info(f"🔒 Fechando posição #{ticket}")
        
        result = self.position_closer.close_position(ticket)
        
        if result['success']:
            # Atualizar BD
            update_trade_status(ticket, 'closed', 0, 'manual')
        
        return result


# Exemplos de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not mt5.initialize():
        logger.error("❌ Falha ao conectar MT5")
        exit(1)
    
    ops = TradingOperations()
    
    # Teste: Abrir BUY
    result = ops.open_buy_order("EURUSDc", 0.01, sl=1.16000, tp=1.16200)
    logger.info(f"Resultado: {result}")
    
    # Teste: Abrir SELL
    result = ops.open_sell_order("GBPUSDc", 0.01, sl=1.33700, tp=1.33500)
    logger.info(f"Resultado: {result}")
    
    mt5.shutdown()
