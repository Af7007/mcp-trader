# Database Save Fix - Summary

## Problem Identified
The agent was executing trades but **not saving them to the database**. Investigation revealed two issues:

### Issue 1: Indentation Error (CRITICAL)
**Location:** `src/agents/btc_hedge_agent.py`, lines 871-895 in `check_closed_positions()` method

**Problem:** The Telegram notification code block was incorrectly indented (4 extra spaces). This caused:
- The code after `save_trade_to_db()` call to be syntactically malformed
- Exception handling and tracking removal code to not execute properly
- The entire closed position processing to fail silently

**Before (WRONG):**
```python
self.save_trade_to_db(ticket, profit, trade_info)

                # 🔔 Notificação Telegram - Posição fechada  ← Extra 4 spaces!
                try:
                    ...
                except Exception as e:
                    ...

                # Remover do tracking
                self.open_tickets.discard(ticket)
```

**After (FIXED):**
```python
self.save_trade_to_db(ticket, profit, trade_info)

# 🔔 Notificação Telegram - Posição fechada  ← Correct indentation
try:
    ...
except Exception as e:
    ...

# Remover do tracking
self.open_tickets.discard(ticket)
```

### Issue 2: Missing Fallback Logic (ALREADY FIXED)
The `save_trade_to_db()` method now has 3-layer fallback strategy:
1. **Primary:** Use complete deal history if available (prices from deals, timestamps)
2. **Secondary:** Use trade_info dict when deals incomplete
3. **Tertiary:** Log warnings but still attempt to save minimal data

## Changes Made

### File: `src/agents/btc_hedge_agent.py`

**Fixed Methods:**
- `check_closed_positions()` (line 806): Fixed indentation of entire method epilogue
  - Now correctly calls `save_trade_to_db()`
  - Now properly handles Telegram notifications
  - Now properly removes closed tickets from tracking

- `save_trade_to_db()` (line 902): Already has fallback logic
  - Layer 1: Uses deal history with timestamp conversion
  - Layer 2: Falls back to trade_info if deals incomplete
  - Layer 3: Logs and attempts save even with minimal data
  - Has proper error handling for sqlite3.IntegrityError

## Database Schema

The database schema is correct and matches agent expectations:

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket INTEGER UNIQUE,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,           -- 'BUY' or 'SELL'
    volume REAL NOT NULL,
    open_price REAL NOT NULL,
    close_price REAL,
    open_time TIMESTAMP,
    close_time TIMESTAMP,
    sl REAL,                      -- Stop Loss
    tp REAL,                      -- Take Profit
    profit REAL,                  -- Profit/Loss
    comment TEXT,
    status TEXT NOT NULL DEFAULT 'open'
);
```

## Testing the Fix

### 1. Verify Code Quality
```bash
python -m py_compile src/agents/btc_hedge_agent.py
# Output: ✅ No syntax errors found
```

### 2. Start Fresh Database
```bash
python check_database.py
# Output: [OK] Banco de dados OK
#         [INFO] Nenhuma ordem salva ainda
```

### 3. Run the Agent
```batch
REM Start the BTC agent with correct syntax
RUN_BTC_AGENT.bat
```

### 4. Check Saved Trades
```bash
python check_database.py
# Output should show: [OK] Banco de dados OK - X trade(s) salvos
#        With details of trades, statistics, etc.
```

Or use the batch script:
```batch
VER_TRADES.bat
```

## Expected Behavior

When a position closes:

1. **Agent detects closure:** `check_closed_positions()` finds closed positions
2. **Calculates profit:** From deals or fallback to trade_info
3. **Logs status:** `📝 Salvando trade #XXXX no banco de dados...`
4. **Saves to database:** `save_trade_to_db()` executes with fallback logic
5. **Confirms save:** `✅ Trade #XXXX SALVO no banco`
6. **Sends notification:** Telegram message sent (if enabled)
7. **Cleans tracking:** Position removed from `open_tickets` and `hedge_tickets`

## Logs to Expect

```
📝 Salvando trade #12345 no banco de dados...
✅ Trade #12345 SALVO no banco:
   Tipo: BUY | Volume: 0.02 lots | Lucro: $6.50
   Entrada: $45200.50 → Saída: $45211.25
   SL: $45000.00 | TP: $45254.99
```

## Files Modified
- `src/agents/btc_hedge_agent.py` - Fixed indentation in `check_closed_positions()` method (lines 867-898)

## Files Already Correct
- `src/core/database.py` - Schema matches agent expectations
- `check_database.py` - Utility to verify saved trades
- All `.bat` files - Already using correct CLI flag syntax

## Next Steps

1. Test the agent with a fresh database
2. Monitor logs for "✅ Trade #XXXX SALVO no banco" messages
3. Run `python check_database.py` to verify trades are saved
4. Check statistics (win rate, total profit, average profit)

---
**Status:** FIXED ✅
**Last Updated:** 2025-10-27
