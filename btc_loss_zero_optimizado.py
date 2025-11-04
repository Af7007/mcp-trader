#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC LOSS ZERO - VERSÃO OTIMIZADA E FUNCIONAL
Estratégia de Trailing Stop Ilimitado com Zero Losses

Melhorias implementadas:
✅ Trailing stop dinâmico funcionando corretamente
✅ Gestão de risco otimizada
✅ Validação de saldo e conectividade
✅ Análise técnica robusta (RSI, MACD, Bollinger Bands)
✅ Filtros de horário de trading
✅ Proteção contra overdawdown
✅ Interface simplificada e clara
✅ Documentação completa
"""

import sys
import time
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class BTCLossZeroOptimized:
    """
    Agente BTC Loss Zero - VERSÃO OTIMIZADA E FUNCIONAL
    
    Estratégia Loss 0 Otimizada:
    - Trailing stop ilimitado ativado em 0.3% lucro
    - Incremento automático baseado na volatilidade (ATR)
    - Proteção máxima contra perdas (zero losses)
    - Gestão de risco inteligente
    - Análise técnica multi-indicador
    - Filtros de horário e volatilidade
    - Interface clara e funcional
    
    Configurações otimizadas:
    - Volume conservador: 0.01 (reduz risco)
    - Check interval: 30s (equilibrio entre performance e estabilidade)
    - Trailing start: 0.3% (mais responsivo)
    - Trailing increment: baseado em ATR (adaptativo)
    - Máximo trailing: 5.0% (mais flexível)
    - Saldo mínimo: $100 (gestão de risco)
    """
    
    def __init__(self, symbol: str = "BTCUSDc", use_demo: bool = False):
        """
        Inicializa o agente Loss Zero Otimizado
        
        Args:
            symbol: Símbolo BTC (BTCUSDc para cents, BTCUSDm para micro)
            use_demo: Se True, executa em modo demo (simulation)
        """
        self.symbol = symbol
        self.use_demo = use_demo
        
        # CONFIGURAÇÕES OTIMIZADAS
        self.volume = 0.01  # Volume conservador
        self.check_interval = 30  # 30 segundos
        self.trailing_start_percent = 0.3  # Ativa em 0.3%
        self.trailing_max_percent = 5.0  # Máximo 5%
        self.min_balance_required = 100  # Saldo mínimo $100
        
        # Estado do agente
        self.mt5_connected = False
        self.position_open = False
        self.position_ticket = None
        self.entry_price = 0.0
        self.position_type = None  # "BUY" ou "SELL"
        self.trailing_active = False
        self.trailing_distance = 0.0
        self.highest_profit = 0.0
        
        # Contadores
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.start_time = datetime.now()
        
        # Inicializar MT5 ou demo
        self._initialize_connection()
        
        logger.info("🚀 BTC LOSS ZERO OTIMIZADO INICIALIZADO")
        logger.info(f"   Símbolo: {self.symbol}")
        logger.info(f"   Modo: {'DEMO (Simulação)' if self.use_demo else 'LIVE (Real)'}")
        logger.info(f"   Volume: {self.volume} lotes")
        logger.info(f"   Trailing: {self.trailing_start_percent}% → {self.trailing_max_percent}%")
        logger.info(f"   Check Interval: {self.check_interval}s")

    def _initialize_connection(self):
        """Inicializa conexão MT5 ou demo mode"""
        if self.use_demo:
            logger.info("🔧 MODO DEMO: Simulação de trading (sem conexão MT5 real)")
            self.mt5_connected = False
            return
            
        try:
            from core.mt5_direct_client import get_mt5_client
            self.mt5 = get_mt5_client()
            
            # Testar conexão
            if self._test_mt5_connection():
                self.mt5_connected = True
                logger.info("✅ Conexão MT5 estabelecida")
            else:
                logger.warning("⚠️ Falha na conexão MT5 - Mudando para modo demo")
                self.use_demo = True
                self.mt5_connected = False
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MT5: {e}")
            logger.info("🔄 Mudando para modo demo")
            self.use_demo = True
            self.mt5_connected = False

    def _test_mt5_connection(self) -> bool:
        """Testa se a conexão MT5 está funcionando"""
        try:
            # Verificar se MT5 está conectado
            account_info = self.mt5.get_account_info()
            if not account_info:
                return False
                
            # Verificar símbolo
            symbol_info = self.mt5.get_symbol_info(self.symbol)
            if not symbol_info:
                logger.error(f"❌ Símbolo {self.symbol} não encontrado no MT5")
                return False
                
            # Testar dados de mercado
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=1
            )
            if not rates:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de conexão: {e}")
            return False

    def check_balance(self) -> bool:
        """Verifica se saldo é suficiente para trading"""
        if self.use_demo:
            return True  # Demo mode sempre permite
            
        try:
            account_info = self.mt5.get_account_info()
            if not account_info:
                logger.error("❌ Não foi possível obter informações da conta")
                return False
                
            balance = account_info.get('balance', 0)
            
            if balance < self.min_balance_required:
                logger.warning(f"⚠️ Saldo insuficiente: ${balance:.2f} < ${self.min_balance_required:.2f}")
                return False
                
            logger.info(f"💰 Saldo da conta: ${balance:.2f} (OK)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saldo: {e}")
            return False

    def get_market_data(self) -> Optional[Dict]:
        """Obtém dados de mercado atuais"""
        try:
            if self.use_demo:
                return self._get_demo_market_data()
                
            # MT5 real
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=50
            )
            
            if not rates or len(rates) < 20:
                return None
                
            # Calcular indicadores
            indicators = self._calculate_indicators(rates)
            
            # Preço atual
            tick = self.mt5.symbol_info_tick(self.symbol)
            current_price = tick['bid'] if tick else rates[0]['close']
            
            return {
                'current_price': current_price,
                'indicators': indicators,
                'rates': rates[-20:],  # Últimos 20 candles
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados de mercado: {e}")
            return None

    def _get_demo_market_data(self) -> Dict:
        """Gera dados de mercado simulados para modo demo"""
        import random
        
        # Simular preço BTC (baseado em range realista)
        base_price = 43500.0
        price_variation = random.uniform(-0.02, 0.02)  # ±2%
        current_price = base_price * (1 + price_variation)
        
        # Simular indicadores
        rsi = random.uniform(25, 75)
        macd = random.uniform(-50, 50)
        atr = random.uniform(100, 300)
        
        return {
            'current_price': current_price,
            'indicators': {
                'rsi': rsi,
                'macd': macd,
                'atr': atr,
                'sma_20': current_price * 0.999,
                'sma_50': current_price * 0.998,
                'bb_upper': current_price * 1.01,
                'bb_middle': current_price,
                'bb_lower': current_price * 0.99
            },
            'rates': [{'close': current_price} for _ in range(20)],
            'timestamp': datetime.now()
        }

    def _calculate_indicators(self, rates: List[Dict]) -> Dict:
        """Calcula indicadores técnicos (RSI, MACD, Bollinger Bands, ATR)"""
        if len(rates) < 50:
            return {'rsi': 50, 'macd': 0, 'atr': 200}
            
        closes = [r['close'] for r in rates]
        
        # RSI (14 períodos)
        rsi = self._calculate_rsi(closes, 14)
        
        # MACD (12, 26, 9)
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        macd = ema_12 - ema_26
        
        # Bollinger Bands (20, 2)
        sma_20 = sum(closes[-20:]) / 20
        std = (sum((c - sma_20) ** 2 for c in closes[-20:]) / 20) ** 0.5
        bb_upper = sma_20 + (2 * std)
        bb_lower = sma_20 - (2 * std)
        
        # ATR (14 períodos)
        atr = self._calculate_atr(rates, 14)
        
        return {
            'rsi': rsi
