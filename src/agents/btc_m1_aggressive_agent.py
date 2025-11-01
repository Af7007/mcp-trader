#!/usr/bin/env python3
"""
Agente de Trading BTCUSD CENTS - Timeframe M1 - Versão Agressiva

Características principais:
- Timeframe M1 para scalping (movimentos mais rápidos)
- Símbolo: BTCUSDc (cents - menor spread)
- Abordagem AGGRESSIVE: volume maior, TP menor, hedge mais sensível
- Operações rápidas com analise multi-indicador otimizada para M1
- SL dinâmico baseado em ATR 1.5x (mais apertado para M1)
- SL mínimo: $2.0 para evitar stops prematuros
- TP de $1.0 por operação (trades rápidos)
- Check interval: 15 segundos (maior frequência)

Gestão de Posições:
- 1 posição normal por vez (igual ao otimizado)
- Hedge ativado mais rapidamente: -$3.0 (vs -$4.0)
- Hedge TP: $3.0 (fecha par rapidamente)
- Volume agressivo: 0.05 lots (vs 0.03 otimizado)

Agressividade:
- Volume 67% maior (0.05 vs 0.03)
- Hedge 25% mais sensível (-$3.0 vs -$4.0)
- TP menor: $1.0 (vs $2.5) para trades rápidos
- Check 2x mais frequente (15s vs 30s)
- Rejeição menor de sinais BUY (abrir mais oportunidades)
"""

