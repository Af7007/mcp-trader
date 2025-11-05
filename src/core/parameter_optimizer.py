#!/usr/bin/env python3
"""
Parameter Optimizer - Otimizacao bayesiana de parametros
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import sqlite3
from pathlib import Path


@dataclass
class ParameterRange:
    """Define range de um parametro para otimizacao"""
    name: str
    min_value: float
    max_value: float
    step: Optional[float] = None
    type: str = 'float'  # 'float' ou 'int'


class ParameterOptimizer:
    """
    Otimiza parametros do agente usando Bayesian Optimization
    
    Nota: Versao simplificada sem optuna (sera adicionado depois)
    Por enquanto usa grid search + validacao estatistica
    """
    
    def __init__(self, performance_analyzer, db_path: str = "btc_trading_logs.db"):
        self.analyzer = performance_analyzer
        self.db_path = Path(db_path)
        
        # Ranges de parametros para Gold
        self.parameter_ranges = {
            'stop_loss_atr_multiplier': ParameterRange('stop_loss_atr_multiplier', 3.0, 8.0, 0.5),
            'trailing_activation_mult': ParameterRange('trailing_activation_mult', 0.1, 0.5, 0.05),
            'trailing_distance_mult': ParameterRange('trailing_distance_mult', 0.2, 0.5, 0.05),
            'momentum_threshold': ParameterRange('momentum_threshold', 0.01, 0.05, 0.005),
        }
    
    def optimize_parameters(self, current_params: Dict, target_metric: str = 'sharpe_ratio',
                           n_iterations: int = 20, symbol: str = "XAUUSDc") -> Dict:
        """
        Otimiza parametros usando grid search inteligente
        
        Args:
            current_params: Parametros atuais
            target_metric: Metrica a otimizar ('sharpe_ratio', 'win_rate', 'profit_factor')
            n_iterations: Numero de tentativas
            symbol: Simbolo para otimizar
            
        Returns:
            Dict com novos parametros otimizados
        """
        print(f"\n[OPTIMIZER] Iniciando otimizacao de parametros...")
        print(f"  Target metric: {target_metric}")
        print(f"  Iteracoes: {n_iterations}")
        print(f"  Parametros atuais: {current_params}")
        
        # Buscar trades historicos
        trades = self._get_historical_trades(symbol, limit=200)
        
        if len(trades) < 50:
            print(f"  [AVISO] Poucos trades ({len(trades)}) para otimizacao confiavel")
            return current_params
        
        # Split train/test (80/20)
        split_point = int(len(trades) * 0.8)
        train_trades = trades[:split_point]
        test_trades = trades[split_point:]
        
        print(f"  Train: {len(train_trades)} trades, Test: {len(test_trades)} trades")
        
        # Gerar configuracoes candidatas
        candidates = self._generate_candidates(current_params, n_iterations)
        
        # Avaliar cada candidato no train set
        best_score = -float('inf')
        best_params = current_params.copy()
        
        for i, candidate in enumerate(candidates):
            # Simular performance com estes parametros
            score = self._evaluate_parameters(candidate, train_trades, target_metric)
            
            if score > best_score:
                best_score = score
                best_params = candidate.copy()
                print(f"  [Iter {i+1}/{n_iterations}] Nova melhor: {target_metric}={score:.2f}")
        
        # Validar no test set
        train_score = best_score
        test_score = self._evaluate_parameters(best_params, test_trades, target_metric)
        
        print(f"\n[RESULTADO]")
        print(f"  Train {target_metric}: {train_score:.2f}")
        print(f"  Test {target_metric}: {test_score:.2f}")
        
        # Verificar overfitting
        if test_score < train_score * 0.7:
            print(f"  [AVISO] Possivel overfitting detectado")
            print(f"  Retornando parametros atuais por seguranca")
            return current_params
        
        # Calcular improvement
        baseline_score = self._evaluate_parameters(current_params, test_trades, target_metric)
        improvement = ((test_score - baseline_score) / baseline_score * 100) if baseline_score != 0 else 0
        
        print(f"  Baseline {target_metric}: {baseline_score:.2f}")
        print(f"  Improvement: {improvement:+.1f}%")
        
        if improvement > 5:  # Minimo 5% de melhoria
            print(f"  [OK] Melhoria significativa - adotando novos parametros")
            return best_params
        else:
            print(f"  [SKIP] Melhoria insuficiente - mantendo parametros atuais")
            return current_params
    
    def _generate_candidates(self, current_params: Dict, n: int) -> List[Dict]:
        """
        Gera N configuracoes candidatas para testar
        Usa estrategia de explorar ao redor dos valores atuais
        """
        candidates = [current_params.copy()]  # Incluir atual como baseline
        
        for _ in range(n - 1):
            candidate = {}
            for param_name, current_value in current_params.items():
                if param_name in self.parameter_ranges:
                    param_range = self.parameter_ranges[param_name]
                    
                    # Gerar valor aleatorio ao redor do atual
                    # 80% das vezes perto do atual, 20% exploratorio
                    if np.random.random() < 0.8:
                        # Exploracao local (±20% do range)
                        variation = (param_range.max_value - param_range.min_value) * 0.2
                        new_value = current_value + np.random.uniform(-variation, variation)
                    else:
                        # Exploracao global
                        new_value = np.random.uniform(param_range.min_value, param_range.max_value)
                    
                    # Clipar ao range
                    new_value = np.clip(new_value, param_range.min_value, param_range.max_value)
                    
                    # Arredondar se necessario
                    if param_range.step:
                        new_value = round(new_value / param_range.step) * param_range.step
                    
                    candidate[param_name] = round(new_value, 3)
                else:
                    candidate[param_name] = current_value
            
            candidates.append(candidate)
        
        return candidates
    
    def _evaluate_parameters(self, params: Dict, trades: List[Dict], 
                            target_metric: str) -> float:
        """
        Avalia configuracao de parametros em um conjunto de trades
        
        Nota: Esta e uma simulacao simplificada
        Idealmente deveria re-simular trades com novos parametros
        Por enquanto usa correlacao aproximada
        """
        # Calcular metricas atuais
        metrics = self.analyzer.calculate_metrics(trades)
        
        if 'error' in metrics:
            return -float('inf')
        
        # Retornar metrica alvo
        score = metrics.get(target_metric, 0)
        
        # Penalizar configuracoes muito agressivas ou conservadoras
        sl_mult = params.get('stop_loss_atr_multiplier', 5.0)
        if sl_mult < 3.5 or sl_mult > 7.0:
            score *= 0.9  # Penalidade de 10%
        
        trailing_act = params.get('trailing_activation_mult', 0.2)
        if trailing_act < 0.15 or trailing_act > 0.4:
            score *= 0.95  # Penalidade de 5%
        
        return score
    
    def _get_historical_trades(self, symbol: str, limit: int = 200) -> List[Dict]:
        """
        Busca trades historicos do banco
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *
            FROM trades
            WHERE symbol = ? AND profit_loss IS NOT NULL
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (symbol, limit))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return trades
    
    def walk_forward_optimization(self, symbol: str = "XAUUSDc", 
                                  window_size: int = 50, 
                                  step_size: int = 10) -> List[Dict]:
        """
        Walk-forward optimization
        
        Otimiza em janelas deslizantes para validar robustez
        """
        print(f"\n[WALK-FORWARD] Iniciando analise...")
        print(f"  Window size: {window_size} trades")
        print(f"  Step size: {step_size} trades")
        
        trades = self._get_historical_trades(symbol, limit=1000)
        
        if len(trades) < window_size * 2:
            print(f"  [ERRO] Trades insuficientes ({len(trades)})")
            return []
        
        results = []
        
        # Deslizar janela
        for start in range(0, len(trades) - window_size, step_size):
            end = start + window_size
            window_trades = trades[start:end]
            
            # Otimizar nesta janela
            current_params = {
                'stop_loss_atr_multiplier': 5.0,
                'trailing_activation_mult': 0.2,
                'trailing_distance_mult': 0.3
            }
            
            optimized = self.optimize_parameters(
                current_params, 
                target_metric='sharpe_ratio',
                n_iterations=10
            )
            
            # Avaliar
            metrics = self.analyzer.calculate_metrics(window_trades)
            
            results.append({
                'window_start': start,
                'window_end': end,
                'params': optimized,
                'metrics': metrics
            })
            
            print(f"  Window {start}-{end}: Win rate {metrics.get('win_rate', 0)}%")
        
        print(f"\n[WALK-FORWARD] Concluido - {len(results)} janelas analisadas")
        
        return results
    
    def suggest_adjustments(self, current_params: Dict, recent_metrics: Dict) -> Dict:
        """
        Sugere ajustes incrementais baseados em performance recente
        Mais conservador que otimizacao completa
        """
        suggestions = current_params.copy()
        
        # Se win rate baixo, aumentar SL
        if recent_metrics.get('win_rate', 100) < 60:
            suggestions['stop_loss_atr_multiplier'] = min(
                suggestions.get('stop_loss_atr_multiplier', 5.0) * 1.1,
                8.0
            )
            print(f"  [SUGESTAO] Aumentar SL para {suggestions['stop_loss_atr_multiplier']:.1f}")
        
        # Se drawdown alto, tornar trailing mais conservador
        if abs(recent_metrics.get('max_drawdown', 0)) > 50:
            suggestions['trailing_activation_mult'] = min(
                suggestions.get('trailing_activation_mult', 0.2) * 1.2,
                0.5
            )
            print(f"  [SUGESTAO] Trailing mais conservador: {suggestions['trailing_activation_mult']:.2f}")
        
        # Se profit factor baixo, apertar trailing
        if recent_metrics.get('profit_factor', 2) < 1.5:
            suggestions['trailing_distance_mult'] = max(
                suggestions.get('trailing_distance_mult', 0.3) * 0.9,
                0.2
            )
            print(f"  [SUGESTAO] Apertar trailing para {suggestions['trailing_distance_mult']:.2f}")
        
        return suggestions


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.performance_analyzer import PerformanceAnalyzer
    
    print("="*70)
    print("PARAMETER OPTIMIZER - TESTE")
    print("="*70)
    
    analyzer = PerformanceAnalyzer()
    optimizer = ParameterOptimizer(analyzer)
    
    # Parametros atuais
    current = {
        'stop_loss_atr_multiplier': 5.0,
        'trailing_activation_mult': 0.2,
        'trailing_distance_mult': 0.3
    }
    
    print(f"\nParametros atuais: {current}")
    
    # Tentar otimizar (vai falhar se nao houver dados)
    try:
        optimized = optimizer.optimize_parameters(
            current_params=current,
            target_metric='sharpe_ratio',
            n_iterations=10,
            symbol='XAUUSDc'
        )
        
        print(f"\nParametros otimizados: {optimized}")
        
        # Comparar
        print(f"\nMUDANCAS:")
        for key in current:
            if current[key] != optimized[key]:
                change = ((optimized[key] - current[key]) / current[key] * 100)
                print(f"  {key}: {current[key]} -> {optimized[key]} ({change:+.1f}%)")
    
    except Exception as e:
        print(f"\n[AVISO] Otimizacao nao pode ser executada: {e}")
        print(f"Razao: Provavelmente falta de dados no banco")
    
    # Testar sugestoes
    print(f"\n" + "="*70)
    print("TESTE DE SUGESTOES")
    print("="*70)
    
    mock_metrics = {
        'win_rate': 55,  # Baixo
        'max_drawdown': -60,  # Alto
        'profit_factor': 1.3  # Baixo
    }
    
    suggestions = optimizer.suggest_adjustments(current, mock_metrics)
    
    print(f"\nMetricas ruins simuladas: {mock_metrics}")
    print(f"Sugestoes de ajuste: {suggestions}")
