# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MetaTrader 5 (MT5) MCP Server that provides AI assistants access to the MetaTrader 5 trading platform through the Model Context Protocol. The project includes:

- **MCP Server**: FastMCP-based server for MT5 terminal integration
- **Trading Chatbot**: Conversational interface for trading operations
- **Agent System**: Automated trading agents with lifecycle management
- **Web Interface**: Flask-based dashboard for agent management
- **Database**: SQLite persistence for trade history and agent state

## Development Setup

### Installation and Environment

```bash
# Install dependencies
uv sync

# Install with test dependencies
uv sync --extra dev

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### Quick Start - Running All Services

**IMPORTANT**: Make sure MetaTrader 5 terminal is open and logged in before starting!

**Option 1: Automatic (Recommended)**
```batch
START_ALL_SERVICES.bat
```
This starts:
- MT5 MCP Server (port 8000)
- Web Dashboard (port 3000)
- Worker Service (background)

**Option 2: Manual - Open 3 separate terminals**

Terminal 1 - MT5 MCP Server:
```bash
python start_mt5_http.py
```

Terminal 2 - Web Dashboard:
```bash
python run_simple_web.py
```

Terminal 3 - Worker (optional):
```bash
python src/core/main.py
```

**Access the dashboard**: http://localhost:3000

### Stopping All Services

```batch
STOP_ALL_SERVICES.bat
```
Or manually: `taskkill /F /IM python.exe`

### Running Individual Components

```bash
# MCP Server (stdio mode for MCP clients)
uv run mt5mcp

# MCP Server (HTTP mode for development)
python start_mt5_http.py

# Simple chatbot (command line)
python run_chatbot_simple.py

# Web interface only
python run_simple_web.py
```

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only (no MT5 required)
uv run pytest -m unit

# Integration tests (requires MT5 running)
uv run pytest -m integration

# With coverage
uv run pytest --cov=mcp_mt5 --cov-report=html

# Specific test file
uv run pytest tests/test_connection.py
```

### Building and Publishing

```bash
# Build package
uv build

# Publish to PyPI
uv publish

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/
```

## Architecture

### Core Components

1. **MT5 Connection Manager** (`src/core/mt5_connection.py`)
   - Singleton pattern for managing MT5 terminal connection
   - Handles initialization, login, and session state
   - Must be initialized before any trading operations

2. **MCP Server** (`src/mcp_mt5/main.py`)
   - FastMCP-based server exposing MT5 functionality
   - Tools for market data, trading operations, account info
   - Resources provide trading guides and API documentation
   - Prompts help AI assistants with common workflows

3. **Agent System** (`src/agents/`)
   - `generator.py`: Creates agents from configuration
   - `manager.py`: Manages agent lifecycle (create, pause, resume, stop)
   - `hedge_agent.py`: Example hedge trading strategy implementation
   - Agents run in separate threads with event tracking

4. **Chatbot** (`src/chatbot/`)
   - `client.py`: Main chatbot orchestration
   - `mt5_integration.py`: MT5-specific command handlers
   - Integrates Ollama LLM with MT5 operations

5. **Database** (`src/core/database.py`)
   - SQLite backend for trade persistence
   - Tables: `trades`, `agents`, `agent_events`
   - Use `setup_database()` on first run

6. **Web Interface** (`src/web/app.py`)
   - Flask app for agent management
   - REST API for creating/monitoring agents
   - Optional Flask-Admin interface

### Key Design Patterns

- **Singleton Connection**: MT5Connection ensures single terminal connection
- **Event-Driven Agents**: Agents emit events (created, started, paused, trade_opened, etc.)
- **Thread-Based Execution**: Each agent runs in a separate thread
- **Pydantic Models**: All MT5 data validated with Pydantic

## MT5 Integration Notes

### Connection Flow

1. Initialize MT5 connection: `mt5_connection.initialize()`
2. Login (optional if already logged in terminal): `mt5_connection.login(account, password, server)`
3. Perform operations
4. Shutdown: `mt5_connection.shutdown()`

### Symbol Format

The broker uses symbols with 'c' suffix (e.g., `EURUSDc`, `XAUUSDc`). Always verify available symbols with `get_symbols()` or `get_symbols_by_group()`.

### Order Management

- Orders require: symbol, volume, type (BUY/SELL), price, deviation
- Use `order_check()` before `order_send()` to validate
- Close positions via `order_send()` with opposite direction
- Position tickets are unique identifiers

### Timeframes

Common timeframes: M1, M5, M15, M30, H1, H4, D1, W1, MN1
Convert string to MT5 constant in `main.py` timeframe mapping

## Testing Strategy

