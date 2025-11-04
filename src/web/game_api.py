#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold Loss Zero Game - API Backend
Integração com o agente gold_loss_zero_game.py
"""

import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Blueprint, jsonify, request, render_template
from core.mt5_direct_client import get_mt5_client

# Blueprint
game_bp = Blueprint('game', __name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'trading.db'

# Game state with FIXED magic number for history persistence
GAME_MAGIC_NUMBER = 777777  # Fixed magic number for Gold Game
GAME_STATE = {
    'positions': {},  # ticket -> position_data
    'last_prediction': None,
    'last_price': 0,
    'magic_number': GAME_MAGIC_NUMBER
}


def _ensure_game_table():
    """Ensure game history table exists"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket INTEGER NOT NULL UNIQUE,
                magic_number INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                volume REAL NOT NULL,
                open_price REAL,
                close_price REAL,
                sl REAL,
                tp REAL,
                profit REAL NOT NULL,
                open_time TEXT,
                close_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_magic 
            ON game_history(magic_number, close_time DESC)
        """)
        
        conn.commit()
        conn.close()
        print("[GAME DB] Table created/verified")
    except Exception as e:
        print(f"[GAME DB] Error creating table: {e}")


def _save_trade_to_db(trade_data: dict):
    """Save completed trade to database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if already exists (by ticket AND magic number)
        cursor.execute(
            "SELECT id FROM game_history WHERE ticket = ? AND magic_number = ?", 
            (trade_data['ticket'], GAME_MAGIC_NUMBER)
        )
        if cursor.fetchone():
            conn.close()
            return False  # Already saved
        
        cursor.execute("""
            INSERT INTO game_history 
            (ticket, magic_number, symbol, type, volume, open_price, close_price, sl, tp, profit, open_time, close_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data['ticket'],
            GAME_MAGIC_NUMBER,
            trade_data.get('symbol', 'XAUUSDc'),
            trade_data['type'],
            trade_data['volume'],
            trade_data.get('open_price', 0),
            trade_data.get('close_price', 0),
            trade_data.get('sl'),
            trade_data.get('tp'),
            trade_data['profit'],
            trade_data.get('open_time', datetime.now().isoformat()),
            trade_data['close_time']
        ))
        
        conn.commit()
        conn.close()
        print(f"[GAME DB] Saved trade #{trade_data['ticket']}: ${trade_data['profit']:.2f}")
        return True
    except Exception as e:
        print(f"[GAME DB] Error saving trade: {e}")
        return False


def _get_history_from_db(limit: int = 50) -> list:
    """Get game history from database - ONLY CLOSED POSITIONS"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # IMPORTANT: Filter only CLOSED positions (profit != 0 AND close_time is not None)
        cursor.execute("""
            SELECT ticket, type, volume, profit, close_time
            FROM game_history
            WHERE magic_number = ? 
            AND profit != 0 
            AND close_time IS NOT NULL
            ORDER BY close_time DESC
            LIMIT ?
        """, (GAME_MAGIC_NUMBER, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        print(f"[GAME HISTORY] Loaded {len(rows)} CLOSED positions from database")
        
        history = []
        for row in rows:
            ticket, trade_type, volume, profit, close_time = row
            
            # Handle timestamp formatting - convert Unix timestamp to ISO string
            if close_time:
                try:
                    # Check if it's a Unix timestamp (integer)
                    if isinstance(close_time, (int, float)) or str(close_time).isdigit():
                        from datetime import datetime
                        timestamp = int(close_time)
                        dt = datetime.fromtimestamp(timestamp)
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # Already formatted string
                        formatted_time = str(close_time)
                except:
                    formatted_time = "2025-01-01 12:00:00"  # Fallback
            else:
                formatted_time = "2025-01-01 12:00:00"  # Fallback
            
            history.append({
                'ticket': ticket,
                'type': trade_type,
                'volume': volume,
                'profit': float(profit) if profit is not None else 0.0,
                'close_time': formatted_time
            })
        
        return history
    except Exception as e:
        print(f"[GAME DB] Error loading history: {e}")
        import traceback
        traceback.print_exc()
        return []


def _get_stats_from_db() -> dict:
    """Calculate stats from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(profit) as total_profit,
                COUNT(CASE WHEN profit > 0 THEN 1 END) as wins,
                COUNT(CASE WHEN profit < 0 THEN 1 END) as losses
            FROM game_history
            WHERE magic_number = ?
        """, (GAME_MAGIC_NUMBER,))
        
        row = cursor.fetchone()
        conn.close()
        
        total_profit = row[0] if row[0] else 0
        wins = row[1] if row[1] else 0
        losses = row[2] if row[2] else 0
        
        # Calculate streak from recent trades
        history = _get_history_from_db(limit=10)
        streak = 0
        if history:
            last_result = 1 if history[0]['profit'] > 0 else -1
            for trade in history:
                current_result = 1 if trade['profit'] > 0 else -1
                if current_result == last_result:
                    streak += current_result
                else:
                    break
        
        return {
            'total_profit': total_profit,
            'wins': wins,
            'losses': losses,
            'streak': streak
        }
    except Exception as e:
        print(f"[GAME DB] Error loading stats: {e}")
        return {'total_profit': 0, 'wins': 0, 'losses': 0, 'streak': 0}


# Initialize database on import
_ensure_game_table()


@game_bp.route('/game')
def game_page():
    """Render game page v2 (premium)"""
    try:
        import time
        timestamp = int(time.time())
        return render_template('game_v2.html', timestamp=timestamp)
    except Exception as e:
        return f"Error loading game: {e}<br><br>Template folder: {game_bp.root_path}", 500

@game_bp.route('/game/v1')
def game_page_v1():
    """Render game page v1 (simple)"""
    try:
        return render_template('game.html')
    except Exception as e:
        return f"Error loading game v1: {e}", 500


@game_bp.route('/api/game/prediction')
def get_prediction():
    """
    Get prediction for next candle + chart data + account balance
    
    Returns:
        {
            "prediction": {...},
            "price": current_price,
            "candles": [...],
            "balance": account_balance
        }
    """
    try:
        mt5 = get_mt5_client()
        
        # Get prediction
        prediction = _predict_next_candle(mt5)
        
        # Get current price
        tick = mt5.get_symbol_info_tick("XAUUSDc")
        price = tick['bid'] if tick else 0
        
        # Get last 20 candles for chart
        rates = mt5.copy_rates_from_pos(
            symbol="XAUUSDc",
            timeframe="M1",
            start_pos=0,
            count=20
        )
        
        candles = []
        if rates:
            for rate in rates:
                candles.append({
                    'time': rate['time'].isoformat() if hasattr(rate['time'], 'isoformat') else str(rate['time']),
                    'open': float(rate['open']),
                    'high': float(rate['high']),
                    'low': float(rate['low']),
                    'close': float(rate['close'])
                })
        
        # Get account balance
        account_info = mt5.get_account_info()
        balance = account_info['balance'] if account_info else 0
        
        GAME_STATE['last_prediction'] = prediction
        GAME_STATE['last_price'] = price
        
        return jsonify({
            'prediction': prediction,
            'price': price,
            'candles': candles,
            'balance': balance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/api/game/positions')
def get_positions():
    """
    Get active positions
    
    Returns:
        {
            "positions": [
                {
                    "ticket": int,
                    "type": "BUY" | "SELL",
                    "volume": float,
                    "entry_price": float,
                    "sl": float,
                    "profit": float,
                    "trailing_active": bool
                }
            ]
        }
    """
    try:
        mt5 = get_mt5_client()
        
        # Get positions from MT5 (filter by magic number 777777)
        mt5_positions = mt5.positions_get(symbol="XAUUSDc", magic=GAME_MAGIC_NUMBER)
        
        if not mt5_positions:
            GAME_STATE['positions'] = {}
            return jsonify({'positions': []})
        
        positions = []
        for pos in mt5_positions:
            ticket = pos['ticket']
            
            # Calculate profit (XAUUSDc formula)
            if pos['type'] == 0:  # BUY
                price_movement = pos['price_current'] - pos['price_open']
            else:  # SELL
                price_movement = pos['price_open'] - pos['price_current']
            
            # XAUUSDc: 1 lot = $100 per $1 movement
            profit = price_movement * pos['volume'] * 100
            
            # Check if trailing is active
            trailing_active = GAME_STATE['positions'].get(ticket, {}).get('trailing_active', False)
            
            positions.append({
                'ticket': ticket,
                'type': 'BUY' if pos['type'] == 0 else 'SELL',
                'volume': pos['volume'],
                'entry_price': pos['price_open'],
                'sl': pos['sl'],
                'profit': profit,
                'trailing_active': trailing_active
            })
            
            # Update state
            if ticket not in GAME_STATE['positions']:
                GAME_STATE['positions'][ticket] = {
                    'ticket': ticket,
                    'entry_price': pos['price_open'],
                    'trailing_active': False
                }
        
        return jsonify({'positions': positions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/api/game/history')
def get_history():
    """
    Get trade history and stats from DATABASE
    
    Returns:
        {
            "history": [
                {
                    "ticket": int,
                    "type": "BUY" | "SELL",
                    "volume": float,
                    "profit": float,
                    "close_time": datetime
                }
            ],
            "stats": {
                "total_profit": float,
                "wins": int,
                "losses": int,
                "streak": int
            }
        }
    """
    try:
        print(f"[GAME HISTORY] Starting...")
        mt5 = get_mt5_client()
        
        # First, sync recent deals from MT5 to database (expand range to 7 days)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        deals = mt5.history_deals_get(
            date_from=week_ago,
            date_to=now,
            symbol="XAUUSDc"
        )
        
        print(f"[GAME HISTORY] Found {len(deals) if deals else 0} deals for XAUUSDc in last 7 days")
        print(f"[GAME HISTORY] Game magic number: {GAME_MAGIC_NUMBER}")
        
        # Show details of found deals
        if deals:
            for i, deal in enumerate(deals[:5]):  # Show first 5 deals
                magic = deal.get('magic', 0)
                print(f"[GAME HISTORY] Deal {i+1}: Ticket={deal.get('ticket')}, Magic={magic}, Type={deal.get('type')}, Profit={deal.get('profit')}")
        
        # Sync new closed positions to database
        if deals:
            positions_map = {}
            
            for deal in deals:
                magic = deal.get('magic', 0)
                
                # Only process deals with our magic number (777777)
                if magic != GAME_MAGIC_NUMBER:
                    print(f"[GAME HISTORY] Skipping deal {deal.get('ticket')} - magic {magic} != {GAME_MAGIC_NUMBER}")
                    continue
                
                pos_id = deal.get('position_id')
                if not pos_id:
                    print(f"[GAME HISTORY] Skipping deal {deal.get('ticket')} - no position_id")
                    continue
                
                entry_type = deal.get('entry')
                deal_type = deal.get('type')  # 0=BUY, 1=SELL
                deal_profit = deal.get('profit', 0)
                
                print(f"[GAME HISTORY] Processing deal {deal.get('ticket')}: pos_id={pos_id}, entry_type={entry_type}, profit={deal_profit}")
                
                # Entry = 0 (IN), 1 (OUT), 2 (INOUT)
                if entry_type == 0:  # IN deal - position opened
                    # Store the initial deal info
                    if pos_id not in positions_map:
                        positions_map[pos_id] = {
                            'ticket': pos_id,
                            'type': 'BUY' if deal_type == 0 else 'SELL',
                            'volume': deal.get('volume', 0),
                            'profit': 0,  # Will be updated by OUT deal
                            'close_price': 0,
                            'close_time': None,
                            'open_time': deal.get('time')
                        }
                        print(f"[GAME HISTORY] Added position entry: {pos_id}")
                elif entry_type == 1:  # OUT deal - position closed
                    # Update with closing info
                    if pos_id in positions_map:
                        positions_map[pos_id]['profit'] = deal_profit
                        positions_map[pos_id]['close_price'] = deal.get('price', 0)
                        positions_map[pos_id]['close_time'] = deal.get('time')
                        print(f"[GAME HISTORY] Updated position exit: {pos_id} profit={deal_profit}")
                    else:
                        # Handle case where we only have OUT deal
                        positions_map[pos_id] = {
                            'ticket': pos_id,
                            'type': 'BUY' if deal_type == 0 else 'SELL',  # This might be wrong, need to infer
                            'volume': deal.get('volume', 0),
                            'profit': deal_profit,
                            'close_price': deal.get('price', 0),
                            'close_time': deal.get('time'),
                            'open_time': deal.get('time')  # Fallback
                        }
                        print(f"[GAME HISTORY] Added position exit only: {pos_id} profit={deal_profit}")
            
            # Save to database (if not already saved)
            saved_count = 0
            print(f"[GAME HISTORY] Total positions to save: {len(positions_map)}")
            for pos_id, pos in positions_map.items():
                trade_data = {
                    'ticket': pos['ticket'],
                    'type': pos['type'],
                    'volume': pos['volume'],
                    'profit': pos['profit'],
                    'close_price': pos['close_price'],
                    'close_time': pos['close_time'].isoformat() if hasattr(pos['close_time'], 'isoformat') else str(pos['close_time'])
                }
                
                print(f"[GAME HISTORY] Attempting to save trade: {trade_data}")
                if _save_trade_to_db(trade_data):
                    saved_count += 1
                    print(f"[GAME HISTORY] Successfully saved trade #{pos['ticket']}")
                else:
                    print(f"[GAME HISTORY] Trade #{pos['ticket']} already exists or failed to save")
            
            if saved_count > 0:
                print(f"[GAME DB] Saved {saved_count} new trades")
        
        # Get history from database
        history = _get_history_from_db(limit=50)
        stats = _get_stats_from_db()
        
        print(f"[GAME HISTORY] Loaded {len(history)} trades from database")
        print(f"[GAME HISTORY] Stats: ${stats['total_profit']:.2f} | {stats['wins']}W {stats['losses']}L")
        
        # Show history details
        if history:
            print(f"[GAME HISTORY] First trade: {history[0]}")
        
        return jsonify({
            'history': history,
            'stats': stats
        })
        
    except Exception as e:
        print(f"[GAME HISTORY] Error in get_history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@game_bp.route('/api/game/close', methods=['POST'])
def close_position():
    """
    Close an active position using close_position method
    
    Request:
        {
            "ticket": int
        }
    
    Returns:
        {
            "success": bool,
            "profit": float | null,
            "error": str | null
        }
    """
    try:
        data = request.json
        ticket = int(data.get('ticket'))
        
        mt5 = get_mt5_client()
        
        # Get position info BEFORE closing
        positions = mt5.positions_get(ticket=ticket)
        
        if not positions or len(positions) == 0:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        pos = positions[0]
        
        # Calculate profit BEFORE closing (XAUUSDc formula)
        if pos['type'] == 0:  # BUY
            price_movement = pos['price_current'] - pos['price_open']
        else:  # SELL
            price_movement = pos['price_open'] - pos['price_current']
        
        # XAUUSDc: 1 lot = $100 per $1 movement
        profit = price_movement * pos['volume'] * 100
        
        print(f"[GAME] Closing position #{ticket}: Type={pos['type']}, Profit=${profit:.2f}")
        
        # Close position using close_position method (not new market order!)
        result = mt5.close_position(ticket=ticket)
        
        print(f"[GAME] Close result: {result}")
        
        if result and result.get('retcode') == 10009:
            # Remove from state
            if ticket in GAME_STATE['positions']:
                del GAME_STATE['positions'][ticket]
            
            print(f"[GAME] Position #{ticket} closed successfully: ${profit:.2f}")
            
            return jsonify({
                'success': True,
                'profit': profit
            })
        else:
            error_code = result.get('retcode') if result else 'None'
            error_msg = result.get('comment', 'Unknown error') if result else 'No result'
            print(f"[GAME] Failed to close #{ticket}: retcode={error_code}, msg={error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
    except Exception as e:
        print(f"[GAME] Exception closing position: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@game_bp.route('/api/game/worker-status')
def worker_status():
    """
    Get worker status and debug information
    
    Returns:
        {
            "worker_running": bool,
            "positions_state": dict,
            "magic_number": int,
            "mt5_positions": list,
            "debug_info": dict
        }
    """
    try:
        from web.game_worker import _worker
        
        # Get MT5 positions
        mt5 = get_mt5_client()
        mt5_positions = mt5.positions_get(symbol="XAUUSDc", magic=GAME_MAGIC_NUMBER)
        
        # Debug info
        debug_info = {
            'worker_exists': _worker is not None,
            'worker_running': _worker.running if _worker else False,
            'magic_number': GAME_MAGIC_NUMBER,
            'positions_state_keys': list(GAME_STATE['positions'].keys()),
            'positions_state_data': GAME_STATE['positions'],
            'mt5_positions_count': len(mt5_positions) if mt5_positions else 0,
            'mt5_position_tickets': [pos['ticket'] for pos in mt5_positions] if mt5_positions else []
        }
        
        # If worker exists, get more info
        if _worker:
            debug_info.update({
                'worker_positions_data': _worker.positions_data,
                'worker_check_count': getattr(_worker, '_check_count', 0),
                'worker_magic': _worker.magic_number
            })
        
        return jsonify({
            'worker_running': _worker.running if _worker else False,
            'positions_state': GAME_STATE['positions'],
            'magic_number': GAME_MAGIC_NUMBER,
            'mt5_positions': [
                {
                    'ticket': pos['ticket'],
                    'type': pos['type'],
                    'volume': pos['volume'],
                    'profit': (pos['price_current'] - pos['price_open']) * pos['volume'] * 100 if pos['type'] == 0 else (pos['price_open'] - pos['price_current']) * pos['volume'] * 100,
                    'sl': pos['sl'],
                    'magic': pos.get('magic', 0)
                }
                for pos in mt5_positions
            ] if mt5_positions else [],
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/api/game/open', methods=['POST'])
def open_position():
    """
    Open new position
    
    Request:
        {
            "type": "BUY" | "SELL",
            "volume": float,
            "sl": float (dollars)
        }
    
    Returns:
        {
            "success": bool,
            "ticket": int | null,
            "error": str | null
        }
    """
    try:
        data = request.json
        signal_type = data.get('type')
        volume = float(data.get('volume', 0.02))
        sl_dollars = float(data.get('sl', 5.0))
        
        mt5 = get_mt5_client()
        
        # Get price
        tick = mt5.get_symbol_info_tick("XAUUSDc")
        if not tick:
            return jsonify({'success': False, 'error': 'No price data'}), 400
        
        # Calculate SL in price movement
        # XAUUSDc: 1 lot = $100 per $1 movement, so 0.01 lots = $1 per $1
        # sl_dollars = price_movement × volume × 100
        # price_movement = sl_dollars / (volume × 100)
        sl_price_movement = sl_dollars / (volume * 100)
        
        if signal_type == 'BUY':
            entry_price = tick['ask']
            sl_price = entry_price - sl_price_movement
            
            result = mt5.buy_market(
                symbol="XAUUSDc",
                volume=volume,
                sl=sl_price,
                comment=f"GoldGame_{GAME_MAGIC_NUMBER}",
                magic=GAME_MAGIC_NUMBER
            )
        elif signal_type == 'SELL':
            entry_price = tick['bid']
            sl_price = entry_price + sl_price_movement
            
            result = mt5.sell_market(
                symbol="XAUUSDc",
                volume=volume,
                sl=sl_price,
                comment=f"GoldGame_{GAME_MAGIC_NUMBER}",
                magic=GAME_MAGIC_NUMBER
            )
        else:
            return jsonify({'success': False, 'error': 'Invalid type'}), 400
        
        if result and result.get('retcode') == 10009:
            ticket = result.get('order', 0)
            
            # Add to state with SL dollars for trailing
            GAME_STATE['positions'][ticket] = {
                'ticket': ticket,
                'entry_price': entry_price,
                'sl_dollars': sl_dollars,  # Store SL for dynamic trailing
                'trailing_active': False
            }
            
            return jsonify({
                'success': True,
                'ticket': ticket
            })
        else:
            error_msg = result.get('comment', 'Unknown error') if result else 'No result'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _predict_next_candle(mt5) -> Dict:
    """
    Prediction system (same logic as gold_loss_zero_game.py)
    
    Returns:
        {
            "type": "BUY" | "SELL" | "WAIT",
            "score": 0-100,
            "confidence": 0-100,
            "reason": "explanation"
        }
    """
    try:
        print("[PREDICTION] Starting analysis...")
        
        # === M5 Confirmation ===
        rates_m5 = mt5.copy_rates_from_pos(
            symbol="XAUUSDc",
            timeframe="M5",
            start_pos=0,
            count=30
        )
        
        print(f"[PREDICTION] M5 candles: {len(rates_m5) if rates_m5 else 0}")
        
        if not rates_m5 or len(rates_m5) < 10:
            print("[PREDICTION] ERROR: Insufficient M5 data")
            return {"type": "WAIT", "score": 0, "confidence": 0, "reason": "Insufficient M5 data"}
        
        closes_m5 = [r['close'] for r in rates_m5[:6]]
        m5_ups = sum([1 for i in range(5) if closes_m5[i] > closes_m5[i+1]])
        m5_downs = sum([1 for i in range(5) if closes_m5[i] < closes_m5[i+1]])
        
        # Menos rigoroso: 3+ ao invés de 4+
        m5_uptrend = m5_ups >= 3
        m5_downtrend = m5_downs >= 3
        
        # Se empate, usar o que tem mais
        if m5_ups == m5_downs:
            m5_uptrend = False
            m5_downtrend = False
        elif m5_ups > m5_downs:
            m5_uptrend = True
            m5_downtrend = False
        else:
            m5_uptrend = False
            m5_downtrend = True
        
        print(f"[PREDICTION] M5 trend: ups={m5_ups}, downs={m5_downs}, uptrend={m5_uptrend}, downtrend={m5_downtrend}")
        
        if not m5_uptrend and not m5_downtrend:
            print("[PREDICTION] No clear M5 trend - analyzing M1 only")
            # Continua para análise M1 ao invés de retornar 0
        
        # === M1 Analysis ===
        rates_m1 = mt5.copy_rates_from_pos(
            symbol="XAUUSDc",
            timeframe="M1",
            start_pos=0,
            count=25
        )
        
        print(f"[PREDICTION] M1 candles: {len(rates_m1) if rates_m1 else 0}")
        
        if not rates_m1 or len(rates_m1) < 25:
            print("[PREDICTION] ERROR: Insufficient M1 data")
            return {"type": "WAIT", "score": 0, "confidence": 0, "reason": "Insufficient M1 data"}
        
        closes = [r['close'] for r in rates_m1[:21]]
        highs = [r['high'] for r in rates_m1[:21]]
        lows = [r['low'] for r in rates_m1[:21]]
        
        current = closes[0]
        
        # Averages
        sma_5 = sum(closes[:5]) / 5
        sma_10 = sum(closes[:10]) / 10
        sma_20 = sum(closes[:20]) / 20
        
        # Trends
        ups_20 = sum([1 for i in range(20) if closes[i] > closes[i+1]])
        downs_20 = sum([1 for i in range(20) if closes[i] < closes[i+1]])
        ups_10 = sum([1 for i in range(10) if closes[i] > closes[i+1]])
        downs_10 = sum([1 for i in range(10) if closes[i] < closes[i+1]])
        ups_5 = sum([1 for i in range(5) if closes[i] > closes[i+1]])
        downs_5 = sum([1 for i in range(5) if closes[i] < closes[i+1]])
        
        # Momentum
        momentum_recent = ((closes[0] - closes[5]) / closes[5]) * 100
        
        # Volatility check
        avg_range = sum([highs[i] - lows[i] for i in range(10)]) / 10
        current_range = highs[0] - lows[0]
        if current_range > avg_range * 2.5:
            return {"type": "WAIT", "score": 0, "confidence": 0, "reason": "High volatility"}
        
        # === BUY Score ===
        if m5_uptrend or (not m5_downtrend and ups_20 > downs_20):
            score = 0
            
            if ups_20 >= 15:
                score += 25
            elif ups_20 >= 12:
                score += 15
            
            if ups_10 >= 7:
                score += 20
            elif ups_10 >= 6:
                score += 10
            
            if ups_5 >= 4:
                score += 20
            elif ups_5 >= 3:
                score += 10
            
            if current > sma_5 > sma_10 > sma_20:
                score += 15
            elif current > sma_5 and current > sma_10:
                score += 10
            elif current > sma_5:
                score += 5
            
            if momentum_recent > 0.01:
                score += 10
            elif momentum_recent > 0:
                score += 5
            
            confidence = min(abs(momentum_recent) * 1000, 100)
            
            # Lower threshold for signal
            if score >= 70:
                signal_type = "BUY"
            elif score >= 50:
                signal_type = "WAIT"  # Frontend will show as weak buy
            else:
                signal_type = "WAIT"
            
            m5_badge = "✓M5" if m5_uptrend else "M1"
            print(f"[PREDICTION] BUY signal: score={score}, type={signal_type}, confidence={confidence:.1f}")
            
            return {
                "type": signal_type,
                "score": score,
                "confidence": confidence,
                "reason": f"{m5_badge} | Score:{score} | Up20:{ups_20} Up10:{ups_10} Up5:{ups_5}"
            }
        
        # === SELL Score ===
        if m5_downtrend or (not m5_uptrend and downs_20 > ups_20):
            score = 0
            
            if downs_20 >= 15:
                score += 25
            elif downs_20 >= 12:
                score += 15
            
            if downs_10 >= 7:
                score += 20
            elif downs_10 >= 6:
                score += 10
            
            if downs_5 >= 4:
                score += 20
            elif downs_5 >= 3:
                score += 10
            
            if current < sma_5 < sma_10 < sma_20:
                score += 15
            elif current < sma_5 and current < sma_10:
                score += 10
            elif current < sma_5:
                score += 5
            
            if momentum_recent < -0.01:
                score += 10
            elif momentum_recent < 0:
                score += 5
            
            confidence = min(abs(momentum_recent) * 1000, 100)
            
            # Lower threshold for signal
            if score >= 70:
                signal_type = "SELL"
            elif score >= 50:
                signal_type = "WAIT"  # Frontend will show as weak sell
            else:
                signal_type = "WAIT"
            
            m5_badge = "✓M5" if m5_downtrend else "M1"
            print(f"[PREDICTION] SELL signal: score={score}, type={signal_type}, confidence={confidence:.1f}")
            
            return {
                "type": signal_type,
                "score": score,
                "confidence": confidence,
                "reason": f"{m5_badge} | Score:{score} | Down20:{downs_20} Down10:{downs_10} Down5:{downs_5}"
            }
        
        print("[PREDICTION] No trend detected after analysis")
        return {"type": "WAIT", "score": 0, "confidence": 0, "reason": "No trend detected"}
        
    except Exception as e:
        print(f"[PREDICTION] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"type": "WAIT", "score": 0, "confidence": 0, "reason": f"Error: {str(e)}"}
