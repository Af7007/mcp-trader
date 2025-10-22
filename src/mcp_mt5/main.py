import logging
from datetime import datetime
from typing import Any

import MetaTrader5 as mt5
import pandas as pd
from fastmcp import FastMCP
from pydantic import BaseModel

from core.mt5_connection import mt5_connection
from core.exceptions import MT5ConnectionError, MT5InitializationError, MT5LoginError

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "MetaTrader 5 MCP Server",
    instructions="""
    This server is used to control MetaTrader 5 terminal.
    It provides a simple interface to interact with MetaTrader 5 terminal.
    """,
)


# Models for request/response data
class SymbolInfo(BaseModel):
    """Information about a trading symbol"""

    name: str
    description: str | None = None
    path: str | None = None
    session_deals: int | None = None
    session_buy_orders: int | None = None
    session_sell_orders: int | None = None
    volume: float | None = None
    volumehigh: float | None = None
    volumelow: float | None = None
    time: int | None = None
    digits: int | None = None
    spread: int | None = None
    spread_float: bool | None = None
    trade_calc_mode: int | None = None
    trade_mode: int | None = None
    start_time: int | None = None
    expiration_time: int | None = None
    trade_stops_level: int | None = None
    trade_freeze_level: int | None = None
    trade_exemode: int | None = None
    swap_mode: int | None = None
    swap_rollover3days: int | None = None
    margin_hedged_use_leg: bool | None = None
    expiration_mode: int | None = None
    filling_mode: int | None = None
    order_mode: int | None = None
    order_gtc_mode: int | None = None
    option_mode: int | None = None
    option_right: int | None = None
    bid: float | None = None
    bidhigh: float | None = None
    bidlow: float | None = None
    ask: float | None = None
    askhigh: float | None = None
    asklow: float | None = None
    last: float | None = None
    lasthigh: float | None = None
    lastlow: float | None = None
    point: float | None = None
    tick_value: float | None = None
    tick_value_profit: float | None = None
    tick_value_loss: float | None = None
    tick_size: float | None = None
    contract_size: float | None = None
    volume_min: float | None = None
    volume_max: float | None = None
    volume_step: float | None = None
    swap_long: float | None = None
    swap_short: float | None = None
    margin_initial: float | None = None
    margin_maintenance: float | None = None


class AccountInfo(BaseModel):
    """Trading account information"""

    login: int
    trade_mode: int
    leverage: int
    limit_orders: int
    margin_so_mode: int
    trade_allowed: bool
    trade_expert: bool
    margin_mode: int
    currency_digits: int
    fifo_close: bool
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float
    name: str
    server: str
    currency: str
    company: str


class OrderRequest(BaseModel):
    """Order request parameters"""

    action: int
    symbol: str
    volume: float
    type: int
    price: float
    sl: float | None = None
    tp: float | None = None
    deviation: int | None = None
    magic: int | None = None
    comment: str | None = None
    type_time: int | None = None
    type_filling: int | None = None


class OrderResult(BaseModel):
    """Order execution result"""

    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int
    request: dict[str, Any]


class Position(BaseModel):
    """Trading position information"""

    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: int
    magic: int
    identifier: int
    reason: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str


class HistoryOrder(BaseModel):
    """Historical order information"""

    ticket: int
    time_setup: int
    time_setup_msc: int
    time_expiration: int
    type: int
    type_time: int
    type_filling: int
    state: int
    magic: int
    position_id: int
    position_by_id: int
    reason: int
    volume_initial: float
    volume_current: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    price_stoplimit: float
    symbol: str
    comment: str
    external_id: str


class Deal(BaseModel):
    """Deal information"""

    ticket: int
    order: int
    time: int
    time_msc: int
    type: int
    entry: int
    magic: int
    position_id: int
    reason: int
    volume: float
    price: float
    commission: float
    swap: float
    profit: float
    fee: float
    symbol: str
    comment: str
    external_id: str


timeframe_map = {
    # Minutes
    1: mt5.TIMEFRAME_M1,  # 1 minute
    2: mt5.TIMEFRAME_M2,  # 2 minutes
    3: mt5.TIMEFRAME_M3,  # 3 minutes
    4: mt5.TIMEFRAME_M4,  # 4 minutes
    5: mt5.TIMEFRAME_M5,  # 5 minutes
    6: mt5.TIMEFRAME_M6,  # 6 minutes
    10: mt5.TIMEFRAME_M10,  # 10 minutes
    12: mt5.TIMEFRAME_M12,  # 12 minutes
    15: mt5.TIMEFRAME_M15,  # 15 minutes
    20: mt5.TIMEFRAME_M20,  # 20 minutes
    30: mt5.TIMEFRAME_M30,  # 30 minutes
    # Hours
    60: mt5.TIMEFRAME_H1,  # 1 hour
    120: mt5.TIMEFRAME_H2,  # 2 hours
    180: mt5.TIMEFRAME_H3,  # 3 hours
    240: mt5.TIMEFRAME_H4,  # 4 hours
    360: mt5.TIMEFRAME_H6,  # 6 hours
    480: mt5.TIMEFRAME_H8,  # 8 hours
    720: mt5.TIMEFRAME_H12,  # 12 hours
    # Days/Weeks/Months
    1440: mt5.TIMEFRAME_D1,  # 1 day
    10080: mt5.TIMEFRAME_W1,  # 1 week
    43200: mt5.TIMEFRAME_MN1,  # 1 month
}


