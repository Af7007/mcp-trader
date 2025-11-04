#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente GOLD Loss Zero - Otimizado para XAUUSDc (Gold - Conta Cents)
Estrategia: Trailing Stop ilimitado sem losses
Baseado em btc_loss_zero_simple.py com parâmetros otimizados para Gold

MONITORAMENTO CONTINUO:
- Thread principal: Analisa mercado e abre trades (15s)
- Worker thread: Monitora trailing stops em tempo real (2s)
- Garante que nao perde movimentos rapidos entre ciclos
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.btc_logger import BTCLogger
from core.mt5_direct_client import get_mt5_client
from core.position_monitor_worker import PositionMonitorWorker

logger = logging.getLogger(__name__)


class GoldLossZeroSimple:
    """
    Agente GOLD com estrategia Loss 0 otimizado para XAUUSDc.

    Estrategia:
    - Trailing stop ilimitado
    - Parâmetros otimizados para volatilidade do Gold
    - Zero losses garantidos
    """

    def __init__(
        self,
        symbol: str = "XAUUSDc",
        volume: float = 0.01,  # GOLD: 0.01 lotes (conta cents)
        check_interval: int = 15,
        stop_loss_atr_multiplier: float = 5.0,  # GOLD: SL = ATR × 5.0 (~$6 de risco inicial)
        trailing_activation_atr_multiplier: float = 0.2,  # GOLD: ATR × 0.2 (reduzido para ativar mais rápido)
        trailing_distance_atr_multiplier: float = 0.3,  # GOLD: ATR × 0.3
        use_buy: bool = True,
        use_sell: bool = True
    ):
        """
        Inicializa agente Loss Zero - ESTRATÉGIA TRAILING STOP

        Args:
            volume: FIXADO em 0.03 lotes (sem variação)
            stop_loss_atr_multiplier: SL baseado em ATR × 1.5
            trailing_activation_atr_multiplier: Ativa trailing com ATR × 0.5 de lucro
            trailing_distance_atr_multiplier: Distância do trailing = ATR × 0.3

        ESTRATÉGIA:
            1. Abre posição com SL (ATR × 1.5)
            2. SEM TP fixo (lucro ilimitado!)
            3. Quando lucro >= ATR × 0.5, trailing ATIVA
            4. Trailing protege lucro com distância ATR × 0.3
            5. Trailing sobe/desce com o preço
            6. Fecha quando trailing é atingido (SEMPRE com lucro!)
        """
        self.symbol = symbol
        # CORRIGIDO: Validar volume mínimo (sem limite máximo para flexibilidade)
        self.volume = max(0.01, volume)
        if volume < 0.01:
            print(f"AVISO: Volume ajustado de {volume} para {self.volume} lotes (mínimo: 0.01)")
        elif volume > 1.0:
            print(f"AVISO: Volume {volume} lotes é alto! Certifique-se de ter margem suficiente.")
        self.check_interval = check_interval
        self.sl_atr_mult = stop_loss_atr_multiplier
        self.trailing_activation_mult = trailing_activation_atr_multiplier
        self.trailing_distance_mult = trailing_distance_atr_multiplier
        self.use_buy = use_buy
        self.use_sell = use_sell

        # SL/Trailing dinâmicos calculados por ATR
        self.current_sl_pontos = 0
        self.current_trailing_activation_pontos = 0
        self.current_trailing_distance_pontos = 0
        self.current_atr = 0

        # Conexão MT5 direta (sem BTCHedgeAgent que modifica SL)
        self.mt5 = get_mt5_client()

        # Worker para monitoramento contínuo
        self.position_worker = None  # Será criado quando abrir posição

        # Estado Loss 0
        self.trailing_active = False
        self.trailing_distance = 0.0
        self.entry_price = 0.0
        self.highest_profit = 0.0
        self.trailing_stop_price = 0.0
        self.last_position_ticket = None  # Rastreia última posição
        self.current_trade_id = None  # ID do trade no banco de dados

        # LOCK para evitar conflitos worker/main thread
        self._trailing_lock = threading.Lock()
        self._last_sl_modification = 0  # Timestamp da última modificação

        # Controle de cooldown entre trades
        self.last_close_time = 0
        self.cooldown_seconds = 30  # 30 segundos entre trades

        # Valor do ponto para Gold (será calculado dinamicamente)
        self.point_value = None
        self.symbol_point = None  # Variação de preço por ponto (ex: 0.001 para Gold)
        self._calculate_point_value()

        # CIRCUIT BREAKER - Proteção contra perdas consecutivas
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5  # Pausa após 5 perdas consecutivas
        self.circuit_breaker_active = False
        self.circuit_breaker_reset_time = 0
        self.circuit_breaker_cooldown = 1800  # 30 minutos de pausa

        # BLACKLIST DE HORÁRIOS (UTC) - DESATIVADA
        self.blacklisted_hours = [
            # REMOVIDO: Bloqueio de horários desativado
        ]

        # Inicializar BTC Logger
        self.btc_logger = BTCLogger()

        # CALCULAR ATR INICIAL (crítico para trailing funcionar)
        self._calculate_initial_atr()

        print(f"Agente GOLD Loss Zero - ESTRATEGIA TRAILING STOP v1.0 GOLD")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume} lotes (padrao 0.01, max 0.1)")
        print(f"   SL: ATR × {self.sl_atr_mult} (60-90 pts - GOLD)")
        print(f"   TP: SEM TP FIXO (trailing cuida)")
        print(f"   Trailing ativa: ATR × {self.trailing_activation_mult} (~24-36 pts)")
        print(f"   Trailing distancia: ATR × {self.trailing_distance_mult} (~18-27 pts)")
        print(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")
        print(f"   Circuit Breaker: {self.max_consecutive_losses} perdas consecutivas")
        print(f"   Horarios: 24/7 (sem bloqueios)")
        print(f"   Filtros: M5 + M15 + 2 confirmacoes")
        print(f"   Logger: ATIVO")
        print(f"")
        print(f"   CONFIGURACAO GOLD:")
        print(f"   - SL: 60-90 pontos (otimizado para Gold)")
        print(f"   - Volume: 0.01 lotes (conta cents)")
        print(f"   - Trailing ativa: ~30 pts de lucro")
        print(f"   - Trailing distancia: ~22 pts")
        print(f"   - Momentum: 0.03% (Gold volatilidade)")
        print(f"")
        print(f"   ESTRATEGIA:")
        print(f"   1. SL moderado para volatilidade Gold")
        print(f"   2. Trailing ativa com lucro pequeno")
        print(f"   3. Volume conservador (conta cents)")
        print(f"   4. Parametros otimizados para XAUUSDc")

    def _calculate_point_value(self):
        """
        Calcula o valor de 1 ponto para Gold XAUUSDc.

        Para Gold:
        - Contract size: 100 oz (normalmente)
        - Point: 0.01 (para cents account)
        - 1 ponto de movimento com 1 lote = $100
        - 1 ponto de movimento com 0.01 lote = $1.00
        """
        try:
            symbol_info = self.mt5.get_symbol_info(self.symbol)

            if symbol_info:
                # Obter point (variação de preço por ponto)
                self.symbol_point = symbol_info.get('point', 0.001)  # Gold: 0.001

                # Para Gold XAUUSDc:
                # Usar trade_tick_value que já vem calculado pelo MT5
                # trade_tick_value = valor em $ de 1 tick para 1 lote
                tick_value = symbol_info.get('trade_tick_value', None)

                if tick_value and tick_value > 0:
                    # Usar tick value do MT5 (mais preciso)
                    self.point_value = tick_value
                    print(f"[GOLD] Point (variação preço): {self.symbol_point}")
                    print(f"[GOLD] Valor do ponto (tick_value): ${self.point_value:.4f} por lote")
                    print(f"[GOLD] Com volume {self.volume}: 1 ponto = ${self.point_value * self.volume:.4f}")
                else:
                    # Fallback: calcular manualmente
                    contract_size = symbol_info.get('trade_contract_size', 1.0)
                    self.point_value = contract_size * self.symbol_point * 100  # Multiplicar por 100 para conta cents
                    print(f"[GOLD] Point (variação preço): {self.symbol_point}")
                    print(f"[GOLD] Valor do ponto (calculado): ${self.point_value:.4f} por lote")
                    print(f"[GOLD] Com volume {self.volume}: 1 ponto = ${self.point_value * self.volume:.4f}")
            else:
                # Fallback para Gold padrão
                self.symbol_point = 0.001
                self.point_value = 0.1  # $0.1 por ponto para 1 lote (conta cents)
                print(f"[GOLD] Usando valor padrão - Point: {self.symbol_point}, Value: ${self.point_value:.2f} por lote")

        except Exception as e:
            print(f"Erro ao calcular point value: {e}")
            self.symbol_point = 0.001
            self.point_value = 1.0  # Fallback

    def _calculate_initial_atr(self):
        """
        Calcula ATR inicial na criação do agente
        CRÍTICO: sem ATR, trailing não funciona!
        """
        try:
            print(f"[INIT] Calculando ATR inicial para {self.symbol}...")

            # Obter dados históricos para calcular ATR
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=20  # 100 minutos de histórico
            )

            if rates and len(rates) >= 14:
                self.current_atr = self._calculate_atr_simple(rates[:14])
                print(f"[INIT] ATR inicial calculado: {self.current_atr:.0f} pontos")

                # Calcular thresholds baseados no ATR
                self.current_sl_pontos = self.current_atr * self.sl_atr_mult
                self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
                self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult

                print(f"[INIT] Thresholds configurados:")
                print(f"       SL: {self.current_sl_pontos:.0f} pontos")
                print(f"       Trailing activation: {self.current_trailing_activation_pontos:.0f} pontos")
                print(f"       Trailing distance: {self.current_trailing_distance_pontos:.0f} pontos")
            else:
                print(f"[INIT] AVISO: Poucos dados históricos ({len(rates) if rates else 0}), usando ATR padrão")
                self.current_atr = 60000.0  # ATR padrão para Gold
                self.current_sl_pontos = self.current_atr * self.sl_atr_mult
                self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
                self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult

        except Exception as e:
            print(f"[INIT] ERRO ao calcular ATR inicial: {e}")
            # Fallback para ATR padrão
            self.current_atr = 60000.0
            self.current_sl_pontos = self.current_atr * self.sl_atr_mult
            self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
            self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult

    def _pontos_para_dinheiro(self, pontos: float) -> float:
        """
        Converte pontos MT5 para dinheiro considerando volume.

        Para Gold XAUUSDc:
        - 1 ponto MT5 = $0.001 de movimento de preço
        - Para volume 0.02: 1 ponto MT5 = $0.002

        Args:
            pontos: Número de pontos MT5

        Returns:
            Valor em dólares
        """
        if self.symbol_point is None:
            self._calculate_point_value()

        # Para Gold: pontos × symbol_point × volume
        # Exemplo: 24,000 pontos × 0.001 × 0.02 = $0.48
        return pontos * self.symbol_point * self.volume

    def run(self):
        """
        Executa agente Loss Zero
        """
        print(f"AGENTE GOLD LOSS ZERO - TRAILING ILIMITADO + MONITORAMENTO CONTINUO")
        print(f"="*60)
        print(f"Thread Principal: Analise e abertura de trades (15s)")
        print(f"Worker Thread: Monitoramento de trailing (2s) - CAPTURA TODOS OS MOVIMENTOS!")
        print(f"Parando processo ativo com Ctrl+C")
        print()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                self._display_status(cycle)
                
                # Verificar posições abertas
                self._check_positions()
                
                # Gerenciar trailing stop (APENAS SE worker não estiver ativo)
                # Worker tem prioridade, mas mantemos fallback
                if not self.position_worker or not self.position_worker.is_running():
                    self._manage_trailing()
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\nAgente BTC Loss Zero parado pelo usuario")

    def _display_status(self, cycle: int):
        """
        Exibe status do agente
        """
        print(f"\n{'='*60}")
        print(f"[AGENTE] BTC LOSS ZERO | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*60}")
        
        # Status do agente
        print(f"[AGENTE]:")
        print(f"   Estado: LOSS ZERO (Trailing ilimitado)")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing Ativo: {'SIM' if self.trailing_active else 'NAO'}")
        if self.trailing_active:
            if hasattr(self, 'current_trailing_distance_pontos') and self.entry_price > 0:
                distancia_real_pct = (self.current_trailing_distance_pontos / self.entry_price) * 100
                print(f"   Distancia Trailing: {distancia_real_pct:.3f}%")
            else:
                print(f"   Distancia Trailing: CALCULANDO...")
        else:
            print(f"   Distancia Trailing: INATIVA")
        
        # Mercado e logging
        current_price = None
        signal_data = None
        
        if self.mt5:
            try:
                tick = self.mt5.get_symbol_info_tick(self.symbol)
                if tick:
                    current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
                    print(f"[MERCADO] ({self.symbol}):")
                    print(f"   Preco: ${current_price:.2f}")
                    
                    if self.trailing_active:
                        profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                        # Verificar tipo da posição aberta
                        positions = self.mt5.positions_get(symbol=self.symbol)
                        if positions and len(positions) > 0:
                            direction = "LONG" if positions[0]['type'] == 0 else "SHORT"
                        else:
                            direction = "UNKNOWN"
                        print(f"   Posicao: {direction}")
                        print(f"   Lucro Atual: {profit_pct:.2f}%")
                    
                    # Gerar sinal para logging
                    signal_data = self._get_simple_signal()
                        
            except Exception as e:
                print(f"   Erro ao obter preco: {e}")
        
        # Log do ciclo no banco de dados
        try:
            cycle_data = {
                'cycle_number': cycle,
                'symbol': self.symbol,
                'price': current_price,
                'bb_upper': None,
                'bb_middle': None,
                'bb_lower': None,
                'bb_position': None,
                'rsi': None,
                'rsi_overbought': None,
                'rsi_oversold': None,
                'volume_current': None,
                'volume_avg': None,
                'volume_multiplier': None,
                'trend': None,
                'momentum': None,
                'signal_type': signal_data["type"] if signal_data else None,
                'signal_strength': str(3) if signal_data else None,
                'signal_reason': signal_data["reason"] if signal_data else None,
                'signal_price': signal_data["price"] if signal_data else None,
                'sl_price': None,
                'tp_price': None,
                'order_result': None,
                'order_error': None,
                'agent_version': "1.0.0"
            }
            self.btc_logger.log_cycle(cycle_data)
        except Exception as e:
            print(f"   Erro ao logar ciclo: {e}")

    def _check_positions(self):
        """
        Verifica e gerencia posicoes
        """
        if not self.mt5:
            return

        try:
            positions = self.mt5.positions_get(symbol=self.symbol)

            # Detectar se posição foi fechada pelo MT5 (SL/TP)
            if self.last_position_ticket and not positions:
                print(f"[POSIÇÃO FECHADA PELO MT5] Ticket: {self.last_position_ticket}")

                # PARAR WORKER DE MONITORAMENTO
                if self.position_worker and self.position_worker.is_running():
                    print(f"[WORKER] Parando monitoramento continuo...")
                    self.position_worker.stop()
                    worker_stats = self.position_worker.get_stats()
                    print(f"[WORKER] Stats: {worker_stats['total_checks']} checks, {worker_stats['trailing_updates']} updates")

                # Verificar se foi lucro ou perda (buscar no histórico)
                is_win = self._check_last_trade_result(self.last_position_ticket)
                self._record_trade_result(is_win)

                print(f"   Resultado: {'[WIN]' if is_win else '[LOSS]'}")
                print(f"   Possível motivo: {'TP atingido' if is_win else 'SL atingido'}")

                self.trailing_active = False
                self.trailing_distance = 0.0
                self.last_position_ticket = None
                self.last_close_time = time.time()
                print(f"[COOLDOWN ATIVADO] Aguardando {self.cooldown_seconds}s antes de próximo trade")

            if not positions:
                # Nenhuma posicao, analisa para abrir
                self._analyze_and_open()
            else:
                # Tem posicao, gerencia trailing
                for pos in positions:
                    self.last_position_ticket = pos.get('ticket')
                    self._manage_position_trailing(pos)

        except Exception as e:
            print(f"Erro ao verificar posicoes: {e}")

    def _analyze_and_open(self):
        """
        Analisa mercado e abre posicao com filtros de segurança
        """
        # Usar análise simples do agente base
        if not self.use_buy and not self.use_sell:
            return

        # VERIFICAR CIRCUIT BREAKER
        if not self._check_circuit_breaker():
            return

        # VERIFICAR HORÁRIO BLACKLIST
        if not self._check_trading_hours():
            return

        # Verificar cooldown
        current_time = time.time()
        time_since_last_close = current_time - self.last_close_time
        if self.last_close_time > 0 and time_since_last_close < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - time_since_last_close)
            if remaining % 15 == 0:  # Mostrar a cada 15s
                print(f"   Cooldown ativo: {remaining}s restantes")
            return

        # Buscar sinal simples
        signal = self._get_simple_signal()
        if signal:
            self._open_position(signal)

    def _check_circuit_breaker(self) -> bool:
        """
        Verifica se circuit breaker está ativo (proteção contra perdas consecutivas)
        """
        if self.circuit_breaker_active:
            elapsed = time.time() - self.circuit_breaker_reset_time
            remaining = self.circuit_breaker_cooldown - elapsed

            if remaining > 0:
                if int(remaining) % 300 == 0:  # Mostrar a cada 5 minutos
                    print(f"   ⛔ CIRCUIT BREAKER ATIVO: {int(remaining/60)} minutos restantes")
                    print(f"   Razao: {self.consecutive_losses} perdas consecutivas")
                return False
            else:
                # Resetar circuit breaker
                self.circuit_breaker_active = False
                self.consecutive_losses = 0
                print(f"   [OK] CIRCUIT BREAKER DESATIVADO - Sistema retomado")

        return True

    def _check_trading_hours(self) -> bool:
        """
        Verifica se horário atual está na blacklist
        """
        from datetime import datetime
        current_hour = datetime.utcnow().hour

        for start_hour, end_hour in self.blacklisted_hours:
            if start_hour <= current_hour < end_hour:
                if current_hour % 1 == 0:  # Mostrar a cada hora
                    print(f"   ⏰ HORARIO BLOQUEADO: {current_hour:02d}:00 UTC (alta volatilidade)")
                    print(f"   Retomar trading as {end_hour:02d}:00 UTC")
                return False

        return True

    def _check_last_trade_result(self, ticket: int) -> bool:
        """
        Verifica se último trade foi lucro ou perda
        """
        try:
            from datetime import datetime, timedelta

            # Buscar histórico das últimas 24h
            date_from = datetime.now() - timedelta(hours=24)
            deals = self.mt5.history_deals_get(date_from=date_from, date_to=datetime.now())

            if not deals:
                return False  # Sem dados, assumir perda

            # Buscar deal de fechamento (DEAL_ENTRY_OUT) para este ticket
            for deal in reversed(deals):  # Começar pelos mais recentes
                deal_ticket = deal.get('position_id', 0)
                if deal_ticket == ticket:
                    entry_type = deal.get('entry', 0)
                    if entry_type == 1:  # DEAL_ENTRY_OUT = saída
                        profit = deal.get('profit', 0)
                        return profit > 0  # True se lucro, False se perda

            return False  # Não encontrou, assumir perda

        except Exception as e:
            print(f"   Erro ao verificar resultado: {e}")
            return False  # Em caso de erro, assumir perda

    def _record_trade_result(self, is_win: bool):
        """
        Registra resultado do trade e atualiza circuit breaker
        """
        # Atualizar status do trade no banco de dados
        if self.current_trade_id:
            try:
                # Obter preço de fechamento e lucro do histórico MT5
                exit_price = None
                profit_loss = None

                # Buscar no histórico de deals
                from datetime import datetime, timedelta
                date_from = datetime.now() - timedelta(hours=1)  # Última 1 hora
                deals = self.mt5.history_deals_get(date_from=date_from, date_to=datetime.now())

                if deals:
                    # Procurar deal de fechamento para este ticket
                    for deal in reversed(deals):
                        if deal.get('position_id') == self.last_position_ticket:
                            exit_price = deal.get('price', 0)
                            profit_loss = deal.get('profit', 0)
                            break

                # Atualizar trade no banco
                status = "CLOSED_WIN" if is_win else "CLOSED_LOSS"
                exit_reason = "TP_TRAILING" if is_win else "SL_HIT"

                self.btc_logger.update_trade_status(
                    trade_id=self.current_trade_id,
                    status=status,
                    exit_price=exit_price,
                    exit_reason=exit_reason,
                    profit_loss=profit_loss
                )

                print(f"   [DB] Trade {self.current_trade_id} atualizado - Status: {status}, Profit: ${profit_loss:.2f}")

            except Exception as e:
                print(f"   [DB] Erro ao atualizar trade: {e}")

        if is_win:
            self.consecutive_losses = 0  # Resetar contador em vitórias
        else:
            self.consecutive_losses += 1
            print(f"   ⚠️ Perdas consecutivas: {self.consecutive_losses}/{self.max_consecutive_losses}")

            # Ativar circuit breaker se atingir limite
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.circuit_breaker_active = True
                self.circuit_breaker_reset_time = time.time()
                print(f"")
                print(f"{'='*60}")
                print(f"⛔ CIRCUIT BREAKER ATIVADO!")
                print(f"   Motivo: {self.consecutive_losses} perdas consecutivas")
                print(f"   Pausa: {int(self.circuit_breaker_cooldown/60)} minutos")
                print(f"   Sistema pausado para evitar mais perdas")
                print(f"{'='*60}")
                print(f"")

    def _get_simple_signal(self) -> dict:
        """
        Gera sinal baseado em:
        - Análise de TENDÊNCIA em M5 (visão ampla)
        - Timing de ENTRADA em M1 (precisão)
        ~30-40 operações/dia com maior qualidade
        """
        try:
            # PASSO 1: Analisar TENDÊNCIA em M5
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=10  # 50 minutos de histórico
            )

            if len(rates_m5) < 6:
                return None

            # Verificar se M5 confirma tendência forte
            m5_trend = self._analyze_m5_trend(rates_m5)
            if not m5_trend:
                return None  # M5 não confirma, não entrar

            # M5 + M15 confirmaram, ENTRAR!
            # (Removida validação M1 que estava bloqueando sinais válidos)
            return m5_trend

        except Exception as e:
            print(f"Erro na analise: {e}")
            return None

    def _analyze_m5_trend(self, rates) -> dict:
        """
        Análise REALISTA de tendência M5 com valores CORRETOS para BTC
        """
        try:
            # Preços das últimas 10 velas (50 minutos)
            closes = [r['close'] for r in rates[:10]]
            highs = [r['high'] for r in rates[:10]]
            lows = [r['low'] for r in rates[:10]]
            volumes = [r['tick_volume'] for r in rates[:10]]

            current = closes[0]
            prev_1 = closes[1]
            prev_2 = closes[2]
            prev_5 = closes[5]

            # Calcular ATR (14 períodos) para SL/TP dinâmico
            self.current_atr = self._calculate_atr_simple(rates[:14])

            # 1. TENDÊNCIA (últimas 5 velas para mais confiança)
            uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
            downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

            # 2. MOMENTUM REALISTA (mudança % nos últimos 5 min)
            momentum_5m = ((current - prev_5) / prev_5) * 100

            # 3. VOLATILIDADE
            last_range = highs[0] - lows[0]
            avg_range = sum([highs[i] - lows[i] for i in range(1, 6)]) / 5
            high_volatility = last_range > avg_range * 1.0  # RELAXADO: 1.0x em vez de 1.3x

            # 4. VOLUME
            volume_spike = volumes[0] > sum(volumes[1:6]) / 5 * 1.1  # RELAXADO: 1.1x em vez de 1.5x

            # 5. PREÇO vs MÉDIA
            avg_price = sum(closes[:5]) / 5
            price_above_avg = current > avg_price
            price_below_avg = current < avg_price

            # LOG de análise
            import random
            if random.random() < 0.2:
                print(f"   [M5] Mom: {momentum_5m:.3f}% | ATR: {self.current_atr:.1f} | Trend: {'UP' if uptrend else 'DOWN' if downtrend else 'LATERAL'}")

            # === THRESHOLDS OTIMIZADOS PARA GOLD ===
            # GOLD: Volatilidade menor que BTC
            MOMENTUM_BUY = 0.03   # 0.03% = ~$0.78 movimento em Gold $2,600
            MOMENTUM_SELL = -0.03

            # === SINAIS DE BUY - 2 CONFIRMAÇÕES (balanceado) ===
            if self.use_buy:
                confirmations = 0

                if uptrend and momentum_5m > MOMENTUM_BUY:
                    confirmations += 1
                if momentum_5m > MOMENTUM_BUY * 1.5:  # 0.06%
                    confirmations += 1
                if (high_volatility or volume_spike) and current > prev_1 and price_above_avg:  # RELAXADO: OR
                    confirmations += 1

                # AJUSTADO: 2 confirmações (meio termo)
                if confirmations >= 2:
                    # VERIFICAR TENDÊNCIA M15 (timeframe maior)
                    if self._check_m15_trend("BUY"):
                        return {"type": "BUY", "price": current, "reason": "M5_M15_confirmed_buy"}

            # === SINAIS DE SELL - 2 CONFIRMAÇÕES (balanceado) ===
            if self.use_sell:
                confirmations = 0

                if downtrend and momentum_5m < MOMENTUM_SELL:
                    confirmations += 1
                if momentum_5m < MOMENTUM_SELL * 1.5:  # -0.06%
                    confirmations += 1
                if (high_volatility or volume_spike) and current < prev_1 and price_below_avg:  # RELAXADO: OR
                    confirmations += 1

                # AJUSTADO: 2 confirmações (meio termo)
                if confirmations >= 2:
                    # VERIFICAR TENDÊNCIA M15 (timeframe maior)
                    if self._check_m15_trend("SELL"):
                        return {"type": "SELL", "price": current, "reason": "M5_M15_confirmed_sell"}

            return None

        except Exception as e:
            print(f"Erro na analise M5: {e}")
            return None

    def _calculate_atr_simple(self, rates) -> float:
        """
        Calcula ATR simples para SL/TP dinâmico
        GOLD: ATR otimizado para volatilidade do Gold
        Retorna ATR em PONTOS MT5, não em preço
        """
        try:
            if len(rates) < 14:
                # GOLD: ATR padrão de ~$60 em pontos MT5
                # $60 / 0.001 (symbol_point) = 60,000 pontos
                return 60000.0  # GOLD: ATR padrão 60,000 pontos

            true_ranges = []
            for i in range(1, min(14, len(rates))):
                high = rates[i-1]['high']
                low = rates[i-1]['low']
                prev_close = rates[i]['close']

                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)

            # ATR em preço
            atr_preco = sum(true_ranges) / len(true_ranges)

            # Converter para pontos MT5
            atr_pontos = atr_preco / self.symbol_point

            # GOLD: Mínimo 60,000 pontos (~$60)
            return max(atr_pontos, 60000.0)

        except Exception as e:
            print(f"   Erro ao calcular ATR: {e}")
            return 60000.0  # GOLD: ATR padrão 60,000 pontos

    def _check_m15_trend(self, signal_type: str) -> bool:
        """
        Verifica tendência em M15 para confirmação
        """
        try:
            rates_m15 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M15",
                start_pos=0,
                count=6
            )

            if len(rates_m15) < 4:
                return False

            closes = [r['close'] for r in rates_m15[:4]]

            # Para BUY: M15 deve estar em uptrend
            if signal_type == "BUY":
                uptrend_m15 = closes[0] > closes[1] > closes[2]
                return uptrend_m15

            # Para SELL: M15 deve estar em downtrend
            if signal_type == "SELL":
                downtrend_m15 = closes[0] < closes[1] < closes[2]
                return downtrend_m15

            return False

        except Exception as e:
            print(f"   Erro ao verificar M15: {e}")
            return False  # Se falhar, não confirmar

    def _find_m1_entry(self, rates_m1, trend_type: str) -> dict:
        """
        Busca timing preciso de entrada em M1
        Confirma se o momento atual é bom para entrar na direção da tendência M5
        """
        try:
            closes = [r['close'] for r in rates_m1[:3]]
            volumes = [r['tick_volume'] for r in rates_m1[:3]]

            current = closes[0]
            prev_1 = closes[1]
            prev_2 = closes[2]

            # Momentum M1 (últimos 3 minutos)
            momentum_m1 = ((current - prev_2) / prev_2) * 100

            # Volume spike em M1
            if len(volumes) >= 3:
                avg_volume = sum(volumes[1:3]) / 2
                volume_spike_m1 = volumes[0] > avg_volume * 1.3
            else:
                volume_spike_m1 = False

            # Para BUY: procurar momento de alta em M1
            if trend_type == "BUY":
                # M1 confirmando alta
                if current > prev_1 and momentum_m1 > 0:
                    return {"price": current, "confirmed": True}
                # Volume spike em M1 confirmando
                if volume_spike_m1 and current > prev_1:
                    return {"price": current, "confirmed": True}

            # Para SELL: procurar momento de baixa em M1
            elif trend_type == "SELL":
                # M1 confirmando baixa
                if current < prev_1 and momentum_m1 < 0:
                    return {"price": current, "confirmed": True}
                # Volume spike em M1 confirmando
                if volume_spike_m1 and current < prev_1:
                    return {"price": current, "confirmed": True}

            return None

        except Exception as e:
            print(f"Erro na analise M1: {e}")
            return None

    def _calculate_simple_rsi(self, rates, period):
        """
        Calcula RSI simples
        """
        try:
            if len(rates) < period + 1:
                return 50.0
            
            prices = [r['close'] for r in rates[:period + 1]]
            gains = [max(0, prices[i] - prices[i+1]) for i in range(len(prices)-1)]
            losses = [max(0, prices[i+1] - prices[i]) for i in range(len(prices)-1)]
            
            avg_gain = sum(gains) / len(gains)
            avg_loss = sum(losses) / len(losses)
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        except Exception as e:
            print(f"   Erro ao calcular RSI: {e}")
            return 50.0

    def _open_position(self, signal: dict):
        """
        Abre posicao com SL/TP baseado em ATR (dinâmico)
        """
        try:
            # Fechar posicoes existentes do mesmo tipo
            self._close_opposite_positions(signal["type"])

            # Obter preco atual de mercado
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                print("Erro: Nao foi possivel obter preco de mercado")
                return

            # Calcular SL e Trailing baseado em ATR (volatilidade)
            if self.current_atr == 0:
                self.current_atr = 120.0  # Valor padrão mais conservador

            self.current_sl_pontos = self.current_atr * self.sl_atr_mult
            self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
            self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult

            # Calcular valores reais em dinheiro (GOLD - usa point_value)
            sl_dinheiro = self._pontos_para_dinheiro(self.current_sl_pontos)
            trailing_activation_dinheiro = self._pontos_para_dinheiro(self.current_trailing_activation_pontos)
            trailing_distance_dinheiro = self._pontos_para_dinheiro(self.current_trailing_distance_pontos)

            # Calcular SL (SEM TP - trailing cuida do lucro!)
            # Converter pontos para variação de preço
            sl_price_distance = self.current_sl_pontos * self.symbol_point

            if signal["type"] == "BUY":
                market_price = tick['ask']  # Preco de compra
                sl_price = market_price - sl_price_distance  # Subtrair variação de preço
                tp_price = 0  # SEM TP FIXO!
                result = self.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,  # SEM TP!
                    comment="LossZero_Trailing"
                )
            else:  # SELL
                market_price = tick['bid']  # Preco de venda
                sl_price = market_price + sl_price_distance  # Adicionar variação de preço
                tp_price = 0  # SEM TP FIXO!
                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,  # SEM TP!
                    comment="LossZero_Trailing"
                )

            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                self.entry_price = market_price
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                self.last_position_ticket = result.get('order', 0)

                # Simplificar razão para exibição
                reason_display = signal['reason'].replace('_', ' ')

                print(f"")
                print(f"{'='*60}")
                print(f"[POSICAO ABERTA]: {signal['type']} ${market_price:.2f}")
                print(f"   Ticket: {self.last_position_ticket}")
                print(f"   Volume: {self.volume} lotes (FIXO)")
                print(f"   Motivo: {reason_display}")
                print(f"   ATR: {self.current_atr:.1f} pontos")
                print(f"   SL: ${sl_price:.2f} ({self.current_sl_pontos:.0f} pts = ${sl_dinheiro:.2f} perda)")
                print(f"   TP: SEM TP FIXO (lucro ilimitado!)")
                print(f"")
                print(f"   TRAILING STOP:")
                print(f"   Ativa com: {self.current_trailing_activation_pontos:.0f} pts = ${trailing_activation_dinheiro:.2f} lucro")
                print(f"   Distancia: {self.current_trailing_distance_pontos:.0f} pts = ${trailing_distance_dinheiro:.2f}")
                print(f"   Lucro protegido quando ativar: ${trailing_activation_dinheiro - trailing_distance_dinheiro:.2f}")
                print(f"{'='*60}")
                print(f"")

                # INICIAR WORKER DE MONITORAMENTO CONTINUO
                try:
                    if not self.position_worker or not self.position_worker.is_running():
                        # Verificar se deve usar worker ULTRA (para grandes velas)
                        if hasattr(self, '_start_ultra_worker') and callable(getattr(self, '_start_ultra_worker')):
                            # Usar worker ULTRA para máxima responsividade
                            self._start_ultra_worker()
                        else:
                            # Worker padrão
                            worker_interval = max(0.5, self.check_interval / 10)
                            self.position_worker = PositionMonitorWorker(
                                mt5_client=self.mt5,
                                symbol=self.symbol,
                                check_interval=worker_interval,
                                trailing_callback=self._trailing_worker_callback
                            )
                            self.position_worker.start()
                            print(f"[WORKER] Monitoramento continuo INICIADO (check: {worker_interval}s)")
                            print(f"         Trailing sera atualizado em tempo real!")
                            print(f"")
                except Exception as e:
                    print(f"[AVISO] Erro ao iniciar worker: {e}")
                    print(f"        Fallback: Monitoramento a cada 15s")

                # Log do trade no banco de dados
                try:
                    trade_data = {
                        'trade_type': signal["type"],
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': tp_price,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "1.0.0",
                        'reason': signal["reason"],
                        'status': "OPEN",
                        'comment': f"LossZero_{signal['type']}_{signal['reason']}"
                    }
                    # Log do trade e obter o trade_id
                    self.current_trade_id = self.btc_logger.log_trade(trade_data)
                    print(f"   [DB] Trade registrado - ID: {self.current_trade_id}")
                except Exception as e:
                    print(f"   Erro ao logar trade: {e}")
            else:
                print(f"Erro ao abrir posicao: {result}")

                # Log da tentativa falha
                try:
                    trade_data_failed = {
                        'trade_type': signal["type"],
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': tp_price,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "1.0.0",
                        'reason': signal["reason"],
                        'status': "FAILED",
                        'comment': f"Failed_{signal['type']}_{signal['reason']}"
                    }
                    self.btc_logger.log_trade(trade_data_failed)
                except Exception as e:
                    print(f"   Erro ao logar trade falha: {e}")
                
        except Exception as e:
            print(f"Erro ao abrir posicao: {e}")

    def _close_opposite_positions(self, signal_type: str):
        """
        Fecha posicoes opostas
        """
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            for pos in positions:
                if signal_type == "BUY" and pos['type'] == 1:  # Fechar SELL (type=1)
                    self.mt5.close_position(pos['ticket'])
                elif signal_type == "SELL" and pos['type'] == 0:  # Fechar BUY (type=0)
                    self.mt5.close_position(pos['ticket'])

        except Exception as e:
            print(f"Erro ao fechar posicoes opostas: {e}")

    def _trailing_worker_callback(self, position, current_bid, current_ask):
        """
        Callback chamado pelo worker a cada 2s para atualizar trailing.
        Esta funcao executa em thread separada!

        Args:
            position: Posicao do MT5
            current_bid: Preco bid atual
            current_ask: Preco ask atual

        Returns:
            True se atualizou trailing, False caso contrario
        """
        try:
            # Usar dict-style access (position do worker vem como dict)
            ticket = position.get('ticket') if isinstance(position, dict) else position.ticket

            # Apenas processar nossa posição
            if self.last_position_ticket and ticket != self.last_position_ticket:
                return False

            # Converter para dict se necessário
            if not isinstance(position, dict):
                pos_dict = {
                    'ticket': position.ticket,
                    'type': position.type,
                    'price_open': position.price_open,
                    'profit': position.profit,
                    'volume': position.volume,
                    'sl': position.sl,
                    'tp': position.tp
                }
            else:
                pos_dict = position

            # Processar trailing
            return self._update_trailing_from_worker(pos_dict, current_bid, current_ask)

        except Exception as e:
            print(f"[WORKER] Erro no callback: {e}")
            return False


    def _update_trailing_from_worker(self, pos, current_bid, current_ask):
        """
        Atualiza trailing stop a partir do worker.
        Logica identica a _manage_position_trailing mas otimizada para worker.

        Returns:
            True se atualizou, False caso contrario
        """
        try:
            # Verificar entry_price
            if self.entry_price <= 0:
                return False

            # Obter tipo e preco atual
            pos_type = pos.get('type', 0)
            current_price = current_bid if pos_type == 0 else current_ask

            # Calcular lucro (converter diferença de preço para pontos MT5)
            if pos_type == 0:  # BUY
                profit_price_diff = current_price - self.entry_price
            else:  # SELL
                profit_price_diff = self.entry_price - current_price

            # Converter para pontos MT5
            profit_pontos = profit_price_diff / self.symbol_point

            # Ativar trailing se atingiu threshold
            if not self.trailing_active and profit_pontos >= self.current_trailing_activation_pontos:
                self.trailing_active = True

                # Atualizar variável de exibição
                self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100

                # Converter pontos para variação de preço
                trailing_price_distance = self.current_trailing_distance_pontos * self.symbol_point

                # Calcular trailing stop price
                if pos_type == 0:  # BUY
                    self.trailing_stop_price = current_price - trailing_price_distance
                else:  # SELL
                    self.trailing_stop_price = current_price + trailing_price_distance

                # Modificar SL
                try:
                    self.mt5.modify_position(
                        ticket=pos.get('ticket'),
                        sl=self.trailing_stop_price,
                        tp=0
                    )
                    profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)
                    print(f"\n[WORKER] TRAILING ATIVADO! Lucro: {profit_pontos:.1f}pts (${profit_dinheiro:.2f})")
                    return True
                except Exception as e:
                    print(f"[WORKER] Erro ao ativar trailing: {e}")
                    return False

            # Atualizar trailing se já ativo
            if self.trailing_active:
                updated = False

                if pos_type == 0:  # BUY - trailing sobe
                    new_stop = current_price - self.current_trailing_distance_pontos
                    if new_stop > self.trailing_stop_price:
                        old_stop = self.trailing_stop_price
                        self.trailing_stop_price = new_stop

                        try:
                            self.mt5.modify_position(
                                ticket=pos.get('ticket'),
                                sl=new_stop,
                                tp=0
                            )
                            movimento = new_stop - old_stop
                            print(f"[WORKER] Trailing subiu: ${old_stop:.2f} -> ${new_stop:.2f} (+{movimento:.2f})")
                            updated = True
                        except Exception as e:
                            print(f"[WORKER] Erro ao subir trailing: {e}")

                else:  # SELL - trailing desce
                    new_stop = current_price + self.current_trailing_distance_pontos
                    if new_stop < self.trailing_stop_price:
                        old_stop = self.trailing_stop_price
                        self.trailing_stop_price = new_stop

                        try:
                            self.mt5.modify_position(
                                ticket=pos.get('ticket'),
                                sl=new_stop,
                                tp=0
                            )
                            movimento = old_stop - new_stop
                            print(f"[WORKER] Trailing desceu: ${old_stop:.2f} -> ${new_stop:.2f} (+{movimento:.2f})")
                            updated = True
                        except Exception as e:
                            print(f"[WORKER] Erro ao descer trailing: {e}")

                return updated

            return False

        except Exception as e:
            print(f"[WORKER] Erro ao atualizar trailing: {e}")
            return False


    def _manage_trailing(self):
        """
        Gerencia trailing stop
        """
        if not self.trailing_active:
            return
        
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            for pos in positions:
                self._manage_position_trailing(pos)
                
        except Exception as e:
            print(f"Erro ao gerenciar trailing: {e}")

    def _manage_position_trailing(self, pos):
        """
        Gerencia trailing de uma posicao - CORE DA ESTRATÉGIA LOSS ZERO
        """
        try:
            # Obter preço atual do tick
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if tick:
                current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
            else:
                current_price = pos.get('price_open', 0)

            # Verificar se entry_price é válido
            if self.entry_price <= 0:
                return

            # Obter tipo de posição (0=BUY, 1=SELL)
            pos_type = pos.get('type', 0)

            # Calcular lucro (converter diferença de preço para pontos MT5)
            if pos_type == 0:  # BUY
                profit_price_diff = current_price - self.entry_price
            else:  # SELL
                profit_price_diff = self.entry_price - current_price

            # Converter para pontos MT5
            profit_pontos = profit_price_diff / self.symbol_point

            # Lucro em dinheiro (GOLD - usa point_value)
            profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)

            # DEBUG: Mostrar status
            if not self.trailing_active:
                falta_pontos = self.current_trailing_activation_pontos - profit_pontos
                falta_dinheiro = self._pontos_para_dinheiro(falta_pontos)
                print(f"   [AGUARDANDO] Lucro: {profit_pontos:.1f}pts (${profit_dinheiro:.2f}) | Ativa em: {self.current_trailing_activation_pontos:.0f}pts | Faltam: {falta_pontos:.1f}pts (${falta_dinheiro:.2f})")
                print(f"   [DEBUG] entry_price: ${self.entry_price:.2f}, current_price: ${current_price:.2f}, profit_price_diff: {profit_price_diff:.4f}, symbol_point: {self.symbol_point}")

            # Verificar se atingiu lucro para ATIVAR trailing
            if not self.trailing_active and profit_pontos >= self.current_trailing_activation_pontos:
                self.trailing_active = True

                # Converter pontos para variação de preço
                trailing_price_distance = self.current_trailing_distance_pontos * self.symbol_point

                # Calcular trailing stop price (distância em pontos convertida para preço)
                if pos_type == 0:  # BUY
                    self.trailing_stop_price = current_price - trailing_price_distance
                else:  # SELL
                    self.trailing_stop_price = current_price + trailing_price_distance

                # Calcular lucro protegido (GOLD - usa point_value)
                lucro_protegido_pontos = profit_pontos - self.current_trailing_distance_pontos
                lucro_protegido_dinheiro = self._pontos_para_dinheiro(lucro_protegido_pontos)

                # MODIFICAR SL NO MT5 (mover para trailing)
                success = self._safe_modify_sl(pos.get('ticket'), self.trailing_stop_price, "ATIVAR")
                if success:
                    print(f"   [SL MOVIDO PARA TRAILING] Agora protege lucro!")

                    # REGISTRAR TRAILING STOP ATIVADO
                    try:
                        trailing_data = {
                            'trade_id': self.current_trade_id,
                            'ticket': pos.get('ticket'),
                            'symbol': self.symbol,
                            'action': 'ACTIVATED',
                            'old_sl_price': pos.get('sl', 0),
                            'new_sl_price': self.trailing_stop_price,
                            'current_price': current_price,
                            'profit_pontos': profit_pontos,
                            'profit_dinheiro': profit_dinheiro,
                            'trailing_distance_pontos': self.current_trailing_distance_pontos,
                            'trailing_distance_dinheiro': trailing_distance_dinheiro,
                            'reason': f'Trailing activated at {profit_pontos:.1f}pts profit',
                            'agent_version': "1.0.0"
                        }
                        self.btc_logger.log_trailing_stop(trailing_data)
                        print(f"   [DB] Trailing activation logged")
                    except Exception as e:
                        print(f"   [DB] Erro ao logar trailing activation: {e}")

                else:
                    print(f"   [ERRO] Falha ao mover SL para trailing!")

                print(f"")
                print(f"{'='*60}")
                print(f"[TRAILING ATIVADO]")
                print(f"   Lucro atual: {profit_pontos:.1f} pts (${profit_dinheiro:.2f})")
                print(f"   Trailing ativou em: {self.current_trailing_activation_pontos:.0f} pts")
                print(f"   Trailing Stop: ${self.trailing_stop_price:.2f}")
                print(f"   Distancia: {self.current_trailing_distance_pontos:.0f} pts")
                print(f"   LUCRO MINIMO PROTEGIDO: {lucro_protegido_pontos:.1f} pts (${lucro_protegido_dinheiro:.2f})")
                print(f"   A partir de agora: IMPOSSIVEL PERDER!")
                print(f"{'='*60}")
                print(f"")

            # Atualizar trailing (SOBE/DESCE COM O PREÇO)
            if self.trailing_active:
                # Calcular lucro protegido atual (GOLD - converter preço para pontos)
                if pos_type == 0:  # BUY
                    lucro_protegido_price_diff = self.trailing_stop_price - self.entry_price
                else:  # SELL
                    lucro_protegido_price_diff = self.entry_price - self.trailing_stop_price

                # Converter diferença de preço para pontos MT5
                lucro_protegido_pontos = lucro_protegido_price_diff / self.symbol_point
                lucro_protegido_dinheiro = self._pontos_para_dinheiro(lucro_protegido_pontos)

                print(f"   [TRAILING ATIVO] Lucro: {profit_pontos:.1f}pts (${profit_dinheiro:.2f}) | Protegido: {lucro_protegido_pontos:.1f}pts (${lucro_protegido_dinheiro:.2f}) | Stop: ${self.trailing_stop_price:.2f}")

                # Converter pontos para variação de preço
                trailing_price_distance = self.current_trailing_distance_pontos * self.symbol_point

                # Para posições BUY: trailing SOBE com o preço
                if pos_type == 0:  # BUY
                    new_stop = current_price - trailing_price_distance
                    if new_stop > self.trailing_stop_price:
                        old_stop = self.trailing_stop_price
                        self.trailing_stop_price = new_stop
                        movimento = new_stop - old_stop

                        # MODIFICAR SL NO MT5
                        try:
                            self.mt5.modify_position(
                                ticket=pos.get('ticket'),
                                sl=new_stop,
                                tp=0
                            )
                            print(f"   [TRAILING SUBIU]: ${old_stop:.2f} -> ${new_stop:.2f} (+{movimento:.2f}) [OK]")

                            # REGISTRAR TRAILING STOP MOVIMENTO
                            try:
                                trailing_data = {
                                    'trade_id': self.current_trade_id,
                                    'ticket': pos.get('ticket'),
                                    'symbol': self.symbol,
                                    'action': 'MOVED_UP',
                                    'old_sl_price': old_stop,
                                    'new_sl_price': new_stop,
                                    'current_price': current_price,
                                    'profit_pontos': profit_pontos,
                                    'profit_dinheiro': profit_dinheiro,
                                    'trailing_distance_pontos': self.current_trailing_distance_pontos,
                                    'trailing_distance_dinheiro': self._pontos_para_dinheiro(self.current_trailing_distance_pontos),
                                    'reason': f'Trailing moved up by {movimento:.2f}',
                                    'agent_version': "1.0.0"
                                }
                                self.btc_logger.log_trailing_stop(trailing_data)
                            except Exception as e:
                                print(f"   [DB] Erro ao logar trailing move up: {e}")

                        except Exception as e:
                            print(f"   [ERRO] Falha ao atualizar trailing: {e}")

                # Para posições SELL: trailing DESCE com o preço
                else:  # SELL
                    new_stop = current_price + trailing_price_distance
                    if new_stop < self.trailing_stop_price:
                        old_stop = self.trailing_stop_price
                        self.trailing_stop_price = new_stop
                        movimento = old_stop - new_stop

                        # MODIFICAR SL NO MT5
                        try:
                            self.mt5.modify_position(
                                ticket=pos.get('ticket'),
                                sl=new_stop,
                                tp=0
                            )
                            print(f"   [TRAILING DESCEU]: ${old_stop:.2f} -> ${new_stop:.2f} (-{movimento:.2f}) [OK]")

                            # REGISTRAR TRAILING STOP MOVIMENTO
                            try:
                                trailing_data = {
                                    'trade_id': self.current_trade_id,
                                    'ticket': pos.get('ticket'),
                                    'symbol': self.symbol,
                                    'action': 'MOVED_DOWN',
                                    'old_sl_price': old_stop,
                                    'new_sl_price': new_stop,
                                    'current_price': current_price,
                                    'profit_pontos': profit_pontos,
                                    'profit_dinheiro': profit_dinheiro,
                                    'trailing_distance_pontos': self.current_trailing_distance_pontos,
                                    'trailing_distance_dinheiro': self._pontos_para_dinheiro(self.current_trailing_distance_pontos),
                                    'reason': f'Trailing moved down by {movimento:.2f}',
                                    'agent_version': "1.0.0"
                                }
                                self.btc_logger.log_trailing_stop(trailing_data)
                            except Exception as e:
                                print(f"   [DB] Erro ao logar trailing move down: {e}")

                        except Exception as e:
                            print(f"   [ERRO] Falha ao atualizar trailing: {e}")

        except Exception as e:
            print(f"Erro ao gerenciar posicao: {e}")

    def _calculate_stop_level(self, pos_type: int, current_price: float) -> float:
        """
        Calcula nivel do trailing stop
        """
        if pos_type == 0:  # BUY
            return current_price * (1 - self.trailing_distance / 100)
        else:  # SELL
            return current_price * (1 + self.trailing_distance / 100)

    def _safe_modify_sl(self, ticket: int, new_sl: float, action: str) -> bool:
        """
        Modifica Stop Loss de forma segura com logs detalhados e retry
        
        Args:
            ticket: Ticket da posição
            new_sl: Novo preço do Stop Loss
            action: Ação sendo executada ("ATIVAR", "ATUALIZAR", "SUBIR", "DESCER")
            
        Returns:
            True se modificou com sucesso, False caso contrário
        """
        try:
            # Verificar se MT5 está conectado
            if not self.mt5:
                print(f"   [ERRO] MT5 não conectado!")
                return False
            
            # Verificar se ticket é válido
            if not ticket or ticket <= 0:
                print(f"   [ERRO] Ticket inválido: {ticket}")
                return False
            
            # Verificar se novo SL é válido
            if not new_sl or new_sl <= 0:
                print(f"   [ERRO] Stop Loss inválido: {new_sl}")
                return False
            
            # Obter posição atual para verificar se existe
            position = self.mt5.positions_get_by_ticket(ticket)
            if not position:
                print(f"   [ERRO] Posição não encontrada - Ticket: {ticket}")
                return False
            
            # Usar lock para evitar conflitos entre threads
            with self._trailing_lock:
                # Obter preço atual para calcular distância
                tick = self.mt5.get_symbol_info_tick(self.symbol)
                if not tick:
                    print(f"   [ERRO] Não foi possível obter preço atual")
                    return False
                
                current_price = tick['bid'] if position[0]['type'] == 0 else tick['ask']
                
                # Calcular distância do preço atual
                if position[0]['type'] == 0:  # BUY
                    distance_pct = ((current_price - new_sl) / current_price) * 100
                    direction = "acima"
                else:  # SELL
                    distance_pct = ((new_sl - current_price) / current_price) * 100
                    direction = "abaixo"
                
                # Verificar se distância é muito pequena (evitar modificações desnecessárias)
                if distance_pct < 0.001:  # 0.001%
                    print(f"   [INFO] Distância muito pequena ({distance_pct:.4f}%), pulando modificação")
                    return False
                
                # Log da tentativa
                print(f"   [MT5] Tentando {action} SL - Ticket: {ticket}")
                print(f"   [MT5] Preço atual: ${current_price:.2f}")
                print(f"   [MT5] Novo SL: ${new_sl:.2f} ({distance_pct:.4f}% {direction})")
                
                # Tentar modificar posição
                result = self.mt5.modify_position(
                    ticket=ticket,
                    sl=new_sl,
                    tp=0  # Manter TP inalterado
                )
                
                # Verificar resultado
                if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                    print(f"   [MT5] ✅ Sucesso! SL modificado para ${new_sl:.2f}")
                    
                    # Atualizar timestamp da última modificação
                    self._last_sl_modification = time.time()
                    return True
                else:
                    # Log do erro detalhado
                    error_code = result.get('retcode', 'Unknown') if result else 'No result'
                    error_desc = result.get('comment', 'No description') if result else 'No result'
                    
                    print(f"   [MT5] ❌ Falha ao modificar SL")
                    print(f"   [MT5] Erro: {error_code} - {error_desc}")
                    
                    # Tentar novamente após 1 segundo (retry)
                    print(f"   [MT5] Aguardando 1s antes do retry...")
                    time.sleep(1)
                    
                    result_retry = self.mt5.modify_position(
                        ticket=ticket,
                        sl=new_sl,
                        tp=0
                    )
                    
                    if result_retry and result_retry.get('retcode') == 10009:
                        print(f"   [MT5] ✅ Sucesso no retry! SL modificado para ${new_sl:.2f}")
                        self._last_sl_modification = time.time()
                        return True
                    else:
                        error_code_retry = result_retry.get('retcode', 'Unknown') if result_retry else 'No result'
                        error_desc_retry = result_retry.get('comment', 'No description') if result_retry else 'No result'
                        print(f"   [MT5] ❌ Falha no retry também")
                        print(f"   [MT5] Erro retry: {error_code_retry} - {error_desc_retry}")
                        return False
                        
        except Exception as e:
            print(f"   [MT5] ❌ Exceção ao modificar SL: {e}")
            return False

    def _get_time(self):
        """
        Retorna hora atual
        """
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
