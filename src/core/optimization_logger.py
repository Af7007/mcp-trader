#!/usr/bin/env python3
"""
Optimization Logger - Registra mudancas de parametros e otimizacoes
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class OptimizationLogger:
    """
    Logger para sistema de otimizacao automatica
    """
    
    def __init__(self, db_path: str = "btc_trading_logs.db"):
        self.db_path = Path(db_path)
        self._init_tables()
    
    def _init_tables(self):
        """
        Cria tabelas para otimizacao se nao existirem
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de historico de parametros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parameter_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                old_value REAL,
                new_value REAL,
                reason TEXT,
                expected_improvement REAL,
                actual_improvement REAL,
                trades_before_change INTEGER,
                trades_after_change INTEGER,
                status TEXT,  -- 'APPLIED', 'TESTING', 'REVERTED'
                agent_version TEXT
            )
        ''')
        
        # Tabela de otimizacoes completas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                optimization_type TEXT,  -- 'BAYESIAN', 'GRID_SEARCH', 'MANUAL'
                parameters_json TEXT,  -- JSON com todos os parametros
                metrics_before_json TEXT,  -- Metricas antes da otimizacao
                metrics_after_json TEXT,  -- Metricas depois
                improvement_percent REAL,
                success BOOLEAN,
                notes TEXT,
                agent_version TEXT
            )
        ''')
        
        # Tabela de deteccao de regime
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regime_detection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                regime_type TEXT,  -- 'TRENDING', 'RANGING', 'HIGH_VOL', 'LOW_VOL'
                confidence REAL,
                indicators_json TEXT,  -- JSON com indicadores usados
                recommended_strategy TEXT,
                applied BOOLEAN,
                agent_version TEXT
            )
        ''')
        
        # Tabela de A/B testing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_testing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                test_name TEXT NOT NULL,
                config_a_json TEXT,  -- Configuracao A (baseline)
                config_b_json TEXT,  -- Configuracao B (teste)
                trades_a INTEGER,
                trades_b INTEGER,
                win_rate_a REAL,
                win_rate_b REAL,
                profit_factor_a REAL,
                profit_factor_b REAL,
                winner TEXT,  -- 'A', 'B', 'INCONCLUSIVE'
                p_value REAL,
                status TEXT,  -- 'RUNNING', 'COMPLETED', 'ADOPTED'
                agent_version TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_parameter_change(self, symbol: str, parameter_name: str, old_value: float,
                           new_value: float, reason: str, expected_improvement: float = None) -> int:
        """
        Registra mudanca de parametro
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO parameter_changes (
                symbol, parameter_name, old_value, new_value, reason,
                expected_improvement, status, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, 'APPLIED', '2.0')
        ''', (symbol, parameter_name, old_value, new_value, reason, expected_improvement))
        
        change_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return change_id
    
    def update_parameter_change_result(self, change_id: int, actual_improvement: float,
                                      trades_after: int, status: str = 'APPLIED'):
        """
        Atualiza resultado de uma mudanca de parametro
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE parameter_changes
            SET actual_improvement = ?, trades_after_change = ?, status = ?
            WHERE id = ?
        ''', (actual_improvement, trades_after, status, change_id))
        
        conn.commit()
        conn.close()
    
    def log_optimization(self, symbol: str, optimization_type: str, parameters: Dict,
                        metrics_before: Dict, metrics_after: Dict = None,
                        success: bool = None, notes: str = None) -> int:
        """
        Registra uma otimizacao completa
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        improvement = None
        if metrics_before and metrics_after:
            improvement = (
                (metrics_after.get('win_rate', 0) - metrics_before.get('win_rate', 0))
                / metrics_before.get('win_rate', 1) * 100
            )
        
        cursor.execute('''
            INSERT INTO optimization_history (
                symbol, optimization_type, parameters_json, metrics_before_json,
                metrics_after_json, improvement_percent, success, notes, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '2.0')
        ''', (
            symbol, optimization_type, json.dumps(parameters),
            json.dumps(metrics_before), json.dumps(metrics_after) if metrics_after else None,
            improvement, success, notes
        ))
        
        opt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return opt_id
    
    def log_regime_detection(self, symbol: str, regime_type: str, confidence: float,
                            indicators: Dict, recommended_strategy: str = None,
                            applied: bool = False) -> int:
        """
        Registra deteccao de regime de mercado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO regime_detection (
                symbol, regime_type, confidence, indicators_json,
                recommended_strategy, applied, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, '2.0')
        ''', (symbol, regime_type, confidence, json.dumps(indicators),
              recommended_strategy, applied))
        
        regime_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return regime_id
    
    def start_ab_test(self, symbol: str, test_name: str, config_a: Dict, config_b: Dict) -> int:
        """
        Inicia novo A/B test
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_testing (
                symbol, test_name, config_a_json, config_b_json,
                status, agent_version
            ) VALUES (?, ?, ?, ?, 'RUNNING', '2.0')
        ''', (symbol, test_name, json.dumps(config_a), json.dumps(config_b)))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return test_id
    
    def update_ab_test_results(self, test_id: int, trades_a: int, trades_b: int,
                               win_rate_a: float, win_rate_b: float,
                               profit_factor_a: float, profit_factor_b: float,
                               p_value: float = None):
        """
        Atualiza resultados de A/B test
        """
        # Determinar vencedor
        winner = 'INCONCLUSIVE'
        if p_value and p_value < 0.05:
            if win_rate_b > win_rate_a and profit_factor_b > profit_factor_a:
                winner = 'B'
            elif win_rate_a > win_rate_b and profit_factor_a > profit_factor_b:
                winner = 'A'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ab_testing
            SET trades_a = ?, trades_b = ?, win_rate_a = ?, win_rate_b = ?,
                profit_factor_a = ?, profit_factor_b = ?, winner = ?, p_value = ?,
                status = 'COMPLETED'
            WHERE id = ?
        ''', (trades_a, trades_b, win_rate_a, win_rate_b, profit_factor_a,
              profit_factor_b, winner, p_value, test_id))
        
        conn.commit()
        conn.close()
        
        return winner
    
    def get_recent_optimizations(self, symbol: str, limit: int = 10) -> list:
        """
        Retorna otimizacoes recentes
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM optimization_history
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_parameter_history(self, symbol: str, parameter_name: str = None) -> list:
        """
        Retorna historico de mudancas de parametros
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if parameter_name:
            cursor.execute('''
                SELECT * FROM parameter_changes
                WHERE symbol = ? AND parameter_name = ?
                ORDER BY timestamp DESC
            ''', (symbol, parameter_name))
        else:
            cursor.execute('''
                SELECT * FROM parameter_changes
                WHERE symbol = ?
                ORDER BY timestamp DESC
            ''', (symbol,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results


if __name__ == "__main__":
    # Teste
    logger = OptimizationLogger()
    print("Tabelas de otimizacao criadas com sucesso!")
    
    # Testar log de parametro
    change_id = logger.log_parameter_change(
        symbol="XAUUSDc",
        parameter_name="stop_loss_atr_multiplier",
        old_value=5.0,
        new_value=4.5,
        reason="Otimizacao automatica - reduzir stops prematuros",
        expected_improvement=5.0
    )
    print(f"Mudanca de parametro registrada - ID: {change_id}")
    
    # Testar log de regime
    regime_id = logger.log_regime_detection(
        symbol="XAUUSDc",
        regime_type="TRENDING",
        confidence=0.85,
        indicators={'adx': 28, 'bb_width': 0.015},
        recommended_strategy="increase_trailing_activation"
    )
    print(f"Regime detectado registrado - ID: {regime_id}")
