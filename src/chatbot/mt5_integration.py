#!/usr/bin/env python3
"""
Integração MT5 para o Chatbot - Simplifica operações de trading
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from core.mt5_connector import MT5Connector, MT5OperationError, MT5ConnectionError

logger = logging.getLogger(__name__)


class ChatbotMT5Integration:
    """
    Integração entre o chatbot e MT5 com operações de alto nível.
    """

    def __init__(self, mt5_server_url: str = "http://localhost:8000"):
        """
        Inicializa a integração.

        Args:
            mt5_server_url: URL do servidor MT5 MCP
        """
        self.connector = MT5Connector(server_url=mt5_server_url)
        self._connection_verified = False

    async def verify_connection(self) -> bool:
        """
        Verifica se a conexão com MT5 está funcionando.

        Returns:
            True se conectado, False caso contrário
        """
        try:
            self._connection_verified = self.connector.check_connection()
            return self._connection_verified
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            self._connection_verified = False
            return False

    async def get_account_summary(self) -> Dict[str, Any]:
        """
        Obtém um resumo da conta de trading.

        Returns:
            Dicionário com informações resumidas da conta
        """
        try:
            account = self.connector.get_account_info()
            return {
                "status": "success",
                "balance": account.get("balance", 0),
                "equity": account.get("equity", 0),
                "margin_free": account.get("margin_free", 0),
                "margin_level": account.get("margin_level", 0),
                "profit": account.get("profit", 0),
                "currency": account.get("currency", "USD"),
                "login": account.get("login"),
                "server": account.get("server")
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao obter resumo da conta: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def get_open_positions_summary(self) -> Dict[str, Any]:
        """
        Obtém um resumo das posições abertas.

        Returns:
            Dicionário com resumo de posições
        """
        try:
            positions = self.connector.get_positions()

            if not positions:
                return {
                    "status": "success",
                    "count": 0,
                    "positions": [],
                    "total_profit": 0
                }

            total_profit = sum(p.get("profit", 0) for p in positions)

            positions_summary = []
            for pos in positions:
                positions_summary.append({
                    "ticket": pos.get("ticket"),
                    "symbol": pos.get("symbol"),
                    "type": "BUY" if pos.get("type") == 0 else "SELL",
                    "volume": pos.get("volume"),
                    "price_open": pos.get("price_open"),
                    "price_current": pos.get("price_current"),
                    "profit": pos.get("profit"),
                    "sl": pos.get("sl"),
                    "tp": pos.get("tp")
                })

            return {
                "status": "success",
                "count": len(positions),
                "positions": positions_summary,
                "total_profit": total_profit
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao obter posições: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def execute_buy_order(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executa uma ordem de compra.

        Args:
            symbol: Símbolo para comprar
            volume: Volume em lotes
            sl: Stop loss (opcional)
            tp: Take profit (opcional)

        Returns:
            Resultado da operação
        """
        try:
            result = self.connector.buy_market(
                symbol=symbol,
                volume=volume,
                sl=sl,
                tp=tp,
                comment="Chatbot BUY order"
            )

            return {
                "status": "success",
                "action": "BUY",
                "symbol": symbol,
                "volume": volume,
                "price": result.get("price"),
                "order": result.get("order"),
                "sl": sl,
                "tp": tp,
                "timestamp": datetime.now().isoformat()
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao executar BUY: {e}")
            return {
                "status": "error",
                "action": "BUY",
                "message": str(e)
            }

    async def execute_sell_order(
        self,
        symbol: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executa uma ordem de venda.

        Args:
            symbol: Símbolo para vender
            volume: Volume em lotes
            sl: Stop loss (opcional)
            tp: Take profit (opcional)

        Returns:
            Resultado da operação
        """
        try:
            result = self.connector.sell_market(
                symbol=symbol,
                volume=volume,
                sl=sl,
                tp=tp,
                comment="Chatbot SELL order"
            )

            return {
                "status": "success",
                "action": "SELL",
                "symbol": symbol,
                "volume": volume,
                "price": result.get("price"),
                "order": result.get("order"),
                "sl": sl,
                "tp": tp,
                "timestamp": datetime.now().isoformat()
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao executar SELL: {e}")
            return {
                "status": "error",
                "action": "SELL",
                "message": str(e)
            }

    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """
        Fecha uma posição aberta.

        Args:
            ticket: Ticket da posição

        Returns:
            Resultado da operação
        """
        try:
            result = self.connector.close_position(ticket)
            return {
                "status": "success",
                "action": "CLOSE",
                "ticket": ticket,
                "price": result.get("price"),
                "timestamp": datetime.now().isoformat()
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao fechar posição: {e}")
            return {
                "status": "error",
                "action": "CLOSE",
                "message": str(e)
            }

    async def get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém o preço atual de um símbolo.

        Args:
            symbol: Símbolo

        Returns:
            Dicionário com preços bid/ask
        """
        try:
            tick = self.connector.get_symbol_tick(symbol)
            return {
                "status": "success",
                "symbol": symbol,
                "bid": tick.get("bid"),
                "ask": tick.get("ask"),
                "last": tick.get("last"),
                "timestamp": datetime.now().isoformat()
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao obter preço: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def validate_symbol(self, symbol: str) -> bool:
        """
        Valida se um símbolo existe e está disponível.

        Args:
            symbol: Símbolo a validar

        Returns:
            True se válido, False caso contrário
        """
        try:
            self.connector.get_symbol_info(symbol)
            return True
        except MT5OperationError:
            return False

    async def get_market_data(
        self,
        symbol: str,
        timeframe: int = 60,
        count: int = 50
    ) -> Dict[str, Any]:
        """
        Obtém dados de mercado (velas).

        Args:
            symbol: Símbolo
            timeframe: Timeframe em minutos
            count: Número de velas

        Returns:
            Dicionário com dados de mercado
        """
        try:
            candles = self.connector.get_candles(
                symbol=symbol,
                timeframe=timeframe,
                count=count
            )

            return {
                "status": "success",
                "symbol": symbol,
                "timeframe": timeframe,
                "count": len(candles) if candles else 0,
                "candles": candles
            }
        except MT5OperationError as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
