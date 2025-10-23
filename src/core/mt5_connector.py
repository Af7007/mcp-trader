#!/usr/bin/env python3
"""
MT5 Connector - Camada de abstração para comunicação com MT5 MCP Server
Fornece retry logic, error handling, e operações de trading simplificadas.
"""

import logging
import requests
import uuid
import time
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Tipos de ordem suportados"""
    BUY = "buy"
    SELL = "sell"


class MT5ConnectorError(Exception):
    """Exceção base para erros de conexão MT5"""
    pass


class MT5ConnectionError(MT5ConnectorError):
    """Erro ao conectar com o servidor MT5"""
    pass


class MT5OperationError(MT5ConnectorError):
    """Erro ao executar operação no MT5"""
    pass


class MT5Connector:
    """
    Conector robusto para MT5 MCP Server com retry logic e tratamento de erros.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Inicializa o conector MT5.

        Args:
            server_url: URL do servidor MT5 MCP
            timeout: Timeout em segundos para requisições
            max_retries: Número máximo de tentativas
            retry_delay: Delay em segundos entre tentativas
        """
        self.server_url = server_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.mcp_endpoint = f"{server_url}/mcp"

    def _call_mcp_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        retry_count: int = 0
    ) -> Any:
        """
        Chama uma ferramenta do MT5 MCP com retry logic.

        Args:
            tool_name: Nome da ferramenta MCP
            parameters: Parâmetros da ferramenta
            retry_count: Contador interno de tentativas

        Returns:
            Resultado da ferramenta

        Raises:
            MT5ConnectionError: Se não conseguir conectar
            MT5OperationError: Se a operação falhar
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }

            logger.debug(f"Chamando MCP tool: {tool_name} com params: {parameters}")

            response = requests.post(
                self.mcp_endpoint,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown error")
                    logger.error(f"MCP Error: {error_msg}")
                    raise MT5OperationError(f"MCP operation failed: {error_msg}")

                return result.get("result")
            else:
                error_text = response.text
                logger.error(f"HTTP {response.status_code}: {error_text}")
                raise MT5ConnectionError(f"HTTP {response.status_code}: {error_text}")

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout ao chamar {tool_name} (tentativa {retry_count + 1}/{self.max_retries})")
            if retry_count < self.max_retries - 1:
                time.sleep(self.retry_delay)
                return self._call_mcp_tool(tool_name, parameters, retry_count + 1)
            else:
                raise MT5ConnectionError(f"Timeout após {self.max_retries} tentativas")

        except requests.exceptions.ConnectionError:
            logger.warning(f"Erro de conexão ao chamar {tool_name} (tentativa {retry_count + 1}/{self.max_retries})")
            if retry_count < self.max_retries - 1:
                time.sleep(self.retry_delay)
                return self._call_mcp_tool(tool_name, parameters, retry_count + 1)
            else:
                raise MT5ConnectionError(f"Não foi possível conectar ao servidor MT5 após {self.max_retries} tentativas")

        except Exception as e:
            logger.error(f"Erro inesperado ao chamar {tool_name}: {e}")
            raise MT5OperationError(f"Erro ao chamar {tool_name}: {str(e)}")

    def check_connection(self) -> bool:
        """
        Verifica se o servidor MT5 está acessível.

        Returns:
            True se conectado, False caso contrário
        """
        try:
            result = self._call_mcp_tool("get_account_info", {})
            logger.info("✅ Conexão com MT5 estabelecida")
            return True
        except MT5ConnectorError as e:
            logger.error(f"❌ Falha na conexão com MT5: {e}")
            return False

    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtém informações da conta de trading.

        Returns:
            Dicionário com informações da conta

        Raises:
            MT5OperationError: Se não conseguir obter as informações
        """
        try:
            result = self._call_mcp_tool("get_account_info", {})
            logger.info(f"Informações da conta obtidas: Balance=${result.get('balance', 'N/A')}")
            return result
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Não foi possível obter informações da conta: {e}")

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um símbolo.

        Args:
            symbol: Nome do símbolo (ex: EURUSD)

        Returns:
            Dicionário com informações do símbolo

        Raises:
            MT5OperationError: Se o símbolo não for encontrado
        """
        try:
            result = self._call_mcp_tool("get_symbol_info", {"symbol": symbol})
            logger.debug(f"Informações do símbolo {symbol} obtidas")
            return result
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Símbolo '{symbol}' não encontrado: {e}")

    def get_symbol_tick(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém o último tick de um símbolo.

        Args:
            symbol: Nome do símbolo

        Returns:
            Dicionário com dados do tick (bid, ask, etc)

        Raises:
            MT5OperationError: Se não conseguir obter o tick
        """
        try:
            result = self._call_mcp_tool("get_symbol_info_tick", {"symbol": symbol})
            logger.debug(f"Tick de {symbol}: bid={result.get('bid')}, ask={result.get('ask')}")
            return result
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Não foi possível obter tick de {symbol}: {e}")

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém posições abertas.

        Args:
            symbol: Símbolo específico (opcional)

        Returns:
            Lista de posições abertas

        Raises:
            MT5OperationError: Se não conseguir obter posições
        """
        try:
            params = {}
            if symbol:
                params["symbol"] = symbol

            result = self._call_mcp_tool("positions_get", params)
            logger.info(f"Posições obtidas: {len(result) if result else 0} abertas")
            return result if result else []
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Não foi possível obter posições: {e}")

    def get_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém ordens pendentes.

        Args:
            symbol: Símbolo específico (opcional)

        Returns:
            Lista de ordens pendentes

        Raises:
            MT5OperationError: Se não conseguir obter ordens
        """
        try:
            params = {}
            if symbol:
                params["symbol"] = symbol

            result = self._call_mcp_tool("orders_get", params)
            logger.info(f"Ordens obtidas: {len(result) if result else 0} pendentes")
            return result if result else []
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Não foi possível obter ordens: {e}")

    def buy_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "Chatbot order"
    ) -> Dict[str, Any]:
        """
        Executa uma ordem de compra a mercado.

        Args:
            symbol: Símbolo para comprar
            volume: Volume em lotes
            sl: Preço de stop loss (opcional)
            tp: Preço de take profit (opcional)
            comment: Comentário da ordem

        Returns:
            Resultado da execução

        Raises:
            MT5OperationError: Se a ordem falhar
        """
        try:
            # Validar símbolo
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                raise MT5OperationError(f"Símbolo '{symbol}' não disponível")

            # Obter preço atual
            tick = self.get_symbol_tick(symbol)
            price = tick.get("ask")

            if not price:
                raise MT5OperationError(f"Não foi possível obter preço para {symbol}")

            # Preparar parâmetros da ordem
            import MetaTrader5 as mt5

            params = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            if sl:
                params["sl"] = sl
            if tp:
                params["tp"] = tp

            result = self._call_mcp_tool("order_send", params)

            if result and result.get("retcode") == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ BUY order executada: {symbol} {volume} lots @ {price}")
                return {
                    "status": "success",
                    "order": result.get("order"),
                    "price": price,
                    "symbol": symbol,
                    "volume": volume
                }
            else:
                error_msg = result.get("comment", "Unknown error") if result else "No response"
                raise MT5OperationError(f"Ordem BUY falhou: {error_msg}")

        except MT5ConnectorError as e:
            raise MT5OperationError(f"Erro ao executar BUY: {e}")

    def sell_market(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "Chatbot order"
    ) -> Dict[str, Any]:
        """
        Executa uma ordem de venda a mercado.

        Args:
            symbol: Símbolo para vender
            volume: Volume em lotes
            sl: Preço de stop loss (opcional)
            tp: Preço de take profit (opcional)
            comment: Comentário da ordem

        Returns:
            Resultado da execução

        Raises:
            MT5OperationError: Se a ordem falhar
        """
        try:
            # Validar símbolo
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                raise MT5OperationError(f"Símbolo '{symbol}' não disponível")

            # Obter preço atual
            tick = self.get_symbol_tick(symbol)
            price = tick.get("bid")

            if not price:
                raise MT5OperationError(f"Não foi possível obter preço para {symbol}")

            # Preparar parâmetros da ordem
            import MetaTrader5 as mt5

            params = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            if sl:
                params["sl"] = sl
            if tp:
                params["tp"] = tp

            result = self._call_mcp_tool("order_send", params)

            if result and result.get("retcode") == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ SELL order executada: {symbol} {volume} lots @ {price}")
                return {
                    "status": "success",
                    "order": result.get("order"),
                    "price": price,
                    "symbol": symbol,
                    "volume": volume
                }
            else:
                error_msg = result.get("comment", "Unknown error") if result else "No response"
                raise MT5OperationError(f"Ordem SELL falhou: {error_msg}")

        except MT5ConnectorError as e:
            raise MT5OperationError(f"Erro ao executar SELL: {e}")

    def close_position(self, ticket: int) -> Dict[str, Any]:
        """
        Fecha uma posição aberta.

        Args:
            ticket: Ticket da posição

        Returns:
            Resultado da operação

        Raises:
            MT5OperationError: Se não conseguir fechar
        """
        try:
            # Obter informações da posição
            positions = self.get_positions()
            position = next((p for p in positions if p.get("ticket") == ticket), None)

            if not position:
                raise MT5OperationError(f"Posição {ticket} não encontrada")

            symbol = position.get("symbol")
            volume = position.get("volume")
            is_buy = position.get("type") == 0  # 0 = BUY, 1 = SELL

            # Obter preço atual
            tick = self.get_symbol_tick(symbol)
            price = tick.get("bid") if is_buy else tick.get("ask")

            # Preparar ordem de fechamento
            import MetaTrader5 as mt5

            order_type = mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY

            params = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": f"Close position {ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = self._call_mcp_tool("order_send", params)

            if result and result.get("retcode") == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Posição {ticket} fechada com sucesso")
                return {
                    "status": "success",
                    "ticket": ticket,
                    "price": price
                }
            else:
                error_msg = result.get("comment", "Unknown error") if result else "No response"
                raise MT5OperationError(f"Falha ao fechar posição: {error_msg}")

        except MT5ConnectorError as e:
            raise MT5OperationError(f"Erro ao fechar posição: {e}")

    def get_candles(
        self,
        symbol: str,
        timeframe: int = 60,
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtém velas históricas.

        Args:
            symbol: Símbolo
            timeframe: Timeframe em minutos (60=H1, 240=H4, 1440=D1)
            count: Número de velas

        Returns:
            Lista de velas

        Raises:
            MT5OperationError: Se não conseguir obter velas
        """
        try:
            result = self._call_mcp_tool(
                "copy_rates_from_pos",
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "start_pos": 0,
                    "count": count
                }
            )
            logger.debug(f"Obtidas {len(result) if result else 0} velas de {symbol}")
            return result if result else []
        except MT5ConnectorError as e:
            raise MT5OperationError(f"Erro ao obter velas: {e}")
