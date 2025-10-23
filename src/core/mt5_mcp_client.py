#!/usr/bin/env python3
"""
Cliente centralizado para comunicação com MetaTrader 5.
TODOS os componentes devem usar este cliente para acessar o MT5.

Este cliente usa conexão DIRETA ao MT5 (não via MCP Server).
O MCP Server é usado apenas para integração com clientes externos (Claude Desktop, etc).
"""

import logging
import MetaTrader5 as mt5
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MT5MCPClient:
    """
    Cliente único para comunicação DIRETA com MetaTrader 5.

    Este cliente centraliza TODA a comunicação com o MetaTrader 5,
    garantindo uma única conexão e evitando conflitos.

    Usa conexão DIRETA ao MT5 Terminal (não via HTTP/MCP).
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
                # Não levantar exceção, apenas logar
            else:
                self._initialized = True
                logger.info("✅ MT5 inicializado com sucesso via conexão direta")

    def _to_dict(self, obj) -> Dict:
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
        kwargs = {"group": group} if group else {}
        return self._call_tool("get_symbols", **kwargs)

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas de um símbolo.

        Args:
            symbol: Nome do símbolo (ex: "EURUSD")
        """
        return self._call_tool("get_symbol_info", symbol=symbol)

    def get_symbol_info_tick(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtém último tick de um símbolo.

        Args:
            symbol: Nome do símbolo
        """
        return self._call_tool("get_symbol_info_tick", symbol=symbol)

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
        return self._call_tool(
            "copy_rates_from_pos",
            symbol=symbol,
            timeframe=timeframe,
            start_pos=start_pos,
            count=count
        )

    # ==================== Trading Operations ====================

    def positions_get(
        self,
        symbol: Optional[str] = None,
        group: Optional[str] = None,
        ticket: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Obtém posições abertas.

        Args:
            symbol: Filtrar por símbolo
            group: Filtrar por grupo
            ticket: Filtrar por ticket específico
        """
        kwargs = {}
        if symbol:
            kwargs["symbol"] = symbol
        if group:
            kwargs["group"] = group
        if ticket:
            kwargs["ticket"] = ticket

        result = self._call_tool("positions_get", **kwargs)

        # Se retornou string JSON, parse
        if isinstance(result, str):
            try:
                import json
                return json.loads(result)
            except:
                return []

        return result if isinstance(result, list) else []

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
        kwargs = {}
        if symbol:
            kwargs["symbol"] = symbol
        if group:
            kwargs["group"] = group
        if ticket:
            kwargs["ticket"] = ticket

        return self._call_tool("orders_get", **kwargs)

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
        kwargs = {}
        if date_from:
            kwargs["date_from"] = int(date_from.timestamp())
        if date_to:
            kwargs["date_to"] = int(date_to.timestamp())
        if symbol:
            kwargs["symbol"] = symbol
        if position:
            kwargs["position"] = position
        if ticket:
            kwargs["ticket"] = ticket

        result = self._call_tool("history_deals_get", **kwargs)

        # Parse if string
        if isinstance(result, str):
            try:
                import json
                return json.loads(result)
            except:
                return []

        return result if isinstance(result, list) else []

    def buy_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Abre posição de COMPRA a mercado.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
            comment: Comentário da ordem (opcional)
        """
        kwargs = {
            "symbol": symbol,
            "volume": volume
        }
        if sl is not None:
            kwargs["sl"] = sl
        if tp is not None:
            kwargs["tp"] = tp
        if comment:
            kwargs["comment"] = comment

        return self._call_tool("buy_market", **kwargs)

    def sell_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Abre posição de VENDA a mercado.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            sl: Stop Loss (opcional)
            tp: Take Profit (opcional)
            comment: Comentário da ordem (opcional)
        """
        kwargs = {
            "symbol": symbol,
            "volume": volume
        }
        if sl is not None:
            kwargs["sl"] = sl
        if tp is not None:
            kwargs["tp"] = tp
        if comment:
            kwargs["comment"] = comment

        return self._call_tool("sell_market", **kwargs)

    def close_position(self, ticket: int) -> Optional[Dict[str, Any]]:
        """
        Fecha uma posição pelo ticket.

        Args:
            ticket: Ticket da posição a fechar
        """
        return self._call_tool("close_position", ticket=ticket)

    # ==================== Health Check ====================

    def health(self) -> Optional[Dict[str, Any]]:
        """Verifica saúde do servidor MCP."""
        return self._call_tool("health")

    def is_connected(self) -> bool:
        """
        Verifica se o cliente está conectado ao MCP server.

        Returns:
            True se conectado, False caso contrário
        """
        try:
            health = self.health()
            return health is not None and health.get("status") == "ok"
        except:
            return False


# Singleton instance - usar esta instância globalmente
_mt5_client_instance: Optional[MT5MCPClient] = None


def get_mt5_client(mcp_url: str = "http://localhost:8000") -> MT5MCPClient:
    """
    Obtém a instância singleton do cliente MCP.

    Args:
        mcp_url: URL do servidor MCP

    Returns:
        Instância do cliente MCP
    """
    global _mt5_client_instance

    if _mt5_client_instance is None:
        _mt5_client_instance = MT5MCPClient(mcp_url)
        logger.info("Nova instância do MT5 MCP Client criada")

    return _mt5_client_instance
