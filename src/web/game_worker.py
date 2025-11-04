#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold Loss Zero Game - Trailing Stop Worker
Monitora e atualiza trailing stops automaticamente
"""

import sys
import time
import logging
from pathlib import Path
from threading import Thread, Event

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client

logger = logging.getLogger(__name__)


class GameTrailingWorker:
    """
    Worker que monitora posições do jogo e atualiza trailing stops
    
    REGRAS DINÂMICAS (v2.0):
    - Ativa trailing quando lucro >= SL configurado
    - Proteção inicial: SL - $0.10 (90% do SL para $1)
    - Sobe trailing a cada $0.10 de lucro adicional
    
    Exemplo: SL=$1 (teste)
    - Lucro $1.00 → Protege $0.90
    - Lucro $1.10 → Protege $1.00 (breakeven)
    - Lucro $1.20 → Protege $1.10 (lucro garantido!)
    """
    
    def __init__(self, magic_number: int, positions_state: dict = None, check_interval: float = 0.1):
        self.magic_number = magic_number
        self.check_interval = check_interval  # Reduzido para 0.1s (100ms) para ativação imediata
        self.mt5 = get_mt5_client()
        self.positions_state = positions_state or {}  # Reference to GAME_STATE['positions']
        
        self.running = False
        self.thread = None
        self.stop_event = Event()
        
        # Tracking
        self.positions_data = {}  # ticket -> {trailing_active, last_trailing_level, sl_dollars, entry_price, pos_type}
        
    def start(self):
        """Start worker thread"""
        if self.running:
            logger.warning("Worker already running")
            return
        
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"Trailing worker started (magic: {self.magic_number})")
        
    def stop(self):
        """Stop worker thread"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Trailing worker stopped")
        
    def _run(self):
        """Main worker loop"""
        logger.info("Worker loop started")
        
        while not self.stop_event.is_set():
            try:
                self._check_positions()
            except Exception as e:
                logger.error(f"Worker error: {e}")
            
            time.sleep(self.check_interval)
        
        logger.info("Worker loop ended")
        
    def _check_positions(self):
        """Check and update all positions"""
        try:
            # Get positions for this magic number
            positions = self.mt5.positions_get(symbol="XAUUSDc", magic=self.magic_number)
            
            # Log every 300 checks (30 seconds at 0.1s interval) - reduzido logs
            if not hasattr(self, '_check_count'):
                self._check_count = 0
            self._check_count += 1
            
            if self._check_count % 300 == 0:
                logger.info(f"[WORKER] Checked {self._check_count} times | Positions: {len(positions) if positions else 0} | Magic: {self.magic_number}")
            
            if not positions:
                # Clear tracking
                if self.positions_data:
                    logger.info(f"[WORKER] No positions found, clearing {len(self.positions_data)} tracked")
                self.positions_data.clear()
                return
            
            # Log active positions com menos frequência
            if self._check_count % 300 == 1:  # Log right after count message
                for pos in positions:
                    ticket = pos['ticket']
                    profit = self._calculate_profit(pos)
                    logger.info(f"[WORKER] Position #{ticket}: Type={pos['type']}, Profit=${profit:.2f}, SL={pos['sl']:.5f}")
            
            mt5_tickets = {pos['ticket'] for pos in positions}
            
            # Remove closed positions from tracking
            closed = set(self.positions_data.keys()) - mt5_tickets
            for ticket in closed:
                del self.positions_data[ticket]
                logger.info(f"[WORKER] Position {ticket} closed (removed from tracking)")
            
            # Update each position
            for pos in positions:
                self._update_position_trailing(pos)
                
        except Exception as e:
            logger.error(f"[WORKER] Error checking positions: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_profit(self, pos: dict) -> float:
        """
        Calculate profit for XAUUSDc position
        
        XAUUSDc specs:
        - Contract size: 1.0 oz
        - Tick value: $0.10
        - 1 lot = 1 oz, $1 movement = $100
        - 0.01 lots = $1 per $1 movement
        """
        pos_type = pos['type']
        entry_price = pos['price_open']
        current_price = pos['price_current']
        volume = pos['volume']
        
        if pos_type == 0:  # BUY
            price_movement = current_price - entry_price
        else:  # SELL
            price_movement = entry_price - current_price
        
        # XAUUSDc: 1 lot = $100 per $1 movement
        profit = price_movement * volume * 100
        return profit
    
    def _update_position_trailing(self, pos: dict):
        """Update trailing stop for a single position"""
        try:
            ticket = pos['ticket']
            pos_type = pos['type']  # 0=BUY, 1=SELL
            entry_price = pos['price_open']
            current_price = pos['price_current']
            current_sl = pos['sl']
            volume = pos['volume']
            
            # Calculate profit in dollars
            profit_dollars = self._calculate_profit(pos)
            
            # Initialize tracking
            if ticket not in self.positions_data:
                # Get SL from state if available, otherwise use default $1 (para teste)
                sl_dollars = 1.0
                if ticket in self.positions_state:
                    sl_dollars = self.positions_state[ticket].get('sl_dollars', 1.0)
                
                self.positions_data[ticket] = {
                    'trailing_active': False,
                    'last_trailing_level': 0,
                    'sl_dollars': sl_dollars
                }
            
            data = self.positions_data[ticket]
            sl_dollars = data['sl_dollars']
            
            # Log only when important changes happen
            if profit_dollars >= sl_dollars and not data['trailing_active']:
                logger.info(f"[TRAILING] #{ticket}: Profit=${profit_dollars:.2f} >= SL=${sl_dollars:.2f} - ACTIVATING TRAILING")
            elif data['trailing_active'] and profit_dollars > 0:
                logger.debug(f"[TRAILING] #{ticket}: Profit=${profit_dollars:.2f} | Active={data['trailing_active']} | SL=${current_sl:.5f}")
            
            # === TRAILING LOGIC DINÂMICO ===
            # Ativa quando lucro >= SL configurado
            # Proteção inicial: SL - $0.10
            # Sobe a cada $0.10 de lucro adicional
            
            if profit_dollars >= sl_dollars:
                logger.info(f"[TRAILING] #{ticket}: LUCRO ATINGIDO! ${profit_dollars:.2f} >= ${sl_dollars:.2f}")
                
                # Calculate how many trailing levels we should be at
                # Level 0: SL até SL+0.09 → Protege (SL - 0.10)
                # Level 1: SL+0.10 até SL+0.19 → Protege SL
                # Level 2: SL+0.20 até SL+0.29 → Protege (SL + 0.10)
                # etc.
                
                profit_above_sl = profit_dollars - sl_dollars
                trailing_level = int(profit_above_sl / 0.10)
                
                # Calculate SL that protects: (SL - 0.10) + (level * 0.10)
                target_protection = (sl_dollars - 0.10) + (trailing_level * 0.10)
                
                logger.info(f"[TRAILING] #{ticket}: Level={trailing_level}, Target Protection=${target_protection:.2f}")
                
                # Convert protection to SL price
                # protection = (sl_price - entry) * point_value (for BUY)
                # sl_price = entry + (protection / point_value)
                
                # CORREÇÃO: XAUUSDc point value calculation
                # 1 lot = $100 per $1 movement
                # 0.01 lots = $1 per $1 movement
                # point_value = volume * 100
                
                point_value = volume * 100
                
                if pos_type == 0:  # BUY
                    new_sl = entry_price + (target_protection / point_value)
                else:  # SELL
                    new_sl = entry_price - (target_protection / point_value)
                
                logger.info(f"[TRAILING] #{ticket}: Calculated new_sl={new_sl:.5f} (Entry={entry_price:.5f}, Protection=${target_protection:.2f})")
                
                # Check if we should update
                should_update = False
                
                if not data['trailing_active']:
                    # First activation
                    should_update = True
                    data['trailing_active'] = True
                    logger.info(f"[ATIVANDO TRAILING] Ticket {ticket}: Lucro ${profit_dollars:.2f} (>= SL ${sl_dollars:.2f}) → Protege ${target_protection:.2f}")
                
                elif trailing_level > data['last_trailing_level']:
                    # Level increased
                    should_update = True
                    logger.info(f"[SUBINDO TRAILING] Ticket {ticket}: Level {data['last_trailing_level']} → {trailing_level} | Protege ${target_protection:.2f}")
                
                if should_update:
                    # Only move SL up (BUY) or down (SELL)
                    if pos_type == 0:  # BUY
                        if new_sl <= current_sl:
                            logger.debug(f"Trailing skip: new_sl ({new_sl:.5f}) <= current_sl ({current_sl:.5f}) on BUY")
                            return
                    else:  # SELL
                        if new_sl >= current_sl:
                            logger.debug(f"Trailing skip: new_sl ({new_sl:.5f}) >= current_sl ({current_sl:.5f}) on SELL")
                            return
                    
                    # Execute modification
                    try:
                        logger.info(f"[EXECUTANDO] modify_position(ticket={ticket}, sl={new_sl:.5f})")
                        result = self.mt5.modify_position(ticket=ticket, sl=new_sl)
                        
                        logger.info(f"[RESULTADO] {result}")
                        
                        if result and result.get('retcode') == 10009:
                            data['last_trailing_level'] = trailing_level
                            logger.info(f"✓ Trailing atualizado: Ticket {ticket} → SL ${new_sl:.5f} (Protege ${target_protection:.2f})")
                        else:
                            error_code = result.get('retcode') if result else 'None'
                            error_msg = result.get('comment') if result else 'No result'
                            logger.error(f"✗ Falha ao atualizar trailing {ticket}: retcode={error_code}, msg={error_msg}")
                    
                    except Exception as e:
                        logger.error(f"Erro ao modificar posição {ticket}: {e}")
                        import traceback
                        traceback.print_exc()
        
        except Exception as e:
            logger.error(f"Error updating trailing for position: {e}")


# Global worker instance
_worker = None


def start_game_worker(magic_number: int, positions_state: dict = None):
    """Start the game trailing worker"""
    global _worker
    
    if _worker is not None:
        logger.warning("Worker already exists")
        return
    
    _worker = GameTrailingWorker(magic_number, positions_state=positions_state)
    _worker.start()
    

def stop_game_worker():
    """Stop the game trailing worker"""
    global _worker
    
    if _worker is None:
        return
    
    _worker.stop()
    _worker = None