def get_timeframe_constant(timeframe: int) -> int:
    """
    Convert user-friendly timeframe integer to MT5 constant with validation.

    Args:
        timeframe: Timeframe in minutes (e.g., 60 for H1)

    Returns:
        MT5 timeframe constant

    Raises:
        ValueError: If timeframe is not supported
    """
    if timeframe not in timeframe_map:
        supported = ", ".join(str(k) for k in sorted(timeframe_map.keys()))
        raise ValueError(
            f"Unsupported timeframe: {timeframe}. Supported timeframes (in minutes): {supported}"
        )
    return timeframe_map[timeframe]


# Initialize MetaTrader 5 connection
@mcp.tool()
def initialize(path: str) -> bool:
    """
    Initialize the MetaTrader 5 terminal.

    Args:
        path: Path to the MetaTrader 5 terminal executable

    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    try:
        # Initialize MT5 using the connection manager
        result = mt5.initialize(path=path)
        if not result:
            error_code, error_msg = mt5.last_error()
            logger.error(f"MT5 initialization failed: {error_msg} (code: {error_code})")
            return False

        logger.info("MT5 initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize MT5: {e}")
        return False


# Shutdown MetaTrader 5 connection
@mcp.tool()
def shutdown() -> bool:
    """
    Shut down the connection to the MetaTrader 5 terminal.

    Returns:
        bool: True if shutdown was successful.
    """
    try:
        mt5.shutdown()
        logger.info("MT5 connection shut down")
        return True
    except Exception as e:
        logger.error(f"Failed to shutdown MT5: {e}")
        return False


# Login to MetaTrader 5 account
@mcp.tool()
def login(login: int, password: str, server: str) -> bool:
    """
    Log in to the MetaTrader 5 trading account.

    Args:
        login: Trading account number
        password: Trading account password
        server: Trading server name

    Returns:
        bool: True if login was successful, False otherwise.
    """
    try:
        # Use the connection manager for login
        result = mt5.login(login=login, password=password, server=server)
        if not result:
            error_code, error_msg = mt5.last_error()
            logger.error(f"MT5 login failed: {error_msg} (code: {error_code})")
            return False

        logger.info(f"MT5 login successful to account #{login} on server {server}")
        return True

    except Exception as e:
        logger.error(f"Failed to login to MT5: {e}")
        return False


# Get account information
@mcp.tool()
def get_account_info() -> AccountInfo:
    """
    Get information about the current trading account.

    Returns:
        AccountInfo: Information about the trading account.
    """
    try:
        account_info = mt5.account_info()
        if account_info is None:
            error_code, error_msg = mt5.last_error()
            logger.error(f"Failed to get account info: {error_msg} (code: {error_code})")
            raise ValueError("Failed to get account info")

        # Convert named tuple to dictionary
        account_dict = account_info._asdict()
        return AccountInfo(**account_dict)

    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise ValueError(f"Error getting account info: {e}")


# Get terminal information
@mcp.tool()
def get_terminal_info() -> dict[str, Any]:
    """
    Get information about the MetaTrader 5 terminal.

    Returns:
        Dict[str, Any]: Information about the terminal.
    """
    try:
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            error_code, error_msg = mt5.last_error()
            logger.error(f"Failed to get terminal info: {error_msg} (code: {error_code})")
            raise ValueError("Failed to get terminal info")

        # Convert named tuple to dictionary
        return terminal_info._asdict()

    except Exception as e:
        logger.error(f"Error getting terminal info: {e}")
        raise ValueError(f"Error getting terminal info: {e}")


# Get version information
@mcp.tool()
def get_version() -> dict[str, Any]:
    """
    Get the MetaTrader 5 version.

    Returns:
        Dict[str, Any]: Version information.
    """
    version = mt5.version()
    if version is None:
        logger.error(f"Failed to get version, error code: {mt5.last_error()}")
        raise ValueError("Failed to get version")

    return {"version": version[0], "build": version[1], "date": version[2]}


# Get symbols
@mcp.tool()
def get_symbols() -> list[str]:
    """
    Get all available symbols (financial instruments) from the MetaTrader 5 terminal.

    Returns:
        List[str]: List of symbol names.
    """
    symbols = mt5.symbols_get()
    if symbols is None:
        logger.error(f"Failed to get symbols, error code: {mt5.last_error()}")
        raise ValueError("Failed to get symbols")

    return [symbol.name for symbol in symbols]


# Get symbols by group
@mcp.tool()
def get_symbols_by_group(group: str) -> list[str]:
    """
    Get symbols that match a specific group or pattern.

    Args:
        group: Filter for arranging a group of symbols (e.g., "*", "EUR*", etc.)

    Returns:
        List[str]: List of symbol names that match the group.
    """
    symbols = mt5.symbols_get(group=group)
    if symbols is None:
        logger.error(f"Failed to get symbols for group {group}, error code: {mt5.last_error()}")
        return []

    return [symbol.name for symbol in symbols]


# Get symbol information
@mcp.tool()
def get_symbol_info(symbol: str) -> SymbolInfo:
    """
    Get information about a specific symbol.

    Args:
        symbol: Symbol name

    Returns:
        SymbolInfo: Information about the symbol.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Failed to get info for symbol {symbol}, error code: {mt5.last_error()}")
        raise ValueError(f"Failed to get info for symbol {symbol}")

    # Convert named tuple to dictionary
    symbol_dict = symbol_info._asdict()
    return SymbolInfo(**symbol_dict)


