#!/usr/bin/env python3
"""Trading Chatbot Client - Integrates Ollama MCP and MT5 MCP"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
from pydantic import BaseModel, Field
import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = None  # Will be initialized in async context

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Ollama"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with self.session.request(method, url, **kwargs) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Ollama API error {response.status}: {error_text}")


class ChatbotConfig(BaseModel):
    """Chatbot configuration"""

    ollama_host: str = Field(default="http://localhost:8001", description="Ollama MCP server URL")
    mt5_host: str = Field(default="http://localhost:8000", description="MT5 MCP server URL")
    chat_model: str = Field(default="llama3.2:1b", description="Default chat model")
    conversation_timeout: int = Field(default=300, description="Conversation timeout in seconds")
    max_conversation_length: int = Field(default=50, description="Maximum conversation history length")


class ChatMessage(BaseModel):
    """Chat message structure"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = Field(..., description="Role: user, assistant, system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ParsedTradingIntent(BaseModel):
    """Parsed trading intent from user message"""

    intent: str = Field(..., description="Intent type: trade|info|analysis|other")
    action: Optional[str] = Field(None, description="Trading action: buy|sell|check|cancel|modify")
    symbol: Optional[str] = Field(None, description="Trading symbol")
    volume: Optional[float] = Field(None, description="Trading volume")
    price: Optional[float] = Field(None, description="Entry price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    timeframe: Optional[str] = Field(None, description="Chart timeframe")
    confidence: float = Field(..., description="Confidence score 0-1")
    parsed_command: str = Field(..., description="Human readable summary")


class TradingChatbot:
    """Trading chatbot that integrates Ollama and MT5 MCPs"""

    def __init__(self, config: ChatbotConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversation_history: List[ChatMessage] = []
        self.user_context: Dict[str, Any] = {}  # User preferences and context

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _call_mcp_tool_sync(self, server_url: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call MCP tool synchronously to avoid event loop issues"""
        import requests

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

            # Use synchronous HTTP call to avoid event loop conflicts
            response = requests.post(
                f"{server_url}/mcp", # Corrected endpoint for FastMCP
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("result")
            else:
                error_text = response.text
                raise Exception(f"MCP call failed: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            raise

    async def _call_ollama_tool(self, tool_name: str, **kwargs) -> Any:
        """Call Ollama MCP tool"""
        return self._call_mcp_tool_sync(self.config.ollama_host, tool_name, kwargs)

    async def _call_mt5_tool(self, tool_name: str, **kwargs) -> Any:
        """Call MT5 MCP tool"""
        return self._call_mcp_tool_sync(self.config.mt5_host, tool_name, kwargs)

    async def initialize(self) -> Dict[str, Any]:
        """Initialize chatbot and check server connectivity"""
        try:
            # Check Ollama health
            ollama_health = await self._call_ollama_tool("check_ollama_health")
            logger.info(f"Ollama health: {ollama_health}")

            # Check MT5 connection (try to get account info)
            try:
                mt5_account = await self._call_mt5_tool("get_account_info")
                mt5_status = {"status": "connected", "account": mt5_account.login}
            except Exception as e:
                mt5_status = {"status": "disconnected", "error": str(e)}
                logger.warning(f"MT5 connection failed: {e}")

            # Initialize conversation with system message
            system_message = ChatMessage(
                role="system",
                content="""You are an AI trading assistant. You can help users with:

TRADING COMMANDS (natural language):
- Buy/sell orders: "buy 100 EURUSD" or "sell 0.01 BTCUSD at 45000 with stop loss 44000"
- Market data: "show me EURUSD price" or "get BTCUSD candles for H1"
- Account info: "how much balance do I have?" or "show my positions"
- Order management: "cancel order 12345" or "close all positions"

ANALYSIS REQUESTS:
- Market analysis: "analyze EURUSD trend" or "what's the best trading opportunity now?"
- Technical indicators: "show RSI for BTCUSD on M15"
- Predictions: "predict EURUSD direction for next hour"

Always be safe, suggest stop losses, and ask for confirmation on risky trades."""
            )

            self.conversation_history = [system_message]

            return {
                "status": "initialized",
                "ollama": ollama_health,
                "mt5": mt5_status,
                "chat_model": self.config.chat_model
            }

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    async def _parse_trading_intent(self, user_message: str) -> ParsedTradingIntent:
        """Parse trading intent from user message using Ollama"""
        try:
            analysis_result = await self._call_ollama_tool("analyze_trading_intent", message=user_message)

            # Ensure confidence is float
            confidence = float(analysis_result.get("confidence", 0.0))

            return ParsedTradingIntent(**analysis_result)

        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            return ParsedTradingIntent(
                intent="error",
                confidence=0.0,
                parsed_command=f"Failed to parse intent: {str(e)}"
            )

    async def _execute_trading_command(self, intent: ParsedTradingIntent) -> Dict[str, Any]:
        """Execute trading command based on parsed intent"""
        try:
            # Validate confidence threshold
            if intent.confidence < 0.6:
                return {
                    "status": "confirmation_required",
                    "message": f"I'm not confident about your request. Did you mean: {intent.parsed_command}?",
                    "parsed_intent": intent.model_dump()
                }

            action = intent.action or ""
            symbol = intent.symbol
            volume = intent.volume
            price = intent.price
            sl = intent.stop_loss
            tp = intent.take_profit

            # TRADE EXECUTION
            if action.lower() == "buy":
                if not symbol:
                    return {"status": "error", "message": "Symbol not specified for buy order"}
                if not volume:
                    return {"status": "error", "message": "Volume not specified for buy order"}

                return await self._execute_buy_order(symbol, volume, sl, tp)

            elif action.lower() == "sell":
                if not symbol:
                    return {"status": "error", "message": "Symbol not specified for sell order"}
                if not volume:
                    return {"status": "error", "message": "Volume not specified for sell order"}

                return await self._execute_sell_order(symbol, volume, sl, tp)

            elif action.lower() == "check":
                if "balance" in intent.parsed_command.lower() or "account" in intent.parsed_command.lower():
                    return await self._get_account_info()
                elif "position" in intent.parsed_command.lower():
                    return await self._get_positions(symbol)
                elif "order" in intent.parsed_command.lower():
                    return await self._get_orders(symbol)
                else:
                    return {"status": "error", "message": "What would you like me to check?"}

            elif action.lower() == "cancel":
                return {"status": "error", "message": "Please specify which order to cancel"}

            elif action.lower() == "modify":
                return {"status": "error", "message": "Position modification not implemented yet"}

            else:
                return {
                    "status": "confusion",
                    "message": f"I'm not sure what you want to do with: {intent.parsed_command}"
                }

        except Exception as e:
            logger.error(f"Trading command execution failed: {e}")
            return {"status": "error", "message": f"Command execution failed: {str(e)}"}

    async def _execute_buy_order(self, symbol: str, volume: float, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict[str, Any]:
        """Execute buy market order"""
        try:
            # Add confirmation for large volumes
            if volume > 1.0:
                return {
                    "status": "confirmation_required",
                    "message": f"Are you sure you want to BUY {volume} lots of {symbol}? This is a large position! (SL: {sl}, TP: {tp})",
                    "command": "confirm_buy",
                    "params": {"symbol": symbol, "volume": volume, "sl": sl, "tp": tp}
                }

            result = await self._call_mt5_tool(
                "buy_market",
                symbol=symbol,
                volume=volume,
                sl=sl,
                tp=tp,
                comment="Chatbot order"
            )

            return {
                "status": "success",
                "message": f"BUY order executed: {symbol} {volume} lots",
                "order_result": result
            }

        except Exception as e:
            return {"status": "error", "message": f"Buy order failed: {str(e)}"}

    async def _execute_sell_order(self, symbol: str, volume: float, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict[str, Any]:
        """Execute sell market order"""
        try:
            # Add confirmation for large volumes
            if volume > 1.0:
                return {
                    "status": "confirmation_required",
                    "message": f"Are you sure you want to SELL {volume} lots of {symbol}? This is a large position! (SL: {sl}, TP: {tp})",
                    "command": "confirm_sell",
                    "params": {"symbol": symbol, "volume": volume, "sl": sl, "tp": tp}
                }

            result = await self._call_mt5_tool(
                "sell_market",
                symbol=symbol,
                volume=volume,
                sl=sl,
                tp=tp,
                comment="Chatbot order"
            )

            return {
                "status": "success",
                "message": f"SELL order executed: {symbol} {volume} lots",
                "order_result": result
            }

        except Exception as e:
            return {"status": "error", "message": f"Sell order failed: {str(e)}"}

    async def _get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            account = await self._call_mt5_tool("get_account_info")
            if account:
                # Access attributes safely
                balance = account.get('balance', 0)
                equity = account.get('equity', 0)
                margin_free = account.get('margin_free', 0)

                return {
                    "status": "success",
                    "message": f"💰 **SALDO ATUAL:**\n• Saldo: ${balance:.2f}\n• Equity: ${equity:.2f}\n• Margem Livre: ${margin_free:.2f}",
                    "account_info": account
                }
            else:
                return {"status": "error", "message": "Não foi possível obter informações da conta"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao obter informações da conta: {str(e)}"}

    async def _get_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get open positions"""
        try:
            positions = await self._call_mt5_tool("positions_get", **({"symbol": symbol} if symbol else {}))
            if not positions:
                return {"status": "success", "message": "No open positions"}

            message = f"Open positions ({len(positions)}):\n"
            for pos in positions:
                message += f"- {pos['symbol']} {pos['type']} {pos['volume']} lots @ {pos['price_open']}\n"

            return {"status": "success", "message": message, "positions": positions}

        except Exception as e:
            return {"status": "error", "message": f"Could not get positions: {str(e)}"}

    async def _get_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get active orders"""
        try:
            orders = await self._call_mt5_tool("orders_get", **({"symbol": symbol} if symbol else {{}}))
            if not orders:
                return {"status": "success", "message": "No active orders"}

            message = f"Active orders ({len(orders)}):\n"
            for order in orders:
                message += f"- {order['ticket']}: {order['symbol']} {order['type']} {order['volume_initial']}\n"
            
            return {"status": "success", "message": message, "orders": orders}

        except Exception as e:
            return {"status": "error", "message": f"Could not get orders: {str(e)}"}

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and return response using MCP only"""
        try:
            message_lower = message.lower().strip()

            # Check for trade confirmation first
            if pending_trade and (message_lower in ['ok', 'sim', 'yes', 'confirmar', 'execute']):
                return await self._execute_pending_trade()

            elif pending_trade and (message_lower in ['cancelar', 'cancel', 'nao', 'no', 'abort']):
                return await self._cancel_pending_trade()

            # Clear old pending trade if user starts a new command
            if pending_trade and (message_lower.startswith(('comprar', 'vender', 'buy', 'sell'))):
                pending_trade = None

            # Simple keyword-based detection for common commands
            if "saldo" in message_lower or "balance" in message_lower or "conta" in message_lower:
                result = await self._get_account_info()
                print(f"DEBUG: Saldo result: {result}")
                return result
            elif "posi" in message_lower or "position" in message_lower:
                result = await self._get_positions()
                return result
            elif "ordem" in message_lower or "orders" in message_lower or "pendente" in message_lower:
                result = await self._get_orders()
                return result
            elif "preco" in message_lower or "price" in message_lower:
                # Extract symbol from message
                symbol = _extract_symbol_from_message(message)
                if symbol:
                    result = await self._get_symbol_price(symbol)
                    return result
                else:
                    return {"status": "error", "message": "Especifique um símbolo para ver o preço"}
            elif "teste" in message_lower or "ping" in message_lower:
                result = await self._test_connection()
                return result
            elif "fechar" in message_lower and "tudo" in message_lower:
                result = await self._close_all_positions()
                return result
            elif "fechar" in message_lower:
                return {"status": "error", "message": "Especifique qual posição fechar ou use 'fechar tudo'"}

            # Parse trading intent using Ollama for complex commands
            intent = await self._parse_trading_intent(message)

            if intent.intent == "trade" and intent.action in ["buy", "sell"]:
                return await self._prepare_trade_order(intent)
            elif intent.intent == "analysis":
                return await self._analyze_market(intent)

            # Fallback response
            return {
                "status": "unknown",
                "message": f"🤖 **Comando não reconhecido:** '{message}'\n\n💡 **Comandos disponíveis:**\n• Saldo: 'quanto tenho de saldo?', 'ver saldo'\n• Posições: 'minhas posições', 'posições abertas'\n• Ordens: 'ordens ativas', 'ordens pendentes'\n• Preço: 'preço EURUSD', 'cotação BTCUSD'\n• Trading: 'comprar 0.1 EURUSD', 'vender 0.01 XAUUSD'\n• Análise: 'analisar EURUSD', 'como está o mercado'\n• Fechar: 'fechar tudo', 'fechar posição 123'",
                "intent": intent.model_dump() if hasattr(intent, 'model_dump') else intent.__dict__
            }

        except Exception as e:
            return {"status": "error", "message": f"[ERRO SISTEMA]: {str(e)}"}

    async def chat(self, message: str) -> Dict[str, Any]:
        """Process a chat message."""
        return await self.process_message(message)

    async def _execute_pending_trade(self) -> Dict[str, Any]:
        """Execute pending trade through MCP"""
        global pending_trade

        if not pending_trade:
            return {"status": "error", "message": "[ERRO] Nenhuma operacao pendente"}

        try:
            symbol = pending_trade['symbol']
            volume = pending_trade['volume']
            tp_price = pending_trade.get('tp_price')
            sl_price = pending_trade.get('sl_price')
            action = pending_trade['action']

            if action.upper() == 'BUY':
                result = await self._call_mt5_tool(
                    "buy_market",
                    symbol=symbol,
                    volume=volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment="Chatbot MCP trade"
                )
            elif action.upper() == 'SELL':
                result = await self._call_mt5_tool(
                    "sell_market",
                    symbol=symbol,
                    volume=volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment="Chatbot MCP trade"
                )
            else:
                return {"status": "error", "message": "[ERRO] Acao invalida"}

            if result and result['retcode'] == 10009:  # TRADE_RETCODE_DONE
                msg = f"[OPERACAO EXECUTADA] {action.upper()} {symbol} {volume} lots Ticket: {result['order']}"
                pending_trade = None
                return {"status": "success", "message": msg}
            else:
                error_msg = f"[FALHA EXECUCAO] {result['comment'] if result else 'Erro desconhecido'}"
                pending_trade = None
                return {"status": "error", "message": error_msg}

        except Exception as e:
            pending_trade = None
            return {"status": "error", "message": f"[ERRO EXECUCAO]: {str(e)}"}

    async def _cancel_pending_trade(self) -> Dict[str, Any]:
        """Cancel pending trade"""
        global pending_trade

        if not pending_trade:
            return {"status": "error", "message": "[ERRO] Nenhuma operacao pendente"}

        symbol = pending_trade['symbol']
        action = pending_trade['action']
        pending_trade = None

        return {
            "status": "cancelled",
            "message": f"[OPERACAO CANCELADA] {action.upper()} {symbol} - Abortada pelo usuario"
        }

    async def _prepare_trade_order(self, intent: ParsedTradingIntent) -> Dict[str, Any]:
        """Prepare trade order for confirmation"""
        global pending_trade

        symbol = intent.symbol
        volume = intent.volume
        action = intent.action.upper() if intent.action else ""

        if not symbol or not volume or not action:
            return {"status": "error", "message": "[ERRO] Parametros insuficientes para trade"}

        try:
            # CHECK AND CLOSE EXISTING POSITIONS BEFORE OPENING NEW ONES
            await self._close_all_existing_positions(symbol)

            # Get current price and symbol info through MCP
            if action == "BUY":
                tick_data = await self._call_mt5_tool("get_symbol_info_tick", symbol=symbol)
                current_price = tick_data['ask'] if tick_data else 0
            else:
                tick_data = await self._call_mt5_tool("get_symbol_info_tick", symbol=symbol)
                current_price = tick_data['bid'] if tick_data else 0

            symbol_info = await self._call_mt5_tool("get_symbol_info", symbol=symbol)
            contract_size = symbol_info['trade_contract_size'] if symbol_info and symbol_info['trade_contract_size'] > 0 else 1.0

            # Convert TP/SL dollar values to price levels
            tp_price = intent.take_profit
            sl_price = intent.stop_loss

            if intent.take_profit and tp_price < 10:  # Assume dollar value if small number
                if action == "BUY":
                    tp_price = current_price + (intent.take_profit / (volume * contract_size))
                else:  # SELL
                    tp_price = current_price - (intent.take_profit / (volume * contract_size))

            if intent.stop_loss and sl_price < 10:  # Assume dollar value if small number
                if action == "BUY":
                    sl_price = current_price - (intent.stop_loss / (volume * contract_size))
                else:  # SELL
                    sl_price = current_price + (intent.stop_loss / (volume * contract_size))

            pending_trade = {
                'symbol': symbol,
                'volume': volume,
                'tp_price': tp_price,
                'sl_price': sl_price,
                'action': action
            }

            msg = f"[PREPARANDO {action}] {symbol} {volume} lots @ ${current_price:.5f}\n"
            if sl_price:
                msg += f"Stop Loss: ${sl_price:.5f}\n"
            if tp_price:
                msg += f"Take Profit: ${tp_price:.5f}\n"
            msg += "\n[CONFIRMACAO] Envie 'ok' para executar ou 'cancelar' para abortar"

            return {"status": "pending_confirmation", "message": msg}

        except Exception as e:
            return {"status": "error", "message": f"[ERRO PREPARACAO]: {str(e)}"}

    async def _close_all_existing_positions(self, new_symbol: str) -> None:
        """Close all existing positions before opening new ones"""
        try:
            # Get all open positions
            positions = await self._call_mt5_tool("positions_get")

            if positions and len(positions) > 0:
                print(f"[AUTO CLOSE] Fechando {len(positions)} posicoes existentes antes de abrir nova operacao")

                # Close all positions one by one
                for position in positions:
                    try:
                        # Extract ticket using safe attribute access
                        ticket = position['ticket']
                        if ticket:
                            close_result = await self._call_mt5_tool(
                                "close_position",
                                ticket=ticket,
                                comment="[AUTO CLOSE] Nova operacao sendo aberta"
                            )
                            if close_result and close_result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                                print(f"[AUTO CLOSE] Posicao {ticket} fechada com sucesso")
                            else:
                                print(f"[AUTO CLOSE] Falha ao fechar posicao {ticket}: {close_result}")
                        else:
                            print(f"[AUTO CLOSE] Ticket nao encontrado para posicao: {position}")
                    except Exception as e:
                        print(f"[AUTO CLOSE] Erro ao fechar posicao: {e}")
                        continue

                print(f"[AUTO CLOSE] Processo de fechamento concluido")
            else:
                print("[AUTO CLOSE] Nenhuma posicao aberta para fechar")

        except Exception as e:
            print(f"[AUTO CLOSE] Erro ao verificar/fechar posicoes: {e}")

    async def _test_connection(self) -> Dict[str, Any]:
        """Test MCP connection to MT5"""
        try:
            health = await self._call_mt5_tool("health")
            if health and health.get('status') == 'ok':
                return {"status": "success", "message": "[CONEXAO OK] MCP MT5 respondendo"}
            else:
                return {"status": "error", "message": "[CONEXAO FALHANDO] MCP MT5 nao responde"}
        except Exception as e:
            return {"status": "error", "message": f"[ERRO CONEXAO]: {str(e)}"}

    async def _get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """Get symbol price information"""
        try:
            tick = await self._call_mt5_tool("get_symbol_info_tick", symbol=symbol)
            if tick:
                bid = tick['bid'] if tick else 0
                ask = tick['ask'] if tick else 0
                return {
                    "status": "success",
                    "message": f"💰 **{symbol}**:\n• Bid: ${bid:.5f}\n• Ask: ${ask:.5f}\n• Spread: {abs(ask - bid):.5f}",
                    "price_info": {"symbol": symbol, "bid": bid, "ask": ask}
                }
            else:
                return {"status": "error", "message": f"Não foi possível obter preço para {symbol}"}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao obter preço: {str(e)}"}

    async def _close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions"""
        try:
            positions = await self._call_mt5_tool("positions_get")
            if not positions:
                return {"status": "success", "message": "Nenhuma posição aberta para fechar"}

            closed_count = 0
            for position in positions:
                try:
                    ticket = position['ticket']
                    if ticket:
                        result = await self._call_mt5_tool("close_position", ticket=ticket)
                        if result and result.get('retcode') == 10009:
                            closed_count += 1
                except Exception as e:
                    print(f"Erro ao fechar posição {ticket}: {e}")
                    continue

            return {
                "status": "success",
                "message": f"✅ Fechadas {closed_count} posições"
            }
        except Exception as e:
            return {"status": "error", "message": f"Erro ao fechar posições: {str(e)}"}

    async def _analyze_market(self, intent: ParsedTradingIntent) -> Dict[str, Any]:
        """Analyze market based on intent"""
        try:
            symbol = intent.symbol
            if symbol:
                # Get symbol information
                tick = await self._call_mt5_tool("get_symbol_info_tick", symbol=symbol)
                if tick:
                    bid = tick['bid'] if tick else 0
                    ask = tick['ask'] if tick else 0
                    return {
                        "status": "success",
                        "message": f"📊 **Análise de {symbol}:**\n• Preço atual: ${ask:.5f}\n• Bid: ${bid:.5f}\n• Spread: {abs(ask - bid):.5f}"
                    }
                else:
                    return {"status": "error", "message": f"Não foi possível obter dados para {symbol}"}
            else:
                return {"status": "error", "message": "Especifique um símbolo para análise"}
        except Exception as e:
            return {"status": "error", "message": f"Erro na análise: {str(e)}"}


def _extract_symbol_from_message(message: str) -> str:
    """Extract trading symbol from message (improved parsing)"""
    import re

    # Find symbol in the exact case it appears, added XAUUSDc explicitly
    symbol_patterns = [
        r'\bBTCUSDC\b',  # BTCUSDc (exactly as needed)
        r'\b(EURUSD|GBPUSD|USDJPY|USDCHF|AUDUSD|USDCAD|NZDUSD|EURGBP|EURJPY|XAUUSD|XAUEUR|BTCUSD|ETHUSD)[a-zA-Z]*\b'
    ]

    for pattern in symbol_patterns:
        symbol_match = re.search(pattern, message)
        if symbol_match:
            # Return exactly what the user typed
            return symbol_match.group()

    # Try case-insensitive if exact match fails
    for pattern in symbol_patterns:
        symbol_match = re.search(pattern, message, re.IGNORECASE)
        if symbol_match:
            original_match = symbol_match.group()
            # Try to preserve the original case from the message
            start_pos = message.upper().find(original_match.upper())
            if start_pos != -1:
                end_pos = start_pos + len(original_match)
                return message[start_pos:end_pos]

    return None


def _extract_volume_from_message(message: str) -> float:
    """Extract volume/lots from message (improved parsing)"""
    import re

    # Look for 0.1, 1.5, etc. patterns that could be volume
    # Match decimal numbers in trading context
    volume_patterns = [
        r'\bcomprar\s+(\d+\.?\d*)\s+de\s+[A-Z]+',
        r'\bvender\s+(\d+\.?\d*)\s+de\s+[A-Z]+',
        r'\bcomprar\s+(\d+\.?\d*)\s+[A-Z]+',
        r'\bvender\s+(\d+\.?\d*)\s+[A-Z]+',
        r'\b(\d+\.?\d*)\s+lots\b',
        r'\b(\d+\.?\d*)\s+de\b',
        r'\bvolume\s*[:=]?\s*(\d+\.?\d*)',
    ]

    for pattern in volume_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            try:
                volume = float(match.group(1))
                if 0.001 <= volume <= 1000:  # Allow smaller volumes like 0.001
                    return volume
            except ValueError:
                continue

    # Look for any isolated decimal number that could be volume
    decimals = re.findall(r'\b\d+\.\d+\b', message)
    for decimal in decimals:
        try:
            volume = float(decimal)
            if 0.001 <= volume <= 1000:
                return volume
        except ValueError:
            continue

    # Default volume for demo safety
    return 0.01


def _extract_tp_sl_from_message(message: str): # Now returns (tp_value, sl_value, tp_unit, sl_unit)
    """Extract take profit and stop loss from message in pips"""
    import re

    tp = None
    sl = None

    # Look for TP patterns
    tp_value = None
    sl_value = None
    tp_unit = "none"
    sl_unit = "none"

    # Look for TP patterns (prioritize dollar values)
    tp_patterns = [
        (r'tp\s+\$(\d+\.?\d*)', "dollars"),  # "TP $1" or "TP $1.50"
        (r'tp\s+de\s+\$(\d+\.?\d*)', "dollars"),  # "tp de $1"
        (r'take\s+profit\s*[:=]?\s*\$(\d+\.?\d*)', "dollars"),  # "take profit: $1"
        (r'tp\s*[:=]?\s*(\d+\.?\d*)', "pips"),  # "tp=500" (default to pips if no $)
        (r'take\s+profit\s*[:=]?\s*(\d+\.?\d*)', "pips"),
    ]

    for pattern, unit in tp_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            tp_value = float(match.group(1))
            tp_unit = unit
            break

    # Look for SL patterns (prioritize dollar values)
    sl_patterns = [
        (r'sl\s+de\s+\$(\d+\.?\d*)', "dollars"),  # "sl de $1"
        (r'stop\s+loss\s*[:=]?\s*\$(\d+\.?\d*)', "dollars"),  # "stop loss: $1"
        (r'sl\s*[:=]?\s*(\d+\.?\d*)', "pips"),  # "sl=1500" (default to pips if no $)
        (r'stop\s+loss\s*[:=]?\s*(\d+\.?\d*)', "pips"),
    ]

    for pattern, unit in sl_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            sl_value = float(match.group(1))
            sl_unit = unit
            break

    return tp_value, sl_value, tp_unit, sl_unit


# Global chatbot instance
chatbot: Optional[TradingChatbot] = None


async def get_chatbot() -> TradingChatbot:
    """Get or create global chatbot instance"""
    global chatbot
    if chatbot is None:
        config = ChatbotConfig()
        chatbot = TradingChatbot(config)
        await chatbot.__aenter__()
    return chatbot


async def initialize_chatbot() -> Dict[str, Any]:
    """Initialize the global chatbot"""
    bot = await get_chatbot()
    return await bot.initialize()


# Global state for pending trades
pending_trade = None

async def send_message(message: str) -> Dict[str, Any]:
    """Send message to chatbot using MCP protocol for MT5 communication"""
    bot = await get_chatbot()
    return await bot.chat(message)


async def send_message_old(message: str) -> Dict[str, Any]: # This function is called by the web interface
    """Send message to chatbot and get response"""
    bot = await get_chatbot()
    return await bot.chat(message)


async def confirm_trading_command(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Confirm and execute high-risk trading command"""
    bot = await get_chatbot()
    return await bot.confirm_command(command, params)





def _extract_price_from_message(message: str) -> float:
    """Extracts price from a message."""
    import re
    match = re.search(r'(\d+\.?\d+)', message)
    return float(match.group(1)) if match else None
