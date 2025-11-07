#!/usr/bin/env python3
"""
GBP AI Agent - Agente que usa IA para decisões de entrada e trailing stop para proteção
Otimizado para GBPUSDc (maior volatilidade que Gold)
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
from core.ollama_client import OllamaClient
from core.btc_logger import BTCLogger

logger = logging.getLogger(__name__)

class GBPAIAgent(GoldLossZeroSimple):
    """
    Agente GBP que usa IA (Ollama) para decisões de entrada e mantém trailing stop para proteção de lucro
    Otimizado para volatilidade maior de moedas Forex
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
        Inicializa GBP AI Agent

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

        # CORRECAO FOREX: Ajustar symbol_point e point_value para GBP
        self._adjust_forex_parameters()

        print("GBP AI AGENT - HIBRIDO (Forex)")
        print("   Base: Gold Loss Zero Simple (trailing stop comprovado)")
        print(f"   IA: {'Ollama habilitado' if self.ai_enabled else 'Desabilitado'}")
        print(f"   Modelo: {ai_model_name}")
        print(f"   Temperatura: {ai_temperature}")
        print("   Estrategia: IA decide entrada + Trailing Stop protege lucro")
        print("")
        print("   OTIMIZACOES PARA GBP:")
        print("   - Volatilidade maior (Forex vs Commodities)")
        print("   - Scalping com trailing stop agressivo")
        print("   - SL e TP ajustáveis por parâmetro")

    def _adjust_forex_parameters(self):
        """
        Ajusta parâmetros Forex (GBP, EUR, etc) para refletir a realidade da moeda
        Moedas Forex têm estrutura completamente diferente de Commodities

        GBPUSDc padrão MT5 (cents account):
        - symbol_point: 0.0001 (4 casas decimais)
        - point_value: $10.0 por ponto para 1 lote (100.000 * 0.0001)

        Isso permite que SL e Trailing funcionem corretamente em dólares.
        """
        if "GBP" in self.symbol.upper():
            # Ajustar valores para GBP
            self.symbol_point = 0.0001  # 4 casas decimais (típico Forex)
            self.point_value = 10.0     # $10 por ponto para 1 lote

            print(f"[FOREX AJUSTADO] GBP:")
            print(f"   symbol_point: {self.symbol_point}")
            print(f"   point_value: ${self.point_value:.2f} por ponto (1 lote)")
            print(f"   Com volume {self.volume}: 1 ponto = ${self.point_value * self.volume:.4f}")
        elif "EUR" in self.symbol.upper():
            # EUR tem mesma estrutura que GBP
            self.symbol_point = 0.0001
            self.point_value = 10.0

            print(f"[FOREX AJUSTADO] EUR:")
            print(f"   symbol_point: {self.symbol_point}")
            print(f"   point_value: ${self.point_value:.2f} por ponto (1 lote)")
            print(f"   Com volume {self.volume}: 1 ponto = ${self.point_value * self.volume:.4f}")

    def _get_market_data_for_ai(self) -> Optional[Dict]:
        """Obtém dados de mercado para análise da IA (otimizado para GBP)"""
        try:
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                return None

            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=20
            )

            if not rates or len(rates) < 10:
                return None

            closes = [r['close'] for r in rates[:15]][::-1]

            # Calcular indicadores
            current = closes[14] if len(closes) > 14 else closes[-1]
            prev_3 = closes[11] if len(closes) > 11 else closes[-1]
            prev_7 = closes[7] if len(closes) > 7 else closes[-1]

            momentum_3m = ((current - prev_3) / prev_3) * 100 if prev_3 != 0 else 0
            momentum_7m = ((current - prev_7) / prev_7) * 100 if prev_7 != 0 else 0

            # Para GBP, usar volatilidade típica
            atr = 100  # GBP é mais volátil que Gold

            return {
                "current_price": current,
                "atr": atr,
                "momentum_3m": momentum_3m,
                "momentum_7m": momentum_7m,
                "volume_current": rates[0].get('tick_volume', 0) if rates else 0,
                "volume_avg": sum([r.get('tick_volume', 0) for r in rates[-7:]]) / 7 if rates else 0,
                "trend_direction": "UP" if momentum_7m > 0 else "DOWN" if momentum_7m < 0 else "LATERAL"
            }
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return None

    def _get_additional_context(self) -> str:
        """Contexto adicional para a IA sobre GBP"""
        hour = time.localtime().tm_hour

        context = f"Horario: {hour:02d}:00 UTC. "

        # Sessões Forex
        if 8 <= hour < 17:
            context += "Sessao EUROPA (volatilidade alta). "
        elif 13 <= hour < 22:
            context += "Sessao USA (volatilidade alta). "
        elif 21 <= hour < 8:
            context += "Sessao ASIA (volatilidade media). "

        context += "GBPUSDc: Par Forex volátil. Usar trailing stop agressivo. "
        context += "Evitar trades perto de noticias economicas UK/USA. "

        return context

    def _analyze_and_open(self):
        """
        Analisa mercado usando IA e abre posições
        CORRIGIDO: Eliminação completa de recursão infinita
        """
        # Verificar se deve processar decisão da IA
        if not self._should_process_ai_decision():
            return

        # Obter dados de mercado
        market_data = self._get_market_data_for_ai()

        if not market_data:
            logger.warning("Nao foi possivel obter dados de mercado para IA")
            return

        # Verificar se IA está disponível e não em cooldown por erros
        current_time = time.time()
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
            start_time = time.time()

            additional_context = self._get_additional_context()
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

            # Verificar se deve abrir posição
            if not self._should_open_position(ai_decision):
                logger.info("Nao atende criterios para abertura de posicao")
                return

            # Abrir posição com a decisão da IA
            signal = {
                "type": ai_decision["action"],
                "price": market_data["current_price"],
                "reason": f"IA_Recommendation: {ai_decision['reasoning']}"
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
            if not self._check_circuit_breaker():
                return

            # VERIFICAR HORÁRIO BLACKLIST
            if not self._check_trading_hours():
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
                        print(f"   [ONDA] Aguardando {remaining}s para proximo {signal['type']} (win streak: {self.consecutive_wins_same_direction})")
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
                        print(f"   [FILTRO] Mudanca de direcao {self.last_trade_type}->{signal['type']}, aguardando confirmacao")
                    return

            # Passou todos os filtros, abrir posição!
            self._open_position(signal)

        except Exception as e:
            logger.error(f"Erro no fallback tradicional (GBP): {e}")

    def _should_process_ai_decision(self) -> bool:
        """
        Verifica se deve processar decisão da IA baseado em:
        - Última decisão
        - Cooldowns
        - Estado do mercado
        """
        current_time = time.time()

        # Cooldown de decisões da IA
        if current_time - self.last_ai_decision_time < 30:  # 30 segundos
            return False

        # Cooldown tradicional
        if current_time - self.last_close_time < self.cooldown_seconds:
            return False

        # Verificar circuit breaker
        if not self._check_circuit_breaker():
            return False

        # Verificar horário
        if not self._check_trading_hours():
            return False

        return True

    def _should_open_position(self, ai_decision: Dict) -> bool:
        """Verificar se deve abrir posição (com filtros adicionais para GBP)"""
        # Se confiança muito baixa, não abrir
        if ai_decision["confidence"] < 0.6:
            logger.info(f"Confianca da IA muito baixa ({ai_decision['confidence']:.2f}), aguardando melhor sinal")
            return False

        # Verificar se houve muitas decisões HOLD recentes
        if self.ai_decisions["HOLD"] > 0 and (self.ai_decisions["BUY"] + self.ai_decisions["SELL"]) == 0:
            logger.info("IA so recomendou HOLD ate agora, nao ha trading signal")
            return False

        return True

    def _log_ai_decision(self, decision: Dict, response_time: float, market_data: Dict):
        """Log detalhado da decisão da IA"""
        self.ai_decisions[decision["action"]] += 1
        self.last_ai_decision_time = time.time()
        self.last_ai_action = decision["action"]

        logger.info("DECISAO DA IA (GBP):")
        logger.info(f"   Acao: {decision['action']}")
        logger.info(f"   Confianca: {decision.get('confidence', 0):.2f}")
        logger.info(f"   Raciocinio: {decision.get('reasoning', 'N/A')}")
        logger.info(f"   Tempo de resposta: {response_time:.2f}s")
        logger.info(f"   Preco: ${market_data['current_price']:.2f}")
        logger.info(f"   Momentum 3m: {market_data['momentum_3m']:.3f}%")
        logger.info(f"   Volume: {market_data['volume_current']:.0f}")

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='GBP AI Agent - IA para entradas + Trailing Stop para protecao (Forex)')
    parser.add_argument('--symbol', type=str, default='GBPUSDc', help='Symbol to trade')
    parser.add_argument('--volume', type=float, default=0.03, help='Volume in lots')
    parser.add_argument('--fixed-sl-dollars', type=float, default=4.0, help='Fixed stop loss in dollars')
    parser.add_argument('--trailing-step-dollar', type=float, default=1.5, help='Trailing step in dollars')
    parser.add_argument('--model-name', type=str, default='llama3.2:1b', help='Ollama model name')
    parser.add_argument('--ai-host', type=str, default='localhost', help='Ollama host')
    parser.add_argument('--ai-port', type=int, default=11434, help='Ollama port')
    parser.add_argument('--ai-temperature', type=float, default=0.1, help='AI temperature (0-1)')
    parser.add_argument('--ai-disabled', action='store_true', help='Disable AI and use traditional method')

    args = parser.parse_args()

    agent = GBPAIAgent(
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
    agent.trailing_step_dollar = args.trailing_step_dollar

    agent.run()
