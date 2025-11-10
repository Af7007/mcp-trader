# Worker Protection v3.5.0 - Fast Protection System

## Problem Discovered

Analysis of recent trades revealed a CRITICAL issue:

```
Pos #115539002: Reached $9.13 profit -> Closed at -$0.02 (LOSS!)
Pos #115539443: Reached $4.32 profit -> Closed at -$0.26 (LOSS!)
Pos #115539042: Reached $9.30 profit -> Closed at $6.42 (could protect $7.30)
```

**Root Cause:**
- Protection logic ran in main loop (1 second intervals)
- Trades lasted only 26-47 seconds
- Market moved too fast for 1s protection checks
- By the time protection checked, market already reversed

## Solution: 20ms Worker Protection

### Implementation

**File:** `src/agents/btc_loss_zero_v3.py`

**Changes:**

1. **Rewritten `_trailing_worker_callback`** (lines 643-746)
   - Now uses SAME logic as `_check_and_move_breakeven`
   - Runs every 20ms (50x per second!)
   - Fast enough to catch profits before reversal

2. **Protection Rules v3.5.0:**
   - $1.00 profit -> SL at entry (break-even, protect $0)
   - $3.00 profit -> SL protects $1.00
   - $5.00 profit -> SL protects $3.00
   - $7.00 profit -> SL protects $5.00
   - $9.00 profit -> SL protects $7.00
   - Formula: `protection = profit - $2.00`

3. **Worker Speed:**
   - Check interval: 20ms (0.02 seconds)
   - Checks per second: 50
   - 50x FASTER than main loop (1s)

## Code Changes

### Before (v3.4.0):

```python
# Old worker had wrong logic ($1.50 margin)
protected_profit = profit_dollars - 1.5
```

### After (v3.5.0):

```python
def _trailing_worker_callback(self, position, current_bid, current_ask):
    """
    v3.5.0 - Worker de Protecao Rapida (20ms)
    Usa MESMA LOGICA do _check_and_move_breakeven mas roda MUITO MAIS RAPIDO!
    """
    # ... setup code ...

    if profit_dollars >= 1.0:
        if profit_dollars < 3.0:
            # Entre $1 e $3: apenas break-even
            new_sl = entry_price
            protection_type = "BREAK-EVEN (protege $0)"
        else:
            # A partir de $3: protege (lucro - $2)
            protected_profit = profit_dollars - 2.0

            # Calcular distancia em preco
            protected_points = protected_profit / (self.point_value * self.volume)
            protected_distance = protected_points * self.symbol_point

            if pos_type == 0:  # BUY
                new_sl = entry_price + protected_distance
            else:  # SELL
                new_sl = entry_price - protected_distance

            protection_type = f"TRAILING (protege ${protected_profit:.2f})"

        # Verificar se deve atualizar
        should_update = False

        if pos_type == 0:  # BUY - SL deve SUBIR
            should_update = new_sl > current_sl
        else:  # SELL - SL deve DESCER
            should_update = new_sl < current_sl

        if should_update:
            result = self.mt5.modify_position(ticket=ticket, sl=new_sl, tp=None)

            if result.get('retcode') == 10009:
                print(f"\n[WORKER PROTECTION] Posicao #{ticket}")
                print(f"   Tipo: {protection_type}")
                print(f"   Lucro atual: ${profit_dollars:.2f}")
                print(f"   SL: ${current_sl:.2f} -> ${new_sl:.2f}")

                # Atualizar dicionarios
                if profit_dollars >= 3.0:
                    self.positions_trailing_active[ticket] = True
                    self.positions_trailing_stop[ticket] = new_sl
                else:
                    self.positions_breakeven_active[ticket] = True

                return True
```

## Timeline Example

```
t=0.00s: Order opens at $102,000
         Worker starts checking every 20ms

t=0.50s: Profit $0.50
         Worker checks -> no action

t=1.00s: Profit $1.00
t=1.02s: Worker checks -> BREAK-EVEN ACTIVATED!
         SL moved to $102,000 (entry)

t=2.00s: Profit $3.00
t=2.02s: Worker checks -> TRAILING ACTIVATED!
         SL moved to $102,020 (protects $1.00)

t=3.00s: Profit $5.00
t=3.02s: Worker checks -> TRAILING UPDATED!
         SL moved to $102,060 (protects $3.00)

t=4.00s: Profit $9.00
t=4.02s: Worker checks -> TRAILING UPDATED!
         SL moved to $102,140 (protects $7.00)

t=4.50s: Market reverses sharply
t=4.52s: SL hit at $102,140
         RESULT: +$7.00 PROFIT PROTECTED!
```

## Before vs After

### Before (v3.4.0):
- Protection checked every 1 second
- Order reaches $9 profit in 30 seconds
- Market reverses in 5 seconds
- Protection checks after reversal
- RESULT: -$0.02 LOSS

### After (v3.5.0):
- Protection checks every 20ms (50x/second)
- Order reaches $9 profit
- Worker immediately protects $7
- Market reverses
- SL triggers at protected level
- RESULT: +$7.00 WIN

## Testing

Run test script:
```bash
python test_worker_protection_v3_5.py
```

## Expected Logs

When worker activates protection:

```
[WORKER] Monitor de trailing iniciado (20ms)

[WORKER] Ticket 115539500: Lucro $1.05

[WORKER PROTECTION] Posicao #115539500
   Tipo: BREAK-EVEN (protege $0)
   Lucro atual: $1.05
   SL: $0.00 -> $102000.00

[WORKER] Ticket 115539500: Lucro $3.12

[WORKER PROTECTION] Posicao #115539500
   Tipo: TRAILING (protege $1.12)
   Lucro atual: $3.12
   SL: $102000.00 -> $102022.40

[WORKER] Ticket 115539500: Lucro $5.48

[WORKER PROTECTION] Posicao #115539500
   Tipo: TRAILING (protege $3.48)
   Lucro atual: $5.48
   SL: $102022.40 -> $102069.60
```

## Summary

- **Fixed:** Trailing protection not working on fast trades
- **Method:** Reactivated 20ms worker with correct v3.5.0 logic
- **Speed:** 50 checks per second (vs 1 check per second)
- **Result:** Protection catches profits before market reverses
- **Rules:** $1 break-even, $3+ trailing with $2 margin
