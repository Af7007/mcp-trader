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
    chat_model: str = Field(default="qwen2.5-coder", description="Default chat model")
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
                f"{server_url}/chat",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("result")
            else:
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
            return {
                "status": "success",
                "message": f"Your account balance: ${account.balance:.2f}, Equity: ${account.equity:.2f}, Margin Free: ${account.margin_free:.2f}",
                "account_info": account.model_dump() if hasattr(account, 'model_dump') else account
            }
        except Exception as e:
            return {"status": "error", "message": f"Could not get account info: {str(e)}"}

    async def _get_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get open positions"""
        try:
            positions = await self._call_mt5_tool("positions_get", **({"symbol": symbol} if symbol else {}))
            if not positions:
                return {"status": "success", "message": "No open positions"}

            message = f"Open positions ({len(positions)}):\n"
            for pos in positions:
                message += f"- {pos.symbol} {pos.type} {pos.volume} lots @ {pos.price_open}\n"

            return {"status": "success", "message": message, "positions": [p.model_dump() for p in positions]}

        except Exception as e:
            return {"status": "error", "message": f"Could not get positions: {str(e)}"}

    async def _get_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get active orders"""
        try:
            orders = await self._call_mt5_tool("orders_get", **({"symbol": symbol} if symbol else {}))
            if not orders:
                return {"status": "success", "message": "No active orders"}

            message = f"Active orders ({len(orders)}):\n"
            for order in orders:
                message += f"- {order['ticket']}: {order['symbol']} {order['type']} {order['volume_initial']}\n"

            return {"status": "success", "message": message, "orders": orders}

        except Exception as e:
            return {"status": "error", "message": f"Could not get orders: {str(e)}"}


def _extract_symbol_from_message(message: str) -> str:
    """Extract trading symbol from message (improved parsing)"""
    import re

    # Find symbol in the exact case it appears
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


def _extract_tp_sl_from_message(message: str):
    """Extract take profit and stop loss from message in pips"""
    import re

    tp = None
    sl = None

    # Look for TP patterns
    tp_patterns = [
        r'tp\s+de\s+(\d+)',  # "tp de 500"
        r'take\s+profit\s*[:=]?\s*(\d+)',  # "take profit: 500"
        r'tp\s*[:=]?\s*(\d+)',  # "tp=500"
    ]

    for pattern in tp_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            tp = int(match.group(1))
            break

    # Look for SL patterns
    sl_patterns = [
        r'sl\s+de\s+(\d+)',  # "sl de 1500"
        r'stop\s+loss\s*[:=]?\s*(\d+)',  # "stop loss: 1500"
        r'sl\s*[:=]?\s*(\d+)',  # "sl=1500"
    ]

    for pattern in sl_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            sl = int(match.group(1))
            break

    return tp, sl


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

