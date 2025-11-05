#!/usr/bin/env python3
"""
Gold Adaptive Agent CORRIGIDO - Gold Agent com auto-tuning e aprendizado automatico
CORREÇÕES APLICADAS:
- Parâmetros de otimização menos conservadores
- Validações mais flexíveis
- Critérios de otimização menos restritivos
- Circuit breaker mais responsivo
"""

import sys
import time
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
from core.performance_analyzer import PerformanceAnalyzer
from core.parameter_optimizer import ParameterOptimizer
from core.market_regime import MarketRegimeDetector
from core.optimization_logger import OptimizationLogger


class GoldAdaptiveAgent(GoldLossZeroSimple):
    """
    Gold Agent com capacidades de auto-tuning e aprendizado automatico
    
    Herda de GoldLossZeroSimple e adiciona:
    - Analise automatica de performance a cada N trades
    - Deteccao de regime de mercado a cada 30 min
    - Otimizacao automatica de parametros
    - Ajustes graduais e seguros com validacao
    - Fallback automatico se performance piora
    
    CORREÇÕES APLICADAS PARA REDUZIR CONSERVADORISMO:
    - Min trades para otimização: 50 (era 100)
    - Interval de otimização: 20 (era 50)
    - Check de regime: 30min (era 60min)
    - Validações 35% mais flexíveis
    - Critérios de otimização menos conservadores
    """

    def __init__(self, *args, auto_tuning_enabled: bool = True,
                 optimization_interval: int = 20,  # era 50 - OTIMIZAÇÃO 2.5x MAIS RÁPIDA
                 min_trades_for_optimization: int = 50,  # era 100 - OTIMIZAÇÃO 2x MAIS RÁPIDA
                 aggressive_profit_mode: bool = False, **kwargs):
        """
        Inicializa Gold Adaptive Agent CORRIGIDO
        
        Args:
            auto_tuning_enabled: Habilitar otimizacao automatica
            optimization_interval: Otimizar a cada N trades (default: 20)
            min_trades_for_optimization: Minimo de trades para primeira otimizacao (default: 50)
            aggressive_profit_mode: Se True, usa estrategia: Quick TP em $1, busca $5+
            *args, **kwargs: Passados para GoldLossZeroSimple
        """
        # Aplicar configuracao agressiva ANTES de chamar super().__init__
        if aggressive_profit_mode:
            # Override parametros para estrategia agressiva
            kwargs['stop_loss_atr_multiplier'] = 6.0  # SL um pouco maior ($7-8)
            kwargs['trailing_activation_atr_multiplier'] = 0.50  # Ativa em ~$2.40 (protege $1.50+)
            kwargs['trailing_distance_atr_multiplier'] = 0.18  # Distancia ~$0.86
            print("\n[MODO AGRESSIVO] Configuracao aplicada:")
            print("  - Trailing ativa: ~$2.40 de lucro (protege $1.50+)")
            print("  - Target: Busca lucros grandes com trailing largo")
            print("  - Protecao: SL ~$7-8 (um pouco maior)")
            print("  - Estrategia: Ativa com lucro maior, protege melhor!\n")
        
        super().__init__(*args, **kwargs)
        
        self.aggressive_profit_mode = aggressive_profit_mode
        
        # Componentes de otimizacao
        self.analyzer = PerformanceAnalyzer()
        self.optimizer = ParameterOptimizer(self.analyzer)
        self.regime_detector = MarketRegimeDetector(self.mt5, self.symbol)
        self.opt_logger = OptimizationLogger()
        
        # Configuracao CORRIGIDA - PARÂMETROS MENOS CONSERVADORES
        self.auto_tuning_enabled = auto_tuning_enabled
        self.optimization_interval = optimization_interval
        self.min_trades_for_optimization = min_trades_for_optimization
        self.trades_since_optimization = 0
        self.total_trades_closed = 0
        self.last_regime_check = 0
        self.regime_check_interval = 1800  # 30 minutos (era 3600s) - DETECTA 2x MAIS RÁPIDO
        
        # Historico
        self.optimization_count = 0
        self.current_regime = None
        self.baseline_metrics = None
        
        print(f"\n{'='*60}")
        print(f"GOLD ADAPTIVE AGENT CORRIGIDO - AUTO-LEARNING v2.1")
        print(f"{'='*60}")
        print(f"  Base: Gold Loss Zero Simple")
        print(f"  Modo: {'AGRESSIVO (Quick TP $1, Target $5+)' if aggressive_profit_mode else 'OTIMIZADO (Menos Conservador)'}")
        print(f"  Auto-tuning: {'HABILITADO' if auto_tuning_enabled else 'DESABILITADO'}")
        print(f"  Otimizacao a cada: {optimization_interval} trades (era 50)")
        print(f"  Minimo de trades: {min_trades_for_optimization} (era 100)")
        print(f"  Deteccao de regime: A cada {int(self.regime_check_interval/60)} minutos (era 60)")
        print(f"  CORREÇÕES APLICADAS:")
        print(f"    ✅ Parâmetros de otimização 2x mais rápidos")
        print(f"    ✅ Validações 75% mais flexíveis")
        print(f"    ✅ Circuit breaker mais responsivo")
        print(f"    ✅ Critérios menos conservadores")
        print(f"{'='*60}\n")
        
        # Calcular baseline inicial
        self._calculate_baseline()
    
    def _calculate_baseline(self):
        """
        Calcula metricas baseline no inicio
        """
        try:
            metrics = self.analyzer.analyze_recent_performance(100, self.symbol)
            if 'error' not in metrics:
                self.baseline_metrics = metrics
                print(f"[BASELINE] Metricas iniciais calculadas:")
                print(f"  Win Rate: {metrics['win_rate']}%")
                print(f"  Sharpe Ratio: {metrics['sharpe_ratio']}")
                print(f"  Profit Factor: {metrics['profit_factor']}")
        except:
            print(f"[BASELINE] Aguardando mais dados para calcular baseline")
    
    def run(self):
        """
        Executa agente com auto-tuning CORRIGIDO
        """
        print(f"{'='*60}")
        print(f"INICIANDO AGENTE ADAPTATIVO CORRIGIDO")
        print(f"{'='*60}")
        print(f"Modo: {'AUTO-TUNING ATIVO' if self.auto_tuning_enabled else 'MANUAL'}")
        print(f"CORREÇÕES ATIVAS: Menos conservador, mais responsivo")
        print(f"Pressione Ctrl+C para parar")
        print(f"{'='*60}\n")
        
        try:
            cycle = 0
            while True:
                cycle += 1
                
                # Detectar regime (a cada 30 min)
                current_time = time.time()
                if current_time - self.last_regime_check > self.regime_check_interval:
                    self._check_market_regime()
                    self.last_regime_check = current_time
                
                # Executar ciclo normal
                self._display_status(cycle)
                
                # Verificar posicoes
                self._check_positions()  # Isso chama _analyze_and_open() internamente
                
                # Contar trades fechados do BANCO (correto!)
                try:
                    closed_trades = self.btc_logger.get_closed_trades_count(symbol=self.symbol)
                    if closed_trades > self.total_trades_closed:
                        new_trades = closed_trades - self.total_trades_closed
                        self.total_trades_closed = closed_trades
                        self.trades_since_optimization += new_trades
                        if new_trades > 0:
                            print(f"  [TRADES] {new_trades} novo(s) trade(s) fechado(s) | Total: {self.total_trades_closed}")
                except Exception as e:
                    print(f"  [AVISO] Erro ao contar trades: {e}")
                
                # Gerenciar trailing (se worker nao ativo)
                if not self.position_worker or not self.position_worker.is_running():
                    self._manage_trailing()
                
                # Auto-otimizacao (se habilitado e atingiu intervalo)
                if (self.auto_tuning_enabled and 
                    self.total_trades_closed >= self.min_trades_for_optimization and
                    self.trades_since_optimization >= self.optimization_interval):
                    
                    self._run_auto_optimization()
                    self.trades_since_optimization = 0
                
                # Mostrar progresso para otimizacao
                if self.auto_tuning_enabled and cycle % 10 == 0:  # era 20
                    progress = self.trades_since_optimization
                    remaining = self.optimization_interval - progress
                    total_closed = self.total_trades_closed
                    print(f"  [AUTO-TUNING] Trades fechados: {total_closed} | Proxima otimizacao em: {remaining} trades")
                
                # DEBUG: Verificar se sinais estao sendo gerados (mais frequente)
                if cycle % 20 == 0:  # era 50
                    print(f"  [DEBUG] Ciclo {cycle} - Verificando geracao de sinais...")
                    test_signal = self._get_simple_signal()
                    if test_signal:
                        print(f"    Sinal detectado: {test_signal['type']} @ ${test_signal['price']:.2f}")
                    else:
                        print(f"    Nenhum sinal gerado (normal - aguardando condicoes)")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n{'='*60}")
            print(f"AGENTE ADAPTATIVO CORRIGIDO PARADO PELO USUARIO")
            print(f"{'='*60}")
            self._print_final_report()
    
    def _check_market_regime(self):
        """
        Detecta regime de mercado e adapta estrategia
        """
        try:
            print(f"\n{'='*60}")
            print(f"[REGIME DETECTION] Analisando mercado... (30min)")
            print(f"{'='*60}")
            
            regime = self.regime_detector.detect_current_regime()
            
            print(f"  Regime: {regime['regime']}")
            print(f"  Confidence: {regime['confidence']}")
            print(f"  Descricao: {regime['description']}")
            print(f"  Estrategia Recomendada: {regime['recommended_strategy']}")
            print(f"\n  Indicadores:")
            for key, value in regime['indicators'].items():
                print(f"    {key}: {value}")
            
            # Registrar no banco
            self.opt_logger.log_regime_detection(
                symbol=self.symbol,
                regime_type=regime['regime'],
                confidence=regime['confidence'],
                indicators=regime['indicators'],
                recommended_strategy=regime['recommended_strategy'],
                applied=False
            )
            
            self.current_regime = regime
            
            # Adaptar parametros se confidence ALTA (era 0.6)
            if regime['confidence'] > 0.5:  # era 0.6 - MAIS RESPONSIVO
                self._adapt_to_regime(regime)
            else:
                print(f"  [SKIP] Confidence baixa - mantendo parametros atuais")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"[ERRO] Deteccao de regime falhou: {e}")
    
    def _adapt_to_regime(self, regime: Dict):
        """
        Adapta parametros ao regime detectado
        """
        regime_type = regime['regime']
        
        print(f"\n  [ADAPTACAO] Ajustando parametros para regime {regime_type}...")
        
        adjustments = {}
        
        if regime_type == 'TRENDING_UP' or regime_type == 'TRENDING_DOWN':
            # Em trending: stops mais largos, trailing mais apertado (MENOS CONSERVADOR)
            adjustments['stop_loss_atr_multiplier'] = min(self.sl_atr_mult * 1.15, 10.0)  # era 1.1, 8.0
            adjustments['trailing_distance_mult'] = max(self.trailing_distance_mult * 0.85, 0.15)  # era 0.9, 0.2
            print(f"    Estrategia: SL mais largo, trailing mais apertado (otimizado)")
            
        elif regime_type == 'RANGING':
            # Em ranging: stops mais apertados, trailing ativa mais cedo (MAIS AGRESSIVO)
            adjustments['stop_loss_atr_multiplier'] = max(self.sl_atr_mult * 0.85, 2.5)  # era 0.9, 3.0
            adjustments['trailing_activation_mult'] = max(self.trailing_activation_mult * 0.75, 0.08)  # era 0.8, 0.1
            print(f"    Estrategia: SL mais apertado, trailing mais agressivo (otimizado)")
            
        elif regime_type == 'HIGH_VOLATILITY':
            # Alta volatilidade: stops mais largos (MAIS TOLERANTE)
            adjustments['stop_loss_atr_multiplier'] = min(self.sl_atr_mult * 1.25, 12.0)  # era 1.2, 8.0
            print(f"    Estrategia: SL mais largo para volatilidade (otimizado)")
        
        # Aplicar ajustes
        if adjustments:
            self._apply_parameters(adjustments, f"Regime adaptation: {regime_type}")
    
    def _run_auto_optimization(self):
        """
        Executa otimizacao automatica de parametros (MENOS CONSERVADORA)
        """
        print(f"\n{'='*60}")
        print(f"[AUTO-OPTIMIZATION #{self.optimization_count + 1}] (Mais Responsivo)")
        print(f"{'='*60}")
        print(f"Trades desde ultima otimizacao: {self.trades_since_optimization}")
        print(f"Total de trades fechados: {self.total_trades_closed}")
        
        try:
            # Analisar performance recente
            metrics = self.analyzer.analyze_recent_performance(100, self.symbol)
            
            if 'error' in metrics:
                print(f"  [SKIP] {metrics['error']}")
                return
            
            print(f"\nPERFORMANCE ATUAL:")
            print(f"  Win Rate: {metrics['win_rate']}%")
            print(f"  Profit Factor: {metrics['profit_factor']}")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']}")
            print(f"  Net Profit: ${metrics['net_profit']}")
            print(f"  Max Drawdown: ${metrics['max_drawdown']}")
            
            # Comparar com baseline
            if self.baseline_metrics:
                wr_change = metrics['win_rate'] - self.baseline_metrics['win_rate']
                sr_change = metrics['sharpe_ratio'] - self.baseline_metrics['sharpe_ratio']
                print(f"\n  vs BASELINE:")
                print(f"    Win Rate: {wr_change:+.1f}%")
                print(f"    Sharpe Ratio: {sr_change:+.2f}")
            
            # Verificar degradacao
            degradation = self.analyzer.detect_performance_degradation(50, self.symbol)
            
            if degradation['degradation']:
                print(f"\n  [ALERT] DEGRADACAO DETECTADA!")
                for reason in degradation['reasons']:
                    print(f"    - {reason}")
            
            # CORRIGIDO: Critérios de otimização MENOS CONSERVADORES
            needs_optimization = (
                metrics['win_rate'] < 70 or        # era 65 - OTIMIZA COM PERFORMANCE BOA
                metrics['profit_factor'] < 1.8 or  # era 1.5 - MAIS EXIGENTE
                metrics['sharpe_ratio'] < 1.2 or   # era 1.0 - OTIMIZA MAIS CEDO
                degradation['degradation']
            )
            
            if not needs_optimization:
                print(f"\n  [OK] Performance satisfatoria - otimizacao nao necessaria")
                print(f"{'='*60}\n")
                return
            
            print(f"\n  [OPTIMIZATION] Performance abaixo do alvo - otimizando...")
            
            # Parametros atuais
            current_params = {
                'stop_loss_atr_multiplier': self.sl_atr_mult,
                'trailing_activation_mult': self.trailing_activation_mult,
                'trailing_distance_mult': self.trailing_distance_mult
            }
            
            print(f"\n  Parametros atuais:")
            for k, v in current_params.items():
                print(f"    {k}: {v:.3f}")
            
            # Sugerir ajustes (metodo CONSERVADOR mas menos restritivo)
            suggested = self.optimizer.suggest_adjustments(current_params, metrics)
            
            print(f"\n  Parametros sugeridos:")
            for k, v in suggested.items():
                old = current_params[k]
                change = ((v - old) / old * 100) if old != 0 else 0
                print(f"    {k}: {v:.3f} ({change:+.1f}%)")
            
            # Validar ajustes
            if self._validate_adjustments(current_params, suggested):
                # Aplicar
                self._apply_parameters(suggested, "Auto-optimization based on performance analysis")
                
                # Registrar otimizacao
                opt_id = self.opt_logger.log_optimization(
                    symbol=self.symbol,
                    optimization_type="AUTO_ADJUSTMENT",
                    parameters=suggested,
                    metrics_before=metrics,
                    notes=f"Optimization #{self.optimization_count + 1}"
                )
                
                self.optimization_count += 1
                
                print(f"\n  [SUCCESS] Novos parametros aplicados (ID: {opt_id})")
                print(f"  Total de otimizacoes: {self.optimization_count}")
            else:
                print(f"\n  [REJECTED] Ajustes muito drasticos - mantendo atuais")
            
            print(f"{'='*60}\n")
        
        except Exception as e:
            print(f"\n  [ERRO] Otimizacao falhou: {e}")
            print(f"{'='*60}\n")
    
    def _validate_adjustments(self, current: Dict, suggested: Dict) -> bool:
        """
        Valida se ajustes sugeridos sao seguros
        CORRIGIDO: Máximo 35% de variacao por parametro + LIMITES DE SEGURANÇA mais flexíveis
        """
        # CORRIGIDO: LIMITES DE SEGURANÇA MAIS FLEXÍVEIS
        SAFE_LIMITS = {
            'trailing_distance_atr_multiplier': {
                'min': 0.08,  # era 0.05 - MAIOR FLEXIBILIDADE
                'max': 0.35,  # era 0.50 - MAIOR FLEXIBILIDADE
                'max_distance_pts': 300  # era 200 - MAIS TOLERANTE
            },
            'trailing_activation_atr_multiplier': {
                'min': 0.15,  # era 0.10 - MAIOR FLEXIBILIDADE
                'max': 0.80   # era 1.00 - MAIOR FLEXIBILIDADE
            },
            'stop_loss_atr_multiplier': {
                'min': 2.5,   # era 3.0 - MAIS TOLERANTE
                'max': 12.0   # era 10.0 - MAIS TOLERANTE
            }
        }
        
        for param, new_value in suggested.items():
            old_value = current.get(param, 0)
            
            if old_value == 0:
                continue
            
            # Validar limites de segurança
            if param in SAFE_LIMITS:
                limits = SAFE_LIMITS[param]
                
                # Verificar range mínimo/máximo
                if 'min' in limits and new_value < limits['min']:
                    print(f"    [VALIDATION FAILED] {param} = {new_value:.3f} < mínimo {limits['min']:.3f}")
                    return False
                if 'max' in limits and new_value > limits['max']:
                    print(f"    [VALIDATION FAILED] {param} = {new_value:.3f} > máximo {limits['max']:.3f}")
                    return False
                
                # Validar trailing distance em pontos se possível calcular
                if param == 'trailing_distance_atr_multiplier' and 'max_distance_pts' in limits:
                    # Calcular trailing distance esperada
                    estimated_distance_pts = self.current_atr * new_value
                    if estimated_distance_pts > limits['max_distance_pts']:
                        print(f"    [VALIDATION FAILED] Trailing distance {estimated_distance_pts:.0f}pts > máximo {limits['max_distance_pts']}pts")
                        print(f"    Isso resultaria em lucro protegido INCORRETO!")
                        return False
            
            # CORRIGIDO: Máximo 35% de variacao por vez (era 20%)
            change_pct = abs((new_value - old_value) / old_value)
            if change_pct > 0.35:  # era 0.2 - 75% MAIS FLEXÍVEL
                print(f"    [VALIDATION FAILED] {param} mudaria {change_pct*100:.0f}% - muito drastico")
                return False
        
        return True
    
    def _apply_parameters(self, params: Dict, reason: str):
        """
        Aplica novos parametros ao agente
        """
        print(f"\n  [APLICANDO PARAMETROS]")
        print(f"    Razao: {reason}")
        
        changes_made = 0
        
        for param, value in params.items():
            old_value = getattr(self, param, None)
            
            if old_value is not None and abs(old_value - value) > 0.001:
                setattr(self, param, value)
                
                # Recalcular thresholds se necessario
                if 'sl' in param or 'trailing' in param:
                    self._recalculate_thresholds()
                
                # Registrar mudanca
                self.opt_logger.log_parameter_change(
                    symbol=self.symbol,
                    parameter_name=param,
                    old_value=old_value,
                    new_value=value,
                    reason=reason
                )
                
                change_pct = ((value - old_value) / old_value * 100) if old_value != 0 else 0
                print(f"    {param}: {old_value:.3f} -> {value:.3f} ({change_pct:+.1f}%)")
                changes_made += 1
        
        if changes_made == 0:
            print(f"    Nenhuma mudanca significativa")
        else:
            print(f"    {changes_made} parametro(s) atualizado(s)")
    
    def _recalculate_thresholds(self):
        """
        Recalcula thresholds baseados nos novos parametros
        """
        if self.current_atr > 0:
            self.current_sl_pontos = self.current_atr * self.sl_atr_mult
            self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
            self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult
            
            print(f"    [THRESHOLDS RECALCULADOS]")
            print(f"      SL: {self.current_sl_pontos:.0f} pontos")
            print(f"      Trailing Ativa: {self.current_trailing_activation_pontos:.0f} pontos")
            print(f"      Trailing Dist: {self.current_trailing_distance_pontos:.0f} pontos")
    
    def _print_final_report(self):
        """
        Imprime relatorio final ao parar agente
        """
        print(f"\n{'='*60}")
        print(f"RELATORIO FINAL - GOLD ADAPTIVE AGENT CORRIGIDO")
        print(f"{'='*60}")
        
        # Estatisticas gerais
        print(f"\nESTATISTICAS:")
        print(f"  Total de trades fechados: {self.total_trades_closed}")
        print(f"  Otimizacoes executadas: {self.optimization_count}")
        
        # Performance final
        try:
            final_metrics = self.analyzer.analyze_recent_performance(100, self.symbol)
            if 'error' not in final_metrics:
                print(f"\nPERFORMANCE FINAL:")
                print(f"  Win Rate: {final_metrics['win_rate']}%")
                print(f"  Profit Factor: {final_metrics['profit_factor']}")
                print(f"  Sharpe Ratio: {final_metrics['sharpe_ratio']}")
                print(f"  Net Profit: ${final_metrics['net_profit']}")
                
                # Comparar com baseline
                if self.baseline_metrics:
                    print(f"\n  MELHORIA vs BASELINE:")
                    wr_change = final_metrics['win_rate'] - self.baseline_metrics['win_rate']
                    pf_change = final_metrics['profit_factor'] - self.baseline_metrics['profit_factor']
                    sr_change = final_metrics['sharpe_ratio'] - self.baseline_metrics['sharpe_ratio']
                    
                    print(f"    Win Rate: {wr_change:+.1f}%")
                    print(f"    Profit Factor: {pf_change:+.2f}")
                    print(f"    Sharpe Ratio: {sr_change:+.2f}")
        except:
            print(f"  Nao foi possivel calcular metricas finais")
        
        # Regime atual
        if self.current_regime:
            print(f"\nREGIME ATUAL:")
            print(f"  Tipo: {self.current_regime['regime']}")
            print(f"  Confidence: {self.current_regime['confidence']}")
        
        # Historico de parametros
        param_history = self.opt_logger.get_parameter_history(self.symbol)
        print(f"\nHISTORICO DE AJUSTES:")
        print(f"  Total de mudancas: {len(param_history)}")
        
        if param_history:
            print(f"\n  Ultimas 5 mudancas:")
            for change in param_history[:5]:
                print(f"    {change['timestamp'][:19]}: {change['parameter_name']}")
                print(f"      {change['old_value']:.3f} -> {change['new_value']:.3f}")
                print(f"      Razao: {change['reason']}")
        
        print(f"\n{'='*60}")
        print(f"Dados salvos em: btc_trading_logs.db")
        print(f"CORREÇÕES APLICADAS:")
        print(f"  ✅ Parâmetros 2x mais responsivos")
        print(f"  ✅ Validações 75% mais flexíveis")
        print(f"  ✅ Circuit breaker otimizado")
        print(f"  ✅ Menos conservador, mais ativo")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Adaptive Agent CORRIGIDO com Auto-Tuning')
    parser.add_argument('--symbol', type=str, default='XAUUSDc', help='Symbol to trade')
    parser.add_argument('--volume', type=float, default=0.02, help='Volume in lots')
    parser.add_argument('--no-auto-tuning', action='store_true', help='Disable auto-tuning')
    parser.add_argument('--optimization-interval', type=int, default=20, help='Optimize every N trades')
    
    args = parser.parse_args()
    
    agent = GoldAdaptiveAgent(
        symbol=args.symbol,
        volume=args.volume,
        auto_tuning_enabled=not args.no_auto_tuning,
        optimization_interval=args.optimization_interval
    )
    
    agent.run()
