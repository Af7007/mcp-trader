#!/usr/bin/env python3
"""
Performance Analyzer - Analisa trades e calcula metricas avancadas
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class PerformanceAnalyzer:
    """
    Analisa performance do agente e calcula metricas avancadas
    """
    
    def __init__(self, db_path: str = "btc_trading_logs.db"):
        self.db_path = Path(db_path)
        
    def analyze_recent_performance(self, n_trades: int = 100, symbol: str = "XAUUSDc") -> Dict:
        """
        Analisa performance dos ultimos N trades
        
        Returns:
            Dict com metricas: win_rate, profit_factor, sharpe_ratio, etc.
        """
        trades = self._get_recent_trades(n_trades, symbol)
        
        if not trades or len(trades) < 10:
            return {
                'error': 'Dados insuficientes',
                'n_trades': len(trades) if trades else 0
            }
        
        return self.calculate_metrics(trades)
    
    def calculate_metrics(self, trades: List[Dict]) -> Dict:
        """
        Calcula todas as metricas de performance
        """
        # Extrair profits
        profits = [t['profit_loss'] for t in trades if t['profit_loss'] is not None]
        
        if not profits:
            return {'error': 'Nenhum trade com profit_loss'}
        
        profits = np.array(profits)
        
        # Metricas basicas
        total_trades = len(profits)
        winning_trades = len([p for p in profits if p > 0])
        losing_trades = len([p for p in profits if p < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum([p for p in profits if p > 0])
        gross_loss = abs(sum([p for p in profits if p < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = gross_loss / losing_trades if losing_trades > 0 else 0
        expectancy = (win_rate/100 * avg_win) - ((1-win_rate/100) * avg_loss)
        
        # Sharpe Ratio (assumindo risk-free rate = 0)
        returns = profits
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        sharpe_ratio_annualized = sharpe_ratio * np.sqrt(252)  # 252 trading days
        
        # Max Drawdown
        cumulative = np.cumsum(profits)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Recovery Factor
        net_profit = np.sum(profits)
        recovery_factor = net_profit / abs(max_drawdown) if max_drawdown != 0 else float('inf')
        
        # Sortino Ratio (downside deviation)
        downside_returns = [p for p in profits if p < 0]
        downside_std = np.std(downside_returns) if downside_returns else 0
        sortino_ratio = np.mean(returns) / downside_std if downside_std > 0 else 0
        
        # Calmar Ratio (annual return / max drawdown)
        annual_return = np.mean(profits) * 252  # Assumindo 1 trade/dia
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else float('inf')
        
        # Consecutive wins/losses
        max_consecutive_wins = self._calculate_max_consecutive(profits, positive=True)
        max_consecutive_losses = self._calculate_max_consecutive(profits, positive=False)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'expectancy': round(expectancy, 2),
            'sharpe_ratio': round(sharpe_ratio_annualized, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'calmar_ratio': round(calmar_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'recovery_factor': round(recovery_factor, 2),
            'net_profit': round(net_profit, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'total_profit': round(net_profit, 2)
        }
    
    def detect_performance_degradation(self, window: int = 50, symbol: str = "XAUUSDc") -> Dict:
        """
        Detecta se performance esta piorando comparando janelas recentes
        """
        recent_trades = self._get_recent_trades(window, symbol)
        older_trades = self._get_recent_trades(window * 2, symbol)[window:]
        
        if not recent_trades or not older_trades:
            return {'degradation': False, 'reason': 'Dados insuficientes'}
        
        recent_metrics = self.calculate_metrics(recent_trades)
        older_metrics = self.calculate_metrics(older_trades)
        
        # Comparar metricas chave
        degradation = False
        reasons = []
        
        if recent_metrics['win_rate'] < older_metrics['win_rate'] - 10:
            degradation = True
            reasons.append(f"Win rate caiu de {older_metrics['win_rate']}% para {recent_metrics['win_rate']}%")
        
        if recent_metrics['profit_factor'] < older_metrics['profit_factor'] * 0.7:
            degradation = True
            reasons.append(f"Profit factor caiu de {older_metrics['profit_factor']} para {recent_metrics['profit_factor']}")
        
        if recent_metrics['sharpe_ratio'] < 0 and older_metrics['sharpe_ratio'] > 1:
            degradation = True
            reasons.append(f"Sharpe ratio deteriorou significativamente")
        
        return {
            'degradation': degradation,
            'reasons': reasons,
            'recent_metrics': recent_metrics,
            'older_metrics': older_metrics,
            'recommendation': 'Otimizar parametros' if degradation else 'Performance estavel'
        }
    
    def analyze_parameter_impact(self, parameter_name: str, symbol: str = "XAUUSDc") -> Dict:
        """
        Analisa impacto de um parametro especifico nos resultados
        
        Nota: Requer que parametros sejam salvos junto com trades
        """
        # TODO: Implementar quando houver tracking de parametros por trade
        return {
            'parameter': parameter_name,
            'status': 'Not implemented - requires parameter tracking'
        }
    
    def get_optimal_trading_hours(self, symbol: str = "XAUUSDc") -> List[int]:
        """
        Identifica melhores horarios (UTC) para trading baseado em historico
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                AVG(CASE WHEN profit_loss > 0 THEN 1.0 ELSE 0.0 END) as win_rate,
                COUNT(*) as trade_count
            FROM trades
            WHERE symbol = ? AND profit_loss IS NOT NULL
            GROUP BY hour
            HAVING trade_count >= 5
            ORDER BY win_rate DESC
        ''', (symbol,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Retornar top 8 horas (1/3 do dia)
        best_hours = [int(row[0]) for row in results[:8]]
        
        return sorted(best_hours)
    
    def _get_recent_trades(self, n: int, symbol: str) -> List[Dict]:
        """
        Busca N trades mais recentes do banco
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *
            FROM trades
            WHERE symbol = ? AND profit_loss IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, n))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return trades
    
    def _calculate_max_consecutive(self, profits: np.ndarray, positive: bool = True) -> int:
        """
        Calcula maxima sequencia consecutiva de wins ou losses
        """
        max_streak = 0
        current_streak = 0
        
        for profit in profits:
            if (positive and profit > 0) or (not positive and profit < 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def generate_report(self, symbol: str = "XAUUSDc", n_trades: int = 100) -> str:
        """
        Gera relatorio textual de performance
        """
        metrics = self.analyze_recent_performance(n_trades, symbol)
        degradation = self.detect_performance_degradation(50, symbol)
        best_hours = self.get_optimal_trading_hours(symbol)
        
        report = f"""
========================================
RELATORIO DE PERFORMANCE - {symbol}
========================================
Periodo: Ultimos {n_trades} trades

METRICAS PRINCIPAIS:
  Win Rate: {metrics.get('win_rate', 0)}%
  Profit Factor: {metrics.get('profit_factor', 0)}
  Sharpe Ratio: {metrics.get('sharpe_ratio', 0)}
  
LUCROS:
  Total: ${metrics.get('net_profit', 0)}
  Gross Profit: ${metrics.get('gross_profit', 0)}
  Gross Loss: ${metrics.get('gross_loss', 0)}
  
DRAWDOWN:
  Maximo: ${metrics.get('max_drawdown', 0)}
  Recovery Factor: {metrics.get('recovery_factor', 0)}
  
SEQUENCIAS:
  Max Wins Consecutivas: {metrics.get('max_consecutive_wins', 0)}
  Max Losses Consecutivas: {metrics.get('max_consecutive_losses', 0)}

DEGRADACAO:
  Status: {'DETECTADA' if degradation['degradation'] else 'NAO DETECTADA'}
  {'Razoes: ' + ', '.join(degradation['reasons']) if degradation['degradation'] else ''}

MELHORES HORARIOS (UTC):
  {', '.join([f'{h}:00' for h in best_hours])}

========================================
"""
        return report


if __name__ == "__main__":
    # Teste
    analyzer = PerformanceAnalyzer()
    
    print("Analisando performance...")
    metrics = analyzer.analyze_recent_performance(100, "XAUUSDc")
    
    print("\nMETRICAS:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n" + analyzer.generate_report("XAUUSDc", 100))