import logging
import time
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client
from core.database import setup_database, get_db_connection
from core.telegram_notifier import get_telegram_notifier

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Estados do agente"""
    ANALYZING = "analyzing"
    TRADING = "trading"
    HEDGING = "hedging"
    PAUSED = "paused"
    STOPPED = "stopped"


class BTCM1AggressiveAgent:
    """
    Agente de Trading AGGRESSIVE para BTCUSD CENTS - M1.
    
    Características:
    - Símbolo: BTCUSDc (cents - menor spread, mais oportunidades)
    - Volume AGGRESSIVE: 0.05 lots (maior exposição)
    - TP: $1.0 por operação (trades rápidos)
    - SL dinâmico baseado em 1.5x ATR (mais apertado para M1)
    - SL mínimo: $2.0 (proporcionais ao preço em cents)
    - Check interval: 15 segundos (maior frequência M1)
    - Hedge AGGRESSIVE: trigger -$3.0, TP $3.0
    - BUY/SELL habilitado (não SELL-only)

    Otimizações M1:
    - Indicadores calculados com períodos menores
    - RSI (10 vs 14) - mais sensível
    - MACD (8,16,6 vs 12,26,9) - resposta mais rápida
    - SMA10 e SMA30 (vs 20,50) - trend mais responsivo
    - Bollinger (14 vs 20) - volatilidade mais atual

    Estratégia Agressiva:
    - Aceita 50% dos sinais BUY (vs 0% SELL-only)
    - Hedge ativado mais facilmente (-$3.0 vs -$4.0)
    - Volume 67% maior (0.05 vs 0.03)
    - TP menor para realizados rápidos ($1.0 vs $2.5)
    - Check mais frequente (15s vs 30s)
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",  # Cents - menor spread
        volume: float = 0.05,     # AGGRESSIVE volume
        target_profit: float = 1.0,  # TP menor para trades rápidos
        max_daily_trades: int = 999,
        check_interval: int = 15,    # M1 - check mais frequente
        hedge_trigger: float = -3.0, # AGGRESSIVE hedge
        hedge_tp_target: float = 3.0,
        atr_multiplier: float = 1.5, # SL mais apertado para M1
        only_sell: bool = False      # BUY/SELL habilitado
    ):
        """
        Inicializa o agente AGGRESSIVE M1.

        Args:
            symbol: BTCUSDc (cents)
            volume: 0.05 (aggressive)
            target_profit: $1.0 (rápido)
            max_daily_trades: 999 (ilimitado)
            check_interval: 15s (M1)
            hedge_trigger: -$3.0 (aggressive)
            hedge_tp_target: $3.0 (rápido)
            atr_multiplier: 1.5 (apertado)
            only_sell: False (BUY habilitado)
        """
        self.symbol = symbol
        self.volume = volume
        self.target_profit = target_profit
        self.max_daily_trades = max_daily_trades
        self.check_interval = check_interval
        self.hedge_trigger = hedge_trigger
        self.hedge_tp_target = hedge_tp_target
        self.only_sell = only_sell

        self.mt5 = get_mt5_client()
        self.state = AgentState.ANALYZING
        self.telegram = get_telegram_notifier()

        # Contadores
        self.daily_trades = 0
        self.total_profit = 0.0
        self.winning_streak = 0
        self.last_trade_time = None
        self.trades_today = []
        self.open_tickets = set()
        self.hedge_tickets = set()
        self.cycle_count = 0
        self.startup_notified = False
        self.last_metrics_count = 0

        # Configurações de hedge AGGRESSIVE
        self.hedge_active = False
        self.original_position_ticket = None
        self.hedge_position_ticket = None
        self.hedge_entry_price = None

        # SL dinâmico para M1
        self.atr_multiplier = atr_multiplier

        # M1 OPTIMIZATIONS
        self.is_m1 = True  # Flag para otimizações M1
        self.is_btc_cents = 'BTC' in symbol.upper() and ('CENTS' in symbol.upper() or 'C' in symbol.upper())
        
        if self.is_btc_cents:
            # Configurações específicas para BTC CENTS
            self.target_profit = 1.0  # TP menor para cents
            self.hedge_trigger = -3.0  # Hedge mais sensível
            self.hedge_tp_target = 3.0  # TP hedge para rápido
            self.volume = 0.05  # Volume agressivo
            self.atr_multiplier = 1.5  # SL mais apertado
            self.only_sell = False  # BUY habilitado
            
            logger.info("🚀 BTC CENTS M1 AGGRESSIVE MODE ATIVADO!")
            logger.info(f"   Symbol: {symbol} (cents)")
            logger.info(f"   Volume: {self.volume} (aggressive)")
            logger.info(f"   Target Profit: ${self.target_profit} (rápido)")
            logger.info(f"   Hedge Trigger: ${self.hedge_trigger}")
            logger.info(f"   Hedge TP: ${self.hedge_tp_target}")
            logger.info(f"   ATR Multiplier: {self.atr_multiplier}x")
            logger.info(f"   BUY/SELL: Habilitado (não SELL-only)")

        logger.info(f"🤖 Agente M1 Aggressive inicializado")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Volume: {self.volume}")
        logger.info(f"   Target Profit: ${self.target_profit}")
        logger.info(f"   Check Interval: {self.check_interval}s")
        logger.info(f"   Max Daily Trades: {max_daily_trades}")

    def calculate_atr_m1(self, periods: int = 10) -> float:
        """Calcula ATR otimizado para M1 - períodos menores."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M1",  # M1 para scalping
            start_pos=0,
            count=periods + 1
        )

        # ATR padrão para BTC CENTS
        symbol_upper = self.symbol.upper()
        if 'BTC' in symbol_upper and 'CENTS' in symbol_upper:
            default_atr = 5.0  # ATR menor para cents
        elif 'BTC' in symbol_upper:
            default_atr = 150.0
        else:
            default_atr = 0.0008

        if not rates or len(rates) < periods:
            logger.warning(f"⚠️ Dados insuficientes para ATR M1. Usando padrão: {default_atr}")
            return default_atr

        # Calcular True Range para M1
        trs = []
        for i in range(1, len(rates)):
            high_low = rates[i]['high'] - rates[i]['low']
            high_close = abs(rates[i]['high'] - rates[i-1]['close'])
            low_close = abs(rates[i]['low'] - rates[i-1]['close'])
            tr = max(high_low, high_close, low_close)
            trs.append(tr)

        # ATR é a média dos True Ranges
        atr = sum(trs) / len(trs) if trs else default_atr

        # Se ATR calculado for muito pequeno, usar padrão
        if atr < 0.0001:
            logger.warning(f"⚠️ ATR M1 muito pequeno ({atr:.8f}). Usando padrão: {default_atr}")
            atr = default_atr

        return atr

    def calculate_indicators_m1(self) -> Dict[str, float]:
        """Calcula indicadores otimizados para M1 - períodos menores."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M1",  # M1
            start_pos=0,
            count=30  # Menos dados para M1