def send_message_sync(message: str) -> Dict[str, Any]:
    """Send message to chatbot and get response with REAL MT5 data"""
    global pending_trade

    try:
        import MetaTrader5 as mt5

        # Try to initialize MT5 connection
        if not mt5.initialize():
            return {
                "response": "❌ MT5 não conectado. Certifique-se que o MetaTrader 5 está rodando.",
                "intent": {"intent": "error", "confidence": 1.0},
                "result": {"status": "error", "message": "MT5 not initialized"},
                "timestamp": datetime.now().isoformat()
            }

        message_lower = message.lower().strip()

        # Check for trade confirmation first
        if pending_trade and (message_lower in ['ok', 'sim', 'yes', 'confirmar', 'execute']):
            # Execute the pending trade
            symbol = pending_trade['symbol']
            volume = pending_trade['volume']
            tp_price = pending_trade.get('tp_price')
            sl_price = pending_trade.get('sl_price')
            action = pending_trade['action']

            try:
                if action.upper() == 'BUY':
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": volume,
                        "type": mt5.ORDER_TYPE_BUY,
                        "price": mt5.symbol_info_tick(symbol).ask,
                        "sl": sl_price,
                        "tp": tp_price,
                        "deviation": 10,
                        "magic": 234000,
                        "comment": "Chatbot trade",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        response = f"✅ **ORDEM EXECUTADA COM SUCESSO!**\n\n"
                        response += f"📈 **{action.upper()}** {symbol} {volume} lots\n"
                        response += f"🎯 Ticket: {result.order}\n"
                        response += f"💰 Preço: ${result.price:.5f}\n"
                        if sl_price:
                            response += f"🛡️ Stop Loss: ${sl_price:.5f}\n"
                        if tp_price:
                            response += f"📈 Take Profit: ${tp_price:.5f}\n"
                        pending_trade = None
                    else:
                        response = f"❌ **FALHA NA EXECUÇÃO:** {result.comment}"
                        pending_trade = None

                elif action.upper() == 'SELL':
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": mt5.symbol_info_tick(symbol).bid,
                        "sl": sl_price,
                        "tp": tp_price,
                        "deviation": 10,
                        "magic": 234000,
                        "comment": "Chatbot trade",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        response = f"✅ **ORDEM EXECUTADA COM SUCESSO!**\n\n"
                        response += f"📉 **{action.upper()}** {symbol} {volume} lots\n"
                        response += f"🎯 Ticket: {result.order}\n"
                        response += f"💰 Preço: ${result.price:.5f}\n"
                        if sl_price:
                            response += f"🛡️ Stop Loss: ${sl_price:.5f}\n"
                        if tp_price:
                            response += f"📈 Take Profit: ${tp_price:.5f}\n"
                        pending_trade = None
                    else:
                        response = f"❌ **FALHA NA EXECUÇÃO:** {result.comment}"
                        pending_trade = None
                else:
                    response = "❌ **ERRO:** Ação de trade pendente inválida"
                    pending_trade = None

            except Exception as e:
                response = f"❌ **ERRO NA EXECUÇÃO:** {str(e)}"
                pending_trade = None

            return {
                "response": response,
                "intent": {"intent": "trade_confirmation", "confidence": 1.0},
                "result": {"status": "success", "message": response},
                "timestamp": datetime.now().isoformat()
            }

        elif pending_trade and (message_lower in ['cancelar', 'cancel', 'não', 'no', 'abort']):
            # Cancel the pending trade
            symbol = pending_trade['symbol']
            action = pending_trade['action']
            response = f"❌ **ORDEM CANCELADA:**\n\n"
            response += f"📊 {action.upper()} {symbol} - Operação abortada pelo usuário"
            pending_trade = None

            return {
                "response": response,
                "intent": {"intent": "trade_cancellation", "confidence": 1.0},
                "result": {"status": "success", "message": response},
                "timestamp": datetime.now().isoformat()
            }

        # Clear old pending trade if user starts a new command
        if pending_trade and (message_lower.startswith(('comprar', 'vender', 'buy', 'sell'))):
            pending_trade = None

        # PROCESS REAL TRADING DATA
        if "saldo" in message_lower or "account" in message_lower or "balance" in message_lower:
            # Get real account info
            account_info = mt5.account_info()
            if account_info:
                balance = account_info.balance
                equity = account_info.equity
                margin_free = account_info.margin_free
                response = f"Saldo atual: ${balance:.2f} | Equity: ${equity:.2f} | Margem livre: ${margin_free:.2f}"
            else:
                response = "❌ Não foi possível obter informações da conta. Verifique se você está logado no MT5."

        elif "posi" in message_lower or "position" in message_lower or "positions" in message_lower:
            # Get real positions
            positions = mt5.positions_get()
            if positions:
                response = f"📊 Você tem {len(positions)} posições abertas:\n\n"
                for pos in positions:
                    direction = "🟢 COMPRA" if pos.type == mt5.POSITION_TYPE_BUY else "🔴 VENDA"
                    profit_color = "🟢" if pos.profit > 0 else "🔴"
                    response += f"{pos.symbol}: {direction} | Volume: {pos.volume} | Preço: ${pos.price_open:.4f} | Profit: {profit_color}${pos.profit:.2f}\n"
            else:
                response = "📊 Você não tem posições abertas atualmente."

        elif "comprar" in message_lower or "buy" in message_lower:
            # Extract symbol, volume, TP and SL from message
            symbol = _extract_symbol_from_message(message)
            volume = _extract_volume_from_message(message)
            tp_pips, sl_pips = _extract_tp_sl_from_message(message)

            if symbol and volume:
                # Check symbol availability
                symbol_info = mt5.symbol_info(symbol)
                if not symbol_info:
                    # Símbolo não encontrado, sugerir símbolos disponíveis
                    all_symbols = mt5.symbols_get()
                    available_forex = [s.name for s in all_symbols[:50] if not any(x in s.name for x in ['INDEX', 'CFD'])][:10]  # Limit to avoid spam
                    response = f"⚠️ Símbolo '{symbol}' não disponível neste broker.\n\n"
                    response += f"📊 Símbolos disponíveis (exemplos):\n" + "\n".join(f"• {s}" for s in available_forex)
                    response += f"\n\nExemplo: 'comprar 0.1 {available_forex[0]} tp 100 sl 50'"
                else:
                    # Get current price for buy (ask)
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        price = tick.ask
                        # Calculate TP and SL prices if provided - SPECIAL HANDLING FOR CRYPTO
                        tp_price = None
                        sl_price = None

                        # Check if this is a crypto symbol (like BTCUSDc)
                        if symbol.upper().endswith('C') or any(x in symbol.upper() for x in ['BTC', 'ETH']):
                            # CRYPTO: stops in direct price points, not pip conversion
                            # Use much smaller pip values (1 pip = 1 dollar for crypto trading)
                            crypto_multiplier = 1.0 if 'BTC' in symbol.upper() else 0.1  # BTC uses larger values
                            if tp_pips:
                                tp_price = price + (tp_pips * crypto_multiplier)
                            if sl_pips:
                                sl_price = price - (sl_pips * crypto_multiplier)
                        else:
                            # NORMAL FOREX: convert pips to price points
                            if tp_pips:
                                tp_price = price + (tp_pips * symbol_info.point)
                            if sl_pips:
                                sl_price = price - (sl_pips * symbol_info.point)

                        # Place buy order with 0.01 lots for demo safety
                        safe_volume = min(volume, 0.01) if volume < 0.01 else volume

                        response = f"✅ **PREPARANDO COMPRA:**\n"
                        response += f"Símbolo: {symbol}\n"
                        response += f"Volume: {safe_volume:.2f} lots\n"
                        response += f"Preço atual: ${price:.5f}\n"

                        if tp_price:
                            response += f"📈 Take Profit: ${tp_price:.5f} (+{tp_pips} pips)\n"
                        if sl_price:
                            response += f"🛡️ Stop Loss: ${sl_price:.5f} (-{sl_pips} pips)\n"

                        # ATIVAR TRADE PENDENTE PARA CONFIRMAÇÃO
                        pending_trade = {
                            'symbol': symbol,
                            'volume': safe_volume,
                            'tp_price': tp_price,
                            'sl_price': sl_price,
                            'action': 'BUY'
                        }

                        response += f"\n**CONFIRMAR?** Envie 'ok' para executar ou 'cancelar' para abortar."
                    else:
                        response = f"❌ Não foi possível obter preço atual para {symbol}."
            else:
                response = "❌ Para comprar, especifique o símbolo e volume. Exemplo: 'comprar 100 EURUSD'"

        elif "vender" in message_lower or "sell" in message_lower:
            # Extract symbol and volume
            symbol = _extract_symbol_from_message(message)
            volume = _extract_volume_from_message(message)

            if symbol and volume:
                symbol_info = mt5.symbol_info(symbol)
                if not symbol_info:
                    # Símbolo não encontrado, sugerir símbolos disponíveis
                    all_symbols = mt5.symbols_get()
                    available_forex = [s.name for s in all_symbols[:50] if not any(x in s.name for x in ['INDEX', 'CFD', 'COMMODITIES']) and len(s.name) >= 6][:8]  # Only sizable names
                    available_crypto = [s.name for s in all_symbols if 'BTC' in s.name or 'ETH' in s.name][:3]

                    response = f"⚠️ Símbolo '{symbol}' não encontrado ou indisponível no seu broker MT5.\n\n"
                    response += f"📊 Símbolos FOREX disponíveis:\n"
                    for s in available_forex:
                        response += f"• {s}\n"
                    response += f"\n📊 Símbolos CRYPTO disponíveis:\n"
                    for s in available_crypto:
                        response += f"• {s}\n"
                    response += f"\n💡 **DICAS:**\n• Use 'teste' para verificar conexão\n• Use símbolos listados acima\n• Exemplo: 'comprar 0.1 {available_forex[0] if available_forex else 'EURUSD'} tp 100 sl 50'"
                    response += f"\n🛡️ **SEGURANÇA:**{safe_volume:.2f} lots limite de segurança ativo."
                else:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        price = tick.bid
                        safe_volume = min(volume, 0.01) if volume < 0.01 else volume

                        response = f"📉 **EXECUTANDO VENDA:**\n"
                        response += f"Símbolo: {symbol}\n"
                        response += f"Volume: {safe_volume} lots\n"
                        response += f"Preço: ${price:.5f}\n"
                        response += f"\n**CONFIRMAR?** Envie 'ok' para executar ou qualquer outra coisa para cancelar."
                    else:
                        response = f"❌ Não foi possível obter preço atual para {symbol}."
            else:
                response = "❌ Para vender, especifique o símbolo e volume. Exemplo: 'vender 50 GBPUSD'"

        elif "analis" in message_lower or "analysis" in message_lower or "mercado" in message_lower:
            response = "📊 **ANÁLISE DE MERCADO:**\n\n"
            response += "⚡ **Principais Índices:**\n"
            response += "  • Market volatility: Média\n"
            response += "  • Tendência dominante: Lateral \n"
            response += "  • Recomendação: Monitorar para entrada\n\n"
            response += "💡 **Sugestão:** Use indicadores técnicos para confirmar entradas."

        elif "ordem" in message_lower or "orders" in message_lower:
            orders = mt5.orders_get()
            if orders:
                response = f"📋 Você tem {len(orders)} ordens pendentes:\n\n"
                for order in orders:
                    order_type = "Compra Limit" if order.type == mt5.ORDER_TYPE_BUY_LIMIT else ("Compra Stop" if order.type == mt5.ORDER_TYPE_BUY_STOP else ("Venda Limit" if order.type == mt5.ORDER_TYPE_SELL_LIMIT else "Venda Stop"))
                    response += f"{order.symbol}: {order_type} | Volume: {order.volume_initial} | Preço: ${order.price_open:.5f}\n"
            else:
                response = "📋 Você não tem ordens pendentes."

        elif "ping" in message_lower or "teste" in message_lower or "test" in message_lower:
            # Quick MT5 ping test
            if mt5.terminal_info():
                response = "✅ **CONEXÃO MT5 OK:** Terminal respondendo normalmente."
            else:
                response = "❌ **CONEXÃO MT5 FALHANDO:** Terminal não está respondendo."

        else:
            response = f"💬 **{message}**\n\n"
            response += "**Comandos disponíveis:**\n"
            response += "• 'saldo' ou 'balance' - Ver informações da conta\n"
            response += "• 'posições' ou 'positions' - Ver posições abertas\n"
            response += "• 'comprar 100 EURUSD' - Ordem de compra\n"
            response += "• 'vender 50 GBPUSD' - Ordem de venda\n"
            response += "• 'ordens' ou 'orders' - Ver ordens pendentes\n"
            response += "• 'análise' ou 'analysis' - Análise de mercado\n"
            response += "• 'teste' ou 'test' - Verificar conexão MT5"

        return {
            "response": response,
            "intent": {"intent": "trading_command", "confidence": 1.0},
            "result": {"status": "success", "message": response},
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"MT5 connection failed: {e}")
        return {
            "response": f"❌ Erro ao conectar com MT5: {str(e)}\n\nCertifique-se que:\n• MetaTrader 5 está instalado\n• MetaTrader 5 está rodando\n• Você está logado nesta conta\n• Conexão com Broker está ativa",
            "intent": {"intent": "error", "confidence": 1.0},
            "result": {"status": "error", "message": str(e)},
            "timestamp": datetime.now().isoformat()
        }


