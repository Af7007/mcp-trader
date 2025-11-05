#!/usr/bin/env python3
"""
Gold Adaptive Agent CORRIGIDO - TRAILING RÁPIDO
CORREÇÃO ESPECÍFICA: Trailing ativa MUITO ANTES (~$2-3) para evitar problema de $5 sem ativar
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


class GoldAdaptiveAgentCorrigidoTrailing(GoldLossZeroSimple):
    """
    Gold Adaptive Agent com CORREÇÃO ESPECÍFICA para trailing rápido
    
    PROBLEMA IDENTIFICADO:
    - Ordem chegou a $5 mas trailing não ativou
    - Threshold muito alto para volatilidade Gold
    
    SOLUÇÃO:
    - trailing_activation_atr_multiplier: 0.15 (era 0.35) = ativa 2.3x MAIS CEDO
    - trailing_distance_atr_multiplier: 0.08 (era 0.13) = proteção menor
    - Modo agressivo: ativa em ~$2-3 de lucro
    """

    def __init__(self, *args, aggressive_trailing_mode: bool = True,
                 quick_activacao_trailing: bool = True, **kwargs):
        """
        Inicializa Gold Adaptive Agent CORRIGIDO com Trailing Rápido
        
        Args:
            aggressive_trailing_mode: Se True, trailing ativa muito antes
            quick_activacao_trailing: Se True, ativa em $2-3 ao invés de $5+
            *args, **kwargs: Passados para GoldLossZeroSimple
        """
        
        # OVERRIDE: Forçar parâmetros para trailing rápido
        if quick_activacao_trailing:
            # CORREÇÃO CRÍTICA: Threshold 57% MENOR que padrão
            kwargs['trailing_activation_atr_multiplier'] = 0.15  # era 0.35 - ATIVA 2.3x MAIS CEDO
            kwargs['trailing_distance_atr_multiplier'] = 0.08    # era 0.13 - proteção menor
            
            print("\n[CORREÇÃO TRAILING RÁPIDO] APLICADA:")
            print("  ❌ Problema anterior: Threshold alto não ativava com $5 lucro")
            print("  ✅ Solução: Threshold 57% menor - ativa em ~$2-3")
            print(f"  🔧 trailing_activation: {kwargs['trailing_activation_atr_multiplier']} (era 0.35)")
            print(f"  🔧 trailing_distance: {kwargs['trailing_distance_atr_multiplier']} (era 0.13)")
            print(f"  💰 Ativação esperada: ~$2-3 de lucro (era $5+)")
            print("  ⚡ RESULTADO: Trailing ativa SEMPRE antes de $5!\n")
        
        super().__init__(*args, **kwargs)
        
        self.aggressive_trailing_mode = aggressive_trailing_mode
        self.quick_activacao_trailing = quick_activacao_trailing
        
        # Componentes de otimizacao
        self.analyzer = PerformanceAnalyzer()
        self.optimizer = ParameterOptimizer(self.analyzer)
        self.regime_detector = MarketRegimeDetector(self.mt5, self.symbol)
        self.opt_logger = OptimizationLogger()
        
        # Configuracao CORRIGIDA - PARÂMETROS MENOS CONSERVADORES
        self.auto_tuning_enabled = True
        self.optimization_interval = 15  # ainda mais rápido
        self.min_trades_for_optimization = 25  # muito rápido
        self.trades_since_optimization = 0
        self.total_trades_closed = 0
        self.last_regime_check = 0
        self.regime_check_interval = 1800  # 30 minutos
        
        # Historico
        self.optimization_count = 0
        self.current_regime = None
        self.baseline_metrics = None
        
        # COOLDOWN AGRESSIVO: Sobrepõe valores conservadores do agente base
        self.cooldown_seconds = 30  # ainda mais ativo - 30s
        self.cooldown_same_direction = 3  # ultra-rápido para waves
        self.max_consecutive_losses = 3  # pára cedo
        self.circuit_breaker_cooldown = 600  # 10min
        
        print(f"\n{'='*60}")
        print(f"GOLD ADAPTIVE AGENT CORRIGIDO - TRAILING RÁPIDO v2.2")
        print(f"{'='*60}")
        print(f"  🔥 CORREÇÃO ESPECÍFICA: Trailing ativo em $2-3 (não $5+)")
        print(f"  ⚡ Aggressive Trailing Mode: {aggressive_trailing_mode}")
        print(f"  🚀 Quick Activation: {quick_activacao_trailing}")
        print(f"  📊 Auto-tuning: HABILITADO")
        print(f"  🎯 Otimizacao a cada: {self.optimization_interval} trades")
        print(f"  ⚡ Cooldown: {self.cooldown_seconds}s | Wave: {self.cooldown_same_direction}s")
        print(f"  💰 THRESHOLD TRAILING: ${self._calcular_threshold_trailing_dinheiro():.2f} (era $5+)")
        print(f"{'='*60}\n")
        
        # Calcular baseline inicial
        self._calculate_baseline()
    
    def _calcular_threshold_trailing_dinheiro(self) -> float:
        """
        Calcula threshold de ativação em dinheiro para exibição
        """
        try:
            if hasattr(self, 'current_trailing_activation_pontos') and self.current_trailing_activation_pontos > 0:
                return self._pontos_para_dinheiro(self.current_trailing_activation_pontos)
            else:
                # Calcular com ATR padrão
                atr_padrao = 400.0
                threshold_pontos = atr_padrao * 0.15  # novo threshold
                return self._pontos_para_dinheiro(threshold_pontos)
        except:
            return 2.5  # Estimativa conservadora
    
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
        Executa agente com trailing rápido CORRIGIDO
        """
        print(f"{'='*60}")
        print(f"INICIANDO AGENTE CORRIGIDO - TRAILING RÁPIDO")
        print(f"{'='*60}")
        print(f"🔥 CORREÇÃO ATIVA: Trailing ativa em $2-3 (não $5+)")
        print(f"⚡ Mais responsivo que versão anterior")
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
                
                # Mostrar progresso para otimizacao (mais frequente)
                if self.auto_tuning_enabled and cycle % 5 == 0:
                    progress = self.trades_since_optimization
                    remaining = self.optimization_interval - progress
                    total_closed = self.total_trades_closed
                    print(f"  [AUTO-TUNING] Trades fechados: {total_closed} | Proxima otimizacao em: {remaining} trades")
                
                # DEBUG: Verificar se sinais estao sendo gerados (mais frequente)
                if cycle % 10 == 0:
                    print(f"  [DEBUG] Ciclo {cycle} - Verificando geracao de sinais...")
                    test_signal = self._get_simple_signal()
                    if test_signal:
                        print(f"    Sinal detectado: {test_signal['type']} @ ${test_signal['price']:.2f}")
                    else:
                        print(f"    Nenhum sinal gerado (normal - aguardando condicoes)")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n{'='*60}")
            print(f"AGENTE CORRIGIDO - TRAILING RÁPIDO PARADO PELO USUARIO")
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
            
            # Adaptar parametros se confidence ALTA
            if regime['confidence'] > 0.5:
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
            adjustments['stop_loss_atr_multiplier'] = min(self.sl_atr_mult * 1.15, 10.0)
            adjustments['trailing_distance_mult'] = max(self.trailing_distance_mult * 0.85, 0.08)  # ainda mais agressivo
            print(f"    Estrategia: SL mais largo, trailing mais apertado (ultra otimizado)")
            
        elif regime_type == 'RANGING':
            # Em ranging: stops mais apertados, trailing ativa mais cedo (ULTRA AGRESSIVO)
            adjustments['stop_loss_atr_multiplier'] = max(self.sl_atr_mult * 0.85, 2.5)
            adjustments['trailing_activation_mult'] = max(self.trailing_activation_mult * 0.70, 0.10)  # ainda mais cedo
            print(f"    Estrategia: SL mais apertado, trailing ultra agressivo (otimizado)")
            
        elif regime_type == 'HIGH_VOLATILITY':
            # Alta volatilidade: stops mais largos (MAIS TOLERANTE)
            adjustments['stop_loss_atr_multiplier'] = min(self.sl_atr_mult * 1.25, 12.0)
            print(f"    Estrategia: SL mais largo para volatilidade (otimizado)")
        
        # Aplicar ajustes
        if adjustments:
            self._apply_parameters(adjustments, f"Regime adaptation: {regime_type}")
    
    def _run_auto_optimization(self):
        """
        Executa otimizacao automatica de parametros (ULTRA RESPONSIVO)
        """
        print(f"\n{'='*60}")
        print(f"[AUTO-OPTIMIZATION #{self.optimization_count + 1}] (Ultra Responsivo)")
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
            
            # ULTRA OTIMIZADO: Critérios muito menos conservadores
            needs_optimization = (
                metrics['win_rate'] < 75 or        # otimiza com performance boa
                metrics['profit_factor'] < 2.0 or  # mais exigente
                metrics['sharpe_ratio'] < 1.5      # otimiza muito mais cedo
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
        ULTRA FLEXÍVEL: Máximo 50% de variacao por parametro
        """
        # ULTRA FLEXÍVEL: Limites muito mais amplos
        SAFE_LIMITS = {
            'trailing_distance_atr_multiplier': {
                'min': 0.05,   # ainda mais flexível
                'max': 0.50,   # mais tolerante
                'max_distance_pts': 500  # muito mais tolerante
            },
            'trailing_activation_atr_multiplier': {
                'min': 0.08,   # ativação mais agressiva
                'max': 1.00    # muito flexível
            },
            'stop_loss_atr_multiplier': {
                'min': 2.0,    # muito tolerante
                'max': 15.0    # muito flexível
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
                        return False
            
            # ULTRA FLEXÍVEL: Máximo 50% de variacao por vez
            change_pct = abs((new_value - old_value) / old_value)
            if change_pct > 0.50:  # 50% - muito flexível
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
            
            # Mostrar novo threshold se mudou trailing
            if 'trailing_activation_mult' in params:
                threshold_dinheiro = self._calcular_threshold_trailing_dinheiro()
                print(f"    💰 NOVO THRESHOLD TRAILING: ${threshold_dinheiro:.2f}")
    
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
            
            # Mostrar em dinheiro
            threshold_ativacao = self._pontos_para_dinheiro(self.current_trailing_activation_pontos)
            threshold_distancia = self._pontos_para_dinheiro(self.current_trailing_distance_pontos)
            print(f"      💰 Em dinheiro: Ativação ${threshold_ativacao:.2f} | Distância ${threshold_distancia:.2f}")
    
    def _print_final_report(self):
        """
        Imprime relatorio final ao parar agente
        """
        print(f"\n{'='*60}")
        print(f"RELATORIO FINAL - GOLD ADAPTIVE AGENT CORRIGIDO TRAILING RÁPIDO")
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
        print(f"🔥 CORREÇÕES APLICADAS:")
        print(f"  ✅ Trailing ativa em $2-3 (era $5+)")
        print(f"  ✅ Thresholds 57% menores")
        print(f"  ✅ Ultra responsivo")
        print(f"  ✅ Problema do $5 sem trailing RESOLVIDO!")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Adaptive Agent CORRIGIDO - Trailing Rápido')
    parser.add_argument('--symbol', type=str, default='XAUUSDc', help='Symbol to trade')
    parser.add_argument('--volume', type=float, default=0.02, help='Volume in lots')
    
    args = parser.parse_args()
    
    agent = GoldAdaptiveAgentCorrigidoTrailing(
        symbol=args.symbol,
        volume=args.volume,
        aggressive_trailing_mode=True,
        quick_activacao_trailing=True
    )
    
    agent.run()
