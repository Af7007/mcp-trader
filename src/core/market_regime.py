#!/usr/bin/env python3
"""
Market Regime Detector - Detecta mudancas no comportamento do mercado
"""

import numpy as np
from typing import Dict, Tuple
from enum import Enum


class MarketRegime(Enum):
    """Tipos de regime de mercado"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    UNKNOWN = "UNKNOWN"


class MarketRegimeDetector:
    """
    Detecta regime atual do mercado usando multiplos indicadores
    """
    
    def __init__(self, mt5_client, symbol: str):
        self.mt5 = mt5_client
        self.symbol = symbol
    
    def detect_current_regime(self, lookback: int = 100) -> Dict:
        """
        Detecta regime atual do mercado
        
        Returns:
            Dict com regime, confidence e indicadores
        """
        # Obter dados
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="H1",  # 1 hora para regime detection
            start_pos=0,
            count=lookback
        )
        
        if not rates or len(rates) < lookback:
            return {
                'regime': MarketRegime.UNKNOWN,
                'confidence': 0.0,
                'reason': 'Dados insuficientes'
            }
        
        # Calcular indicadores
        adx_value, di_plus, di_minus = self._calculate_adx(rates)
        bb_width = self._calculate_bb_width(rates)
        hurst_exp = self._calculate_hurst_exponent(rates)
        trend_strength = self._calculate_trend_strength(rates)
        
        # Detectar regime
        regime, confidence = self._classify_regime(
            adx_value, bb_width, hurst_exp, trend_strength, di_plus, di_minus
        )
        
        # Estrategia recomendada
        strategy = self._recommend_strategy(regime)
        
        return {
            'regime': regime.value,
            'confidence': round(confidence, 2),
            'indicators': {
                'adx': round(adx_value, 2),
                'bb_width': round(bb_width, 4),
                'hurst_exponent': round(hurst_exp, 2),
                'trend_strength': round(trend_strength, 2),
                'di_plus': round(di_plus, 2),
                'di_minus': round(di_minus, 2)
            },
            'recommended_strategy': strategy,
            'description': self._get_regime_description(regime)
        }
    
    def _calculate_adx(self, rates, period: int = 14) -> Tuple[float, float, float]:
        """
        Calcula ADX (Average Directional Index) e DI+/DI-
        ADX > 25 indica trending, < 20 indica ranging
        """
        highs = np.array([r['high'] for r in rates])
        lows = np.array([r['low'] for r in rates])
        closes = np.array([r['close'] for r in rates])
        
        # Calcular True Range
        tr = np.maximum(
            highs[1:] - lows[1:],
            np.maximum(
                np.abs(highs[1:] - closes[:-1]),
                np.abs(lows[1:] - closes[:-1])
            )
        )
        
        # Calcular +DM e -DM
        plus_dm = np.maximum(highs[1:] - highs[:-1], 0)
        minus_dm = np.maximum(lows[:-1] - lows[1:], 0)
        
        # Zerar quando movimento oposto eh maior
        plus_dm[minus_dm > plus_dm] = 0
        minus_dm[plus_dm > minus_dm] = 0
        
        # Smooth com EMA
        atr = self._ema(tr, period)
        plus_di = 100 * self._ema(plus_dm, period) / atr
        minus_di = 100 * self._ema(minus_dm, period) / atr
        
        # Calcular DX e ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = self._ema(dx, period)
        
        return adx[-1] if len(adx) > 0 else 0, plus_di[-1] if len(plus_di) > 0 else 0, minus_di[-1] if len(minus_di) > 0 else 0
    
    def _calculate_bb_width(self, rates, period: int = 20) -> float:
        """
        Calcula largura das Bollinger Bands (normalizada)
        Largura alta = alta volatilidade
        """
        closes = np.array([r['close'] for r in rates[-period:]])
        
        sma = np.mean(closes)
        std = np.std(closes)
        
        bb_upper = sma + (2 * std)
        bb_lower = sma - (2 * std)
        
        # Normalizar pela SMA
        bb_width = (bb_upper - bb_lower) / sma
        
        return bb_width
    
    def _calculate_hurst_exponent(self, rates, max_lag: int = 20) -> float:
        """
        Calcula Hurst Exponent
        H < 0.5 = mean reverting (ranging)
        H = 0.5 = random walk
        H > 0.5 = trending
        """
        closes = np.array([r['close'] for r in rates])
        
        # Calcular log returns
        log_returns = np.diff(np.log(closes))
        
        if len(log_returns) < max_lag:
            return 0.5
        
        # Calcular R/S para diferentes lags
        lags = range(2, max_lag)
        tau = []
        
        for lag in lags:
            # Dividir serie em chunks
            chunks = [log_returns[i:i+lag] for i in range(0, len(log_returns), lag)]
            chunks = [c for c in chunks if len(c) == lag]
            
            if not chunks:
                continue
            
            # Calcular R/S para cada chunk
            rs_values = []
            for chunk in chunks:
                mean = np.mean(chunk)
                deviations = chunk - mean
                cumsum = np.cumsum(deviations)
                r = np.max(cumsum) - np.min(cumsum)
                s = np.std(chunk)
                if s > 0:
                    rs_values.append(r / s)
            
            if rs_values:
                tau.append(np.mean(rs_values))
        
        if len(tau) < 2:
            return 0.5
        
        # Regressao linear log(tau) vs log(lag)
        log_lags = np.log(list(lags[:len(tau)]))
        log_tau = np.log(tau)
        
        hurst = np.polyfit(log_lags, log_tau, 1)[0]
        
        return max(0.0, min(1.0, hurst))
    
    def _calculate_trend_strength(self, rates, period: int = 50) -> float:
        """
        Calcula forca da tendencia usando regressao linear
        1.0 = forte uptrend, -1.0 = forte downtrend, 0 = sem tendencia
        """
        closes = np.array([r['close'] for r in rates[-period:]])
        
        x = np.arange(len(closes))
        slope, _ = np.polyfit(x, closes, 1)
        
        # Normalizar pelo preco medio
        trend_strength = slope / np.mean(closes) * period
        
        return np.clip(trend_strength, -1.0, 1.0)
    
    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calcula Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        
        return ema
    
    def _classify_regime(self, adx: float, bb_width: float, hurst: float,
                        trend: float, di_plus: float, di_minus: float) -> Tuple[MarketRegime, float]:
        """
        Classifica regime baseado nos indicadores
        """
        confidence = 0.0
        regime = MarketRegime.UNKNOWN
        
        # Detectar TRENDING
        if adx > 25:
            if di_plus > di_minus and trend > 0.3:
                regime = MarketRegime.TRENDING_UP
                confidence = min(1.0, adx / 40 + abs(trend))
            elif di_minus > di_plus and trend < -0.3:
                regime = MarketRegime.TRENDING_DOWN
                confidence = min(1.0, adx / 40 + abs(trend))
        
        # Detectar RANGING (overrides trending se hurst baixo)
        if hurst < 0.4 and adx < 20:
            regime = MarketRegime.RANGING
            confidence = 1.0 - hurst
        
        # Detectar HIGH/LOW VOLATILITY
        if bb_width > 0.03:  # Alta volatilidade
            if regime == MarketRegime.UNKNOWN:
                regime = MarketRegime.HIGH_VOLATILITY
            confidence = min(1.0, confidence + 0.2)
        elif bb_width < 0.01:  # Baixa volatilidade
            if regime == MarketRegime.UNKNOWN:
                regime = MarketRegime.LOW_VOLATILITY
            confidence = 0.6
        
        return regime, confidence
    
    def _recommend_strategy(self, regime: MarketRegime) -> str:
        """
        Recomenda estrategia baseada no regime
        """
        recommendations = {
            MarketRegime.TRENDING_UP: "trend_following_buy",
            MarketRegime.TRENDING_DOWN: "trend_following_sell",
            MarketRegime.RANGING: "mean_reversion",
            MarketRegime.HIGH_VOLATILITY: "wider_stops_smaller_size",
            MarketRegime.LOW_VOLATILITY: "tighter_stops_larger_size",
            MarketRegime.UNKNOWN: "conservative_baseline"
        }
        
        return recommendations.get(regime, "conservative_baseline")
    
    def _get_regime_description(self, regime: MarketRegime) -> str:
        """
        Retorna descricao do regime
        """
        descriptions = {
            MarketRegime.TRENDING_UP: "Mercado em forte tendencia de alta",
            MarketRegime.TRENDING_DOWN: "Mercado em forte tendencia de baixa",
            MarketRegime.RANGING: "Mercado lateral/consolidando",
            MarketRegime.HIGH_VOLATILITY: "Alta volatilidade - movimentos bruscos",
            MarketRegime.LOW_VOLATILITY: "Baixa volatilidade - mercado calmo",
            MarketRegime.UNKNOWN: "Regime indeterminado"
        }
        
        return descriptions.get(regime, "Desconhecido")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.mt5_direct_client import get_mt5_client
    
    mt5 = get_mt5_client()
    detector = MarketRegimeDetector(mt5, "XAUUSDc")
    
    print("Detectando regime de mercado para XAUUSDc...")
    regime = detector.detect_current_regime()
    
    print(f"\nREGIME DETECTADO:")
    print(f"  Tipo: {regime['regime']}")
    print(f"  Confidence: {regime['confidence']}")
    print(f"  Descricao: {regime['description']}")
    print(f"  Estrategia Recomendada: {regime['recommended_strategy']}")
    print(f"\nINDICADORES:")
    for key, value in regime['indicators'].items():
        print(f"  {key}: {value}")
