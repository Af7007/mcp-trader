#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss Zero v3.2.0 - ACOES ANTI-LOSS
Estrategia: v3.1.0 + Circuit Breaker + Break-Even + Cooldown

MUDANCAS v3.2.0 (vs v3.1.0):
- NOVO: Circuit Breaker REAL (para apos 3 losses, aguarda 5min) - MAIS AGRESSIVO!
- NOVO: Break-Even Move (SL -> entry apos $1.50 lucro, protege wins)
- NOVO: Cooldown 30s (pausa apos cada trade, evita overtrading)
- RESULTADO ESPERADO: WR 65% -> 70%, menos losses consecutivas

VALORES BTC v3.2.0:
- Volume: 0.05 lotes (ULTRA CONSERVADOR - minimo risco)
- SL Fixo: $20.00 (MAIOR ESPACO - melhor timing de entrada)
- Trailing: Ativa $4.00, protege $2.00
- Break-Even: Move SL para entry apos $1.50 lucro (NOVO!)
- Circuit Breaker: Para apos 3 losses consecutivas (NOVO! AGRESSIVO!)
- Cooldown: 30s entre trades (NOVO!)
- Score M5: 4.5 (apenas sinais fortes)
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
from core.btc_logger import BTCLogger
from core.mt5_direct_client import get_mt5_client
from core.position_monitor_worker import PositionMonitorWorker

logger = logging.getLogger(__name__)


