#!/usr/bin/env python3
"""
Cliente centralizado para comunicação DIRETA com MetaTrader 5.
TODOS os componentes devem usar este cliente para acessar o MT5.

Este cliente usa conexão DIRETA ao MT5 Terminal (não via MCP Server).
O MCP Server é usado apenas para integração com clientes externos (Claude Desktop, etc).
"""

import logging
import MetaTrader5 as mt5
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MT5Client:
    """
    Cliente único para comunicação DIRETA com MetaTrader 5.

    Este cliente centraliza TODA a comunicação com o MetaTrader 5,
    garantindo uma única conexão e evitando conflitos.

    Usa conexão DIRETA ao MT5 Terminal.
    """

    def __init__(self):
        """Inicializa o cliente MT5."""
        self._initialized = False
        self._ensure_initialized()

    def _ensure_initialized(self):
        """Garante que o MT5 está inicializado."""
        if not self._initialized:
            if not mt5.initialize():
                error_code, error_msg = mt5.last_error()
                logger.error(f"Falha ao inicializar MT5: {error_msg} (código: {error_code})")
                logger.error("Certifique-se que o MT5 Terminal está aberto!")
            else:
                self._initialized = True
                logger.info("✅ MT5 inicializado com sucesso via conexão direta")

    def _to_dict(self, obj) -> Optional[Dict]:
        """Converte named tuple do MT5 para dict."""
        if obj is None:
            return None
        if hasattr(obj, '_asdict'):
            return obj._asdict()
        return obj

    # ==================== Account Information ====================

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Obtém informações da conta MT5."""
        self._ensure_initialized()
        info = mt5.account_info()
        if info is None:
            logger.error(f"Erro ao obter account_info: {mt5.last_error()}")
            return None
        return self._to_dict(info)

    def get_terminal_info(self) -> Optional[Dict[str, Any]]:
        """Obtém informações do terminal MT5."""
        self._ensure_initialized()
        info = mt5.terminal_info()
        if info is None:
            logger.error(f"Erro ao obter terminal_info: {mt5.last_error()}")
            return None
        return self._to_dict(info)

    def get_version(self) -> Optional[tuple]:
        """Obtém versão do MT5."""
        self._ensure_initialized()
        return mt5.version()

    # ==================== Symbol Information ====================

    def get_symbols(self, group: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Obtém lista de símbolos disponíveis.

        Args:
            group: Filtro de grupo (ex: "Forex*", "Crypto*")
        """
        self._ensure_initialized()
        if group:
            symbols = mt5.symbols_get(group=group)
        else:
            symbols = mt5.symbols_get()

        if symbols is None:
            logger.error(f"Erro ao obter símbolos: {mt5.last_error()}")
            return None

        return [self._to_dict(s) for s in symbols]

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas de um símbolo.

        Args:
            symbol: Nome do símbolo (ex: "EURUSD")
        """
        self._ensure_initialized()
        info = mt5.symbol_info(symbol)
        if info is None:
            logger.error(f"Erro ao obter info do símbolo {symbol}: {mt5.last_error()}")
            return None
        return self._to_dict(info)

    def get_symbol_info_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém último tick de um símbolo.

        Args:
            symbol: Nome do símbolo
        """
        self._ensure_initialized()
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(f"Erro ao obter tick do símbolo {symbol}: {mt5.last_error()}")
            return None
        return self._to_dict(tick)

    # ==================== Market Data ====================

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: str,
        start_pos: int = 0,
        count: int = 100
    ) -> Optional[List[Dict]]:
        """
        Obtém barras de preço a partir de uma posição.

        Args:
            symbol: Nome do símbolo
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1, etc)
            start_pos: Posição inicial
            count: Quantidade de barras
        """
        self._ensure_initialized()

        # Mapeamento de timeframe
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }

        tf = timeframe_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)

        rates = mt5.copy_rates_from_pos(symbol, tf, start_pos, count)
        if rates is None or len(rates) == 0:
            logger.error(f"Erro ao obter rates: {mt5.last_error()}")
            return None

        # Converter para lista de dicts
        import pandas as pd
        df = pd.DataFrame(rates)
        return df.to_dict('records')

    # ==================== Trading Operations ====================

    def positions_get(
        self,
        symbol: Optional[str] = None,
        group: Optional[str] = None,
        ticket: Optional[int] = None,
        magic: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Obtém posições abertas.

        Args:
            symbol: Filtrar por símbolo
            group: Filtrar por grupo
            ticket: Filtrar por ticket específico
            magic: Filtrar por magic number (identifica o agente)
        """
        self._ensure_initialized()

        if ticket:
            positions = mt5.positions_get(ticket=ticket)
        elif symbol:
            positions = mt5.positions_get(symbol=symbol)
        elif group:
            positions = mt5.positions_get(group=group)
        else:
            positions = mt5.positions_get()

        if positions is None:
            # Retorna lista vazia se não houver posições (não é erro)
            return []

        result = [self._to_dict(p) for p in positions]

        # Filtrar por magic number se especificado
        if magic is not None:
            result = [p for p in result if p.get('magic') == magic]

        return result

    def orders_get(
        self,
        symbol: Optional[str] = None,
        group: Optional[str] = None,
        ticket: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Obtém ordens pendentes.

        Args:
            symbol: Filtrar por símbolo
            group: Filtrar por grupo
            ticket: Filtrar por ticket específico
        """
        self._ensure_initialized()

        if ticket:
            orders = mt5.orders_get(ticket=ticket)
        elif symbol:
            orders = mt5.orders_get(symbol=symbol)
        elif group:
            orders = mt5.orders_get(group=group)
        else:
            orders = mt5.orders_get()

        if orders is None:
            return []

        return [self._to_dict(o) for o in orders]

    def history_deals_get(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        symbol: Optional[str] = None,
        position: Optional[int] = None,
        ticket: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Obtém histórico de negociações (deals).

        Args:
            date_from: Data inicial
            date_to: Data final
            symbol: Filtrar por símbolo
            position: Filtrar por posição
            ticket: Filtrar por ticket
        """
        self._ensure_initialized()

        if position:
            deals = mt5.history_deals_get(position=position)
        elif ticket:
            deals = mt5.history_deals_get(ticket=ticket)
        elif date_from and date_to:
            deals = mt5.history_deals_get(date_from, date_to)
        else:
            deals = mt5.history_deals_get()

        if deals is None:
            return []

        return [self._to_dict(d) for d in deals]

    def buy_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: Optional[str] = None,
        magic: int = 123456
    ) -> Optional[Dict[str, Any]]:
        """
        Abre posição de COMPRA a mercado.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
            comment: Comentário da ordem (opcional)
            magic: Magic number para identificar o agente (padrão: 123456)
        """
        self._ensure_initialized()

        # Obter preço atual
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(f"Não foi possível obter preço para {symbol}")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 10,
            "magic": magic,
            "comment": comment or "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Adicionar SL e TP apenas se forem especificados
        if sl and sl > 0:
            request["sl"] = sl
        if tp and tp > 0:
            request["tp"] = tp

        result = mt5.order_send(request)
        if result is None:
            logger.error(f"Erro ao enviar ordem: {mt5.last_error()}")
            return None

        return self._to_dict(result)

    def sell_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: Optional[str] = None,
        magic: int = 123456
    ) -> Optional[Dict[str, Any]]:
        """
        Abre posição de VENDA a mercado.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
            comment: Comentário da ordem (opcional)
            magic: Magic number para identificar o agente (padrão: 123456)
        """
        self._ensure_initialized()

        # Obter preço atual
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(f"Não foi possível obter preço para {symbol}")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "deviation": 10,
            "magic": magic,
            "comment": comment or "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Adicionar SL e TP apenas se forem especificados
        if sl and sl > 0:
            request["sl"] = sl
        if tp and tp > 0:
            request["tp"] = tp

        result = mt5.order_send(request)
        if result is None:
            logger.error(f"Erro ao enviar ordem: {mt5.last_error()}")
            return None

        return self._to_dict(result)

    def modify_position(
        self,
        ticket: int,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Modifica SL/TP de uma posição existente.

        Args:
            ticket: Ticket da posição
            sl: Novo Stop Loss (None para manter atual)
            tp: Novo Take Profit (None para manter atual, 0 para remover)
        """
        self._ensure_initialized()

        # Obter informações da posição
        positions = mt5.positions_get(ticket=ticket)
        if positions is None or len(positions) == 0:
            logger.error(f"Posição {ticket} não encontrada")
            return None

        position = positions[0]

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": ticket,
            "sl": sl if sl is not None else position.sl,
            "tp": tp if tp is not None else position.tp,
        }

        result = mt5.order_send(request)
        if result is None:
            logger.error(f"Erro ao modificar posição: {mt5.last_error()}")
            return None

        return self._to_dict(result)

    def close_position(self, ticket: int) -> Optional[Dict[str, Any]]:
        """
        Fecha uma posição pelo ticket.

        Args:
            ticket: Ticket da posição a fechar
        """
        self._ensure_initialized()

        # Obter informações da posição
        positions = mt5.positions_get(ticket=ticket)
        if positions is None or len(positions) == 0:
            logger.error(f"Posição {ticket} não encontrada")
            return None

        position = positions[0]

        # Determinar tipo de ordem oposta
        if position.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 10,
            "magic": 123456,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            logger.error(f"Erro ao fechar posição: {mt5.last_error()}")
            return None

        return self._to_dict(result)

    # ==================== Health Check ====================

    def is_connected(self) -> bool:
        """
        Verifica se o cliente está conectado ao MT5.

        Returns:
            True se conectado, False caso contrário
        """
        try:
            self._ensure_initialized()
            return self._initialized and mt5.terminal_info() is not None
        except:
            return False


# Singleton instance - usar esta instância globalmente
_mt5_client_instance: Optional[MT5Client] = None


def get_mt5_client() -> MT5Client:
    """
    Obtém a instância singleton do cliente MT5.

    Returns:
        Instância do cliente MT5
    """
    global _mt5_client_instance

    if _mt5_client_instance is None:
        _mt5_client_instance = MT5Client()
        logger.info("Nova instância do MT5 Client criada")

    return _mt5_client_instance
