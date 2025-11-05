#!/usr/bin/env python3
"""
Demonstracao do Sistema de Aprendizado Automatico
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.performance_analyzer import PerformanceAnalyzer
from core.optimization_logger import OptimizationLogger
from core.market_regime import MarketRegimeDetector
from core.mt5_direct_client import get_mt5_client

print("="*70)
print("DEMONSTRACAO - SISTEMA DE APRENDIZADO AUTOMATICO")
print("="*70)

# 1. Performance Analyzer
print("\n[1] PERFORMANCE ANALYZER")
print("-"*70)

analyzer = PerformanceAnalyzer()
print("Analisando ultimos 100 trades de XAUUSDc...")

metrics = analyzer.analyze_recent_performance(100, "XAUUSDc")

if 'error' not in metrics:
    print(f"\nMETRICAS PRINCIPAIS:")
    print(f"  Win Rate: {metrics['win_rate']}%")
    print(f"  Profit Factor: {metrics['profit_factor']}")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']}")
    print(f"  Net Profit: ${metrics['net_profit']}")
    print(f"  Max Drawdown: ${metrics['max_drawdown']}")
else:
    print(f"  {metrics['error']} (Trades encontrados: {metrics.get('n_trades', 0)})")
    print(f"  Nota: Precisa ter trades com profit_loss preenchido")

# Degradacao
print("\n[2] DETECCAO DE DEGRADACAO")
print("-"*70)

degradation = analyzer.detect_performance_degradation(50, "XAUUSDc")
print(f"Status: {degradation.get('recommendation', 'N/A')}")
if degradation.get('degradation'):
    print(f"Razoes: {', '.join(degradation['reasons'])}")

# 3. Optimization Logger
print("\n[3] OPTIMIZATION LOGGER")
print("-"*70)

opt_logger = OptimizationLogger()

# Registrar exemplo de mudanca de parametro
change_id = opt_logger.log_parameter_change(
    symbol="XAUUSDc",
    parameter_name="trailing_activation_mult",
    old_value=0.2,
    new_value=0.25,
    reason="Performance analyzer sugeriu ajuste",
    expected_improvement=5.0
)
print(f"Mudanca de parametro registrada - ID: {change_id}")

# Registrar exemplo de otimizacao
opt_id = opt_logger.log_optimization(
    symbol="XAUUSDc",
    optimization_type="MANUAL_DEMO",
    parameters={
        'sl_mult': 5.0,
        'trailing_act': 0.25,
        'trailing_dist': 0.3
    },
    metrics_before={
        'win_rate': 72,
        'profit_factor': 1.8
    },
    metrics_after={
        'win_rate': 76,
        'profit_factor': 2.1
    },
    success=True,
    notes="Demo de otimizacao"
)
print(f"Otimizacao registrada - ID: {opt_id}")

# 4. Market Regime Detector
print("\n[4] MARKET REGIME DETECTOR")
print("-"*70)

mt5 = get_mt5_client()
regime_detector = MarketRegimeDetector(mt5, "XAUUSDc")

regime = regime_detector.detect_current_regime()
print(f"Regime Atual: {regime['regime']}")
print(f"Confidence: {regime['confidence']}")
print(f"Descricao: {regime['description']}")
print(f"Estrategia Recomendada: {regime['recommended_strategy']}")
print(f"\nIndicadores:")
for key, value in regime['indicators'].items():
    print(f"  {key}: {value}")

# Registrar regime no logger
regime_id = opt_logger.log_regime_detection(
    symbol="XAUUSDc",
    regime_type=regime['regime'],
    confidence=regime['confidence'],
    indicators=regime['indicators'],
    recommended_strategy=regime['recommended_strategy'],
    applied=False
)
print(f"\nRegime registrado no banco - ID: {regime_id}")

# 5. Historico
print("\n[5] HISTORICO DE OTIMIZACOES")
print("-"*70)

recent = opt_logger.get_recent_optimizations("XAUUSDc", limit=5)
print(f"Total de otimizacoes registradas: {len(recent)}")

if recent:
    print("\nUltimas otimizacoes:")
    for opt in recent[:3]:
        print(f"  {opt['timestamp']}: {opt['optimization_type']} - {'SUCCESS' if opt['success'] else 'FAILED'}")

# 6. Parametros
param_history = opt_logger.get_parameter_history("XAUUSDc")
print(f"\n[6] HISTORICO DE PARAMETROS")
print("-"*70)
print(f"Total de mudancas de parametros: {len(param_history)}")

if param_history:
    print("\nUltimas mudancas:")
    for change in param_history[:3]:
        print(f"  {change['parameter_name']}: {change['old_value']} -> {change['new_value']}")
        print(f"    Razao: {change['reason']}")

print("\n" + "="*70)
print("DEMONSTRACAO CONCLUIDA")
print("="*70)
print("\nCOMPONENTES IMPLEMENTADOS:")
print("  [OK] PerformanceAnalyzer - Analisa metricas avancadas")
print("  [OK] OptimizationLogger - Registra mudancas e otimizacoes")
print("  [OK] MarketRegimeDetector - Detecta regime de mercado")
print("  [PENDENTE] ParameterOptimizer - Otimizacao bayesiana")
print("  [PENDENTE] AdaptiveStrategyManager - Gerencia multiplas estrategias")
print("  [PENDENTE] GoldAdaptiveAgent - Agente com auto-tuning")
print("\nPROXIMOS PASSOS:")
print("  1. Implementar ParameterOptimizer (Fase 3)")
print("  2. Criar AdaptiveStrategyManager")
print("  3. Desenvolver GoldAdaptiveAgent")
print("  4. Criar dashboard web para visualizacao")
print("  5. Testar sistema completo com trades reais")
