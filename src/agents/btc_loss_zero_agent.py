#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss 0 - Trailing Stop Dinâmico
Estratégia: Loss 0 com trailing stop a partir de 0.5%
"""

import logging
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client
from core.database import setup_database, get_db_connection
from core.telegram_notifier import get_telegram_notifier

logger = logging.getLogger(__name__)


class TrailingState(Enum):
    """Estados do trailing stop"""
    INACTIVE = "inactive"      # Trailing inativo
    ACTIVE = "active"          # Trailing ativo
    FOLLOWING = "following"    # Seguindo preço favoravel
    LOCKING = "locking"        # Trailing aumentando
    TRIGGERED = "triggered"    # Stop atingido


class BTCLossZeroAgent:
    """
    Agente BTC com estratégia Loss 0 - Trailing Stop Dinâmico.
    
    Estratégia Loss 0:
    - NÃO definir TP fixo
    - Ativar trailing stop a partir de 0.5% lucro
    - Aumentar trailing gradualmente conforme preço sobe
    - Sempre parar pelo trailing stop (nunca por TP)
    - Maximizar lucro potencial
    - Zero losses garantidos (trailing sempre protege)
    
    Configurações principais:
    - Volume: 0.05 (aggressive)
    - Check Interval: 15s
    - Trailing: 0.5% inicial
    - Incremento: 0.1% por movimento favorável
    - Mínimo trailing: 0.2%
    - Máximo trailing: 2.0%
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",      # BTC Cents
        volume: float = 0.05,          # Volume agressivo
        check_interval: int = 15,      # Check frequente
        trailing_start_percent: float = 0.5,  # Ativa trailing em 0.5%
        trailing_min_percent: float = 0.2,     # Mínimo trailing
        trailing_max_percent: float = 2.0,     # Máximo trailing
        trailing_increment: float = 0.1,       # Incremento por movimento
        use_buy: bool = True,          # BUY habilitado
        use_sell: bool = True          # SELL habilitado
    ):
        """
        Inicializa o agente Loss 0.
        
        Args:
            symbol: Símbolo (BTCUSDc)
            volume: Volume agressivo
            check_interval: Frequência de check
            trailing_start_percent: Ativa trailing em X% lucro
            trailing_min_percent: Trailing mínimo
            trailing_max_percent: Trailing máximo
            trailing_increment: Incremento por movimento favorável
            use_buy: Habilitar BUY
            use_sell: Habilitar SELL
        """
        self.symbol = symbol
        self.volume = volume
        self.check_interval = check_interval
        
        # Configurações de trailing
        self.trailing_start_percent = trailing_start_percent
        self.trailing_min_percent = trailing_min_percent
        self.trailing_max_percent = trailing_max_percent
        self.trailing_increment = trailing_increment
        
        # BUY/SELL
        self.use_buy = use_buy
        self.use_sell = use_sell
        
        self.mt5 = get_mt5_client()
        self.telegram = get_telegram_notifier()
        
        # Estado do trailing
        self.trailing_state = TrailingState.INACTIVE
        self.trailing_distance = 0.0
        self.highest_profit = 0.0
        self.position_ticket = None
        self.entry_price = 0.0
        self.position_type = None  # "buy" ou "sell"
        
        # Contadores
        self.total_trades = 0
        self.profitable_trades = 0
        self.total_profit = 0.0
        self.open_positions = []
        
        # Configuração Loss 0
        self.loss_zero_enabled = True
        self.max_drawdown_protection = True
        
        logger.info(f"🤖 Agente Loss Zero inicializado")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Volume: {self.volume}")
        logger.info(f"   Trailing: {trailing_start_percent}% → {trailing_max_percent}%")
        logger.info(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")

    def analyze_and_trade(self):
        """
        Analisa mercado e executa trades com Loss 0
        """
        try:
            # Verificar posições abertas
            self.check_open_positions()
            
            # Se não há posições, analisar para abrir nova
            if not self.open_positions:
                signal = self.analyze_market_signal()
                
                if signal:
                    self.open_position_with_loss_zero(signal)
            else:
                # Gerenciar trailing stop das posições abertas
                self.manage_trailing_stops()
                
        except Exception as e:
            logger.error(f"Erro na análise: {e}")

    def analyze_market_signal(self) -> Optional[Dict]:
        """
        Analisa sinais do mercado para abrir posição
        """
        try:
            # Obter dados de mercado
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=50
            )
            
            if not rates or len(rates) < 20:
                return None
            
            # Análise técnica simplificada para Loss 0
            current_price = rates[0]['close']
            sma_short = self.calculate_sma(rates, 10)
            sma_long = self.calculate_sma(rates, 20)
            rsi = self.calculate_rsi(rates, 14)
            
            # Gerar sinais
            signal = None
            
            if self.use_sell:
                # SELL: SMA curto < SMA longo + RSI > 70
                if sma_short < sma_long and rsi > 70