- **Unit tests**: Mock MT5 functions, test logic in isolation
- **Integration tests**: Require running MT5 terminal, test real operations
- **Test markers**: Use `@pytest.mark.unit` or `@pytest.mark.integration`
- **Fixtures**: Shared in `tests/conftest.py`

## Common Development Tasks

### Adding New MCP Tools

1. Add tool function in `src/mcp_mt5/main.py` with `@mcp.tool()` decorator
2. Define Pydantic models for parameters/returns
3. Use `mt5_connection` singleton for MT5 operations
4. Handle errors with custom exceptions from `core.exceptions`
5. Add unit tests in `tests/`

### Creating New Agent Types

1. Extend `HedgeAgent` pattern in `src/agents/`
2. Implement `run()` method with trading logic
3. Emit events via `self.manager.emit_event()`
4. Register in `AgentGenerator.create_agent()`
5. Add configuration model to `AgentConfig`

### Adding Chatbot Commands

1. Add command handler in `src/chatbot/mt5_integration.py`
2. Parse user intent from message
3. Call appropriate MT5 operations
4. Return formatted response
5. Log operations to database

## Important Files

- `pyproject.toml`: Project metadata, dependencies, build config
- `.env`: Environment configuration (transport mode, host, port)
- `src/mcp_mt5/main.py`: Main MCP server with all tools (~1000+ lines)
- **`src/core/mt5_mcp_client.py`**: **CENTRALIZED MCP CLIENT** - ALL components use this!
- `src/core/mt5_connection.py`: Direct connection manager (legacy, use MCP client instead)
- `src/agents/manager.py`: Agent lifecycle management
- `docs/`: MkDocs documentation for API and guides
- `ARQUITETURA_MCP.md`: Detailed MCP architecture documentation

## Entry Points

- `mt5mcp`: Main MCP server entry point (defined in pyproject.toml)
- `run_chatbot_simple.py`: Simple chatbot without agent management
- `run_chatbot_manager.py`: Full chatbot with agent system
- `test_mt5_direct.py`: Quick integration test
- **`RUN_BTC_AGENT.bat`**: Starts BTC Hedge trading agent
- **`RUN_GOLD_AGENT.bat`**: Starts Gold (XAUUSDc) Hedge trading agent
- **`RUN_GBP_AGENT.bat`**: Starts GBP (GBPUSDc) Hedge trading agent
- **`RUN_EUR_AGENT.bat`**: Starts EUR (EURUSDc) Hedge trading agent
- **`RUN_JPY_AGENT.bat`**: Starts JPY (USDJPYc) Hedge trading agent
- **`RUN_MULTI_AGENTS.bat`**: Starts BTC + Gold agents
- **`RUN_ALL_FOREX_AGENTS.bat`**: Starts all Forex agents (GBP + EUR + JPY)
- **`RUN_ALL_AGENTS.bat`**: Starts ALL 5 agents simultaneously
- **`STOP_ALL_AGENTS.bat`**: Stops all running agents
- **`VER_TRADES.bat`**: Shows all trades saved in database
- **`TESTAR_DASHBOARD.bat`**: Tests MT5 visual dashboard with simulated data
- **`TESTAR_FOREX.bat`**: Tests all Forex symbols availability

## Hedge Trading Agents & MT5 Dashboard

### Multi-Symbol Trading System

The Hedge Agent (`src/agents/btc_hedge_agent.py`) is a fully automated trading system that works with **any symbol**.

**Available Symbols:**

*Crypto/Commodities:*
- **BTCUSDm** (Bitcoin): 0.02 lots - `RUN_BTC_AGENT.bat`
- **XAUUSDc** (Gold): 0.01 lots - `RUN_GOLD_AGENT.bat`

*Forex:*
- **GBPUSDc** (British Pound): 0.10 lots - `RUN_GBP_AGENT.bat`
- **EURUSDc** (Euro): 0.10 lots - `RUN_EUR_AGENT.bat`
- **USDJPYc** (Japanese Yen): 0.10 lots - `RUN_JPY_AGENT.bat`

*Multiple Agents:*
- **BTC + Gold**: `RUN_MULTI_AGENTS.bat` (2 agents)
- **All Forex**: `RUN_ALL_FOREX_AGENTS.bat` (3 agents)
- **ALL 5 Symbols**: `RUN_ALL_AGENTS.bat` (5 agents)
- **Custom**: `uv run python src/agents/btc_hedge_agent.py SYMBOL VOLUME`

**Features:**
- Multi-indicator analysis: RSI, MACD, Bollinger Bands, SMA20, SMA50, ATR
- Dynamic SL based on ATR (1.5x multiplier)
- Automatic hedge activation when position loses >$10
- Consecutive trading on winning streaks
- Daily limit: 20 operations per symbol
- Position tracking and database persistence
- Logs and data export every 30 seconds