# Get symbol tick information
@mcp.tool()
def get_symbol_info_tick(symbol: str) -> dict[str, Any]:
    """
    Get the latest tick data for a symbol.

    Args:
        symbol: Symbol name

    Returns:
        Dict[str, Any]: Latest tick data for the symbol.
    """
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"Failed to get tick for symbol {symbol}, error code: {mt5.last_error()}")
        raise ValueError(f"Failed to get tick for symbol {symbol}")

    # Convert named tuple to dictionary
    return tick._asdict()


# Select symbol in Market Watch
@mcp.tool()
def symbol_select(symbol: str, visible: bool = True) -> bool:
    """
    Select a symbol in the Market Watch window or remove a symbol from it.

    Args:
        symbol: Symbol name
        visible: Symbol visibility flag
            - True: Make the symbol visible in Market Watch
            - False: Hide the symbol from Market Watch

    Returns:
        bool: True if the symbol is selected successfully, False otherwise.
    """
    result = mt5.symbol_select(symbol, visible)
    if not result:
        logger.error(f"Failed to select symbol {symbol}, error code: {mt5.last_error()}")

    return result


# Copy rates from position
@mcp.tool()
def copy_rates_from_pos(
    symbol: str, timeframe: int, start_pos: int, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a specified symbol and timeframe starting from the specified position.

    Args:
        symbol: Symbol name
        timeframe: Timeframe as specified in TIMEFRAME_* constants:
            - 1: TIMEFRAME_M1 (1 minute)
            - 5: TIMEFRAME_M5 (5 minutes)
            - 15: TIMEFRAME_M15 (15 minutes)
            - 30: TIMEFRAME_M30 (30 minutes)
            - 60: TIMEFRAME_H1 (1 hour)
            - 240: TIMEFRAME_H4 (4 hours)
            - 1440: TIMEFRAME_D1 (1 day)
            - 10080: TIMEFRAME_W1 (1 week)
            - 43200: TIMEFRAME_MN1 (1 month)
        start_pos: Initial position for bar retrieval
        count: Number of bars to retrieve

    Returns:
        List[Dict[str, Any]]: List of bars with time, open, high, low, close, tick_volume, spread, and real_volume.
    """
    rates = mt5.copy_rates_from_pos(symbol, get_timeframe_constant(timeframe), start_pos, count)
    if rates is None:
        logger.error(f"Failed to copy rates for {symbol}, error code: {mt5.last_error()}")
        raise ValueError(f"Failed to copy rates for {symbol}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(rates)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")

    return df.to_dict("records")


# Copy rates from date
@mcp.tool()
def copy_rates_from_date(
    symbol: str, timeframe: int, date_from: datetime, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a specified symbol and timeframe starting from the specified date.

    Args:
        symbol: Symbol name
        timeframe: Timeframe (use TIMEFRAME_* constants)
        date_from: Start date for bar retrieval
        count: Number of bars to retrieve

    Returns:
        List[Dict[str, Any]]: List of bars with time, open, high, low, close, tick_volume, spread, and real_volume.
    """
    rates = mt5.copy_rates_from_date(symbol, get_timeframe_constant(timeframe), date_from, count)
    if rates is None:
        logger.error(
            f"Failed to copy rates for {symbol} from date {date_from}, error code: {mt5.last_error()}"
        )
        raise ValueError(f"Failed to copy rates for {symbol} from date {date_from}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(rates)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")

    return df.to_dict("records")


# Copy rates range
@mcp.tool()
def copy_rates_range(
    symbol: str, timeframe: int, date_from: datetime, date_to: datetime
) -> list[dict[str, Any]]:
    """
    Get bars from a specified symbol and timeframe within the specified date range.

    Args:
        symbol: Symbol name
        timeframe: Timeframe (use TIMEFRAME_* constants)
        date_from: Start date for bar retrieval
        date_to: End date for bar retrieval

    Returns:
        List[Dict[str, Any]]: List of bars with time, open, high, low, close, tick_volume, spread, and real_volume.
    """
    rates = mt5.copy_rates_range(symbol, get_timeframe_constant(timeframe), date_from, date_to)
    if rates is None:
        logger.error(
            f"Failed to copy rates for {symbol} in range {date_from} to {date_to}, error code: {mt5.last_error()}"
        )
        raise ValueError(f"Failed to copy rates for {symbol} in range {date_from} to {date_to}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(rates)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")

    return df.to_dict("records")


# Copy ticks from position
@mcp.tool()
def copy_ticks_from_pos(
    symbol: str, start_time: datetime, count: int, flags: int = mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a specified symbol starting from the specified position.

    Args:
        symbol: Symbol name
        start_time: Initial time for tick retrieval
        count: Number of ticks to retrieve
        flags: Type of requested ticks:
            - mt5.COPY_TICKS_ALL: All ticks (default)
            - mt5.COPY_TICKS_INFO: Ticks containing bid and/or ask price changes
            - mt5.COPY_TICKS_TRADE: Ticks containing last price and volume changes

    Returns:
        List[Dict[str, Any]]: List of ticks.
    """
    ticks = mt5.copy_ticks_from(symbol, start_time, count, flags)
    if ticks is None:
        logger.error(f"Failed to copy ticks for {symbol}, error code: {mt5.last_error()}")
        raise ValueError(f"Failed to copy ticks for {symbol}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(ticks)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")
    if "time_msc" in df.columns:
        df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

    return df.to_dict("records")


# Copy ticks from date
@mcp.tool()
def copy_ticks_from_date(
    symbol: str, date_from: datetime, count: int, flags: int = mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a specified symbol starting from the specified date.

    Args:
        symbol: Symbol name
        date_from: Start date for tick retrieval
        count: Number of ticks to retrieve
        flags: Type of requested ticks

    Returns:
        List[Dict[str, Any]]: List of ticks.
    """
    ticks = mt5.copy_ticks_from(symbol, date_from, count, flags)
    if ticks is None:
        logger.error(
            f"Failed to copy ticks for {symbol} from date {date_from}, error code: {mt5.last_error()}"
        )
        raise ValueError(f"Failed to copy ticks for {symbol} from date {date_from}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(ticks)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")
    if "time_msc" in df.columns:
        df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

    return df.to_dict("records")


# Copy ticks range
@mcp.tool()
def copy_ticks_range(
    symbol: str, date_from: datetime, date_to: datetime, flags: int = mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a specified symbol within the specified date range.

    Args:
        symbol: Symbol name
        date_from: Start date for tick retrieval
        date_to: End date for tick retrieval
        flags: Type of requested ticks

    Returns:
        List[Dict[str, Any]]: List of ticks.
    """
    ticks = mt5.copy_ticks_range(symbol, date_from, date_to, flags)
    if ticks is None:
        logger.error(
            f"Failed to copy ticks for {symbol} in range {date_from} to {date_to}, error code: {mt5.last_error()}"
        )
        raise ValueError(f"Failed to copy ticks for {symbol} in range {date_from} to {date_to}")

    # Convert numpy array to list of dictionaries
    df = pd.DataFrame(ticks)
    # Convert time to datetime
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], unit="s")
    if "time_msc" in df.columns:
        df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

    return df.to_dict("records")


# Get last error
@mcp.tool()
def get_last_error() -> dict[str, Any]:
    """
    Get the last error code and description.

    Returns:
        Dict[str, Any]: Last error code and description.
    """
    error_code, error_message = mt5.last_error()

    error_descriptions = {
        mt5.RES_S_OK: "OK",
        mt5.RES_E_FAIL: "Generic fail",
        mt5.RES_E_INVALID_PARAMS: "Invalid parameters",
        mt5.RES_E_NO_MEMORY: "No memory",
        mt5.RES_E_NOT_FOUND: "Not found",
        mt5.RES_E_INVALID_VERSION: "Invalid version",
        mt5.RES_E_AUTH_FAILED: "Authorization failed",
        mt5.RES_E_UNSUPPORTED: "Unsupported method",
        mt5.RES_E_AUTO_TRADING_DISABLED: "Auto-trading disabled",
        mt5.RES_E_INTERNAL_FAIL: "Internal failure",
        mt5.RES_E_DONE: "Request completed",
        mt5.RES_E_CANCELED: "Request canceled",
    }

    error_description = error_descriptions.get(error_code, error_message or "Unknown error")

    return {"code": error_code, "description": error_description}


# Resource for timeframe constants
@mcp.resource("mt5://timeframes")
def get_timeframes() -> str:
    """
    Get information about available timeframes in MetaTrader 5.

    Returns:
        str: Information about available timeframes.
    """
    timeframes = {
        "TIMEFRAME_M1": 1,
        "TIMEFRAME_M2": 2,
        "TIMEFRAME_M3": 3,
        "TIMEFRAME_M4": 4,
        "TIMEFRAME_M5": 5,
        "TIMEFRAME_M6": 6,
        "TIMEFRAME_M10": 10,
        "TIMEFRAME_M12": 12,
        "TIMEFRAME_M15": 15,
        "TIMEFRAME_M20": 20,
        "TIMEFRAME_M30": 30,
        "TIMEFRAME_H1": 60,
        "TIMEFRAME_H2": 120,
        "TIMEFRAME_H3": 180,
        "TIMEFRAME_H4": 240,
        "TIMEFRAME_H6": 360,
        "TIMEFRAME_H8": 480,
        "TIMEFRAME_H12": 720,
        "TIMEFRAME_D1": 1440,
        "TIMEFRAME_W1": 10080,
        "TIMEFRAME_MN1": 43200,
    }

    result = "Available timeframes in MetaTrader 5:\n\n"
    for name, value in timeframes.items():
        result += f"{name}: {value}\n"

    return result


# Resource for tick flag constants
@mcp.resource("mt5://tick_flags")
def get_tick_flags() -> str:
    """
    Get information about tick flags in MetaTrader 5.

    Returns:
        str: Information about tick flags.
    """
    tick_flags = {
        "COPY_TICKS_ALL": mt5.COPY_TICKS_ALL,
        "COPY_TICKS_INFO": mt5.COPY_TICKS_INFO,
        "COPY_TICKS_TRADE": mt5.COPY_TICKS_TRADE,
    }

    result = "Available tick flags in MetaTrader 5:\n\n"
    for name, value in tick_flags.items():
        result += f"{name}: {value}\n"

    return result


# Send order
@mcp.tool()
def order_send(request: OrderRequest) -> OrderResult:
    """
    Send an order to the trade server.

    Args:
        request: Order parameters

    Returns:
        OrderResult: Order execution result.
    """
    try:
        # Convert request to dictionary
        request_dict = request.model_dump()

        # Send order
        result = mt5.order_send(request_dict)
        if result is None:
            error_code, error_msg = mt5.last_error()
            logger.error(f"Failed to send order: {error_msg} (code: {error_code})")
            raise ValueError("Failed to send order")

        # Convert named tuple to dictionary
        result_dict = result._asdict()

        # Convert request named tuple to dictionary if needed
        if hasattr(result_dict["request"], "_asdict"):
            result_dict["request"] = result_dict["request"]._asdict()

        return OrderResult(**result_dict)

    except Exception as e:
        logger.error(f"Error sending order: {e}")
        raise ValueError(f"Error sending order: {e}")


# Check order
@mcp.tool()
def order_check(request: OrderRequest) -> dict[str, Any]:
    """
    Check if an order can be placed with the specified parameters.

    Args:
        request: Order parameters

    Returns:
        Dict[str, Any]: Order check result.
    """
    try:
        # Convert request to dictionary
        request_dict = request.model_dump()

        # Check order
        result = mt5.order_check(request_dict)
        if result is None:
            error_code, error_msg = mt5.last_error()
            logger.error(f"Failed to check order: {error_msg} (code: {error_code})")
            raise ValueError("Failed to check order")

        # Convert named tuple to dictionary
        result_dict = result._asdict()

        # Convert request named tuple to dictionary if needed
        if hasattr(result_dict["request"], "_asdict"):
            result_dict["request"] = result_dict["request"]._asdict()

        return result_dict

    except Exception as e:
        logger.error(f"Error checking order: {e}")
        raise ValueError(f"Error checking order: {e}")


# Get positions
@mcp.tool()
def positions_get(symbol: str | None = None, group: str | None = None) -> list[Position]:
    """
    Get open positions.

    Args:
        symbol: Symbol name. If specified, only positions for this symbol will be returned.
        group: Filter for arranging a group of positions (e.g., "*", "USD*", etc.)

    Returns:
        List[Position]: List of open positions.
    """
    if symbol is not None:
        positions = mt5.positions_get(symbol=symbol)
    elif group is not None:
        positions = mt5.positions_get(group=group)
    else:
        positions = mt5.positions_get()

    if positions is None:
        logger.error(f"Failed to get positions, error code: {mt5.last_error()}")
        return []

    result = []
    for position in positions:
        # Convert named tuple to dictionary
        position_dict = position._asdict()
        result.append(Position(**position_dict))

    return result


# Get position by ticket
@mcp.tool()
def positions_get_by_ticket(ticket: int) -> Position | None:
    """
    Get an open position by its ticket.

    Args:
        ticket: Position ticket

    Returns:
        Optional[Position]: Position information or None if not found.
    """
    position = mt5.positions_get(ticket=ticket)
    if position is None or len(position) == 0:
        logger.error(f"Failed to get position with ticket {ticket}, error code: {mt5.last_error()}")
        return None

    # Convert named tuple to dictionary
    position_dict = position[0]._asdict()
    return Position(**position_dict)


# Get orders
@mcp.tool()
def orders_get(symbol: str | None = None, group: str | None = None) -> list[dict[str, Any]]:
    """
    Get active orders.

    Args:
        symbol: Symbol name. If specified, only orders for this symbol will be returned.
        group: Filter for arranging a group of orders (e.g., "*", "USD*", etc.)

    Returns:
        List[Dict[str, Any]]: List of active orders.
    """
    if symbol is not None:
        orders = mt5.orders_get(symbol=symbol)
    elif group is not None:
        orders = mt5.orders_get(group=group)
    else:
        orders = mt5.orders_get()

    if orders is None:
        logger.error(f"Failed to get orders, error code: {mt5.last_error()}")
        return []

    result = []
    for order in orders:
        # Convert named tuple to dictionary
        order_dict = order._asdict()
        result.append(order_dict)

    return result


# Get order by ticket
@mcp.tool()
def orders_get_by_ticket(ticket: int) -> dict[str, Any] | None:
    """
    Get an active order by its ticket.

    Args:
        ticket: Order ticket

    Returns:
        Optional[Dict[str, Any]]: Order information or None if not found.
    """
    order = mt5.orders_get(ticket=ticket)
    if order is None or len(order) == 0:
        logger.error(f"Failed to get order with ticket {ticket}, error code: {mt5.last_error()}")
        return None

    # Convert named tuple to dictionary
    return order[0]._asdict()


# Get history orders
@mcp.tool()
def history_orders_get(
    symbol: str | None = None,
    group: str | None = None,
    ticket: int | None = None,
    position: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[HistoryOrder]:
    """
    Get orders from history within the specified date range.

    Args:
        symbol: Symbol name
        group: Filter for arranging a group of orders
        ticket: Order ticket
        position: Position ticket
        from_date: Start date for order retrieval
        to_date: End date for order retrieval

    Returns:
        List[HistoryOrder]: List of historical orders.
    """
    request = {}
    if symbol is not None:
        request["symbol"] = symbol
    if group is not None:
        request["group"] = group
    if ticket is not None:
        request["ticket"] = ticket
    if position is not None:
        request["position"] = position
    if from_date is not None:
        request["from"] = from_date
    if to_date is not None:
        request["to"] = to_date

    # Get history orders
    if request:
        orders = mt5.history_orders_get(**request)
    else:
        orders = mt5.history_orders_get()

    if orders is None:
        logger.error(f"Failed to get history orders, error code: {mt5.last_error()}")
        return []

    result = []
    for order in orders:
        # Convert named tuple to dictionary
        order_dict = order._asdict()
        result.append(HistoryOrder(**order_dict))

    return result


# Get history deals
@mcp.tool()
def history_deals_get(
    symbol: str | None = None,
    group: str | None = None,
    ticket: int | None = None,
    position: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[Deal]:
    """
    Get deals from history within the specified date range.

    Args:
        symbol: Symbol name
        group: Filter for arranging a group of deals
        ticket: Deal ticket
        position: Position ticket
        from_date: Start date for deal retrieval
        to_date: End date for deal retrieval

    Returns:
        List[Deal]: List of historical deals.
    """
    request = {}
    if symbol is not None:
        request["symbol"] = symbol
    if group is not None:
        request["group"] = group
    if ticket is not None:
        request["ticket"] = ticket
    if position is not None:
        request["position"] = position
    if from_date is not None:
        request["from"] = from_date
    if to_date is not None:
        request["to"] = to_date

    # Get history deals
    if request:
        deals = mt5.history_deals_get(**request)
    else:
        deals = mt5.history_deals_get()

    if deals is None:
        logger.error(f"Failed to get history deals, error code: {mt5.last_error()}")
        return []

    result = []
    for deal in deals:
        # Convert named tuple to dictionary
        deal_dict = deal._asdict()
        result.append(Deal(**deal_dict))

    return result


# Resource for order types
@mcp.resource("mt5://order_types")
def get_order_types() -> str:
    """
    Get information about order types in MetaTrader 5.

    Returns:
        str: Information about order types.
    """
    order_types = {
        "ORDER_TYPE_BUY": mt5.ORDER_TYPE_BUY,
        "ORDER_TYPE_SELL": mt5.ORDER_TYPE_SELL,
        "ORDER_TYPE_BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT,
        "ORDER_TYPE_SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT,
        "ORDER_TYPE_BUY_STOP": mt5.ORDER_TYPE_BUY_STOP,
        "ORDER_TYPE_SELL_STOP": mt5.ORDER_TYPE_SELL_STOP,
        "ORDER_TYPE_BUY_STOP_LIMIT": mt5.ORDER_TYPE_BUY_STOP_LIMIT,
        "ORDER_TYPE_SELL_STOP_LIMIT": mt5.ORDER_TYPE_SELL_STOP_LIMIT,
        "ORDER_TYPE_CLOSE_BY": mt5.ORDER_TYPE_CLOSE_BY,
    }

    result = "Available order types in MetaTrader 5:\n\n"
    for name, value in order_types.items():
        result += f"{name}: {value}\n"

    return result


# Resource for order filling types
@mcp.resource("mt5://order_filling_types")
def get_order_filling_types() -> str:
    """
    Get information about order filling types in MetaTrader 5.

    Returns:
        str: Information about order filling types.
    """
    filling_types = {
        "ORDER_FILLING_FOK": mt5.ORDER_FILLING_FOK,
        "ORDER_FILLING_IOC": mt5.ORDER_FILLING_IOC,
        "ORDER_FILLING_RETURN": mt5.ORDER_FILLING_RETURN,
    }

    result = "Available order filling types in MetaTrader 5:\n\n"
    for name, value in filling_types.items():
        result += f"{name}: {value}\n"

    return result


# Resource for order time types
@mcp.resource("mt5://order_time_types")
def get_order_time_types() -> str:
    """
    Get information about order time types in MetaTrader 5.

    Returns:
        str: Information about order time types.
    """
    time_types = {
        "ORDER_TIME_GTC": mt5.ORDER_TIME_GTC,
        "ORDER_TIME_DAY": mt5.ORDER_TIME_DAY,
        "ORDER_TIME_SPECIFIED": mt5.ORDER_TIME_SPECIFIED,
        "ORDER_TIME_SPECIFIED_DAY": mt5.ORDER_TIME_SPECIFIED_DAY,
    }

    result = "Available order time types in MetaTrader 5:\n\n"
    for name, value in time_types.items():
        result += f"{name}: {value}\n"

    return result


# Resource for trade request actions
@mcp.resource("mt5://trade_actions")
def get_trade_actions() -> str:
    """
    Get information about trade request actions in MetaTrader 5.

    Returns:
        str: Information about trade request actions.
    """
    actions = {
        "TRADE_ACTION_DEAL": mt5.TRADE_ACTION_DEAL,
        "TRADE_ACTION_PENDING": mt5.TRADE_ACTION_PENDING,
        "TRADE_ACTION_SLTP": mt5.TRADE_ACTION_SLTP,
        "TRADE_ACTION_MODIFY": mt5.TRADE_ACTION_MODIFY,
        "TRADE_ACTION_REMOVE": mt5.TRADE_ACTION_REMOVE,
        "TRADE_ACTION_CLOSE_BY": mt5.TRADE_ACTION_CLOSE_BY,
    }

    result = "Available trade request actions in MetaTrader 5:\n\n"
    for name, value in actions.items():
        result += f"{name}: {value}\n"

    return result


# Buy market order
@mcp.tool()
def buy_market(symbol: str, volume: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a market buy order.

    Args:
        symbol: Symbol name
        volume: Volume to buy
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask if mt5.symbol_info_tick(symbol) else 0,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Sell market order
@mcp.tool()
def sell_market(symbol: str, volume: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a market sell order.

    Args:
        symbol: Symbol name
        volume: Volume to sell
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol).bid if mt5.symbol_info_tick(symbol) else 0,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Close position by ticket
@mcp.tool()
def close_position(ticket: int, volume: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Close a position by ticket number.

    Args:
        ticket: Position ticket number
        volume: Volume to close (optional, if None closes entire position)
        comment: Close comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    position = positions_get_by_ticket(ticket)
    if position is None:
        raise ValueError(f"Position with ticket {ticket} not found")

    close_volume = volume if volume is not None else position.volume

    # Determine order type based on position type
    if position.type == mt5.POSITION_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(position.symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).ask

    if price is None:
        raise ValueError(f"Could not get price for symbol {position.symbol}")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": close_volume,
        "type": order_type,
        "price": price,
        "position": position.ticket,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Close all positions for a symbol
@mcp.tool()
def close_positions_by_symbol(symbol: str, comment: str | None = None) -> list[OrderResult]:
    """
    Close all positions for a specific symbol.

    Args:
        symbol: Symbol name
        comment: Close comment (optional)

    Returns:
        List[OrderResult]: List of order execution results.
    """
    positions = positions_get(symbol=symbol)
    results = []

    for position in positions:
        try:
            result = close_position(position.ticket, None, comment)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to close position {position.ticket}: {e}")
            continue

    return results


# Close all positions
@mcp.tool()
def close_all_positions(comment: str | None = None) -> list[OrderResult]:
    """
    Close all open positions.

    Args:
        comment: Close comment (optional)

    Returns:
        List[OrderResult]: List of order execution results.
    """
    positions = positions_get()
    results = []

    for position in positions:
        try:
            result = close_position(position.ticket, None, comment)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to close position {position.ticket}: {e}")
            continue

    return results


# Modify position stop loss and take profit
@mcp.tool()
def modify_position(ticket: int, sl: float | None = None, tp: float | None = None) -> OrderResult:
    """
    Modify stop loss and/or take profit of a position.

    Args:
        ticket: Position ticket number
        sl: New Stop Loss price (optional)
        tp: New Take Profit price (optional)

    Returns:
        OrderResult: Order execution result.
    """
    position = positions_get_by_ticket(ticket)
    if position is None:
        raise ValueError(f"Position with ticket {ticket} not found")

    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": position.symbol,
        "sl": sl if sl is not None else position.sl,
        "tp": tp if tp is not None else position.tp,
        "position": position.ticket,
    }

    return order_send(OrderRequest(**request))


# Cancel pending order by ticket
@mcp.tool()
def cancel_order(ticket: int) -> OrderResult:
    """
    Cancel a pending order by ticket number.

    Args:
        ticket: Order ticket number

    Returns:
        OrderResult: Order execution result.
    """
    order = orders_get_by_ticket(ticket)
    if order is None:
        raise ValueError(f"Order with ticket {ticket} not found")

    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": order["ticket"],
    }

    return order_send(OrderRequest(**request))


# Place limit buy order
@mcp.tool()
def buy_limit(symbol: str, volume: float, price: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a buy limit order.

    Args:
        symbol: Symbol name
        volume: Volume to buy
        price: Limit price
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Place limit sell order
@mcp.tool()
def sell_limit(symbol: str, volume: float, price: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a sell limit order.

    Args:
        symbol: Symbol name
        volume: Volume to sell
        price: Limit price
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Place stop buy order
@mcp.tool()
def buy_stop(symbol: str, volume: float, price: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a buy stop order.

    Args:
        symbol: Symbol name
        volume: Volume to buy
        price: Stop price
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_STOP,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


# Place stop sell order
@mcp.tool()
def sell_stop(symbol: str, volume: float, price: float, sl: float | None = None, tp: float | None = None, comment: str | None = None) -> OrderResult:
    """
    Place a sell stop order.

    Args:
        symbol: Symbol name
        volume: Volume to sell
        price: Stop price
        sl: Stop Loss price (optional)
        tp: Take Profit price (optional)
        comment: Order comment (optional)

    Returns:
        OrderResult: Order execution result.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_STOP,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 0,
        "comment": comment or "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    return order_send(OrderRequest(**request))


@mcp.tool()
def health() -> dict[str, Any]:
    """Health check for MT5 MCP server"""
    try:
        # Quick test if MT5 terminal is accessible
        version = get_version()
        return {
            "status": "ok",
            "service": "MT5 MCP Server",
            "version": version,
            "port": 8000
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "MT5 MCP Server",
            "error": str(e),
            "port": 8000
        }


if __name__ == "__main__":
    import os

    # Check if running in MCP mode
    if os.getenv("MT5_MCP_TRANSPORT") == "stdio":
        # Running as MCP server via stdio
        mcp.run()
    else:
        # Running standalone - just print info
        print("MetaTrader 5 MCP Server")
        print("Set MT5_MCP_TRANSPORT=stdio to run as MCP server")
