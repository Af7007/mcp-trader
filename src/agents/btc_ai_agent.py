#!/usr/bin/env python3
"""
BTC AI Agent - Agente que usa IA para decisões de entrada e trailing stop para proteção
BASEADO NO GOLD AI - SEM INDICADORES TRADICIONAIS - APENAS LLM
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.btc_loss_zero_v3 import BTCLossZeroV3
from core.ollama_client import OllamaClient
from core.btc_logger import BTCLogger

logger = logging.getLogger(__name__)

class BTCAIAgent(BTCLossZeroV3):
    """
    Agente BTC que usa IA (Ollama) para decisões de entrada e mantém trailing stop para proteção de lucro
    SEM INDICADORES TRADICIONAIS - Apenas análise LLM de contexto de mercado
    """
    
    def __init__(self, *args, 
                 ai_model_name: str = "llama3.2:1b",
                 ai_host: str = "localhost", 
                 ai_port: int = 11434,
                 ai_temperature: float = 0.1,
                 ai_enabled: bool = True,
                 ai_timeout: int = 10,
                 **kwargs):
        """
        Inicializa Gold AI Agent
        
        Args:
            ai_model_name: Nome do modelo Ollama
            ai_host: Host do servidor Ollama
            ai_port: Porta do servidor Ollama
            ai_temperature: Temperatura da IA (0-1)
            ai_enabled: Habilitar/desabilitar IA
            ai_timeout: Timeout para requisições da IA
            *args, **kwargs: Passados para GoldLossZeroSimple
        """
        # Inicializar a classe pai
        super().__init__(*args, **kwargs)
        
        # Configurar cliente de IA
        self.ai_enabled = ai_enabled
        self.ai_temperature = ai_temperature
        self.ai_timeout = ai_timeout
        
        if self.ai_enabled:
            self.ai_client = OllamaClient(
                model_name=ai_model_name,
                host=ai_host,
                port=ai_port
            )
            
            # Verificar se IA está funcionando
            if self.ai_client._check_server():
                self.ai_available = True
                logger.info("IA Ollama configurada e disponivel")
            else:
                self.ai_available = False
                logger.warning("IA Ollama nao disponivel, usando fallback")
        else:
            self.ai_client = None
            self.ai_available = False
            logger.info("IA desabilitada, usando metodo tradicional")
        
        # Estatísticas da IA
        self.ai_decisions = {"BUY": 0, "SELL": 0, "HOLD": 0}
        self.ai_response_times = []
        self.last_ai_decision_time = 0

        # Circuit breaker para IA
        self.ai_consecutive_errors = 0
        self.ai_max_consecutive_errors = 5
        self.ai_error_cooldown = 600  # 10 minutos
        self.ai_error_cooldown_until = 0

        # Rastreamento da última decisão
        self.last_ai_action = None

        print("")
        print("=" * 60)
        print("BTC AI AGENT - SEM INDICADORES TRADICIONAIS")
        print("=" * 60)
        print("   Base: BTC Loss Zero v3.2.0 (Circuit Breaker + Break-Even)")
        print(f"   IA: {'Ollama habilitado' if self.ai_enabled else 'Desabilitado'}")
        print(f"   Modelo: {ai_model_name}")
        print(f"   Temperatura: {ai_temperature}")
        print("")
        print("   ESTRATEGIA:")
        print("   - IA (LLM) decide entrada SEM indicadores tecnicos")
        print("   - Trailing Stop + Break-Even protegem lucro")
        print("   - Circuit Breaker para apos 3 perdas")
        print("")
        print("   DIFERENCIAL vs BTC v3.2.0:")
        print("   - SEM RSI, MACD, Bollinger, SMA (ZERO indicadores)")
        print("   - LLM analisa apenas CONTEXTO de mercado")
        print("   - Decisao baseada em momentum + tendencia recente")
        print("")
        print("   CONFIGURACAO BTC AI:")
        print(f"   - SL fixo: ${self.fixed_sl_dollars:.2f}")
        print(f"   - Volume: {self.volume} lotes")
        print(f"   - Trailing: Ativa ${self.trailing_activation_dollar:.2f}, protege ${self.trailing_distance_dollar:.2f}")
        print(f"   - Circuit Breaker: {self.max_consecutive_losses} perdas")
        print(f"   - Break-Even: ${self.breakeven_activation_dollar:.2f} lucro")
        print(f"   - Cooldown: {self.cooldown_seconds}s")
        print("=" * 60)
        print("")

    def _analyze_and_open(self):
        """
        Analisa mercado usando IA e abre posições
        CORRIGIDO: Eliminação completa de recursão infinita
        """
        # Verificar circuit breaker
        if self.circuit_breaker_active:
            return

        # Obter dados de mercado
        market_data = self._get_market_data_for_ai()

        if not market_data:
            logger.warning("Nao foi possivel obter dados de mercado para IA")
            return

        # Verificar cooldowns
        current_time = time.time()
        time_since_last_ai = current_time - self.last_ai_decision_time
        if time_since_last_ai < 30:  # 30 segundos entre consultas da IA
            return

        # Verificar se IA está disponível e não em cooldown por erros
        if not self.ai_enabled or not self.ai_available or current_time < self.ai_error_cooldown_until:
            if current_time < self.ai_error_cooldown_until:
                remaining = int(self.ai_error_cooldown_until - current_time)
                logger.info(f"IA em cooldown por erros ({remaining}s restantes), usando metodo tradicional")
            else:
                logger.info("IA indisponivel, usando metodo tradicional")
            # CORREÇÃO: Usar método próprio de fallback sem recursão
            return self._analyze_traditional_fallback()

        try:
            # Obter decisão da IA
            logger.info("Consultando IA para decisao de trading...")

            # Obter contexto adicional ANTES de usar
            additional_context = self._get_additional_context()

            # LOG DOS DADOS QUE A IA VAI RECEBER
            print(f"\n{'='*60}")
            print(f"[IA ANALYSIS] Consultando LLM para decisao...")
            print(f"{'='*60}")
            print(f"   [INPUT] Dados de mercado:")
            print(f"      Preco: ${market_data['current_price']:.2f}")
            print(f"      Tendencia: {market_data['trend_direction']}")
            print(f"      Momentum 3min: {market_data['momentum_3m']:+.3f}%")
            print(f"      Momentum 7min: {market_data['momentum_7m']:+.3f}%")
            print(f"      Volume atual: {market_data['volume_current']:.0f}")
            print(f"      Volume medio: {market_data['volume_avg']:.0f}")
            print(f"      ATR: {market_data['atr']:.2f}")
            print(f"   [CONTEXT] {additional_context if additional_context else 'Nenhum contexto adicional'}")

            start_time = time.time()
            ai_decision = self.ai_client.get_trading_decision(
                market_data,
                additional_context
            )

            end_time = time.time()
            response_time = end_time - start_time
            self.ai_response_times.append(response_time)

            # Verificar se a decisão é válida (não erro)
            if ai_decision.get("confidence", 0) == 0.0 and "erro" in ai_decision.get("reasoning", "").lower():
                # IA retornou erro, incrementar contador
                self.ai_consecutive_errors += 1
                logger.warning(f"IA retornou erro ({self.ai_consecutive_errors}/{self.ai_max_consecutive_errors})")

                if self.ai_consecutive_errors >= self.ai_max_consecutive_errors:
                    # Ativar cooldown da IA
                    self.ai_error_cooldown_until = current_time + self.ai_error_cooldown
                    logger.error(f"CIRCUIT BREAKER IA ATIVADO! Pausa de {self.ai_error_cooldown} segundos")
                    return self._analyze_traditional_fallback()
                else:
                    # Ainda não atingiu limite, tentar novamente na próxima vez
                    return self._analyze_traditional_fallback()
            else:
                # Decisão válida, resetar contador de erros
                self.ai_consecutive_errors = 0

            # Log da decisão
            self._log_ai_decision(ai_decision, response_time, market_data)

            # Se HOLD, usar fallback tradicional (M5 analysis)
            if ai_decision["action"] == "HOLD":
                logger.info("IA recomenda AGUARDAR, usando metodo tradicional M5")
                return self._analyze_traditional_fallback()

            # VALIDAÇÃO CRÍTICA: Verificar se sinal está alinhado com tendência M5
            # Evita abrir BUY em downtrend ou SELL em uptrend
            validation = self._validate_ai_signal_with_m5(ai_decision["action"])
            if not validation["valid"]:
                logger.info(f"Sinal IA rejeitado: {validation['reason']}")
                print(f"   [IA VALIDATION] {validation['reason']}")
                return self._analyze_traditional_fallback()
            else:
                print(f"   [IA VALIDATION] {validation['reason']}")

            # Verificar se deve abrir posição
            if not self._should_open_position(ai_decision):
                logger.info("Nao atende criterios para abertura de posicao")
                return

            # Abrir posição com a decisão da IA
            signal = {
                "type": ai_decision["action"],
                "price": market_data["current_price"],
                "reason": f"IA_Recommendation: {ai_decision['reasoning']}",
                "score": ai_decision["confidence"] * 10  # Converter confianca (0-1) para score (0-10)
            }

            logger.info(f"Abrindo posicao baseada na IA: {ai_decision['action']}")
            self._open_position(signal)

        except Exception as e:
            logger.error(f"Erro ao consultar IA: {e}")
            # Incrementar contador de erros
            self.ai_consecutive_errors += 1
            logger.warning(f"Erro na IA ({self.ai_consecutive_errors}/{self.ai_max_consecutive_errors})")

            if self.ai_consecutive_errors >= self.ai_max_consecutive_errors:
                # Ativar cooldown da IA
                self.ai_error_cooldown_until = current_time + self.ai_error_cooldown
                logger.error(f"CIRCUIT BREAKER IA ATIVADO! Pausa de {self.ai_error_cooldown} segundos")

            # Fallback para método tradicional
            logger.info("Fallback para metodo tradicional")
            return self._analyze_traditional_fallback()

    def _analyze_traditional_fallback(self):
        """
        Método de fallback que usa análise tradicional sem recursão
        CORREÇÃO: Implementação própria para evitar recursão infinita
        """
        try:
            # Usar análise simples do agente base (sem chamar super())
            if not self.use_buy and not self.use_sell:
                return

            # VERIFICAR CIRCUIT BREAKER
            if self.circuit_breaker_active:
                return

            # Verificar cooldown DINÂMICO
            current_time = time.time()
            time_since_last_close = current_time - self.last_close_time

            # Buscar sinal ANTES de verificar cooldown (para saber a direção)
            signal = self._get_simple_signal()
            if not signal:
                return

            # COOLDOWN INTELIGENTE: Reduzido se mesma direção + último foi WIN
            is_same_direction = (self.last_trade_type == signal["type"])

            if is_same_direction and self.last_trade_was_win:
                # APROVEITANDO A ONDA! Cooldown reduzido
                cooldown_to_use = self.cooldown_same_direction
                if self.last_close_time > 0 and time_since_last_close < cooldown_to_use:
                    remaining = int(cooldown_to_use - time_since_last_close)
                    if remaining % 5 == 0:  # Mostrar a cada 5s
                        print(f"   [ONDA] Aguardando {remaining}s para próximo {signal['type']} (win streak: {self.consecutive_wins_same_direction})")
                    return
                else:
                    print(f"   [ONDA] Aproveitando momentum! Abrindo {signal['type']} consecutivo (win #{self.consecutive_wins_same_direction + 1})")
            else:
                # Direção diferente ou último foi loss: cooldown COMPLETO
                cooldown_to_use = self.cooldown_seconds

                if self.last_close_time > 0 and time_since_last_close < cooldown_to_use:
                    remaining = int(cooldown_to_use - time_since_last_close)
                    if remaining % 30 == 0:  # Mostrar a cada 30s
                        print(f"   Cooldown ativo: {remaining}s restantes")
                    return

                # FILTRO EXTRA: Se mudando direção, aguardar 5 minutos
                if self.last_trade_type and self.last_trade_type != signal["type"]:
                    if time_since_last_close < 300:  # 5 minutos
                        print(f"   [FILTRO] Mudança de direção {self.last_trade_type}→{signal['type']}, aguardando confirmação")
                        return

            # Passou todos os filtros, abrir posição!
            self._open_position(signal)

        except Exception as e:
            logger.error(f"Erro no fallback tradicional: {e}")
    
    def _should_process_ai_decision(self) -> bool:
        """
        Verifica se deve processar decisão da IA baseado em:
        - Última decisão
        - Cooldowns
        - Estado do mercado
        """
        current_time = time.time()

        # Cooldown de decisões da IA
        time_since_last_ai = current_time - self.last_ai_decision_time
        if time_since_last_ai < 30:  # 30 segundos
            remaining = int(30 - time_since_last_ai)
            if remaining % 10 == 0:  # Mostrar a cada 10s
                print(f"   [IA] Aguardando cooldown: {remaining}s")
            return False

        # Cooldown tradicional
        time_since_last_close = current_time - self.last_close_time
        if time_since_last_close < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - time_since_last_close)
            if remaining % 30 == 0:  # Mostrar a cada 30s
                print(f"   [COOLDOWN] Aguardando: {remaining}s")
            return False

        # Verificar circuit breaker
        if self.circuit_breaker_active:
            return False

        return True
    
    def _get_market_data_for_ai(self) -> Optional[Dict]:
        """
        Coleta dados de mercado para envio à IA
        """
        try:
            # Preço atual
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                return None
            
            current_price = tick.get('bid', 0) if tick.get('bid', 0) > 0 else tick.get('ask', 0)
            
            # Dados de volume
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=50  # Aumentado para ter dados suficientes para EMAs
            )
            
            if not rates_m5 or len(rates_m5) < 30: # Garantir dados para EMA(26)
                return None
            
            # Usar pandas para facilitar cálculos
            df = pd.DataFrame(rates_m5)
            df = df.iloc[::-1].reset_index(drop=True) # Inverter para ordem cronológica

            # --- NOVA LÓGICA DE TENDÊNCIA COM EMAs ---
            ema_fast_period = 12
            ema_slow_period = 26
            df['ema_fast'] = df['close'].ewm(span=ema_fast_period, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=ema_slow_period, adjust=False).mean()

            # Pegar os valores mais recentes
            last_ema_fast = df['ema_fast'].iloc[-1]
            last_ema_slow = df['ema_slow'].iloc[-1]

            # Definir a tendência com base no cruzamento de EMAs
            if last_ema_fast > last_ema_slow:
                trend_direction = "UP"
            elif last_ema_fast < last_ema_slow:
                trend_direction = "DOWN"
            else:
                trend_direction = "LATERAL"
            # --- FIM DA NOVA LÓGICA ---

            # Momentum: current é o mais recente (closes[-1])
            closes = df['close'].tolist()
            current = closes[-1]
            prev_3 = closes[-4] if len(closes) > 3 else closes[0]
            prev_7 = closes[-8] if len(closes) > 7 else closes[0]

            momentum_3m = ((current - prev_3) / prev_3) * 100 if prev_3 != 0 else 0
            momentum_7m = ((current - prev_7) / prev_7) * 100 if prev_7 != 0 else 0

            # Volume: volume_current é o volume mais recente
            volumes = df['tick_volume'].tolist()
            volume_current = volumes[-1]
            volume_avg = sum(volumes[:-1]) / len(volumes[:-1])
            
            return {
                "current_price": current_price,
                "atr": self.current_atr,
                "momentum_3m": momentum_3m,
                "momentum_7m": momentum_7m,
                "volume_current": volume_current,
                "volume_avg": volume_avg,
                "trend_direction": trend_direction
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados de mercado: {e}")
            return None
    
    def _get_additional_context(self) -> str:
        """
        Obtém contexto adicional para a IA
        """
        context_parts = []
        
        # Última decisão da IA
        if hasattr(self, 'last_ai_action') and self.last_ai_action:
            context_parts.append(f"Ultima decisao da IA: {self.last_ai_action}")
        
        # Consecutive losses/wins
        if self.consecutive_losses > 0:
            context_parts.append(f"Perdas consecutivas: {self.consecutive_losses}")
        
        if hasattr(self, 'consecutive_wins_same_direction') and self.consecutive_wins_same_direction > 0:
            context_parts.append(f"Vitorias consecutivas: {self.consecutive_wins_same_direction}")
        
        # Horário atual
        from datetime import datetime
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 10:
            context_parts.append("Sessao da Asia (menor volatilidade)")
        elif 13 <= current_hour <= 17:
            context_parts.append("Sessao de Londres (alta volatilidade)")
        elif 18 <= current_hour <= 22:
            context_parts.append("Sessao de NY (alta volatilidade)")
        else:
            context_parts.append("Sessao menos ativa")
        
        return ". ".join(context_parts)
    
    def _log_ai_decision(self, decision: Dict, response_time: float, market_data: Dict):
        """
        Log da decisão da IA
        """
        self.ai_decisions[decision["action"]] += 1
        self.last_ai_decision_time = time.time()
        self.last_ai_action = decision["action"]

        # Emoji baseado na ação
        action_emoji = "BUY" if decision['action'] == "BUY" else "SELL" if decision['action'] == "SELL" else "HOLD"

        print(f"\n   [OUTPUT] Decisao da IA:")
        print(f"      Acao: {action_emoji}")
        print(f"      Confianca: {decision['confidence']:.1%}")
        print(f"      Raciocinio: {decision['reasoning']}")
        print(f"      Tempo de resposta: {response_time:.2f}s")
        print(f"{'='*60}")

        logger.info("DECISAO DA IA:")
        logger.info(f"   Acao: {decision['action']}")
        logger.info(f"   Confianca: {decision['confidence']:.2f}")
        logger.info(f"   Raciocinio: {decision['reasoning']}")
        logger.info(f"   Tempo de resposta: {response_time:.2f}s")
        logger.info(f"   Preco: ${market_data['current_price']:.2f}")
        logger.info(f"   Tendencia: {market_data['trend_direction']}")
        logger.info(f"   Momentum 3m: {market_data['momentum_3m']:.3f}%")
        logger.info(f"   Momentum 7m: {market_data['momentum_7m']:.3f}%")
        logger.info(f"   Volume: {market_data['volume_current']:.0f} (avg: {market_data['volume_avg']:.0f})")
        
        # Estatísticas gerais
        total_decisions = sum(self.ai_decisions.values())
        if total_decisions > 0:
            buy_pct = (self.ai_decisions["BUY"] / total_decisions) * 100
            sell_pct = (self.ai_decisions["SELL"] / total_decisions) * 100
            hold_pct = (self.ai_decisions["HOLD"] / total_decisions) * 100
            
            logger.info(f"Estatisticas IA ({total_decisions} decisoes):")
            logger.info(f"   BUY: {buy_pct:.1f}% | SELL: {sell_pct:.1f}% | HOLD: {hold_pct:.1f}%")
        
        if len(self.ai_response_times) > 0:
            avg_response_time = sum(self.ai_response_times) / len(self.ai_response_times)
            logger.info(f"Tempo medio de resposta: {avg_response_time:.2f}s")

    def _validate_ai_signal_with_m5(self, signal_type: str) -> dict:
        """
        Valida sinal da IA com análise técnica M5 antes de abrir.
        Evita abrir BUY em downtrend ou SELL em uptrend (TREND FOLLOWING).
        NOVO: Evita entrar em vela com reversão forte contra a direção do trade.

        Args:
            signal_type: "BUY" ou "SELL" (decisão da IA)

        Returns:
            {"valid": bool, "reason": str}
        """
        try:
            # Obter dados M5 (mesmo que usa a classe base)
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=15
            )

            if not rates or len(rates) < 8:
                return {"valid": False, "reason": "Dados M5 insuficientes"}

            # Extrair closes e reverter ordem (MT5 retorna newest first)
            closes = [r['close'] for r in rates[:15]][::-1]

            # Obter vela atual (mais recente)
            current_candle = rates[0]  # Primeira vela = mais recente
            candle_open = current_candle['open']
            candle_close = current_candle['close']
            candle_size = abs(candle_close - candle_open)
            candle_direction = "VERDE" if candle_close > candle_open else "VERMELHA"

            # Calcular ATR simplificado (média do range das últimas 5 velas)
            atr = sum(rates[i]['high'] - rates[i]['low'] for i in range(5)) / 5

            # Vela é considerada "forte" se tamanho > 1.5x ATR
            strong_candle = candle_size > (atr * 1.5)

            # VALIDACAO DA VELA ATUAL: Evitar entrar em reversão
            if signal_type == "BUY":
                # BUY: se vela atual está MUITO VERMELHA (caindo forte), aguardar
                if candle_direction == "VERMELHA" and strong_candle:
                    return {
                        "valid": False,
                        "reason": f"Vela atual VERMELHA forte (${candle_size:.2f} > ATR ${atr:.2f}x1.5), aguardando proxima vela para BUY"
                    }

            elif signal_type == "SELL":
                # SELL: se vela atual está MUITO VERDE (subindo forte), aguardar
                if candle_direction == "VERDE" and strong_candle:
                    return {
                        "valid": False,
                        "reason": f"Vela atual VERDE forte (${candle_size:.2f} > ATR ${atr:.2f}x1.5), aguardando proxima vela para SELL"
                    }

            # Calcular tendência M5 (GOLD usa 5/8 velas subindo/descendo)
            uptrend = sum(1 for i in range(7) if closes[i] < closes[i+1]) >= 5  # 5/8 = 62.5%
            downtrend = sum(1 for i in range(7) if closes[i] > closes[i+1]) >= 5

            # Validar micro-trend (3+ velas consecutivas na mesma direção)
            micro_uptrend = False
            micro_downtrend = False

            for i in range(len(closes) - 2):
                if closes[i] < closes[i+1] < closes[i+2]:
                    micro_uptrend = True
                if closes[i] > closes[i+1] > closes[i+2]:
                    micro_downtrend = True

            # Verificar se sinal da IA está alinhado com tendência M5
            if signal_type == "BUY":
                # BUY: precisa de uptrend E micro-uptrend (AMBOS devem confirmar)
                if uptrend and micro_uptrend:
                    return {
                        "valid": True,
                        "reason": f"M5 uptrend E micro confirmados (uptrend: {uptrend}, micro: {micro_uptrend}), vela {candle_direction} OK"
                    }
                else:
                    return {
                        "valid": False,
                        "reason": f"M5 requer uptrend E micro-uptrend (uptrend: {uptrend}, micro: {micro_uptrend})"
                    }

            elif signal_type == "SELL":
                # SELL: precisa de downtrend E micro-downtrend (AMBOS devem confirmar)
                if downtrend and micro_downtrend:
                    return {
                        "valid": True,
                        "reason": f"M5 downtrend E micro confirmados (downtrend: {downtrend}, micro: {micro_downtrend}), vela {candle_direction} OK"
                    }
                else:
                    return {
                        "valid": False,
                        "reason": f"M5 requer downtrend E micro-downtrend (downtrend: {downtrend}, micro: {micro_downtrend})"
                    }

            return {"valid": False, "reason": "Sinal desconhecido"}

        except Exception as e:
            logger.error(f"Erro ao validar sinal IA com M5: {e}")
            return {"valid": False, "reason": f"Erro na validação: {e}"}

    def _should_open_position(self, ai_decision: Dict) -> bool:
        """
        Verifica se deve abrir posição baseado na decisão da IA
        """
        # Se confiança muito baixa, não abrir
        if ai_decision["confidence"] < 0.6:
            logger.info(f"Confianca da IA muito baixa ({ai_decision['confidence']:.2f}), aguardando melhor sinal")
            return False
        
        # Verificar se houve muitas decisões HOLD recentes
        if self.ai_decisions["HOLD"] > 0 and (self.ai_decisions["BUY"] + self.ai_decisions["SELL"]) == 0:
            logger.info("IA so recomendou HOLD ate agora, nao ha trading signal")
            return False
        
        return True
    
    def _display_status(self, cycle: int):
        """
        Exibe status do agente com informações da IA
        """
        super()._display_status(cycle)

        # Adicionar informações da IA
        if self.ai_enabled:
            print(f"   IA: {'ONLINE' if self.ai_available else 'OFFLINE'}")

            if self.ai_available:
                total_decisions = sum(self.ai_decisions.values())
                if total_decisions > 0:
                    last_decision = getattr(self, 'last_ai_action', 'N/A')
                    print(f"      Ultima decisao: {last_decision}")
                    print(f"      Decisoes: BUY={self.ai_decisions['BUY']} | SELL={self.ai_decisions['SELL']} | HOLD={self.ai_decisions['HOLD']}")
            else:
                print(f"      Status: IA nao disponivel, usando fallback")

        # Log no banco de dados
        try:
            cycle_data = {
                'cycle_number': cycle,
                'symbol': self.symbol,
                'ai_enabled': self.ai_enabled,
                'ai_available': self.ai_available,
                'ai_decisions': self.ai_decisions.copy(),
                'ai_response_times_avg': sum(self.ai_response_times) / len(self.ai_response_times) if self.ai_response_times else 0
            }
            # Log adicional para análise de IA
            logger.debug(f"Status IA Ciclo {cycle}: {cycle_data}")
        except Exception as e:
            logger.error(f"Erro ao logar status da IA: {e}")

    def run(self):
        """
        Loop principal - BTC AI Agent (usa IA ao inves de indicadores tradicionais)
        """
        print("\nBTC AI AGENT - INICIANDO (IA SEM INDICADORES)")
        print("=" * 60)
        print()

        cycle = 0

        try:
            while True:
                cycle += 1

                # Verificar circuit breaker
                if self.circuit_breaker_active:
                    print(f"\n[CIRCUIT BREAKER ATIVO] {self.consecutive_losses} perdas consecutivas")
                    print("   Aguardando 5 minutos antes de retomar...")
                    time.sleep(300)
                    self.circuit_breaker_active = False
                    self.consecutive_losses = 0
                    print("[CIRCUIT BREAKER] Resetado, retomando operacoes\n")

                # Header
                from datetime import datetime
                print("\n" + "=" * 60)
                print(f"[BTC AI] Ciclo #{cycle} | {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)

                # Estado
                positions = self.mt5.positions_get(symbol=self.symbol)
                num_positions = len(positions) if positions else 0

                # Detectar se posicao foi fechada pelo MT5 (SL/TP)
                if self.last_position_ticket and not positions:
                    print(f"\n[POSICAO FECHADA PELO MT5] Ticket: {self.last_position_ticket}")

                    # PARAR WORKER DE MONITORAMENTO
                    if self.position_worker and self.position_worker.is_alive():
                        print(f"[WORKER] Parando monitoramento continuo...")
                        self.position_worker.stop()
                        self.position_worker.join(timeout=2)
                        print(f"[WORKER] Parado com sucesso")

                    # Verificar se foi lucro ou perda (buscar no historico)
                    is_win = self._check_last_trade_result(self.last_position_ticket)
                    self._record_trade_result(is_win)

                    print(f"   Resultado: {'[WIN]' if is_win else '[LOSS]'}")
                    print(f"   Possivel motivo: {'Trailing atingido' if is_win else 'SL atingido'}")

                    self.last_close_time = time.time()

                    # Limpar dicionarios da posicao fechada
                    ticket = self.last_position_ticket
                    if ticket:
                        self.positions_entry_price.pop(ticket, None)
                        self.positions_trailing_active.pop(ticket, None)
                        self.positions_trailing_stop.pop(ticket, None)
                        self.positions_breakeven_moved.pop(ticket, None)
                        print(f"   [CLEANUP] Removida posicao #{ticket} dos dicionarios")

                    self.last_position_ticket = None
                    print(f"[COOLDOWN ATIVADO] Aguardando antes de proximo trade")

                # Verificar break-even para posicoes abertas
                if positions and num_positions > 0:
                    self._check_and_move_breakeven(positions)

                print(f"[AGENTE]:")
                print(f"   Estado: BTC AI (IA + Trailing)")
                print(f"   Volume: {self.volume}")
                print(f"   Posicoes Abertas: {num_positions}")
                print(f"   SL Fixo: ${self.fixed_sl_dollars:.2f}")

                # Preco
                tick = self.mt5.get_symbol_info_tick(symbol=self.symbol)
                if tick:
                    price = tick['bid']
                    print(f"[MERCADO] ({self.symbol}):")
                    print(f"   Preco: ${price:.2f}")

                # Verificar se pode abrir (sem posicoes abertas)
                if num_positions == 0:
                    # USAR IA PARA DECISAO (ao inves de _get_simple_signal)
                    self._analyze_and_open()

                # Aguardar proximo ciclo
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n\n[FINALIZANDO] BTC AI Agent parado pelo usuario")
            if self.position_worker:
                self.position_worker.stop()
                self.position_worker.join(timeout=2)
            print("[OK] Agente encerrado com sucesso")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BTC AI Agent - IA para entradas SEM INDICADORES + Trailing Stop')
    parser.add_argument('--symbol', type=str, default='BTCUSDc', help='Symbol to trade')
    parser.add_argument('--volume', type=float, default=0.05, help='Volume in lots (ultra conservador)')
    parser.add_argument('--fixed-sl-dollars', type=float, default=8.0, help='Fixed stop loss in dollars')
    parser.add_argument('--trailing-activation-dollar', type=float, default=4.0, help='Trailing activation in dollars')
    parser.add_argument('--trailing-distance-dollar', type=float, default=2.0, help='Trailing distance in dollars')
    parser.add_argument('--model-name', type=str, default='llama3.2:1b', help='Ollama model name')
    parser.add_argument('--ai-host', type=str, default='localhost', help='Ollama host')
    parser.add_argument('--ai-port', type=int, default=11434, help='Ollama port')
    parser.add_argument('--ai-temperature', type=float, default=0.1, help='AI temperature (0-1)')
    parser.add_argument('--ai-disabled', action='store_true', help='Disable AI and use traditional method')

    args = parser.parse_args()

    agent = BTCAIAgent(
        symbol=args.symbol,
        volume=args.volume,
        fixed_sl_dollars=args.fixed_sl_dollars,
        ai_model_name=args.model_name,
        ai_host=args.ai_host,
        ai_port=args.ai_port,
        ai_temperature=args.ai_temperature,
        ai_enabled=not args.ai_disabled
    )

    # Atualizar trailing step após inicialização
    
    agent.run()