**Starting Agents:**
```batch
# Single symbol - Bitcoin
RUN_BTC_AGENT.bat

# Single symbol - Gold
RUN_GOLD_AGENT.bat

# Multiple symbols simultaneously
RUN_MULTI_AGENTS.bat

# Custom symbol
uv run python src/agents/btc_hedge_agent.py EURUSDc 0.10
```

**Data Export:**
The agent automatically exports real-time data to `C:\mcp-trader\agent_data.json`:
- Agent state (analyzing/trading/hedging/paused)
- Daily trades count and total profit
- Winning streak and hedge status
- All technical indicators
- Position count
- Timestamp

### Visual MT5 Dashboard

The MT5 dashboard (`BTC_Agent_Dashboard.mq5`) provides real-time visualization of the Python agent:

**Setup:**
1. Open MT5 → Tools → MQL5 Editor (F4)
2. Open `BTC_Agent_Dashboard.mq5`
3. Compile (F7)
4. Add to BTCUSDm chart
5. Dashboard updates every 5 seconds

**Display Features:**
- **Info Panel**: Agent state, trades, profit, streak, hedge status
- **Market Data**: Price, trend, RSI, MACD, ATR, SMAs
- **Chart Indicators**: Bollinger Bands, SMA20, SMA50 drawn on chart
- **Trading Signals**: Buy/Sell arrows based on conditions
- **Position Counter**: Number of open positions

**Testing Dashboard:**
```batch
# Generate test data without running real agent
TESTAR_DASHBOARD.bat
```

**Trade Database:**
All trades are automatically saved to SQLite database when positions close:
```batch
# View all trades with statistics
VER_TRADES.bat
```

Database includes:
- Ticket, symbol, type, volume
- Open/close prices and times
- SL, TP, profit
- Win rate, total profit, streaks

**Documentation:**
- `AGENTES_MULTIPLOS.md`: Multi-symbol trading guide (5 symbols)
- `DASHBOARD_MT5_VISUAL.md`: Complete dashboard setup guide
- `INICIAR_TESTE_BTC.md`: BTC agent usage instructions
- `test_btc_symbol.py`: Validates BTCUSDm availability
- `test_gold_symbol.py`: Validates XAUUSDc availability
- `test_forex_symbols.py`: Validates all Forex symbols (GBP, EUR, JPY)

## Environment Variables

```env
# MCP Configuration
MT5_MCP_TRANSPORT=stdio  # or 'http'
MT5_MCP_HOST=127.0.0.1   # for HTTP mode
MT5_MCP_PORT=8000        # for HTTP mode

# AI Model Configuration (optional)
AI_PROVIDER=anthropic           # or 'ollama'
ANTHROPIC_API_KEY=sk-ant-...    # Your Anthropic API key
AI_MODEL=claude-3-5-haiku-20241022  # Claude model
AI_MAX_TOKENS=4096             # Max response tokens
AI_TEMPERATURE=0.7             # 0.0-1.0
```

### Configuring Claude Haiku 4.5

For market analysis and trading decisions using Claude 3.5 Haiku:

1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`
3. Set model: `AI_MODEL=claude-3-5-haiku-20241022`
4. Test: `TESTAR_HAIKU.bat`

**Full guide**: See `CONFIGURAR_HAIKU.md` for complete setup instructions

## Notes for AI Assistants

### MT5 Communication - IMPORTANT!
- **ALWAYS use `mt5_mcp_client` for MT5 operations** - never direct MT5 calls
- All components must use: `from core.mt5_mcp_client import get_mt5_client`
- The client is a singleton - one instance for the entire application
- MT5 MCP Server must be running on port 8000 (start with `start_mt5_http.py`)
- Test connection with: `python test_mcp_connection.py`

### Trading Rules
- Verify symbol names match broker format (often with 'c' suffix)
- Minimum volume is typically 0.01 lots (broker-dependent)
- Account info includes balance, equity, margin, free margin
- Positions have tickets (unique IDs) for management

### Architecture
- The system uses centralized MCP client (singleton pattern)
- MT5 MCP Server runs in HTTP mode on port 8000
- Web dashboard runs on port 3000
- Worker service monitors trades in background
- Database operations are synchronous (sqlite3)
- Agents run in threads, not async tasks

### Adding New Features
When adding features that need MT5 access:
1. Import: `from core.mt5_mcp_client import get_mt5_client`
2. Get client: `mt5_client = get_mt5_client()`
3. Use client methods: `mt5_client.get_account_info()`, `mt5_client.positions_get()`, etc.
4. See `ARQUITETURA_MCP.md` for complete API reference