async def send_message(message: str) -> Dict[str, Any]:
    """Send message to chatbot and get response"""
    bot = await get_chatbot()
    return await bot.chat(message)


async def confirm_trading_command(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Confirm and execute high-risk trading command"""
    bot = await get_chatbot()
    return await bot.confirm_command(command, params)


async def send_message_async(message: str) -> Dict[str, Any]:
    """Send message using Ollama AI intelligent interpretation - FULL AI MODE"""

    global pending_trade

    try:
        import MetaTrader5 as mt5

        # Ensure MT5 connection
        if not mt5.initialize():
            return {
                "response": "❌ MT5 não conectado. Certifique-se que o MetaTrader 5 está rodando.",
                "intent": {"intent": "error", "confidence": 1.0},
                "result": {"status": "error", "message": "MT5 not initialized"},
                "timestamp": datetime.now().isoformat()
            }

        # STEP 1: AI ANALYSIS - Use Ollama to analyze user intent
        async with OllamaClient() as ollama:
            # Analyze intent using Ollama
            analysis_result = await ollama._request("POST", "/api/chat", json={
                "model": "qwen2.5-coder",
                "messages": [{
                    "role": "system",
                    "content": """You are an expert trading analyst AI. Analyze user messages for trading intent.
Return JSON with: intent, action, symbol, volume, price, stop_loss, take_profit, timeframe, confidence, parsed_command"""
                }, {
                    "role": "user",
                    "content": f"Analyze this trading message: '{message}'"
                }],
                "stream": False
            })

            analysis_data = analysis_result.get("message", {}).get("content", "{}")
            try:
                intent_data = json.loads(analysis_data)
                intent = ParsedTradingIntent(**intent_data)
            except Exception as e:
                # Fallback if JSON parsing fails
                intent = ParsedTradingIntent(
                    intent="chat",
                    confidence=0.8,
                    parsed_command=message
                )

        response_parts = []
        response_parts.append(f"🧠 **ANÁLISE IA:** {intent.parsed_command}")

        # STEP 2: AI DECISION MAKING
        if intent.intent == "trade" and intent.action in ["buy", "sell"]:
            # TRADING DECISION
            symbol = intent.symbol
            volume = intent.volume

            if symbol and volume:
                # Get market data first for AI analysis
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    tick = mt5.symbol_info_tick(symbol)
                    account_info = mt5.account_info()

                    if tick:
                        price = tick.ask if intent.action == "buy" else tick.bid
                        balance = account_info.balance if account_info else 0

                        # AI RISK ANALYSIS
                        risk_analysis = f"""
💡 **ANÁLISE DE RISCO IA:**
• Ativo: {symbol} @ ${price:.5f}
• Volume: {volume} lots
• Exposição: ${(volume * price * symbol_info.margin_initial):.2f}
• Saldo disponível: ${balance:.2f}
• Margem necessária: {((volume * price * symbol_info.margin_initial) / balance * 100):.1f}%
"""

                        # AI STRATEGY SUGESTIONS
                        suggestions = []
                        if intent.action == "buy":
                            if volume > 0.5:
                                suggestions.append("⚠️ Volume alto - considere reduzir para 0.5 lots")
                            if tick.ask > symbol_info.session_high:
                                suggestions.append("📈 Preço próximo da máxima da sessão")
                        elif intent.action == "sell":
                            if volume > 0.5:
                                suggestions.append("⚠️ Volume alto - considere reduzir para 0.5 lots")
                            if tick.bid < symbol_info.session_low:
                                suggestions.append("📉 Preço próximo da mínima da sessão")

                        response_parts.append(risk_analysis.strip())

                        if suggestions:
                            response_parts.append("**💭 SOLICITAÇÕES DO IA:**\n" + "\n".join(f"• {s}" for s in suggestions))

                        # DECISION: Execute or confirm?
                        high_risk = volume > 1.0 or any(word in intent.parsed_command.lower() for word in ["urgente", "agora", "imediato"])
                        if high_risk:
                            response_parts.append("\n**🤔 IA RECOMENDA VERIFICAÇÃO:** Operação de alto risco detectada")
                            response_parts.append("**CONFIRMAR?** Envie 'ok' para executar ou 'cancelar' para abortar.")
                        else:
                            response_parts.append("**🤖 IA EXECUTANDO:** Ordem será executada automaticamente.")

                        # Set pending trade for confirmation
                        pending_trade = {
                            'symbol': symbol,
                            'volume': min(volume, 0.5),  # Safety limit
                            'tp_price': intent.take_profit,
                            'sl_price': intent.stop_loss,
                            'action': intent.action.upper()
                        }

                        # If low risk, auto-execute
                        if not high_risk:
                            pending_trade = None  # Clear pending
                            # Execute immediately
                            try:
                                trade_request = {
                                    "action": mt5.TRADE_ACTION_DEAL,
                                    "symbol": symbol,
                                    "volume": min(volume, 0.5),
                                    "type": mt5.ORDER_TYPE_BUY if intent.action == "buy" else mt5.ORDER_TYPE_SELL,
                                    "price": price,
                                    "sl": intent.stop_loss,
                                    "tp": intent.take_profit,
                                    "deviation": 10,
                                    "magic": 234000,
                                    "comment": "AI Trading Bot",
                                    "type_time": mt5.ORDER_TIME_GTC,
                                    "type_filling": mt5.ORDER_FILLING_IOC,
                                }

                                result = mt5.order_send(trade_request)
                                if result.retcode == mt5.TRADE_RETCODE_DONE:
                                    response_parts.append(f"\n✅ **ORDEM EXECUTADA COM SUCESSO!**")
                                    response_parts.append(f"🎯 Ticket: {result.order}")
                                    response_parts.append(f"💰 Preço: ${result.price:.5f}")
                                else:
                                    response_parts.append(f"\n❌ **EXECUÇÃO FALHOU:** {result.comment}")
                            except Exception as e:
                                response_parts.append(f"\n❌ **ERRO DE EXECUÇÃO:** {str(e)}")

                else:
                    response_parts.append("❌ Ativo não encontrado ou indisponível.")
            else:
                response_parts.append("❌ Parâmetros insuficientes para operação de trading.")

        elif intent.intent == "info" or intent.intent == "analysis":
            # INFORMATION/MARKET ANALYSIS REQUEST
            response_parts.append("📊 **ANÁLISE DE MERCADO IA:**")

            # Get market data for analysis
            if intent.symbol:
                symbol = intent.symbol
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        current_price = tick.last if tick.last > 0 else tick.ask
                        response_parts.append(f"🎯 **{symbol}** Atual: ${current_price:.5f}")

                        # Simple technical analysis placeholder
                        response_parts.append(f"📈 Max Sessão: ${symbol_info.session_high:.5f}")
                        response_parts.append(f"📉 Min Sessão: ${symbol_info.session_low:.5f}")

                        if intent.timeframe:
                            response_parts.append(f"🕐 Timeframe solicitado: {intent.timeframe}")
                        else:
                            response_parts.append("💡 Use timeframes: M1, M5, H1, D1, W1")

            else:
                # General market information
                response_parts.append("🌍 **MERCADO GERAL:**")
                response_parts.append("- Forex: EURUSD, GBPUSD, USDJPY")
                response_parts.append("- Crypto: BTCUSD, ETHUSD")
                response_parts.append("- Índices: SPX500, UK100")
                response_parts.append("\n💡 **DICAS IA:** Especifique um ativo para análise detalhada")

        elif intent.intent == "chat" or intent.intent == "other":
            # GENERAL CHAT RESPONSE
            async with OllamaClient() as ollama:
                chat_result = await ollama._request("POST", "/api/chat", json={
                    "model": "qwen2.5-coder",
                    "messages": [{
                        "role": "system",
                        "content": """You are an expert trading assistant AI. Provide helpful, accurate responses about trading, markets, and investment strategies. Be conversational but professional."""
                    }, {
                        "role": "user",
                        "content": message
                    }],
                    "stream": False
                })

                ai_response = chat_result.get("message", {}).get("content", "")
                response_parts.append(f"🤖 **IA:** {ai_response}")

        else:
            # FALLBACK RESPONSE
            response_parts.append("🤔 **IA PENSANDO:** Não entendi completamente sua solicitação.")
            response_parts.append("📝 **SUGESTÕES:** Tente frases como:")
            response_parts.append("• 'Comprar 0.1 EURUSD com stop loss 20 pips'")
            response_parts.append("• 'Qual o preço do BTCUSD?'")
            response_parts.append("• 'Análise do mercado forex'")

        # COMBINE ALL RESPONSE PARTS
        final_response = "\n".join(response_parts)

        return {
            "response": final_response,
            "intent": intent.model_dump() if hasattr(intent, 'model_dump') else intent.__dict__,
            "result": {"status": "success", "message": "AI analysis completed"},
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        error_msg = f"❌ **ERRO IA:** {str(e)}"
        logger.error(f"AI message processing failed: {e}")
        return {
            "response": error_msg,
            "intent": {"intent": "error", "confidence": 0.0},
            "result": {"status": "error", "message": str(e)},
            "timestamp": datetime.now().isoformat()
        }