class BTCLossZeroV3:
    """
    Agente BTC v3.0.0 - COPIA SIMPLIFICADA DO GOLD 2.0.0
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",
        volume: float = 0.30,  # BTC: 0.30 lotes (10x Gold)
        check_interval: int = 1,
        stop_loss_atr_multiplier: float = 5.0,
        fixed_sl_dollars: float = 5.0,
        use_buy: bool = True,
        use_sell: bool = True
    ):
        """
        BTC v3.0.0 - Mesmos parametros do Gold, valores BTC
        """
        self.symbol = symbol
        self.volume = volume
        if volume < 0.01:
            print(f"AVISO: Volume muito baixo {volume}, minimo e 0.01")
            self.volume = 0.01
        elif volume > 0.5:
            print(f"AVISO: Volume {volume} lotes e alto! Certifique-se de ter margem suficiente.")
        self.check_interval = check_interval
        self.sl_atr_mult = stop_loss_atr_multiplier
        self.fixed_sl_dollars = fixed_sl_dollars  # v3.2.0: Usar parametro (default 5.0, ou 8.0 do btc_ai_agent)
        self.use_buy = use_buy
        self.use_sell = use_sell

        # TRAILING STOP - v3.3.0: PROGRESSIVO
        self.trailing_activation_dollar = 3.5   # v3.3.0: Ativa em $3.50 lucro
        self.trailing_distance_dollar = 2.0     # Nao usado (calculo progressivo)
        self.profit_step_for_increment_dollar = 3.0  # Nao usado
        self.protection_increment_dollar = 2.0  # Nao usado

        # FILTROS - v3.1.0: SCORE MAIOR (APENAS SINAIS FORTES)
        self.min_score_m5 = 4.5         # v3.1.0: 4.5 (vs 3.5 v3.0.0) - CORRECAO CRITICA
        self.max_atr_m5_dollars = 999.0 # SEM LIMITE ATR (BTC ATR $20-30 é normal)
        self.max_spread_dollars = 50.0  # Max spread $50 (BTC spread $15-20)

        # SL/Trailing dinamicos
        self.current_sl_pontos = 0
        self.current_atr = 0

        # Conexao MT5
        self.mt5 = get_mt5_client()

        # Worker
        self.position_worker = None

        # Estado Loss 0 - MULTIPLAS POSICOES
        self.trailing_active = False
        self.trailing_distance = 0.0
        self.entry_price = 0.0
        self.highest_profit = 0.0
        self.trailing_stop_price = 0.0
        self.last_position_ticket = None

        # Dicionarios para rastrear multiplas posicoes
        self.positions_entry_price = {}
        self.positions_trailing_active = {}
        self.positions_trailing_stop = {}
        self.positions_trade_id = {}
        self.current_trade_id = None

        # LOCK
        self._trailing_lock = threading.Lock()
        self._last_sl_modification = 0

        # Controle de cooldown
        self.last_close_time = 0
        self.cooldown_seconds = 30
        self.cooldown_same_direction = 10
        self.last_trade_type = None
        self.last_trade_was_win = False
        self.consecutive_wins_same_direction = 0

        # Valor do ponto
        self.point_value = None
        self.symbol_point = None
        self._calculate_point_value()

        # CIRCUIT BREAKER v3.2.0 - REAL (3 PERDAS)
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3  # v3.2.0: 3 perdas (mais agressivo)
        self.circuit_breaker_active = False

        # BREAK-EVEN v3.4.0 - $1.00 para evitar prejuizo
        self.breakeven_activation_dollar = 1.0  # v3.4.0: Move SL para entry apos $1.00 lucro
        self.positions_breakeven_moved = {}  # Rastreia se BE ja foi movido

        # Logger
        self.logger = BTCLogger(db_path="btc_trading_logs.db")

        print()
        print("=" * 60)
        print(f"Agente BTC Loss Zero v3.6.0 - SL DINAMICO ATR")
        print("=" * 60)
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume} lotes")
        print(f"   SL: DINAMICO ({self.sl_atr_mult:.1f}x ATR, min $8, max $20)")
        print(f"   TP: SEM TP FIXO (protecao progressiva)")
        print(f"   BUY/SELL: {'BUY ' if use_buy else ''}{'SELL' if use_sell else ''}")
        print(f"   Horarios: 24/7 (sem bloqueios)")
        print(f"   Filtros: M5 (score >= {self.min_score_m5}) + M1 Timing")
        print(f"   Logger: ATIVO")
        print()
        print("   ACOES ANTI-LOSS v3.6.0:")
        print(f"   [1] Circuit Breaker: Para apos {self.max_consecutive_losses} losses (aguarda 5min)")
        print(f"   [2] Break-Even: SL -> entry apos ${self.breakeven_activation_dollar:.2f} lucro")
        print(f"   [3] Cooldown: {self.cooldown_seconds}s entre trades")
        print()
        print("   PROTECAO PROGRESSIVA v3.5.0 (PASSOS DE $2):")
        print(f"   - $1.00 lucro -> SL em entry (protege $0)")
        print(f"   - $3.00 lucro -> SL protege $1.00")
        print(f"   - $5.00 lucro -> SL protege $3.00")
        print(f"   - $7.00 lucro -> SL protege $5.00")
        print(f"   - Formula: protecao = lucro - $2.00 (deixa $2 de espaco)")
        print()
        print("   FILTROS:")
        print(f"   1. M5: Score >= {self.min_score_m5} (apenas sinais FORTES)")
        print(f"   2. ATR: SEM LIMITE (BTC ATR $20-30 e normal)")
        print(f"   3. Spread: Max ${self.max_spread_dollars:.2f}")
        print(f"   4. M1: 2 velas confirmacao")
        print(f"   5. SL fixo ${self.fixed_sl_dollars:.2f}")
        print()
        print("   MELHORIAS ESPERADAS v3.2.0:")
        print(f"   - Win Rate: 65% -> 70% (+5%)")
        print(f"   - Max Losses Consecutivas: 3 (para agente) - MUITO AGRESSIVO!")
        print(f"   - Trades viram Loss apos $2: ELIMINADO (break-even)")
        print(f"   - Overtrading: ELIMINADO (cooldown 30s)")
        print("=" * 60)
        print()

    def _calculate_point_value(self):
        """Calcula valor do ponto dinamicamente (SEM volume - sera aplicado depois)"""
        try:
            symbol_info = self.mt5.get_symbol_info(symbol=self.symbol)
            if not symbol_info:
                print(f"[ERRO] Nao foi possivel obter info do simbolo {self.symbol}")
                self.point_value = 0.01  # Fallback BTC (por lote)
                self.symbol_point = 0.01
                return

            # Point e a variacao minima de preco (ex: 0.01 para BTC)
            self.symbol_point = symbol_info.get('point', 0.01)

            # Tick value e o valor em dolar de 1 tick (ponto) POR LOTE
            # NAO multiplicamos por volume aqui - sera feito nas formulas
            self.point_value = symbol_info.get('trade_tick_value', 0.01)

            print(f"[{self.symbol[:3]}] Point (variacao preco): {self.symbol_point}")
            print(f"[{self.symbol[:3]}] Valor do ponto: ${self.point_value:.4f} por lote")
            print(f"[{self.symbol[:3]}] Com volume {self.volume}: 1 ponto = ${self.point_value * self.volume:.4f}")

        except Exception as e:
            print(f"[ERRO] Ao calcular point value: {e}")
            self.point_value = 0.01
            self.symbol_point = 0.01

    def _calculate_atr_simple(self, rates, period=14):
        """Calcula ATR (Average True Range)"""
        if len(rates) < period + 1:
            return 0

        atr_sum = 0
        for i in range(period):
            if i >= len(rates):
                break
            high = rates[i]['high']
            low = rates[i]['low']
            close_prev = rates[i+1]['close'] if i+1 < len(rates) else rates[i]['close']

            tr = max(
                high - low,
                abs(high - close_prev),
                abs(low - close_prev)
            )
            atr_sum += tr

        return atr_sum / period if period > 0 else 0

    def _calculate_rsi(self, closes, period=14):
        """Calcula RSI"""
        if len(closes) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(period):
            if i >= len(closes) - 1:
                break
            change = closes[i] - closes[i+1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _get_simple_signal(self):
        """
        Analisa M5 para sinal (score-based)
        ADAPTADO PARA BTC: Mais tolerante (score 3.5 vs 4.0)
        """
        try:
            # Buscar dados M5
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=50
            )

            if not rates_m5 or len(rates_m5) < 50:
                return None

            # Inverter ordem (mais recente primeiro)
            rates_m5 = rates_m5[::-1]

            closes = [r['close'] for r in rates_m5[:50]]
            current = closes[0]

            # Indicadores
            sma20 = sum(closes[:20]) / 20
            sma50 = sum(closes[:50]) / 50
            rsi = self._calculate_rsi(closes, 14)

            # Tendencia
            uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
            downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

            # Momentum
            momentum = (current - closes[9]) / closes[9] * 100

            # ATR
            atr_m5_pontos = self._calculate_atr_simple(rates_m5, 14)
            atr_dollars = atr_m5_pontos * self.point_value * self.volume

            # FILTRO ATR (REMOVIDO - SEM LIMITE)
            # BTC pode ter ATR $20-30, e normal!

            # FILTRO SPREAD (ADAPTADO)
            tick = self.mt5.get_symbol_info_tick(symbol=self.symbol)
            if tick:
                spread_dollars = tick['ask'] - tick['bid']
                if spread_dollars > self.max_spread_dollars:
                    return None

            # Calcular score BUY
            buy_score = 0
            if uptrend:
                buy_score += 1.5
            if current > sma20 > sma50:
                buy_score += 1.0
            if 40 < rsi < 70:
                buy_score += 1.0
            if momentum > 0.05:
                buy_score += 1.5

            # Calcular score SELL
            sell_score = 0
            if downtrend:
                sell_score += 1.5
            if current < sma20 < sma50:
                sell_score += 1.0
            if 30 < rsi < 60:
                sell_score += 1.0
            if momentum < -0.05:
                sell_score += 1.5

            # Verificar score minimo (3.5 vs Gold 4.0)
            if buy_score >= self.min_score_m5:
                return {
                    'type': 'BUY',
                    'score': buy_score,
                    'price': current,
                    'atr': atr_dollars,
                    'rsi': rsi,
                    'momentum': momentum
                }
            elif sell_score >= self.min_score_m5:
                return {
                    'type': 'SELL',
                    'score': sell_score,
                    'price': current,
                    'atr': atr_dollars,
                    'rsi': rsi,
                    'momentum': momentum
                }

            return None

        except Exception as e:
            print(f"[ERRO] _get_simple_signal: {e}")
            return None

    def _confirm_m1_timing(self, signal_type):
        """
        Confirma timing em M1 (2 velas consecutivas)
        IDENTICO AO GOLD
        """
        try:
            rates_m1 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=3
            )

            if not rates_m1 or len(rates_m1) < 3:
                return False

            rates_m1 = rates_m1[::-1]
            closes = [r['close'] for r in rates_m1[:3]]

            if signal_type == "BUY":
                # 2 velas UP consecutivas
                return closes[0] > closes[1] > closes[2]
            else:  # SELL
                # 2 velas DOWN consecutivas
                return closes[0] < closes[1] < closes[2]

        except Exception as e:
            print(f"[ERRO] _confirm_m1_timing: {e}")
            return False

    def _open_position(self, signal: dict):
        """
        Abre posicao BTC
        v3.6.0: SL DINAMICO baseado em ATR (evita bater em volatilidade)
        """
        try:
            signal_type = signal['type']
            current_price = signal['price']

            # CALCULAR ATR M5 ATUAL
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe=5,  # M5
                start_pos=0,
                count=20
            )

            if not rates_m5 or len(rates_m5) < 15:
                print("[ERRO] Sem dados M5 para calcular ATR")
                return False

            # ATR em pontos de preco
            atr_price = self._calculate_atr_simple(rates_m5, 14)

            # Calcular SL DINAMICO baseado em ATR
            # atr_price esta em pontos de preco (ex: $236 para BTC = volatilidade de $236)
            # Formula: SL_dollars = ATR * multiplicador * tick_value * volume
            # tick_value = $0.01 por lote para BTC
            # Multiplicador 40 para ter SL razoavel:
            #   ATR $200 * 40 * $0.01 * 0.05 = $4.00 -> min $8
            #   ATR $300 * 40 * $0.01 * 0.05 = $6.00 -> min $8
            #   ATR $400 * 40 * $0.01 * 0.05 = $8.00
            #   ATR $600 * 40 * $0.01 * 0.05 = $12.00
            #   ATR $1000 * 40 * $0.01 * 0.05 = $20.00 (max)
            atr_multiplier = 40.0
            sl_dollars_atr = atr_price * atr_multiplier * self.point_value * self.volume

            # LIMITES: min $8, max $20 (evita SL muito apertado ou muito largo)
            sl_dollars = max(8.0, min(20.0, sl_dollars_atr))

            # Calcular distancia em preco para o SL final
            # Reverter: sl_distance = sl_dollars / (tick_value * volume)
            sl_distance = sl_dollars / (self.point_value * self.volume)

            if signal_type == 'BUY':
                sl_price = current_price - sl_distance
            else:
                sl_price = current_price + sl_distance

            print(f"\n[ABRINDO POSICAO] {signal_type} {self.symbol}")
            print(f"   Score M5: {signal['score']:.1f}")
            print(f"   Preco: ${current_price:.2f}")
            print(f"   ATR M5: ${atr_price:.2f} (volatilidade)")
            print(f"   SL DINAMICO: ${sl_dollars:.2f} (ATR * 40)")
            print(f"   SL Price: ${sl_price:.2f}")
            print(f"   Volume: {self.volume}")
            if sl_dollars != sl_dollars_atr:
                if sl_dollars == 8.0:
                    print(f"   [LIMITADO MIN] ATR baixo, usando SL minimo $8 (calc ${sl_dollars_atr:.2f})")
                else:
                    print(f"   [LIMITADO MAX] ATR alto, usando SL maximo $20 (calc ${sl_dollars_atr:.2f})")

            # Abrir via MCP
            if signal_type == 'BUY':
                result = self.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment="BTC_LossZero_v3"
                )
            else:
                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment="BTC_LossZero_v3"
                )

            if result and result.get('retcode') == 10009:
                ticket = result.get('order')
                print(f"[OK] Posicao aberta: #{ticket}")

                # Salvar no DB
                trade_id = self.logger.log_trade_open(
                    ticket=ticket,
                    symbol=self.symbol,
                    trade_type=signal_type,
                    volume=self.volume,
                    entry_price=current_price,
                    sl_price=sl_price,
                    tp_price=0,
                    score=signal['score']
                )

                # Rastrear posicao
                self.last_position_ticket = ticket  # v3.2.0: Para detectar fechamento
                self.positions_entry_price[ticket] = current_price
                self.positions_trailing_active[ticket] = False
                self.positions_trailing_stop[ticket] = 0
                self.positions_trade_id[ticket] = trade_id
                self.positions_breakeven_moved[ticket] = False  # v3.2.0: Break-Even

                # Iniciar worker
                if not self.position_worker or not self.position_worker.is_alive():
                    worker_interval = 0.02  # 20ms em segundos
                    self.position_worker = PositionMonitorWorker(
                        mt5_client=self.mt5,
                        symbol=self.symbol,
                        check_interval=worker_interval,
                        trailing_callback=self._trailing_worker_callback
                    )
                    self.position_worker.start()
                    print(f"[WORKER] Monitor de trailing iniciado ({worker_interval*1000:.0f}ms)")

                return True
            else:
                print(f"[ERRO] Falha ao abrir posicao: {result}")
                return False

        except Exception as e:
            print(f"[ERRO] _open_position: {e}")
            return False

    def _check_last_trade_result(self, ticket: int) -> bool:
        """
        Verifica se ultimo trade foi lucro ou perda (v3.2.0)
        """
        try:
            from datetime import datetime, timedelta

            # Buscar historico das ultimas 24h
            date_from = datetime.now() - timedelta(hours=24)
            deals = self.mt5.history_deals_get(date_from=date_from, date_to=datetime.now())

            if not deals:
                return False  # Sem dados, assumir perda

            # Buscar deal de fechamento (DEAL_ENTRY_OUT) para este ticket
            for deal in reversed(deals):  # Comecar pelos mais recentes
                deal_ticket = deal.get('position_id', 0)
                if deal_ticket == ticket:
                    entry_type = deal.get('entry', 0)
                    if entry_type == 1:  # DEAL_ENTRY_OUT = saida
                        profit = deal.get('profit', 0)
                        return profit > 0  # True se lucro, False se perda

            return False  # Nao encontrou, assumir perda

        except Exception as e:
            print(f"   Erro ao verificar resultado: {e}")
            return False  # Em caso de erro, assumir perda

    def _record_trade_result(self, is_win: bool):
        """
        Registra resultado do trade e atualiza circuit breaker (v3.2.0)
        """
        # Atualizar rastreamento
        self.last_trade_was_win = is_win

        if is_win:
            self.consecutive_losses = 0  # Resetar contador em vitorias
            print(f"   [WIN] Circuit breaker resetado")
        else:
            self.consecutive_losses += 1
            print(f"   [LOSS] Perdas consecutivas: {self.consecutive_losses}/{self.max_consecutive_losses}")

            # Ativar circuit breaker se atingir limite
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.circuit_breaker_active = True
                print(f"")
                print(f"{'='*60}")
                print(f"[!] CIRCUIT BREAKER ATIVADO!")
                print(f"   Motivo: {self.consecutive_losses} perdas consecutivas")
                print(f"   Pausa: 5 minutos")
                print(f"   Sistema pausado para evitar mais perdas")
                print(f"{'='*60}")
                print(f"")

    def _check_and_move_breakeven(self, positions):
        """
        v3.5.0 - TRAILING COM PASSOS DE $2

        Regras:
        - $1.00 lucro -> SL em entry (break-even, protege $0)
        - $3.00 lucro -> SL protege $1.00 (sobe a cada $2)
        - $5.00 lucro -> SL protege $3.00 (sobe a cada $2)
        - $7.00 lucro -> SL protege $5.00 (sobe a cada $2)
        - Formula: protecao = lucro - $2.00 (deixa $2 de margem para respirar)
        """
        if not positions:
            return

        for position in positions:
            ticket = position.get('ticket')
            if not ticket:
                continue

            # Calcular lucro atual
            entry_price = self.positions_entry_price.get(ticket)
            if not entry_price:
                # FALLBACK: Buscar entry_price do MT5
                entry_price = position.get('price_open')
                if entry_price:
                    print(f"[PROTECTION DEBUG] Ticket {ticket} sem entry nos dicionarios, usando MT5: ${entry_price:.2f}")
                    # Adicionar ao dicionario para proximas checagens
                    self.positions_entry_price[ticket] = entry_price
                    self.positions_breakeven_moved[ticket] = False
                    self.positions_trailing_active[ticket] = False
                    self.positions_trailing_stop[ticket] = 0
                else:
                    print(f"[PROTECTION ERROR] Ticket {ticket} sem entry_price nem no dicionario nem no MT5!")
                    continue

            position_type = position.get('type')  # 0 = BUY, 1 = SELL
            current_price = position.get('price_current', 0)

            # Calcular lucro em pontos
            if position_type == 0:  # BUY
                profit_pontos = (current_price - entry_price) / self.symbol_point
            else:  # SELL
                profit_pontos = (entry_price - current_price) / self.symbol_point

            # Lucro em dolares
            profit_dollars = profit_pontos * self.point_value * self.volume

            # DEBUG: Mostrar calculo sempre que tiver lucro
            if profit_dollars > 0.3:
                print(f"[PROTECTION DEBUG] Ticket {ticket}: Lucro ${profit_dollars:.2f}")

            # Calcular qual SL deveria estar baseado no lucro atual
            new_sl = None
            protection_type = None

            if profit_dollars >= 1.0:
                # A partir de $1, calcula protecao progressiva
                if profit_dollars < 3.0:
                    # Entre $1 e $3: apenas break-even (protege $0)
                    new_sl = entry_price
                    protection_type = "BREAK-EVEN (protege $0)"
                else:
                    # A partir de $3: protege (lucro - $2)
                    protected_profit = profit_dollars - 2.0

                    # Calcular distancia em preco
                    protected_points = protected_profit / (self.point_value * self.volume)
                    protected_distance = protected_points * self.symbol_point

                    if position_type == 0:  # BUY
                        new_sl = entry_price + protected_distance
                    else:  # SELL
                        new_sl = entry_price - protected_distance

                    protection_type = f"TRAILING (protege ${protected_profit:.2f})"

            # Se calculou um novo SL, verificar se precisa mover
            if new_sl is not None:
                current_sl = position.get('sl', 0)
                should_update = False

                if position_type == 0:  # BUY - SL deve SUBIR
                    should_update = new_sl > current_sl
                else:  # SELL - SL deve DESCER
                    should_update = new_sl < current_sl

                if should_update:
                    try:
                        with self._trailing_lock:
                            result = self.mt5.modify_position(ticket=ticket, sl=new_sl)

                            if result and result.get('retcode') == 10009:
                                print(f"")
                                print(f"[PROTECTION] Posicao #{ticket}")
                                print(f"   Tipo: {protection_type}")
                                print(f"   Lucro atual: ${profit_dollars:.2f}")
                                print(f"   SL: ${current_sl:.2f} -> ${new_sl:.2f}")
                                print(f"")

                                # Marcar break-even como movido se for o primeiro movimento
                                if not self.positions_breakeven_moved.get(ticket, False):
                                    self.positions_breakeven_moved[ticket] = True
                            else:
                                print(f"[PROTECTION] Falha ao mover SL: {result}")

                    except Exception as e:
                        print(f"[PROTECTION] Erro: {e}")

    def _trailing_worker_callback(self, position, current_bid, current_ask):
        """
        v3.5.0 - Worker de Protecao Rapida (20ms)

        Usa MESMA LOGICA do _check_and_move_breakeven mas roda MUITO MAIS RAPIDO!

        Regras:
        - $1.00 lucro -> SL em entry (break-even, protege $0)
        - $3.00 lucro -> SL protege $1.00 (sobe a cada $2)
        - $5.00 lucro -> SL protege $3.00 (sobe a cada $2)
        - Formula: protecao = lucro - $2.00
        """
        try:
            # Obter ticket (position pode ser dict ou objeto)
            ticket = position.get('ticket') if isinstance(position, dict) else position.ticket

            # Verificar se esta posicao pertence a este agente
            if ticket not in self.positions_entry_price:
                return False

            # Converter para dict se necessario
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

            # Obter dados da posicao
            pos_type = pos_dict.get('type', 0)
            entry_price = self.positions_entry_price.get(ticket, pos_dict.get('price_open', 0))

            if entry_price <= 0:
                return False

            # Lucro em dolares (MT5 retorna profit direto em dolares)
            profit_dollars = float(pos_dict.get('profit', 0.0))
            current_sl = pos_dict.get('sl', 0)

            # DEBUG: Mostrar lucro quando > $0.30
            if profit_dollars > 0.3:
                print(f"[WORKER] Ticket {ticket}: Lucro ${profit_dollars:.2f}")

            # PROTECAO PROGRESSIVA v3.5.0 (MESMA LOGICA DO CHECK_AND_MOVE_BREAKEVEN)
            if profit_dollars >= 1.0:
                new_sl = None
                protection_type = None

                if profit_dollars < 3.0:
                    # Entre $1 e $3: apenas break-even
                    new_sl = entry_price
                    protection_type = "BREAK-EVEN (protege $0)"
                else:
                    # A partir de $3: protege (lucro - $2)
                    protected_profit = profit_dollars - 2.0

                    # Calcular distancia em preco
                    protected_points = protected_profit / (self.point_value * self.volume)
                    protected_distance = protected_points * self.symbol_point

                    if pos_type == 0:  # BUY
                        new_sl = entry_price + protected_distance
                    else:  # SELL
                        new_sl = entry_price - protected_distance

                    protection_type = f"TRAILING (protege ${protected_profit:.2f})"

                # Verificar se deve atualizar
                should_update = False

                if pos_type == 0:  # BUY - SL deve SUBIR
                    should_update = new_sl > current_sl
                else:  # SELL - SL deve DESCER
                    should_update = new_sl < current_sl

                if should_update:
                    result = self.mt5.modify_position(ticket=ticket, sl=new_sl, tp=None)

                    if result.get('retcode') == 10009:
                        print(f"\n[WORKER PROTECTION] Posicao #{ticket}")
                        print(f"   Tipo: {protection_type}")
                        print(f"   Lucro atual: ${profit_dollars:.2f}")
                        print(f"   SL: ${current_sl:.2f} -> ${new_sl:.2f}")

                        # Atualizar dicionarios
                        if profit_dollars >= 3.0:
                            self.positions_trailing_active[ticket] = True
                            self.positions_trailing_stop[ticket] = new_sl
                        else:
                            self.positions_breakeven_active[ticket] = True

                        return True

            return False

        except Exception as e:
            print(f"[WORKER CALLBACK] Erro: {e}")
            return False

    def run(self):
        """
        Loop principal - v3.2.0 ACOES ANTI-LOSS
        """
        print("\nAGENTE BTC LOSS ZERO v3.2.0 - INICIANDO (ANTI-LOSS ATIVAS)")
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
                print(f"[AGENTE] BTC LOSS ZERO v3.2 | Ciclo #{cycle} | {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)

                # Estado
                positions = self.mt5.positions_get(symbol=self.symbol)
                num_positions = len(positions) if positions else 0

                # v3.2.0: Detectar se posicao foi fechada pelo MT5 (SL/TP)
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
                        self.positions_breakeven_moved.pop(ticket, None)  # v3.2.0
                        print(f"   [CLEANUP] Removida posicao #{ticket} dos dicionarios")

                    self.last_position_ticket = None
                    print(f"[COOLDOWN ATIVADO] Aguardando antes de proximo trade")

                # v3.2.0: Verificar break-even para posicoes abertas
                if positions and num_positions > 0:
                    self._check_and_move_breakeven(positions)

                print(f"[AGENTE]:")
                print(f"   Estado: LOSS ZERO (Trailing ilimitado)")
                print(f"   Volume: {self.volume}")
                print(f"   Posicoes Abertas: {num_positions}")

                # Preco
                tick = self.mt5.get_symbol_info_tick(symbol=self.symbol)
                if tick:
                    price = tick['bid']
                    print(f"[MERCADO] ({self.symbol}):")
                    print(f"   Preco: ${price:.2f}")

                # Verificar se pode abrir (cooldown)
                if num_positions == 0:
                    current_time = time.time()

                    if self.last_close_time > 0:
                        elapsed = current_time - self.last_close_time

                        # Cooldown dinamico
                        if self.last_trade_was_win and self.last_trade_type:
                            cooldown_needed = self.cooldown_same_direction
                        else:
                            cooldown_needed = self.cooldown_seconds

                        if elapsed < cooldown_needed:
                            remaining = int(cooldown_needed - elapsed)
                            print(f"\n[COOLDOWN] Aguardando {remaining}s antes do proximo trade")
                            time.sleep(self.check_interval)
                            continue

                    # Buscar sinal M5
                    print(f"\n[M5] Analisando sinal (score >= {self.min_score_m5})...")
                    signal = self._get_simple_signal()

                    if signal:
                        print(f"[M5 SINAL] {signal['type']} (score {signal['score']:.1f})")
                        print(f"   ATR: ${signal['atr']:.2f}")
                        print(f"   RSI: {signal['rsi']:.1f}")
                        print(f"   Momentum: {signal['momentum']:.2f}%")

                        # Confirmar M1
                        print(f"\n[M1] Verificando timing (2 velas {signal['type']})...")
                        if self._confirm_m1_timing(signal['type']):
                            print(f"[M1 OK] 2 velas {signal['type']} consecutivas")
                            print(f"\n[SINAL CONFIRMADO] M5 {signal['type']} (score {signal['score']:.1f}) + M1 timing OK")

                            # Abrir posicao
                            self._open_position(signal)
                        else:
                            print(f"[M1 BLOQUEIO] Aguardando 2 velas {signal['type']} em M1")
                    else:
                        print(f"[M5] Nenhum sinal com score >= {self.min_score_m5}")

                # Aguardar proximo ciclo
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n\n[FINALIZANDO] Agente parado pelo usuario")
            if self.position_worker:
                self.position_worker.stop()
                self.position_worker.join(timeout=2)
            print("[OK] Agente encerrado com sucesso")


def main():
    """Entry point"""
    agent = BTCLossZeroV3(
        symbol="BTCUSDc",
        volume=0.05,  # v3.2.0: ULTRA CONSERVADOR (minimo risco)
        fixed_sl_dollars=5.0,
        use_buy=True,
        use_sell=True
    )

    agent.run()


if __name__ == '__main__':
    main()
