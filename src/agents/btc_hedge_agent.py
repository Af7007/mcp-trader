#!/usr/bin/env python3
"""
Agente de Trading BTCUSD com Estratégia de Hedge Inteligente

Características principais:
- Operações 24/7 com análise multi-indicador (RSI, MACD, Bollinger, SMA, ATR)
- SL dinâmico baseado em 2.5x ATR (configurável)
- SL mínimo: $250 ou 0.3% do preço para evitar stops prematuros
- TP de $6 por operação (trades normais)
- Timeframe M15 com check a cada 60 segundos

Gestão de Posições:
- APENAS 1 posição normal por vez
- Novas posições só abrem após fechamento da anterior
- Hedge não impede futuras posições (é proteção temporária)
- Máximo de 2 posições simultâneas: 1 normal + 1 hedge

Estratégia de Hedge com TP Agressivo:
- Ativa hedge quando posição atinge prejuízo de -$10
- Abre posição oposta com TP agressivo de $8
- Fecha automaticamente ambas posições quando hedge atinge TP
- Reduz prejuízo de -$10 para aproximadamente -$2
- Previne acúmulo de posições travadas e custos de swap

Notificações em tempo real via Telegram para todos eventos.
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


class BTCHedgeAgent:
    """
    Agente de Trading para BTCUSD com estratégia de hedge inteligente.

    Características:
    - Lote fixo: 0.02 (configurável)
    - TP: $6 por operação para trades normais
    - SL dinâmico baseado em 2.5x ATR (configurável)
    - SL mínimo: $250 ou 0.3% do preço (o maior)
    - Operações 24/7 sem limite diário (configurável)
    - Timeframe: M15 (15 minutos)
    - Check interval: 60 segundos

    Gestão de Posições:
    - APENAS 1 posição normal por vez
    - Novas posições só abrem após fechamento da anterior
    - Hedge não conta como posição normal (é proteção)
    - Máximo de 2 posições simultâneas: 1 normal + 1 hedge

    Estratégia de Hedge com TP Agressivo:
    - Trigger: Posição em prejuízo de -$10 (configurável)
    - Abre posição oposta com TP de $8 (configurável)
    - Fecha ambas posições quando hedge atinge TP
    - Resultado final: Prejuízo de -$10 reduzido para ~-$2
    - Previne acúmulo de posições travadas
    - Notificações Telegram em tempo real

    Análise Multi-Indicador:
    - RSI (14 períodos)
    - MACD (12, 26, 9)
    - Bollinger Bands (20, 2)
    - SMA20 e SMA50
    - ATR (14 períodos)
    """

    def __init__(
        self,
        symbol: str = "BTCUSDm",
        volume: float = 0.03,
        target_profit: float = 2.5,
        max_daily_trades: int = 999,
        check_interval: int = 30,
        hedge_trigger: float = -4.0,
        hedge_tp_target: float = 4.0,
        atr_multiplier: float = 2.5,
        only_sell: bool = False
    ):
        """
        Inicializa o agente.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            target_profit: Lucro alvo por operação ($)
            max_daily_trades: Máximo de operações por dia
            check_interval: Intervalo de verificação (segundos)
            hedge_trigger: Prejuízo que ativa hedge ($)
            hedge_tp_target: Lucro do hedge para fechar par ($)
            atr_multiplier: Multiplicador do ATR para SL (default: 2.5)
            only_sell: Se True, apenas abre SELL positions (default False)
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
        self.open_tickets = set()  # Rastreia tickets de posições abertas
        self.hedge_tickets = set()  # Rastreia apenas tickets de hedge
        self.cycle_count = 0  # Para controlar resumos periódicos
        self.startup_notified = False  # Flag para enviar notificação de inicialização uma vez
        self.last_metrics_count = 0  # Controla quando enviar resumo de métricas

        # Configurações de hedge
        self.hedge_active = False
        self.original_position_ticket = None
        self.hedge_position_ticket = None
        self.hedge_entry_price = None  # Preço de entrada do hedge

        # SL dinâmico
        self.atr_multiplier = atr_multiplier

        # GOLD-SPECIFIC OPTIMIZATIONS
        self.is_gold = 'XAU' in symbol.upper() or 'GOLD' in symbol.upper()
        if self.is_gold:
            # Otimizacoes para Gold: ORDENS ACERTIVAS sem hedge
            # Aumentado TP/SL para serem mais realistas e menos apertados
            self.target_profit = 5.0  # $5.0 por trade (mais realista, menos SL hits)
            self.only_sell = True  # Apenas SELL para Gold (melhor performance)
            self.volume = 0.01  # Lot size conservador para Gold
            self.hedge_trigger = -10000.0  # DESATIVADO - Foco em ordens acertivas
            self.hedge_tp_target = 1.5  # Não usado (hedge desativado)
            self.atr_multiplier = 1.5  # SL mais aberto para Gold (menos hits)
            logger.info(f"🏆 GOLD MODE ATIVADO - Ordens Acertivas (Hedge DESATIVADO)!")
            logger.info(f"   Target: $5.0 por trade (mais realista)")
            logger.info(f"   Modo: SELL-ONLY (rejeita BUY)")
            logger.info(f"   Volume: 0.01 lot (conservador)")
            logger.info(f"   Hedge: DESATIVADO - Foco em qualidade de entrada")
            logger.info(f"   SL: ATR × 1.5 (espaço real para mercado)")

        logger.info(f"🤖 Agente inicializado")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Volume: {self.volume}")
        logger.info(f"   Target Profit: ${self.target_profit}")
        logger.info(f"   ATR Multiplier: {self.atr_multiplier}x")
        logger.info(f"   Hedge Trigger: ${self.hedge_trigger}")
        logger.info(f"   Hedge TP Target: ${self.hedge_tp_target}")
        logger.info(f"   Max Daily Trades: {max_daily_trades}")
        if self.only_sell:
            logger.info(f"   MODE: SELL-ONLY (rejeitara BUY signals)")

    def save_sl_tp_backup(self, ticket: int, sl: float, tp: float):
        """Salva SL/TP em backup persistente (MT5 nao armazena isso nos deals)."""
        try:
            backup_file = Path(__file__).parent.parent.parent / "backup_sl_tp.json"

            # Carregar dados existentes
            backup_data = {}
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    try:
                        backup_data = json.load(f)
                    except:
                        backup_data = {}

            # Adicionar novo ticket
            backup_data[str(ticket)] = {
                'sl': sl,
                'tp': tp,
                'timestamp': datetime.now().isoformat()
            }

            # Salvar
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)

            logger.debug(f"Backup SL/TP salvo: Ticket {ticket} | SL=${sl:.2f} | TP=${tp:.2f}")
        except Exception as e:
            logger.error(f"Erro ao salvar backup SL/TP: {e}")

    def load_sl_tp_from_backup(self, ticket: int) -> tuple:
        """Carrega SL/TP do backup persistente."""
        try:
            backup_file = Path(__file__).parent.parent.parent / "backup_sl_tp.json"

            if not backup_file.exists():
                return (0, 0)

            with open(backup_file, 'r') as f:
                try:
                    backup_data = json.load(f)
                    if str(ticket) in backup_data:
                        data = backup_data[str(ticket)]
                        sl = float(data.get('sl', 0))
                        tp = float(data.get('tp', 0))

                        logger.debug(f"SL/TP carregado do backup: Ticket {ticket} | SL=${sl:.2f} | TP=${tp:.2f}")
                        return (sl, tp)
                except:
                    pass

            return (0, 0)
        except Exception as e:
            logger.error(f"Erro ao carregar backup SL/TP: {e}")
            return (0, 0)

    def calculate_atr(self, periods: int = 14) -> float:
        """Calcula ATR para SL dinâmico."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M15",  # Mudado de M5 para M15 para reduzir ruído
            start_pos=0,
            count=periods + 1
        )

        # ATR padrão por tipo de símbolo
        symbol_upper = self.symbol.upper()
        if 'BTC' in symbol_upper:
            default_atr = 150.0
        elif 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            default_atr = 1.0
        elif 'JPY' in symbol_upper:
            default_atr = 0.10
        else:
            # Forex padrão
            default_atr = 0.0008

        if not rates or len(rates) < periods:
            logger.warning(f"⚠️ Dados insuficientes para ATR. Usando padrão: {default_atr}")
            return default_atr

        # Calcular True Range
        trs = []
        for i in range(1, len(rates)):
            high_low = rates[i]['high'] - rates[i]['low']
            high_close = abs(rates[i]['high'] - rates[i-1]['close'])
            low_close = abs(rates[i]['low'] - rates[i-1]['close'])
            tr = max(high_low, high_close, low_close)
            trs.append(tr)

        # ATR é a média dos True Ranges
        atr = sum(trs) / len(trs) if trs else default_atr

        # Se ATR calculado for muito pequeno ou zero, usar padrão
        if atr < 0.0001:
            logger.warning(f"⚠️ ATR muito pequeno ({atr:.8f}). Usando padrão: {default_atr}")
            atr = default_atr

        return atr

    def calculate_indicators(self) -> Dict[str, float]:
        """Calcula todos os indicadores disponíveis."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M15",  # Mudado de M5 para M15 para reduzir ruído
            start_pos=0,
            count=50
        )

        if not rates:
            return {}

        closes = [r['close'] for r in rates]
        highs = [r['high'] for r in rates]
        lows = [r['low'] for r in rates]

        # RSI
        rsi = self._calculate_rsi(closes, 14)

        # Médias Móveis
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50

        # MACD
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        macd = ema_12 - ema_26

        # Bollinger Bands
        bb_middle = sma_20
        std = (sum((c - bb_middle) ** 2 for c in closes[-20:]) / 20) ** 0.5
        bb_upper = bb_middle + (2 * std)
        bb_lower = bb_middle - (2 * std)

        # ATR
        atr = self.calculate_atr()

        current_price = closes[-1]

        return {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'macd': macd,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'atr': atr,
            'current_price': current_price,
            'trend': 'UP' if sma_20 > sma_50 else 'DOWN'
        }

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcula RSI."""
        if len(prices) < period + 1:
            return 50

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calcula EMA."""
        if len(prices) < period:
            return sum(prices) / len(prices)

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def analyze_signal(self, indicators: Dict) -> str:
        """
        Analisa indicadores e retorna sinal.
        Para Gold SELL, criterios mais rigorosos para maior consistencia.

        Returns:
            'BUY', 'SELL' ou 'NEUTRAL'
        """
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        current_price = indicators.get('current_price', 0)
        bb_upper = indicators.get('bb_upper', 0)
        bb_middle = indicators.get('bb_middle', 0)
        bb_lower = indicators.get('bb_lower', 0)
        trend = indicators.get('trend', 'NEUTRAL')

        buy_signals = 0
        sell_signals = 0

        # PARA GOLD: criterios otimizados para SELL (2.5+ sinais necessários)
        # Equilibra qualidade e frequência de entradas
        if self.is_gold or self.only_sell:
            # RSI - Prioridade para overbought, mas também conta undersold com Trend DOWN
            if rsi > 70:
                sell_signals += 2  # Super overbought - entrada forte
            elif rsi > 65:
                sell_signals += 1.5  # Overbought
            elif rsi > 55:
                sell_signals += 0.5  # Leve sinalizacao
            elif rsi < 50 and trend == 'DOWN':
                sell_signals += 0.5  # Se está caindo e RSI baixo = continuação da queda

            # MACD - Importante para confirmar momentum
            if macd_histogram is not None:
                if macd_histogram < -0.1:
                    sell_signals += 1.5  # Histogram claramente negativo
                elif macd_histogram < -0.05:
                    sell_signals += 1.0  # Negativo moderado
                elif macd_histogram < 0:
                    sell_signals += 0.75  # Levemente negativo
                else:
                    sell_signals += 0.25  # Positivo mas podemos aproveitar
            elif macd < -0.1:
                sell_signals += 1.0  # Fallback: MACD negativo

            # Bollinger Bands - preço próximo ao topo (entrada natural)
            bb_range = bb_upper - bb_lower
            distance_from_upper = bb_upper - current_price

            if current_price > bb_upper:
                sell_signals += 2  # Price acima da banda = reversal iminente
            elif distance_from_upper < (bb_range * 0.25):  # Últimos 25% (foi 20%)
                sell_signals += 1.0  # Próximo ao topo
            elif current_price > bb_middle:
                sell_signals += 0.75  # Acima do meio = média-alta (foi 0.5)

            # Trend - confirma direção (muito importante)
            if trend == 'DOWN':
                sell_signals += 1.5  # Downtrend em andamento (mantém importância)
            elif trend == 'NEUTRAL':
                sell_signals += 0

            # ATR - confirmação de volatilidade (importante para SL não apertar)
            atr = indicators.get('atr', 0)
            if atr > 12:  # ATR alto = volatilidade maior
                sell_signals += 0.5
            elif atr > 8:  # ATR médio = volatilidade normal
                sell_signals += 0.25

            # BUY - apenas rejeita (ja que only_sell=True para Gold)
            if rsi < 30:
                buy_signals += 3
            elif rsi < 45:
                buy_signals += 1

            # Decisão com criterios GOLD otimizados
            if self.only_sell:
                # Em modo SELL-ONLY, rejeita BUY automaticamente
                # 2.5 sinais para equilíbrio: qualidade + frequência
                # Permite combinações como: Trend(1.5) + MACD(0.5) + BB(0.5) = 2.5
                # Ainda mantém seletividade mas abre com mais frequência
                if sell_signals >= 2.5:
                    return 'SELL'
                else:
                    return 'NEUTRAL'
            else:
                if buy_signals >= 3 and buy_signals > sell_signals:
                    return 'BUY'
                elif sell_signals >= 3 and sell_signals > buy_signals:
                    return 'SELL'
                else:
                    return 'NEUTRAL'
        else:
            # Para outros symbols: logica original
            # RSI
            if rsi < 30:
                buy_signals += 2
            elif rsi > 70:
                sell_signals += 2
            elif rsi < 45:
                buy_signals += 1
            elif rsi > 55:
                sell_signals += 1

            # MACD
            if macd > 0:
                buy_signals += 1
            else:
                sell_signals += 1

            # Bollinger Bands
            if current_price < bb_lower:
                buy_signals += 1
            elif current_price > bb_upper:
                sell_signals += 1

            # Trend
            if trend == 'UP':
                buy_signals += 1
            elif trend == 'DOWN':
                sell_signals += 1

            # Decisão
            if buy_signals >= 3 and buy_signals > sell_signals:
                return 'BUY'
            elif sell_signals >= 3 and sell_signals > buy_signals:
                return 'SELL'
            else:
                return 'NEUTRAL'

    def get_minimum_sl_distance(self, symbol_info: Dict, current_price: float) -> float:
        """Calcula distância mínima de SL baseada nas regras do broker."""
        # Pegar stops_level do broker (distância mínima em pontos)
        stops_level = symbol_info.get('trade_stops_level', 0)
        point = symbol_info.get('point', 0.00001)

        # Converter stops_level para preço
        min_distance_broker = stops_level * point

        # Valores mínimos padrão por tipo de símbolo (como fallback)
        symbol = self.symbol.upper()
        if 'BTC' in symbol:
            min_distance_default = 250.0  # Bitcoin - aumentado para evitar stops prematuros
        elif 'XAU' in symbol or 'GOLD' in symbol:
            min_distance_default = 1.0   # Ouro
        elif 'JPY' in symbol:
            min_distance_default = 0.15   # Yen (cotação em 3 dígitos)
        else:
            # Forex padrão (EUR, GBP, etc)
            min_distance_default = 0.0015  # 15 pips

        # Usar o maior entre o mínimo do broker e o padrão
        min_distance = max(min_distance_broker, min_distance_default)

        # Garantir pelo menos 0.3% do preço como SL (aumentado de 0.1%)
        min_percentage = current_price * 0.003

        return max(min_distance, min_percentage)

    def open_position(self, signal: str, indicators: Dict) -> Optional[int]:
        """
        Abre uma posição com validacoes e otimizacoes para Gold.

        Para Gold (XAUUSDm):
        - Apenas SELL (rejeita BUY)
        - Preco deve estar entre $4050-$4100 (zona ideal)
        - Rejeita SELL acima de $4100 (zona perdedora)
        - TP de $3.5 com SL otimizado para R:R 1:1.5 (excelente ratio)
        """
        if self.daily_trades >= self.max_daily_trades:
            logger.warning(f"⚠️ Limite diário atingido: {self.daily_trades}/{self.max_daily_trades}")
            return None

        # ===== VALIDACOES GOLD-SPECIFIC =====

        # 1. Rejeitar BUY em modo SELL-ONLY
        if signal == 'BUY' and self.only_sell:
            logger.info(f"ℹ️  Rejeitando BUY: Modo SELL-ONLY ativado para {self.symbol}")
            return None

        current_price = indicators.get('current_price', 0)
        if current_price == 0:
            logger.error("Preço atual é 0, impossível abrir posição")
            return None

        # 2. Filtros de preco para Gold
        if self.is_gold and signal == 'SELL':
            # Rejeitar SELL acima de $4100 (zona perdedora)
            if current_price > 4100:
                logger.warning(f"⛔ Rejeitando SELL: Preco ${current_price:.2f} > $4100 (zona perdedora)")
                return None

            # Preferir zona ideal $4050-$4100
            if 4050 <= current_price <= 4100:
                logger.info(f"✅ Entrada na zona ideal: ${current_price:.2f} (entre $4050-$4100)")
            elif current_price < 4050:
                logger.info(f"ℹ️  Entrada abaixo da zona ideal: ${current_price:.2f} (< $4050)")

        # Obter informações do símbolo
        symbol_info = self.mt5.get_symbol_info(self.symbol)
        if not symbol_info:
            logger.error("Não foi possível obter informações do símbolo")
            return None

        # ===== CALCULAR SL E TP =====
        atr = indicators.get('atr', 0)

        # Obter informações do contrato para cálculo correto do TP
        contract_size = symbol_info.get('trade_contract_size', 1.0)
        point = symbol_info.get('point', 0.00001)

        if contract_size == 0 or self.volume == 0:
            logger.error(f"Valores inválidos: contract_size={contract_size}, volume={self.volume}")
            return None

        # Valor em $ de 1 ponto de movimento de preço para o volume atual
        point_value_for_volume = contract_size * self.volume

        # Distância do TP em pontos de preço
        tp_distance = self.target_profit / point_value_for_volume

        # ===== CALCULO DE SL =====
        # Para Gold e outros: SL baseado em ATR (mais realista e flexível)
        # Não usamos ratio apertado - deixamos espaço real para o mercado
        if atr > 0:
            sl_distance = atr * self.atr_multiplier
        else:
            # Fallback se ATR não disponível
            sl_distance = (current_price * 0.002) / point

        min_sl_distance = self.get_minimum_sl_distance(symbol_info, current_price)
        sl_distance = max(sl_distance, min_sl_distance)

        # Calcular ratio para log
        rr_ratio = (tp_distance / sl_distance) if sl_distance > 0 else 0

        logger.info(f"📏 SL & TP Calculation (Ordens Acertivas):")
        logger.info(f"   ATR: {atr:.5f} × {self.atr_multiplier} = {sl_distance:.5f}")
        logger.info(f"   SL Distance: ${sl_distance * point_value_for_volume:.2f}")
        logger.info(f"   TP Distance: ${self.target_profit:.2f}")
        logger.info(f"   Ratio R:R: 1:{rr_ratio:.2f}")

        # Garantir TP mínimo (já que aumentamos target_profit)
        tp_distance = max(tp_distance, 0.5)

        if signal == 'BUY':
            sl = current_price - sl_distance
            tp = current_price + tp_distance

            # Calcular R:R ratio e valores em $
            risk_in_price = sl_distance
            reward_in_price = tp_distance
            rr_ratio = reward_in_price / risk_in_price if risk_in_price > 0 else 0

            # Calcular risco em $ (distância × contract_size × volume)
            risk_in_dollars = sl_distance * point_value_for_volume
            sl_percentage = (sl_distance / current_price) * 100

            logger.info(f"🔵 Preparando COMPRA:")
            logger.info(f"   Preço: ${current_price:.2f}")
            logger.info(f"   SL: ${sl:.2f} (distância: ${sl_distance:.2f} = ${risk_in_dollars:.2f} = {sl_percentage:.2f}%)")
            logger.info(f"   TP: ${tp:.2f} (distância: ${tp_distance:.2f})")
            logger.info(f"   Lucro esperado: ${self.target_profit:.2f}")
            logger.info(f"   ⚖️  Risk/Reward: 1:{rr_ratio:.2f}")

            result = self.mt5.buy_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"Hedge_Agent_{self.daily_trades+1}"
            )
        else:  # SELL
            sl = current_price + sl_distance
            tp = current_price - tp_distance

            # Calcular R:R ratio e valores em $
            risk_in_price = sl_distance
            reward_in_price = tp_distance
            rr_ratio = reward_in_price / risk_in_price if risk_in_price > 0 else 0

            # Calcular risco em $ (distância × contract_size × volume)
            risk_in_dollars = sl_distance * point_value_for_volume
            sl_percentage = (sl_distance / current_price) * 100

            logger.info(f"🔴 Preparando VENDA:")
            logger.info(f"   Preço: ${current_price:.2f}")
            logger.info(f"   SL: ${sl:.2f} (distância: ${sl_distance:.2f} = ${risk_in_dollars:.2f} = {sl_percentage:.2f}%)")
            logger.info(f"   TP: ${tp:.2f} (distância: ${tp_distance:.2f})")
            logger.info(f"   Lucro esperado: ${self.target_profit:.2f}")
            logger.info(f"   ⚖️  Risk/Reward: 1:{rr_ratio:.2f}")

            result = self.mt5.sell_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"Hedge_Agent_{self.daily_trades+1}"
            )

        if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
            ticket = result.get('order')
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            self.open_tickets.add(ticket)
            self.trades_today.append({
                'ticket': ticket,
                'type': signal,
                'time': datetime.now(),
                'price': current_price,
                'sl': sl,
                'tp': tp
            })

            # Salvar SL/TP em backup (MT5 nao armazena isso nos deals)
            self.save_sl_tp_backup(ticket, sl, tp)

            logger.info(f"✅ Posição aberta: {signal} | Ticket: {ticket} | SL: {sl:.2f} | TP: {tp:.2f}")

            # 🔔 Notificação Telegram
            try:
                self.telegram.send_trade_opened(
                    ticket=ticket,
                    symbol=self.symbol,
                    trade_type=signal,
                    volume=self.volume,
                    entry_price=current_price,
                    tp=tp,
                    sl=sl,
                    indicators={
                        'rsi': indicators.get('rsi', 0),
                        'macd': indicators.get('macd', 0),
                        'trend': indicators.get('trend', 'N/A'),
                        'atr': atr
                    }
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar notificação Telegram: {e}")

            return ticket
        else:
            error = result.get('comment', 'Unknown error') if result else 'No result'
            logger.error(f"❌ Erro ao abrir posição: {error}")

            return None

    def open_hedge_position(self, signal: str, indicators: Dict, original_price: float) -> Optional[int]:
        """
        Abre uma posição de hedge com TP agressivo.

        Args:
            signal: 'BUY' ou 'SELL' (oposto à posição original)
            indicators: Indicadores de mercado
            original_price: Preço da posição original (para logging)

        Returns:
            Ticket da posição hedge ou None
        """
        # Obter informações do símbolo
        symbol_info = self.mt5.get_symbol_info(self.symbol)
        if not symbol_info:
            logger.error("Não foi possível obter informações do símbolo")
            return None

        # Calcular SL e TP para hedge
        atr = indicators.get('atr', 0)
        current_price = indicators.get('current_price', 0)

        if current_price == 0:
            logger.error("Preço atual é 0, impossível abrir hedge")
            return None

        # SL baseado em ATR (mesmo cálculo)
        sl_distance = atr * self.atr_multiplier if atr > 0 else 0
        min_sl_distance = self.get_minimum_sl_distance(symbol_info, current_price)
        sl_distance = max(sl_distance, min_sl_distance)

        # TP agressivo usando hedge_tp_target
        contract_size = symbol_info.get('trade_contract_size', 1.0)
        if contract_size == 0 or self.volume == 0:
            logger.error(f"Valores inválidos: contract_size={contract_size}, volume={self.volume}")
            return None

        point_value_for_volume = contract_size * self.volume
        tp_distance = self.hedge_tp_target / point_value_for_volume
        tp_distance = max(tp_distance, min_sl_distance)

        logger.info(f"🔄 HEDGE Position Calculation:")
        logger.info(f"   Original Price: {original_price:.5f}")
        logger.info(f"   Current Price: {current_price:.5f}")
        logger.info(f"   Hedge TP Target: ${self.hedge_tp_target:.2f}")
        logger.info(f"   TP Distance: {tp_distance:.5f}")

        if signal == 'BUY':
            sl = current_price - sl_distance
            tp = current_price + tp_distance

            logger.info(f"🔵 HEDGE COMPRA:")
            logger.info(f"   Preço: {current_price:.5f}")
            logger.info(f"   SL: {sl:.5f}")
            logger.info(f"   TP: {tp:.5f} (Lucro esperado: ${self.hedge_tp_target:.2f})")

            result = self.mt5.buy_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"HEDGE_DEFENSE_{self.daily_trades+1}"
            )
        else:  # SELL
            sl = current_price + sl_distance
            tp = current_price - tp_distance

            logger.info(f"🔴 HEDGE VENDA:")
            logger.info(f"   Preço: {current_price:.5f}")
            logger.info(f"   SL: {sl:.5f}")
            logger.info(f"   TP: {tp:.5f} (Lucro esperado: ${self.hedge_tp_target:.2f})")

            result = self.mt5.sell_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"HEDGE_DEFENSE_{self.daily_trades+1}"
            )

        if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
            ticket = result.get('order')
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            self.open_tickets.add(ticket)
            self.hedge_tickets.add(ticket)  # Marcar como hedge
            self.hedge_entry_price = current_price

            self.trades_today.append({
                'ticket': ticket,
                'type': signal,
                'time': datetime.now(),
                'price': current_price,
                'sl': sl,
                'tp': tp,
                'is_hedge': True
            })

            # Salvar SL/TP em backup (MT5 nao armazena isso nos deals)
            self.save_sl_tp_backup(ticket, sl, tp)

            logger.info(f"✅ Hedge aberto: {signal} | Ticket: {ticket} | TP: ${self.hedge_tp_target:.2f}")
            return ticket
        else:
            error = result.get('comment', 'Unknown error') if result else 'No result'
            logger.error(f"❌ Erro ao abrir hedge: {error}")
            return None

    def activate_hedge(self, original_ticket: int) -> Optional[int]:
        """Ativa estratégia de hedge com TP agressivo."""
        positions = self.mt5.positions_get(ticket=original_ticket)
        if not positions or len(positions) == 0:
            return None

        position = positions[0]
        original_price = position.get('price_open', 0)
        original_profit = position.get('profit', 0)

        # Abrir posição oposta
        opposite_signal = 'SELL' if position['type'] == 0 else 'BUY'

        logger.info(f"🔄 Ativando HEDGE para posição {original_ticket}")
        logger.info(f"   Prejuízo Original: ${original_profit:+.2f}")
        logger.info(f"   TP Hedge Target: ${self.hedge_tp_target:.2f}")

        # Obter indicadores atuais
        indicators = self.calculate_indicators()

        # Hedge com TP agressivo usando método específico
        hedge_ticket = self.open_hedge_position(opposite_signal, indicators, original_price)

        if hedge_ticket:
            self.hedge_active = True
            self.original_position_ticket = original_ticket
            self.hedge_position_ticket = hedge_ticket
            logger.info(f"✅ Hedge ativado: Original={original_ticket}, Hedge={hedge_ticket}")

        return hedge_ticket

    def check_hedge_status(self):
        """
        Verifica status do hedge e fecha par quando hedge atingir TP target.

        Returns:
            True se par foi fechado, False caso contrário
        """
        if not self.hedge_active:
            return False

        # Obter posições abertas
        hedge_position = None
        original_position = None

        positions = self.mt5.positions_get(symbol=self.symbol)
        if not positions:
            # Todas posições fechadas, resetar hedge
            self.hedge_active = False
            self.original_position_ticket = None
            self.hedge_position_ticket = None
            self.hedge_entry_price = None
            return False

        for pos in positions:
            if pos['ticket'] == self.hedge_position_ticket:
                hedge_position = pos
            if pos['ticket'] == self.original_position_ticket:
                original_position = pos

        # Se alguma das posições foi fechada (SL/TP), resetar hedge
        if not hedge_position or not original_position:
            logger.info(f"⚠️ Uma das posições do hedge foi fechada. Resetando hedge...")
            self.hedge_active = False
            self.original_position_ticket = None
            self.hedge_position_ticket = None
            self.hedge_entry_price = None
            return False

        # Verificar lucro do hedge
        hedge_profit = hedge_position.get('profit', 0)
        original_profit = original_position.get('profit', 0)
        total_profit = hedge_profit + original_profit

        logger.debug(f"💹 Hedge Status: Hedge={hedge_profit:+.2f} | Original={original_profit:+.2f} | Total={total_profit:+.2f}")

        # Condição de fechamento: hedge atingiu TP target
        if hedge_profit >= self.hedge_tp_target:
            logger.info(f"✅ Hedge atingiu TP de ${self.hedge_tp_target:.2f}! Fechando par...")
            logger.info(f"   Hedge: ${hedge_profit:+.2f}")
            logger.info(f"   Original: ${original_profit:+.2f}")
            logger.info(f"   Resultado Final: ${total_profit:+.2f}")

            # Fechar posição original
            original_type = original_position.get('type')
            original_close_signal = 'SELL' if original_type == 0 else 'BUY'

            logger.info(f"🔄 Fechando posição original #{self.original_position_ticket}...")
            close_original = self.mt5.close_position(ticket=self.original_position_ticket)

            # Fechar posição hedge
            hedge_type = hedge_position.get('type')
            hedge_close_signal = 'SELL' if hedge_type == 0 else 'BUY'

            logger.info(f"🔄 Fechando posição hedge #{self.hedge_position_ticket}...")
            close_hedge = self.mt5.close_position(ticket=self.hedge_position_ticket)

            if close_original and close_hedge:
                logger.info(f"✅ Par de hedge fechado com sucesso!")
                logger.info(f"   Resultado: ${total_profit:+.2f}")

                # Resetar flags de hedge
                self.hedge_active = False
                self.original_position_ticket = None
                self.hedge_position_ticket = None
                self.hedge_entry_price = None

                # Remover tickets do tracking
                self.open_tickets.discard(self.original_position_ticket)
                self.open_tickets.discard(self.hedge_position_ticket)
                self.hedge_tickets.discard(self.hedge_position_ticket)

                return True
            else:
                logger.error(f"❌ Erro ao fechar par de hedge")
                return False

        return False

    def check_and_reset_daily_counter(self):
        """Reseta contador diário à meia-noite."""
        now = datetime.now()

        if self.trades_today:
            first_trade_today = self.trades_today[0]['time']
            if first_trade_today.date() < now.date():
                logger.info(f"🔄 Novo dia! Resetando contador. Trades ontem: {self.daily_trades}")
                self.daily_trades = 0
                self.trades_today = []
                self.open_tickets.clear()
                self.hedge_tickets.clear()
                self.total_profit = 0.0
                self.winning_streak = 0

    def check_closed_positions(self):
        """
        Verifica se alguma posição foi fechada e atualiza métricas.
        Retorna lista de posições fechadas.
        """
        if not self.open_tickets:
            return []

        # Obter posições atualmente abertas
        current_positions = self.mt5.positions_get(symbol=self.symbol)
        current_tickets = set()
        if current_positions:
            current_tickets = {pos['ticket'] for pos in current_positions}

        # Detectar posições que foram fechadas
        closed_tickets = self.open_tickets - current_tickets

        if not closed_tickets:
            return []

        closed_positions = []

        for ticket in closed_tickets:
            # Buscar informações da posição fechada
            # Usar histórico de deals para obter resultado final
            deals = self.mt5.history_deals_get(ticket=ticket)

            # Profit será obtido dos deals se disponível
            profit = 0
            if deals and len(deals) >= 2:
                close_deal = deals[-1]
                profit = close_deal.get('profit', 0)
            else:
                logger.warning(f"⚠️  Posição #{ticket}: não conseguiu obter deals completos")

            # Encontrar trade original na lista (sempre tentar)
            trade_info = None
            for trade in self.trades_today:
                if trade['ticket'] == ticket:
                    trade_info = trade
                    break

            if trade_info is None:
                logger.warning(f"⚠️  Posição #{ticket}: não encontrada em trades_today")

            closed_positions.append({
                'ticket': ticket,
                'profit': profit,
                'trade_info': trade_info
            })

            # Atualizar métricas
            self.total_profit += profit

            if profit > 0:
                self.winning_streak += 1
                logger.info(f"✅ Posição #{ticket} fechada com LUCRO: ${profit:+.2f} | Streak: {self.winning_streak}")
            else:
                self.winning_streak = 0
                logger.info(f"❌ Posição #{ticket} fechada com PREJUÍZO: ${profit:+.2f} | Streak resetado")

            # Salvar no banco (mesmo se não tiver trade_info ou deals completos)
            logger.info(f"📝 Salvando trade #{ticket} no banco de dados...")
            self.save_trade_to_db(ticket, profit, trade_info)

            # 🔔 Notificação Telegram - Posição fechada
            try:
                if trade_info:
                    close_deal = deals[-1] if deals else {}
                    open_deal = deals[0] if deals else {}

                    # Calcular wins e losses
                    wins = sum(1 for t in self.trades_today if t.get('profit', 0) > 0)
                    losses = sum(1 for t in self.trades_today if t.get('profit', 0) <= 0)

                    # Obter info da conta
                    account_info = self.mt5.get_account_info()
                    account_balance = account_info.get('balance', 0) if account_info else 0

                    # Calcular percentual de lucro em relação ao balance
                    profit_percentage = (self.total_profit / account_balance * 100) if account_balance > 0 else 0

                    self.telegram.send_trade_closed(
                        ticket=ticket,
                        symbol=self.symbol,
                        trade_type=trade_info.get('type', 'UNKNOWN'),
                        entry_price=trade_info.get('price', 0),
                        close_price=close_deal.get('price', 0),
                        profit=profit,
                        duration_seconds=int((close_deal.get('time', 0) - open_deal.get('time', 0))),
                        daily_stats={
                            'total_profit': self.total_profit,
                            'win_rate': (wins / len(self.trades_today) * 100) if self.trades_today else 0,
                            'winning_streak': self.winning_streak,
                            'trades_count': self.daily_trades,
                            'wins': wins,
                            'losses': losses
                        },
                        total_wins=wins,
                        total_losses=losses,
                        account_balance=account_balance,
                        profit_percentage=profit_percentage
                    )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar notificação de fechamento Telegram: {e}")

            # Remover do tracking
            self.open_tickets.discard(ticket)
            self.hedge_tickets.discard(ticket)  # Remover se for hedge

        return closed_positions

    def save_trade_to_db(self, ticket: int, profit: float, trade_info: dict):
        """Salva trade no banco de dados com SL/TP sincronizados."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Tentar obter histórico completo do deal
            deals = self.mt5.history_deals_get(ticket=ticket)

            # Log de debug
            logger.debug(f"Tentando salvar trade #{ticket}: deals={deals}, trade_info={trade_info}")

            # Inicializar variáveis padrão
            open_price = 0
            close_price = 0
            volume = self.volume
            open_time = datetime.now().isoformat()
            close_time = datetime.now().isoformat()
            trade_type = 'UNKNOWN'
            sl = 0
            tp = 0

            # Se conseguir história completa, usar dados de lá
            if deals and len(deals) >= 2:
                open_deal = deals[0]
                close_deal = deals[-1]

                open_price = open_deal.get('price', 0)
                close_price = close_deal.get('price', 0)
                volume = open_deal.get('volume', 0) or self.volume  # Fallback para volume do agente

                # Extrair SL/TP dos deals (se disponível)
                # MT5 pode ter SL/TP em um campo específico
                sl = open_deal.get('sl', 0)
                tp = open_deal.get('tp', 0)

                # Converter timestamps com fallback
                try:
                    open_timestamp = open_deal.get('time', 0)
                    if open_timestamp and open_timestamp > 0:
                        open_time = datetime.fromtimestamp(open_timestamp).isoformat()
                    else:
                        open_time = datetime.now().isoformat()
                except:
                    open_time = datetime.now().isoformat()

                try:
                    close_timestamp = close_deal.get('time', 0)
                    if close_timestamp and close_timestamp > 0:
                        close_time = datetime.fromtimestamp(close_timestamp).isoformat()
                    else:
                        close_time = datetime.now().isoformat()
                except:
                    close_time = datetime.now().isoformat()

                logger.info(f"📊 Usando histórico de deals para ticket {ticket}")

            # Senão, usar dados de trade_info (fallback)
            if trade_info:
                # Usar trade_info como principal fonte de SL/TP
                open_price = trade_info.get('price', open_price)
                close_price = trade_info.get('close_price', open_price)
                sl = trade_info.get('sl', sl)  # Priorizar SL do trade_info
                tp = trade_info.get('tp', tp)  # Priorizar TP do trade_info
                trade_type = trade_info.get('type', 'UNKNOWN')

                # Converter time se for datetime object
                if 'time' in trade_info:
                    trade_time = trade_info.get('time', datetime.now())
                    if isinstance(trade_time, datetime):
                        open_time = trade_time.isoformat()
                    else:
                        open_time = str(trade_time)

                close_time = datetime.now().isoformat()

                logger.info(f"✅ Usando trade_info para ticket {ticket} com SL=${sl:.2f} e TP=${tp:.2f}")

            # Se não temos trade_info, log aviso
            else:
                logger.warning(f"⚠️  Posição #{ticket}: sem trade_info, usando dados de deals")
                trade_type = 'UNKNOWN'

            # Se SL/TP ainda estão zerados, tentar recuperar do backup
            if (sl == 0 or tp == 0) and ticket:
                backup_sl, backup_tp = self.load_sl_tp_from_backup(ticket)
                if backup_sl != 0 or backup_tp != 0:
                    sl = backup_sl if sl == 0 else sl
                    tp = backup_tp if tp == 0 else tp
                    logger.info(f"✅ SL/TP recuperado do backup para ticket {ticket}: SL=${sl:.2f} | TP=${tp:.2f}")

            # Salvar no banco
            cursor.execute("""
                INSERT INTO trades (
                    ticket, symbol, type, volume,
                    open_price, close_price, open_time, close_time,
                    sl, tp, profit, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket,
                self.symbol,
                trade_type,
                volume,
                open_price,
                close_price,
                open_time,
                close_time,
                sl,
                tp,
                profit,
                "BTC_Hedge_Agent"
            ))

            conn.commit()
            conn.close()

            # Log de sucesso com todos os detalhes
            logger.info(f"✅ Trade #{ticket} SALVO no banco:")
            logger.info(f"   Tipo: {trade_type} | Volume: {volume} lots | Lucro: ${profit:+.2f}")
            logger.info(f"   Entrada: ${open_price:.2f} → Saída: ${close_price:.2f}")
            logger.info(f"   SL: ${sl:.2f} | TP: ${tp:.2f}")

        except sqlite3.IntegrityError as e:
            logger.warning(f"⚠️  Trade #{ticket} já existe no banco de dados (duplicado)")
        except Exception as e:
            logger.error(f"❌ ERRO ao salvar trade #{ticket}: {e}", exc_info=True)
            logger.error(f"   Detalhes: ticket={ticket}, symbol={self.symbol}, trade_type={trade_type}, profit=${profit:.2f}")

    def get_status(self) -> Dict:
        """Retorna status atual do agente."""
        positions = self.mt5.positions_get(symbol=self.symbol)
        indicators = self.calculate_indicators()

        return {
            'agent': 'BTC_Hedge_Agent',
            'state': self.state.value,
            'symbol': self.symbol,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'total_profit': self.total_profit,
            'winning_streak': self.winning_streak,
            'hedge_active': self.hedge_active,
            'positions_count': len(positions) if positions else 0,
            'positions': positions if positions else [],
            'indicators': indicators,
            'last_trade': self.last_trade_time.isoformat() if self.last_trade_time else None
        }

    def export_to_json(self, indicators: Dict, positions: List):
        """
        Exporta dados do agente para JSON (lido pelo MT5 dashboard).

        Arquivo: C:\\mcp-trader\\agent_data.json
        """
        try:
            # Calcular lucro total das posições
            total_positions_profit = 0.0
            if positions:
                for pos in positions:
                    total_positions_profit += pos.get('profit', 0)

            data = {
                "agent": "BTC_Hedge_Agent",
                "state": self.state.value,
                "symbol": self.symbol,
                "daily_trades": self.daily_trades,
                "max_daily_trades": self.max_daily_trades,
                "total_profit": round(total_positions_profit, 2),
                "winning_streak": self.winning_streak,
                "hedge_active": self.hedge_active,
                "positions_count": len(positions) if positions else 0,
                "timestamp": datetime.now().isoformat(),
                # Indicadores
                "current_price": round(indicators.get('current_price', 0), 2),
                "trend": indicators.get('trend', 'NEUTRAL'),
                "rsi": round(indicators.get('rsi', 50), 1),
                "macd": round(indicators.get('macd', 0), 2),
                "atr": round(indicators.get('atr', 0), 2),
                "sma_20": round(indicators.get('sma_20', 0), 2),
                "sma_50": round(indicators.get('sma_50', 0), 2),
                "bb_upper": round(indicators.get('bb_upper', 0), 2),
                "bb_middle": round(indicators.get('bb_middle', 0), 2),
                "bb_lower": round(indicators.get('bb_lower', 0), 2)
            }

            json_path = Path('C:/mcp-trader/agent_data.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")

    def run(self):
        """Loop principal do agente."""
        logger.info("🚀 Iniciando agente de trading BTCUSD...")

        cycle = 0

        try:
            while self.state != AgentState.STOPPED:
                cycle += 1
                self.cycle_count += 1

                # Reset diário
                self.check_and_reset_daily_counter()

                # Calcular indicadores
                indicators = self.calculate_indicators()

                if not indicators:
                    logger.error("❌ Erro ao calcular indicadores")
                    time.sleep(self.check_interval)
                    continue

                # Verificar posições fechadas e atualizar métricas
                closed = self.check_closed_positions()

                # Verificar status do hedge (fechar par se TP atingido)
                self.check_hedge_status()

                # Obter posições abertas
                positions = self.mt5.positions_get(symbol=self.symbol)
                positions_count = len(positions) if positions else 0

                # LOG A CADA CICLO
                self.print_status(cycle, indicators, positions)

                # EXPORTAR DADOS PARA MT5 DASHBOARD
                self.export_to_json(indicators, positions)

                # 📱 Telegram simplificado: APENAS sinais (entrada) e ordens (saída)
                # Nenhuma outra notificação

                # Verificar se pode operar
                if self.daily_trades >= self.max_daily_trades:
                    logger.warning(f"⚠️  Limite diário atingido. Pausando...")
                    self.state = AgentState.PAUSED
                    time.sleep(self.check_interval)
                    continue

                # Analisar sinal
                signal = self.analyze_signal(indicators)

                # Verificar posições existentes
                if positions_count > 0:
                    # Verificar se precisa de hedge
                    for pos in positions:
                        profit = pos.get('profit', 0)

                        # Se estiver em prejuízo significativo e não tem hedge
                        if profit < self.hedge_trigger and not self.hedge_active:
                            logger.warning(f"⚠️  Posição em prejuízo: ${profit:.2f} (trigger: ${self.hedge_trigger})")
                            self.activate_hedge(pos['ticket'])

                # Contar apenas posições normais (não-hedge)
                normal_positions_count = 0
                if positions:
                    normal_positions_count = len([p for p in positions if p['ticket'] not in self.hedge_tickets])

                # Abrir nova posição SOMENTE se:
                # 1. Sinal válido (não NEUTRAL)
                # 2. Não houver posição normal aberta (normal_positions_count == 0)
                # 3. Não houver hedge ativo
                if signal != 'NEUTRAL' and normal_positions_count == 0 and not self.hedge_active:
                    logger.info(f"📊 Sinal {signal} detectado - Abrindo posição")
                    self.open_position(signal, indicators)
                elif signal != 'NEUTRAL' and normal_positions_count > 0:
                    logger.debug(f"⏸️  Sinal {signal} ignorado - Já existe {normal_positions_count} posição(ões) normal(is) aberta(s)")
                elif signal != 'NEUTRAL' and self.hedge_active:
                    logger.debug(f"⏸️  Sinal {signal} ignorado - Hedge ativo")

                # Aguardar próximo ciclo
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n⚠️  Agente interrompido pelo usuário")
            self.state = AgentState.STOPPED

        except Exception as e:
            logger.error(f"❌ Erro no agente: {e}", exc_info=True)
            self.state = AgentState.STOPPED

    def print_status(self, cycle: int, indicators: Dict, positions: List):
        """Imprime status detalhado."""
        print("\n" + "="*80)
        print(f"🤖 AGENTE BTC HEDGE | Ciclo #{cycle} | {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)

        # Agente
        print(f"\n📊 AGENTE:")
        print(f"   Estado: {self.state.value.upper()}")
        print(f"   Operações Hoje: {self.daily_trades}/{self.max_daily_trades}")
        print(f"   Lucro Total: ${self.total_profit:+.2f}")
        print(f"   Winning Streak: {self.winning_streak}")
        print(f"   Hedge Ativo: {'SIM' if self.hedge_active else 'NÃO'}")

        # Mercado
        print(f"\n📈 MERCADO ({self.symbol}):")
        print(f"   Preço: ${indicators.get('current_price', 0):.2f}")
        print(f"   Tendência: {indicators.get('trend', 'N/A')}")
        print(f"   RSI: {indicators.get('rsi', 0):.1f}")
        print(f"   MACD: {indicators.get('macd', 0):+.2f}")
        print(f"   ATR: {indicators.get('atr', 0):.2f}")
        print(f"   SMA20: ${indicators.get('sma_20', 0):.2f}")
        print(f"   SMA50: ${indicators.get('sma_50', 0):.2f}")

        # Posições
        normal_count = len([p for p in positions if p['ticket'] not in self.hedge_tickets]) if positions else 0
        hedge_count = len([p for p in positions if p['ticket'] in self.hedge_tickets]) if positions else 0

        print(f"\n💼 POSIÇÕES ABERTAS: {len(positions) if positions else 0} (Normal: {normal_count}, Hedge: {hedge_count})")
        if positions:
            total_profit = 0
            for i, pos in enumerate(positions, 1):
                profit = pos.get('profit', 0)
                total_profit += profit
                tipo = "COMPRA" if pos.get('type') == 0 else "VENDA"
                ticket = pos.get('ticket')
                is_hedge = ticket in self.hedge_tickets
                badge = "🛡️ HEDGE" if is_hedge else "📍 NORMAL"
                print(f"   {i}. {badge} | Ticket {ticket} | {tipo} | {pos.get('volume')} lots | Lucro: ${profit:+.2f}")
            print(f"   💰 TOTAL: ${total_profit:+.2f}")

        print("="*80 + "\n")


def main():
    """Função principal."""
    import argparse

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup database
    setup_database()

    # Parse argumentos
    parser = argparse.ArgumentParser(description='BTC Hedge Trading Agent')
    parser.add_argument('symbol', nargs='?', default='BTCUSDm',
                        help='Trading symbol (default: BTCUSDm)')
    parser.add_argument('--volume', type=float, default=0.02,
                        help='Trading volume in lots (default: 0.02)')
    parser.add_argument('--target-profit', type=float, default=None,
                        help='Target profit per trade in $ (default: depends on symbol)')
    parser.add_argument('--max-daily-trades', type=int, default=999,
                        help='Maximum daily trades (default: 999 - ilimitado)')
    parser.add_argument('--hedge-trigger', type=float, default=-10.0,
                        help='Prejuízo que ativa hedge em $ (default: -10.0)')
    parser.add_argument('--hedge-tp-target', type=float, default=8.0,
                        help='Lucro do hedge para fechar par em $ (default: 8.0)')
    parser.add_argument('--atr-multiplier', type=float, default=2.5,
                        help='Multiplicador do ATR para distância do SL (default: 2.5)')
    parser.add_argument('--only-sell', action='store_true',
                        help='Apenas SELL (rejeita BUY) - ideal para Gold')

    args = parser.parse_args()

    symbol = args.symbol
    volume = args.volume
    max_daily_trades = args.max_daily_trades
    hedge_trigger = args.hedge_trigger
    hedge_tp_target = args.hedge_tp_target
    atr_multiplier = args.atr_multiplier
    only_sell = args.only_sell

    # Target profit padrão por símbolo
    target_profit_map = {
        'BTCUSDm': 2.5,  # Aumentado de 2.0 para melhor R:R
        'XAUUSDm': 3.5,  # Ouro - OTIMIZADO (ganhos consistentes)
        'GBPUSDc': 2.0,  # Libra
        'EURUSDc': 2.0,  # Euro
        'USDJPYc': 2.0,  # Iene
    }
    target_profit = args.target_profit if args.target_profit else target_profit_map.get(symbol, 2.0)

    logger.info(f"Iniciando com símbolo: {symbol}, volume: {volume}, target_profit: ${target_profit}, max_daily_trades: {max_daily_trades}")
    logger.info(f"Hedge config: trigger=${hedge_trigger}, tp_target=${hedge_tp_target}")
    logger.info(f"SL config: ATR multiplier={atr_multiplier}x")
    if only_sell:
        logger.info(f"MODE: SELL-ONLY (rejeitara BUY signals)")

    agent = BTCHedgeAgent(
        symbol=symbol,
        volume=volume,
        target_profit=target_profit,
        max_daily_trades=max_daily_trades,
        check_interval=30,  # Aumentado de 30s para 60s (M15 requer menos frequência)
        hedge_trigger=hedge_trigger,
        hedge_tp_target=hedge_tp_target,
        atr_multiplier=atr_multiplier,
        only_sell=only_sell
    )

    # Executar
    agent.run()


if __name__ == "__main__":
    main()
