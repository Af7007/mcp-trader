#!/usr/bin/env python3
"""
Hedge Agent - Sistema especializado para estratégias de hedge multi-ativo
Implementa proteção através de correlação entre pares correlacionados
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class HedgeType(str, Enum):
    """Tipos de estratégias de hedge"""
    CORRELATION_HEDGE = "CORRELATION_HEDGE"  # Hedge baseado em correlação
    OPPORTUNITY_HEDGE = "OPPORTUNITY_HEDGE"  # Hedge aproveitando divergências
    MARKET_NEUTRAL = "MARKET_NEUTRAL"     # Posição neutra ao mercado
    PROTECTIVE_COLLAR = "PROTECTIVE_COLLAR" # Proteção bilateral


class HedgeAgent:
    """
    Agente especializado em estratégias de hedge
    Opera com múltiplos ativos visando proteção/redução de risco
    """

    def __init__(self, config):
        self.config = config
        self.hedge_type = self._determine_hedge_type()
        self.correlation_cache = {}
        self.positions = {}  # Symbol -> position_data
        self.hedge_positions = {}  # Hedge pairs tracking
        logger.info(f"🎯 Hedge Agent initialized: {config.name} ({self.hedge_type.value})")

    def _determine_hedge_type(self) -> HedgeType:
        """Determinar tipo de estrategia baseado na configuração"""
        symbols = self.config.hedge_symbols or []

        if len(symbols) == 2 and self.config.strategy == "HEDGE_PAIR":
            return HedgeType.CORRELATION_HEDGE
        elif len(symbols) > 2:
            return HedgeType.MARKET_NEUTRAL
        else:
            return HedgeType.CORRELATION_HEDGE

    def analyze_hedge_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisar dados de mercado e gerar sinais de hedge

        Args:
            market_data: Dados de mercado para todos os símbolos

        Returns:
            Dict com análise e recomendações
        """
        try:
            symbols = self.config.hedge_symbols or []
            if len(symbols) < 2:
                return {'error': 'Hedge requires at least 2 symbols'}

            # Calcular correlações
            correlations = self._calculate_correlations(market_data)

            # Análise por tipo de hedge
            if self.hedge_type == HedgeType.CORRELATION_HEDGE:
                return self._analyze_correlation_hedge(market_data, correlations)
            elif self.hedge_type == HedgeType.MARKET_NEUTRAL:
                return self._analyze_market_neutral_hedge(market_data, correlations)
            else:
                return self._analyze_correlation_hedge(market_data, correlations)

        except Exception as e:
            logger.error(f"❌ Error analyzing hedge signal: {e}")
            return {'error': str(e)}

    def _calculate_correlations(self, market_data: Dict[str, Any],
                               periods: int = 20) -> Dict[str, float]:
        """Calcular correlações entre pares de ativos"""
        correlations = {}
        symbols = list(market_data.keys())

        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                key = f"{sym1}_{sym2}"

                # Obter dados de preços
                prices1 = self._extract_prices(market_data[sym1])
                prices2 = self._extract_prices(market_data[sym2])

                if len(prices1) >= periods and len(prices2) >= periods:
                    # Calcular correlação das últimas 'periods' barras
                    price_data1 = prices1[-periods:]
                    price_data2 = prices2[-periods:]

                    corr = np.corrcoef(price_data1, price_data2)[0, 1]
                    correlations[key] = corr
                    self.correlation_cache[key] = corr

        return correlations

    def _extract_prices(self, symbol_data: Dict[str, Any]) -> List[float]:
        """Extrair preços de fechamento dos dados de símbolo"""
        if 'close' in symbol_data:
            return symbol_data['close']
        elif 'rates' in symbol_data and isinstance(symbol_data['rates'], list):
            return [rate.get('close', rate.get('price', 0)) for rate in symbol_data['rates']]
        else:
            return []

    def _analyze_correlation_hedge(self, market_data: Dict[str, Any],
                                  correlations: Dict[str, float]) -> Dict[str, Any]:
        """Analisar estratégia de hedge baseada em correlação"""
        symbols = self.config.hedge_symbols or []
        correlation_threshold = self.config.correlation_threshold

        main_symbol = symbols[0]
        hedge_symbol = symbols[1] if len(symbols) > 1 else None

        if not hedge_symbol:
            return {'error': 'Need at least 2 symbols for correlation hedge'}

        key = f"{main_symbol}_{hedge_symbol}"
        correlation = correlations.get(key, 0)

        # Verificar indicadores técnicos
        main_signals = self._get_technical_signals(market_data.get(main_symbol, {}))
        hedge_signals = self._get_technical_signals(market_data.get(hedge_symbol, {}))

        # Lógica de hedge baseada em divergências
        hedge_signal = self._calculate_hedge_signal(
            main_signals, hedge_signals, correlation, correlation_threshold
        )

        return {
            'strategy': 'correlation_hedge',
            'main_symbol': main_symbol,
            'hedge_symbol': hedge_symbol,
            'correlation': correlation,
            'correlation_threshold': correlation_threshold,
            'main_signals': main_signals,
            'hedge_signals': hedge_signals,
            'hedge_signal': hedge_signal,
            'recommendation': self._generate_hedge_recommendation(hedge_signal, symbols)
        }

    def _analyze_market_neutral_hedge(self, market_data: Dict[str, Any],
                                     correlations: Dict[str, float]) -> Dict[str, Any]:
        """Analisar estratégia market neutral com múltiplos ativos"""
        symbols = self.config.hedge_symbols or []

        # Calcular pesos para neutralizar exposição
        weights = self._calculate_market_neutral_weights(market_data, symbols)

        # Verificar se posição está equilibrada
        position_balance = self._check_market_neutral_balance(weights)

        return {
            'strategy': 'market_neutral',
            'symbols': symbols,
            'weights': weights,
            'balance_score': position_balance,
            'is_neutral': abs(position_balance) < 0.1,
            'recommendation': self._generate_market_neutral_recommendation(position_balance, weights)
        }

    def _get_technical_signals(self, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrair sinais técnicos dos indicadores configurados"""
        signals = {}

        # Verificar se temos dados suficientes
        if not symbol_data or 'close' not in symbol_data:
            return signals

        prices = symbol_data['close']
        if len(prices) < 2:
            return signals

        # Aplicar indicadores configurados
        for indicator in self.config.indicators:
            signal = self._calculate_indicator_signal(indicator, symbol_data)
            signals[indicator.type.value] = signal

        return signals

    def _calculate_indicator_signal(self, indicator, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular sinal de um indicador específico"""
        if indicator.type == "RSI":
            return self._calculate_rsi_signal(indicator, symbol_data)
        elif indicator.type == "BOLLINGER":
            return self._calculate_bollinger_signal(indicator, symbol_data)
        elif indicator.type == "MA":
            return self._calculate_ma_signal(indicator, symbol_data)
        else:
            return {'signal': 'NEUTRAL', 'value': None, 'description': f'Unsupported indicator: {indicator.type}'}

    def _calculate_rsi_signal(self, indicator, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular sinal RSI"""
        # Implementação simplificada (em produção usaria biblioteca como talib)
        if 'close' not in symbol_data or len(symbol_data['close']) < indicator.period + 1:
            return {'signal': 'NEUTRAL', 'value': None, 'description': 'Insufficient data'}

        prices = symbol_data['close']

        # Calcular RSI aproximado
        gains = []
        losses = []

        for i in range(len(prices) - 1, len(prices) - indicator.period - 1, -1):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Gerar sinal baseado nos thresholds
        if rsi < indicator.threshold_low:
            signal = 'BUY'
        elif rsi > indicator.threshold_high:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'

        return {
            'signal': signal,
            'value': rsi,
            'description': f'RSI({indicator.period}) = {rsi:.2f}, Threshold Low: {indicator.threshold_low}, High: {indicator.threshold_high}'
        }

    def _calculate_bollinger_signal(self, indicator, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular sinal Bollinger Bands (implementação básica)"""
        if 'close' not in symbol_data or len(symbol_data['close']) < indicator.period:
            return {'signal': 'NEUTRAL', 'value': None, 'description': 'Insufficient data'}

        prices = symbol_data['close']
        ma_period = min(indicator.period, len(prices))

        # Calcular média móvel simples
        sma = sum(prices[-ma_period:]) / ma_period

        # Calcular desvio padrão (aproximação)
        variance = sum([(price - sma) ** 2 for price in prices[-ma_period:]]) / ma_period
        std = variance ** 0.5

        # Bandas de Bollinger (aproximadamente ±2 std)
        upper_band = sma + 2 * std
        lower_band = sma - 2 * std

        current_price = prices[-1]

        # Análise de toque nas bandas
        if current_price <= lower_band:
            signal = 'BUY'
        elif current_price >= upper_band:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'

        return {
            'signal': signal,
            'value': current_price,
            'bands': {'upper': upper_band, 'middle': sma, 'lower': lower_band},
            'description': f'Bollinger: Price {current_price:.4f}, Upper {upper_band:.4f}, Lower {lower_band:.4f}'
        }

    def _calculate_ma_signal(self, indicator, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular sinal de Moving Average"""
        if 'close' not in symbol_data or len(symbol_data['close']) < indicator.period * 2:
            return {'signal': 'NEUTRAL', 'value': None, 'description': 'Insufficient data'}

        prices = symbol_data['close']

        # Calcular MA
        ma_values = []
        for i in range(indicator.period, len(prices) + 1):
            ma = sum(prices[i-indicator.period:i]) / indicator.period
            ma_values.append(ma)

        current_price = prices[-1]
        current_ma = ma_values[-1] if ma_values else current_price

        # Simples crossover (preço vs MA)
        if current_price > current_ma:
            signal = 'BUY'
        elif current_price < current_ma:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'

        return {
            'signal': signal,
            'value': current_price,
            'ma_value': current_ma,
            'description': f'MA({indicator.period}): Price {current_price:.4f}, MA {current_ma:.4f}'
        }

    def _calculate_hedge_signal(self, main_signals: Dict, hedge_signals: Dict,
                               correlation: float, threshold: float) -> Dict[str, Any]:
        """Calcular sinal de hedge baseado em correlação e divergências"""

        # Verificar se os sinais principais são divergentes
        main_consensus = self._get_consensus_signal(main_signals)
        hedge_consensus = self._get_consensus_signal(hedge_signals)

        # Análise básica de divergência
        divergence_score = 0
        if main_consensus != hedge_consensus:
            divergence_score = 1  # Sinal de oportunidade de hedge

        # Fator de correlação (quanto menor, melhor para hedge)
        correlation_factor = max(0, 1 - correlation / threshold) if correlation < threshold else 0

        # Combinar fatores
        hedge_score = (divergence_score + correlation_factor) / 2

        # Determinar tipo de hedge recomendado
        if hedge_score > 0.5:
            hedge_action = 'OPEN_HEDGE'
            if correlation > 0:  # Correlação positiva - posição inversa
                hedge_type = 'INVERSE_POSITION'
            else:  # Correlação negativa - mesma direção
                hedge_type = 'SAME_DIRECTION'
        elif hedge_score > 0.3:
            hedge_action = 'MONITOR'
            hedge_type = 'NEUTRAL'
        else:
            hedge_action = 'NO_HEDGE'
            hedge_type = 'NEUTRAL'

        return {
            'hedge_score': hedge_score,
            'hedge_action': hedge_action,
            'hedge_type': hedge_type,
            'divergence_score': divergence_score,
            'correlation_factor': correlation_factor,
            'main_consensus': main_consensus,
            'hedge_consensus': hedge_consensus
        }

    def _get_consensus_signal(self, signals: Dict[str, Any]) -> str:
        """Obter sinal consensado dos indicadores"""
        buy_count = 0
        sell_count = 0

        for signal_data in signals.values():
            if isinstance(signal_data, dict) and 'signal' in signal_data:
                signal = signal_data['signal']
                if signal == 'BUY':
                    buy_count += 1
                elif signal == 'SELL':
                    sell_count += 1

        if buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'NEUTRAL'

    def _generate_hedge_recommendation(self, hedge_signal: Dict, symbols: List[str]) -> str:
        """Gerar recomendação de ação baseada no sinal de hedge"""
        action = hedge_signal.get('hedge_action', 'NO_HEDGE')

        if action == 'OPEN_HEDGE':
            main_symbol, hedge_symbol = symbols[0], symbols[1]
            hedge_type = hedge_signal.get('hedge_type', 'UNKNOWN')

            if hedge_type == 'INVERSE_POSITION':
                return f"Abrir posições opostas em {main_symbol} e {hedge_symbol} para proteção"
            elif hedge_type == 'SAME_DIRECTION':
                return f"Abrir posições na mesma direção em {main_symbol} e {hedge_symbol}"

        return "Monitorar sinais - nenhuma ação de hedge necessária"

    def _calculate_market_neutral_weights(self, market_data: Dict, symbols: List[str]) -> Dict[str, float]:
        """Calcular pesos para estratégia market neutral"""
        weights = {}

        for symbol in symbols:
            # Peso baseado na volatilidade inversa (menores pesos para ativos mais voláteis)
            data = market_data.get(symbol, {})
            prices = self._extract_prices(data)

            if len(prices) > 1:
                # Calcular volatilidade
                changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility = np.mean(changes) if changes else 0.001
            else:
                volatility = 0.001

            # Weight inversamente proporcional à volatilidade
            weights[symbol] = 1 / volatility

        # Normalizar pesos
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {symbol: weight/total_weight for symbol, weight in weights.items()}

        return weights

    def _check_market_neutral_balance(self, weights: Dict[str, float]) -> float:
        """Verificar se os pesos estão equilibrados para neutralidade"""
        # Ideal: todos os pesos próximos de 1/n_symbols
        n_symbols = len(weights)
        if n_symbols == 0:
            return 1.0

        equal_weight = 1.0 / n_symbols
        balance_deviations = [abs(weight - equal_weight) for weight in weights.values()]

        return np.mean(balance_deviations)

    def _generate_market_neutral_recommendation(self, balance_score: float,
                                              weights: Dict[str, float]) -> str:
        """Gerar recomendação para estratégia market neutral"""
        if abs(balance_score) < 0.1:
            return "Posição equilibrada - manter estratégia"
        else:
            # Identificar desequilíbrios
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            heaviest = sorted_weights[0][0]
            lightest = sorted_weights[-1][0]

            return f"Rebalancear: reduzir exposição em {heaviest}, aumentar em {lightest}"

    def execute_hedge_trade(self, hedge_analysis: Dict[str, Any]) -> bool:
        """
        Executar trade baseado na análise de hedge
        Integra com sistema MT5 via MCP
        """
        try:
            recommendation = hedge_analysis.get('recommendation', '')

            if 'Abrir posições opostas' in recommendation:
                # Implementar lógica de abertura de hedge
                logger.info(f"🎯 Executing hedge trade: {recommendation}")
                return self._open_hedge_positions(hedge_analysis)
            elif 'Abrir posições na mesma direção' in recommendation:
                logger.info(f"🎯 Executing correlated positions: {recommendation}")
                return self._open_correlated_positions(hedge_analysis)
            else:
                logger.info(f"📊 Monitoring only: {recommendation}")
                return True  # Sucesso - apenas monitorar

        except Exception as e:
            logger.error(f"❌ Error executing hedge trade: {e}")
            return False

    def _open_hedge_positions(self, hedge_analysis: Dict[str, Any]) -> bool:
        """Abrir posições de hedge opostas"""
        # Placeholder - implementar integração com MT5 MCP
        logger.info("🔄 Opening hedge positions (placeholder)")
        return True

    def _open_correlated_positions(self, hedge_analysis: Dict[str, Any]) -> bool:
        """Abrir posições correlacionadas"""
        # Placeholder - implementar integração com MT5 MCP
        logger.info("🔄 Opening correlated positions (placeholder)")
        return True
