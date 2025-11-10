#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente GOLD Loss Zero - Otimizado para XAUUSDc (Gold - Conta Cents)
Estrategia: Trailing Stop ilimitado sem losses
Baseado em btc_loss_zero_simple.py com parametros otimizados para Gold

VERSAO 2.0.0 - MELHORIAS PARA SCALPING M5/M1:
- REMOVIDO: Validacao M15 (conflitava com operacoes rapidas)
- FOCO TOTAL: M5 (tendencia) + M1 (timing)
- Score minimo M5: 4.0 (apenas sinais fortes)
- Trailing Stop: ativa com $2.00 de lucro (ajustado para scalping)
- Filtro ATR M5: max $2.00 (evita alta volatilidade)
- Filtro Spread: max $0.50 (evita custos altos)
- Confirmacao M1: 2 velas consecutivas na direcao M5
- SL fixo: $5.00 (evita stops por ruido)

MONITORAMENTO CONTINUO:
- Thread principal: Analisa mercado e abre trades (1s)
- Worker thread: Monitora trailing stops em tempo real (20ms)
- Garante que nao perde movimentos rapidos entre ciclos
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
        volume: float = 0.03,  # GOLD: 0.03 lotes (aumentado de 0.02)
        check_interval: int = 1,  # CHANGED: 15s → 1s (mais responsivo com FALLBACK)
        stop_loss_atr_multiplier: float = 5.0,  # GOLD: SL = ATR × 5.0 (deprecated, usar fixed_sl_dollars)
        fixed_sl_dollars: float = 5.0,  # SL fixo em dólares ($5.00 - compensa slippage)
        use_buy: bool = True,
        use_sell: bool = True
    ):
        """
        Inicializa agente Loss Zero - ESTRATÉGIA TRAILING STOP

        Args:
            volume: FIXADO em 0.03 lotes (conta cents, aumentado)
            fixed_sl_dollars: SL fixo em $4.00
            stop_loss_atr_multiplier: Deprecated (usar fixed_sl_dollars)
            trailing_activation_dollar: Ativa trailing com $1 de lucro
            trailing_distance_dollar: Distância do trailing = $0.5

        ESTRATÉGIA:
            1. Abre posição com SL (ATR × 5.0)
            2. SEM TP fixo (lucro ilimitado!)
            3. Quando lucro >= $1, trailing ATIVA
            4. Trailing protege lucro com distância $0.5
            5. Trailing sobe/desce com o preço
            6. Fecha quando trailing é atingido (SEMPRE com lucro!)
        """
        self.symbol = symbol
        # CORRIGIDO: Volume fixo para conta cents
        self.volume = volume
        if volume < 0.01:
            print(f"AVISO: Volume muito baixo {volume}, mínimo é 0.01")
            self.volume = 0.01
        elif volume > 0.1:
            print(f"AVISO: Volume {volume} lotes é alto! Certifique-se de ter margem suficiente.")
        self.check_interval = check_interval
        self.sl_atr_mult = stop_loss_atr_multiplier
        self.fixed_sl_dollars = fixed_sl_dollars  # SL fixo em dólares
        self.use_buy = use_buy
        self.use_sell = use_sell

        # TRAILING STOP OTIMIZADO PARA SCALPING - BASEADO EM DÓLARES
        self.trailing_activation_dollar = 2.0   # Ativa com $2.00 de lucro (ajustado para scalping)
        self.trailing_distance_dollar = 1.0     # Protege $1.00 inicialmente
        self.profit_step_for_increment_dollar = 1.5 # A cada $1.50 de lucro adicional...
        self.protection_increment_dollar = 1.0  # ...protege $1.00 a mais

        # FILTROS DE QUALIDADE - NOVOS (para melhor assertividade)
        self.min_score_m5 = 4.0         # Score minimo M5 para entrada (apenas sinais fortes)
        self.max_atr_m5_dollars = 2.0   # ATR M5 maximo em dolares (evitar alta volatilidade)
        self.max_spread_dollars = 0.5   # Spread maximo permitido (evitar custos altos)

        # SL/Trailing dinâmicos calculados por ATR
        self.current_sl_pontos = 0
        self.current_atr = 0

        # Conexão MT5 direta (sem BTCHedgeAgent que modifica SL)
        self.mt5 = get_mt5_client()

        # Worker para monitoramento contínuo
        self.position_worker = None  # Será criado quando abrir posição

        # Estado Loss 0 - SUPORTE PARA MÚLTIPLAS POSIÇÕES
        self.trailing_active = False  # Mantido para compatibilidade
        self.trailing_distance = 0.0
        self.entry_price = 0.0  # Mantido para compatibilidade
        self.highest_profit = 0.0
        self.trailing_stop_price = 0.0
        self.last_position_ticket = None
        
        # NOVO: Dicionários para rastrear múltiplas posições
        self.positions_entry_price = {}  # {ticket: entry_price}
        self.positions_trailing_active = {}  # {ticket: True/False}
        self.positions_trailing_stop = {}  # {ticket: stop_price}
        self.positions_trade_id = {}  # {ticket: trade_id} - IMPORTANTE: Linkar ordem com banco!
        self.current_trade_id = None  # ID do trade no banco de dados (compatibilidade)

        # LOCK para evitar conflitos worker/main thread
        self._trailing_lock = threading.Lock()
        self._last_sl_modification = 0  # Timestamp da última modificação

        # Controle de cooldown entre trades
        self.last_close_time = 0
        self.cooldown_seconds = 30  # 30 segundos entre trades diferentes (era 120s = 2min)
        self.cooldown_same_direction = 10  # 10 segundos se mesma direção (aproveita onda! era 15s)
        self.last_trade_type = None  # Rastrear último tipo (BUY/SELL)
        self.last_trade_was_win = False  # Rastrear se último foi vitória
        self.consecutive_wins_same_direction = 0  # Contador de wins consecutivos na mesma direção

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

        # SL fixo em dólares (removido ATR dinâmico)
        # SL é preço absoluto, não precisa converter para pontos
        self.current_sl_pontos = None  # Deprecado, mantém para compatibilidade

        print(f"Agente GOLD Loss Zero v1.4.0 - SL DINAMICO ATR + PROTECAO PROGRESSIVA")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume} lotes (conta cents)")
        print(f"   SL: DINAMICO (ATR * 150, min $4, max $10)")
        print(f"   TP: SEM TP FIXO (trailing cuida)")
        print(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")
        print(f"   Circuit Breaker: {self.max_consecutive_losses} perdas consecutivas")
        print(f"   Horarios: 24/7 (sem bloqueios)")
        print(f"   Filtros: M5 + M15 + MULTIPLE_CONFIRMACOES")
        print(f"   Logger: ATIVO")
        print(f"")
        print(f"   PROTECAO PROGRESSIVA v1.4.0 (Worker 20ms):")
        print(f"   - $1.00 lucro -> Break-even (SL = entry, protege $0)")
        print(f"   - $3.00 lucro -> Trailing (protege $1.00)")
        print(f"   - $5.00 lucro -> Trailing (protege $3.00)")
        print(f"   - Formula: protecao = lucro - $2.00")
        print(f"   - CORRIGE BUG: Ordem atingia $7 mas protegia apenas $3.9")
        print(f"")

        print(f"   ESTRATEGIA CORRIGIDA:")
        print(f"   1. BUY: M15 DOWNTREND (comprar na baixa)")
        print(f"   2. SELL: M15 UPTREND (vender na alta)")
        print(f"   3. Multiple confirmacoes obrigatorias")
        print(f"   4. SL moderado para volatilidade Gold")
        print(f"   5. Trailing direto em dólares")
        print(f"   6. Zero losses garantidos")

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

    def _pontos_para_dinheiro(self, pontos: float) -> float:
        """
        Converte pontos MT5 para dinheiro considerando volume.

        Para Gold XAUUSDc:
        - Point value: $0.10 por lote por ponto
        - Com volume 0.02: 1 ponto = $0.0020
        - 3000 pontos × $0.0020 = $6.00

        Args:
            pontos: Número de pontos MT5

        Returns:
            Valor em dólares
        """
        if self.point_value is None or self.symbol_point is None:
            self._calculate_point_value()

        # CORRECAO: Usar point_value (nao symbol_point!)
        # point_value = valor em $ de 1 ponto para 1 lote
        # Formula: pontos × point_value × volume
        # Exemplo: 3000 pontos × $0.10 × 0.02 = $6.00
        return pontos * self.point_value * self.volume

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

        # INICIALIZAR WORKER SE JA EXISTIREM POSICOES ABERTAS
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            if positions and len(positions) > 0:
                print(f"[STARTUP] Detectadas {len(positions)} posicoes abertas")
                print(f"[STARTUP] Inicializando worker para posicoes existentes...")

                import os
                USE_WORKER = os.getenv("GOLD_USE_WORKER", "true").lower() == "true"

                if USE_WORKER:
                    try:
                        from core.position_monitor_worker import PositionMonitorWorker
                        worker_interval = 0.02
                        self.position_worker = PositionMonitorWorker(
                            mt5_client=self.mt5,
                            symbol=self.symbol,
                            check_interval=worker_interval,
                            trailing_callback=self._trailing_worker_callback
                        )
                        self.position_worker.start()

                        import time as t
                        t.sleep(0.1)

                        if self.position_worker.is_running():
                            print(f"[STARTUP] Worker ATIVO (20ms checks, 50/segundo)")

                            # REGISTRAR POSICOES EXISTENTES NO DICIONARIO
                            for pos in positions:
                                ticket = pos.get('ticket')
                                entry_price = pos.get('price_open', 0)
                                if ticket and entry_price > 0:
                                    self.positions_entry_price[ticket] = entry_price
                                    print(f"[STARTUP] Posicao #{ticket} registrada (entry ${entry_price:.2f})")
                        else:
                            print(f"[STARTUP] Worker falhou - usando FALLBACK (1s)")
                            self.position_worker = None
                    except Exception as e:
                        print(f"[STARTUP] Erro ao iniciar worker: {e}")
                        print(f"[STARTUP] Usando FALLBACK (1s)")
                        self.position_worker = None
        except Exception as e:
            print(f"[STARTUP] Erro ao verificar posicoes: {e}")

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
        print(f"[AGENTE] GOLD LOSS ZERO | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*60}")
        
        # Status do agente
        print(f"[AGENTE]:")
        print(f"   Estado: LOSS ZERO (Trailing ilimitado)")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing Ativo: {'SIM' if self.trailing_active else 'NAO'}")
        if self.trailing_active:
            print(f"   Distancia Trailing: SISTEMA SIMPLIFICADO (em dólares)")
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
                        if self.entry_price > 0:
                            profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                            print(f"   Lucro Atual: {profit_pct:.2f}%")
                        # Verificar tipo da posição aberta
                        positions = self.mt5.positions_get(symbol=self.symbol)
                        if positions and len(positions) > 0:
                            direction = "LONG" if positions[0]['type'] == 0 else "SHORT"
                            print(f"   Posicao: {direction}")
                        else:
                            print(f"   Posicao: UNKNOWN")
                    
                    # Gerar sinal para logging (CORRIGIDO: apenas uma vez!)
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
                'agent_version': "2.0.0"
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

            # CAPTURAR DADOS DA POSICAO ANTES QUE ELA SUMA (se ainda existe)
            position_data_before_close = None
            if self.last_position_ticket and positions:
                for pos in positions:
                    if pos.get('ticket') == self.last_position_ticket:
                        position_data_before_close = {
                            'exit_price': pos.get('price_current', 0),
                            'profit_loss': pos.get('profit', 0),
                            'volume': pos.get('volume', 0)
                        }
                        break

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
                self._record_trade_result(is_win, position_data_before_close)

                print(f"   Resultado: {'[WIN]' if is_win else '[LOSS]'}")
                print(f"   Possível motivo: {'TP atingido' if is_win else 'SL atingido'}")

                self.trailing_active = False
                self.trailing_distance = 0.0
                self.last_close_time = time.time()
                
                # NOVO: Limpar dicionários da posição fechada
                ticket = self.last_position_ticket
                if ticket:
                    self.positions_entry_price.pop(ticket, None)
                    self.positions_trailing_active.pop(ticket, None)
                    self.positions_trailing_stop.pop(ticket, None)
                    print(f"   [CLEANUP] Removida posição #{ticket} dos dicionários")
                
                self.last_position_ticket = None
                print(f"[COOLDOWN ATIVADO] Aguardando {self.cooldown_seconds}s antes de próximo trade")

            if not positions:
                # Nenhuma posicao, analisa para abrir
                self._analyze_and_open()
            else:
                # Tem posicao
                print(f"   [POSITIONS] Encontradas {len(positions)} posições abertas")

                # Se worker está ativo, deixa ele cuidar do trailing (20ms checks)
                # Não faça gerenciamento duplicado no loop principal (1s FALLBACK)
                worker_is_active = self.position_worker and self.position_worker.is_running()

                # DEBUG: Ver status do worker
                if self.position_worker:
                    is_running = self.position_worker.is_running()
                    print(f"   [WORKER STATUS] Existe: True | Rodando: {is_running}")
                    if not is_running:
                        print(f"      ⚠️  Worker criado mas não está rodando! Verificar thread...")
                else:
                    print(f"   [WORKER STATUS] Existe: False ⚠️")
                    print(f"      Worker não foi inicializado - Verificar logs acima")

                if not worker_is_active:
                    # Worker NÃO está ativo, gerencia trailing aqui (fallback)
                    print(f"   [WORKER] FALLBACK ATIVADO - Gerenciando trailing no loop principal (1s)")
                    for pos in positions:
                        self.last_position_ticket = pos.get('ticket')
                        self._manage_position_trailing(pos)
                else:
                    # Worker está ativo - só atualiza last_position_ticket, não faz trailing
                    for pos in positions:
                        self.last_position_ticket = pos.get('ticket')

        except Exception as e:
            print(f"Erro ao verificar posicoes: {e}")

    def _analyze_and_open(self):
        """
        Analisa mercado e abre posicao com filtros de segurança
        
        MODIFICADO: Permite múltiplas posições simultâneas (hedging)
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
        from datetime import datetime, timezone
        current_hour = datetime.now(timezone.utc).hour

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

    def _record_trade_result(self, is_win: bool, position_data_before_close: dict = None):
        """
        Registra resultado do trade e atualiza circuit breaker
        
        Args:
            is_win: True se trade foi lucrativo
            position_data_before_close: Dados capturados antes da posição fechar
        """
        # Atualizar status do trade no banco de dados
        if self.current_trade_id:
            try:
                # PRIORIDADE 1: Usar dados capturados ANTES do fechamento
                exit_price = None
                profit_loss = None
                
                if position_data_before_close:
                    exit_price = position_data_before_close.get('exit_price')
                    profit_loss = position_data_before_close.get('profit_loss')
                    print(f"   [DB] Usando dados capturados da posição")
                
                # PRIORIDADE 2: Buscar no histórico de deals (com delay e retry)
                if not exit_price or not profit_loss:
                    print(f"   [DB] Buscando dados no histórico MT5...")
                    from datetime import datetime, timedelta
                    import time
                    
                    # Delay para MT5 gravar histórico
                    time.sleep(3)
                    
                    # Janela maior: últimas 24 horas
                    date_from = datetime.now() - timedelta(hours=24)
                    
                    # Retry: 3 tentativas
                    for attempt in range(3):
                        deals = self.mt5.history_deals_get(date_from=date_from, date_to=datetime.now())
                        
                        if deals:
                            # Procurar deal de fechamento para este ticket
                            for deal in reversed(deals):
                                if deal.get('position_id') == self.last_position_ticket:
                                    exit_price = exit_price or deal.get('price', 0)
                                    profit_loss = profit_loss or deal.get('profit', 0)
                                    if exit_price and profit_loss:
                                        print(f"   [DB] Dados encontrados no histórico (tentativa {attempt+1})")
                                        break
                        
                        if exit_price and profit_loss:
                            break
                        
                        if attempt < 2:
                            print(f"   [DB] Tentativa {attempt+1} falhou, aguardando...")
                            time.sleep(2)
                
                # PRIORIDADE 3: Fallback - calcular manualmente
                if not exit_price or not profit_loss:
                    print(f"   [DB] FALLBACK - Calculando manualmente")
                    
                    # Usar último preço conhecido
                    if not exit_price:
                        tick = self.mt5.get_symbol_info_tick(self.symbol)
                        if tick:
                            exit_price = tick.get('bid' if self.trade_type == 'SELL' else 'ask', self.entry_price)
                        else:
                            exit_price = self.entry_price  # Estimativa
                    
                    # Calcular profit manualmente
                    if not profit_loss and exit_price and self.entry_price:
                        if self.trade_type == "SELL":
                            profit_pontos = (self.entry_price - exit_price) / self.symbol_point
                        else:
                            profit_pontos = (exit_price - self.entry_price) / self.symbol_point
                        
                        profit_loss = profit_pontos * self.point_value * self.volume
                        print(f"   [DB] Profit calculado: {profit_pontos:.0f} pts = ${profit_loss:.2f}")

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

                profit_str = f"${profit_loss:.2f}" if profit_loss else "N/A"
                print(f"   [DB] Trade {self.current_trade_id} atualizado - Status: {status}, Profit: {profit_str}")

            except Exception as e:
                print(f"   [DB] Erro ao atualizar trade: {e}")

        # NOVO: Atualizar rastreamento de momentum
        self.last_trade_was_win = is_win
        
        if is_win:
            self.consecutive_losses = 0  # Resetar contador em vitórias
            
            # NOVO: Incrementar win streak se mesma direção
            # (last_trade_type já foi setado ao abrir, então compara com anterior)
            if hasattr(self, '_previous_trade_type') and self._previous_trade_type == self.last_trade_type:
                self.consecutive_wins_same_direction += 1
                print(f"   🔥 WIN STREAK na mesma direção: {self.consecutive_wins_same_direction} ({self.last_trade_type})")
            else:
                self.consecutive_wins_same_direction = 1  # Primeiro win desta direção
            
            # Salvar tipo atual para próxima comparação
            self._previous_trade_type = self.last_trade_type
        else:
            self.consecutive_losses += 1
            self.consecutive_wins_same_direction = 0  # Resetar win streak
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
        NOVA ESTRATEGIA OTIMIZADA PARA SCALPING M5/M1:
        - PASSO 1: Analisar M5 para sinal PRINCIPAL (score >= 4.0)
        - PASSO 2: Filtros de seguranca (ATR, Spread)
        - PASSO 3: Confirmar timing em M1 (2 velas consecutivas)

        Foco em QUALIDADE, nao quantidade de trades
        """
        try:
            # PASSO 1: Analisar M5 para SINAL PRINCIPAL (tendencia)
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=50  # 50 velas para calcular indicadores
            )
            if not rates_m5 or len(rates_m5) < 50:
                return None

            m5_signal = self._analyze_m5_trend(rates_m5)
            if not m5_signal:
                return None  # Sem sinal forte em M5, aguardar

            # PASSO 2: FILTROS DE SEGURANCA
            # Filtro ATR: evitar alta volatilidade
            # IMPORTANTE: Converter ATR de pontos para "dolares de expectativa"
            # Formula: atr_pontos × point_value × volume = dolares de movimento
            atr_m5_pontos = self._calculate_atr_simple(rates_m5)
            atr_dollars = atr_m5_pontos * self.point_value * self.volume
            if atr_dollars > self.max_atr_m5_dollars:
                print(f"   [FILTRO ATR] M5 ATR muito alto (${atr_dollars:.2f} > ${self.max_atr_m5_dollars}), aguardando")
                return None

            # Filtro Spread: evitar custos altos
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if tick:
                spread_dollars = tick.get('ask', 0) - tick.get('bid', 0)
                if spread_dollars > self.max_spread_dollars:
                    print(f"   [FILTRO SPREAD] Spread muito alto (${spread_dollars:.2f} > ${self.max_spread_dollars}), aguardando")
                    return None

            # PASSO 3: Confirmar TIMING em M1 (2 velas consecutivas)
            rates_m1 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=3
            )
            if not rates_m1 or len(rates_m1) < 3:
                return None

            if not self._confirm_m1_timing(rates_m1, m5_signal):
                return None  # M1 nao confirmou, aguardar

            # TUDO OK: Retornar sinal M5 com confirmacao M1
            print(f"   [SINAL CONFIRMADO] M5 {m5_signal['type']} (score {m5_signal['score']:.1f}) + M1 timing OK")
            return m5_signal

        except Exception as e:
            print(f"Erro na analise: {e}")
            return None

    def _analyze_m5_trend(self, rates_m5) -> dict:
        """
        Analisa M5 para sinal PRINCIPAL com score minimo 4.0
        Foco em sinais FORTES e confirmados
        """
        try:
            # Preco atual
            current = rates_m5[0]['close']

            # Calcular indicadores M5
            closes = [r['close'] for r in rates_m5[:50]]
            sma20 = sum(closes[:20]) / 20
            sma50 = sum(closes[:50]) / 50
            rsi = self._calculate_simple_rsi(rates_m5, 14)

            # Tendencia M5 (ultimas 5 velas)
            uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
            downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

            # Momentum M5 (ultimas 10 velas)
            momentum_m5 = ((current - closes[9]) / closes[9]) * 100 if closes[9] > 0 else 0

            # Volume M5
            volumes = [r['tick_volume'] for r in rates_m5[:10]]
            avg_volume = sum(volumes) / len(volumes)
            volume_spike = volumes[0] > avg_volume * 1.3

            # === SINAL BUY - Score minimo 4.0 ===
            if self.use_buy:
                score = 0

                # Tendencia (1.5 pts)
                if uptrend:
                    score += 1.5

                # SMA (1.0 pt)
                if current > sma20 > sma50:
                    score += 1.0

                # RSI (1.0 pt)
                if 40 < rsi < 70:
                    score += 1.0

                # Momentum (1.5 pts)
                if momentum_m5 > 0.05:  # +0.05% nos ultimos 10 velas
                    score += 1.5

                # Volume (1.0 pt)
                if volume_spike:
                    score += 1.0

                # SCORE MINIMO: 4.0
                if score >= self.min_score_m5:
                    print(f"   [M5 BUY] Score: {score:.1f} | RSI: {rsi:.1f} | Momentum: {momentum_m5:.2f}%")
                    return {
                        "type": "BUY",
                        "price": current,
                        "reason": f"M5_uptrend_follow_score_{score:.1f}",
                        "score": score
                    }

            # === SINAL SELL - Score minimo 4.0 ===
            if self.use_sell:
                score = 0

                # Tendencia (1.5 pts)
                if downtrend:
                    score += 1.5

                # SMA (1.0 pt)
                if current < sma20 < sma50:
                    score += 1.0

                # RSI (1.0 pt)
                if 30 < rsi < 60:
                    score += 1.0

                # Momentum (1.5 pts)
                if momentum_m5 < -0.05:  # -0.05% nos ultimos 10 velas
                    score += 1.5

                # Volume (1.0 pt)
                if volume_spike:
                    score += 1.0

                # SCORE MINIMO: 4.0
                if score >= self.min_score_m5:
                    print(f"   [M5 SELL] Score: {score:.1f} | RSI: {rsi:.1f} | Momentum: {momentum_m5:.2f}%")
                    return {
                        "type": "SELL",
                        "price": current,
                        "reason": f"M5_downtrend_follow_score_{score:.1f}",
                        "score": score
                    }

            return None

        except Exception as e:
            print(f"Erro na analise M5: {e}")
            return None

    def _confirm_m1_timing(self, rates_m1, m5_signal: dict) -> bool:
        """
        Confirma timing de entrada em M1
        Exige 2 velas consecutivas na direcao M5
        """
        try:
            closes = [r['close'] for r in rates_m1[:3]]
            volumes = [r['tick_volume'] for r in rates_m1[:3]]

            # Para BUY M5: esperar 2 velas M1 subindo
            if m5_signal["type"] == "BUY":
                # Ultimas 2 velas subindo
                if closes[0] > closes[1] > closes[2]:
                    print(f"   [M1 CONFIRM] BUY confirmado (2 velas up)")
                    return True

                # OU: Volume spike + vela atual subindo
                avg_volume = sum(volumes[1:]) / 2
                if volumes[0] > avg_volume * 1.5 and closes[0] > closes[1]:
                    print(f"   [M1 CONFIRM] BUY confirmado (volume spike)")
                    return True

                print(f"   [M1 WAIT] Aguardando confirmacao BUY em M1...")
                return False

            # Para SELL M5: esperar 2 velas M1 caindo
            elif m5_signal["type"] == "SELL":
                # Ultimas 2 velas caindo
                if closes[0] < closes[1] < closes[2]:
                    print(f"   [M1 CONFIRM] SELL confirmado (2 velas down)")
                    return True

                # OU: Volume spike + vela atual caindo
                avg_volume = sum(volumes[1:]) / 2
                if volumes[0] > avg_volume * 1.5 and closes[0] < closes[1]:
                    print(f"   [M1 CONFIRM] SELL confirmado (volume spike)")
                    return True

                print(f"   [M1 WAIT] Aguardando confirmacao SELL em M1...")
                return False

            return False

        except Exception as e:
            print(f"Erro na confirmacao M1: {e}")
            return False

    def _analyze_m1_realtime(self, rates) -> dict:
        """
        Análise REALISTA de M1 com valores OTIMIZADOS para Gold.
        Foco nos últimos 5 minutos para timing rápido.
        Usa sistema de SCORE para qualidade do sinal.
        """
        try:
            # Preços das últimas 5 velas M1 (5 minutos)
            closes = [r['close'] for r in rates[:6]]
            highs = [r['high'] for r in rates[:6]]
            lows = [r['low'] for r in rates[:6]]
            volumes = [r['tick_volume'] for r in rates[:6]]

            current = closes[0]

            # Calcular ATR (14 períodos) para SL/TP dinâmico
            self.current_atr = self._calculate_atr_simple(rates[:14])

            # 1. TENDÊNCIA M1 (3 das últimas 4 velas)
            uptrend = sum(1 for i in range(3) if closes[i] > closes[i+1]) >= 2
            downtrend = sum(1 for i in range(3) if closes[i] < closes[i+1]) >= 2

            # 2. MOMENTUM M1 (mudança % nos últimos 3 min)
            momentum_1m = ((current - closes[2]) / closes[2]) * 100 if closes[2] > 0 else 0

            # 3. VOLATILIDADE
            last_range = highs[0] - lows[0]
            avg_range = sum([highs[i] - lows[i] for i in range(1, 4)]) / 3
            high_volatility = last_range > avg_range * 1.2

            # 4. VOLUME
            avg_volume = sum(volumes[1:4]) / 3
            volume_spike = volumes[0] > avg_volume * 1.5

            # LOG de análise
            import random
            if random.random() < 0.3: # Log mais frequente
                print(f"   [ANÁLISE M1] Mom: {momentum_1m:.3f}% | Vol: {high_volatility} | Volume: {volume_spike} | Trend: {'UP' if uptrend else 'DOWN' if downtrend else 'LATERAL'}")

            # === THRESHOLDS OTIMIZADOS PARA GOLD M1 ===
            MOMENTUM_BUY = 0.08   # Movimento rápido em M1
            MOMENTUM_SELL = -0.08

            # === SINAIS DE BUY - Mínimo 3 pontos ===
            if self.use_buy:
                score = 0
                if uptrend: score += 1.5
                if momentum_1m > MOMENTUM_BUY: score += 2.5
                elif momentum_1m > MOMENTUM_BUY * 0.6: score += 1.0 # Momentum médio
                if volume_spike: score += 1.0
                if high_volatility: score += 1.0

                if score >= 3:
                    return {"type": "BUY", "price": current, "reason": f"M1_BUY_Score_{score:.1f}"}

            # === SINAIS DE SELL - Mínimo 3 pontos ===
            if self.use_sell:
                score = 0
                if downtrend: score += 1.5
                if momentum_1m < MOMENTUM_SELL: score += 2.5
                elif momentum_1m < MOMENTUM_SELL * 0.6: score += 1.0
                if volume_spike: score += 1.0
                if high_volatility: score += 1.0

                if score >= 3:
                    return {"type": "SELL", "price": current, "reason": f"M1_SELL_Score_{score:.1f}"}

            return None

        except Exception as e:
            print(f"Erro na analise M1: {e}")
            return None

    def _calculate_atr_simple(self, rates) -> float:
        """
        Calcula ATR simples para SL/TP dinâmico
        GOLD: ATR otimizado para volatilidade do Gold
        Retorna ATR em PONTOS MT5, não em preço
        """
        try:
            if len(rates) < 14:
                # GOLD: ATR padrão de ~$0.40 em pontos MT5
                # $0.40 / 0.001 (symbol_point) = 400 pontos
                return 400.0  # GOLD: ATR padrão 400 pontos

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

            # GOLD: Mínimo 400 pontos (~$0.40)
            return max(atr_pontos, 400.0)

        except Exception as e:
            print(f"   Erro ao calcular ATR: {e}")
            return 400.0  # GOLD: ATR padrão 400 pontos (fallback seguro)

    # REMOVIDO: M15 validation - conflita com scalping M5/M1
    # Para operacoes rapidas, M15 pode estar em tendencia oposta
    # Foco total em M5 (tendencia) + M1 (timing)

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
            # REMOVIDO: Nao fechar posicoes opostas automaticamente
            # Deixar o trailing stop fazer seu trabalho sem interferencia

            # Obter preco atual de mercado
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                print("Erro: Nao foi possivel obter preco de mercado")
                return

            # CALCULAR ATR M5 para SL DINAMICO
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe=5,  # M5
                start_pos=0,
                count=20
            )

            if not rates_m5 or len(rates_m5) < 15:
                print("[ERRO] Sem dados M5 para calcular ATR, usando SL fixo")
                sl_dinheiro = self.fixed_sl_dollars
            else:
                # ATR em pontos de preco
                atr_price = self._calculate_atr_simple(rates_m5)

                # Calcular SL DINAMICO baseado em ATR
                # Para GOLD: ATR tipico ~$2-5, multiplicador 40 para ter SL razoavel
                # Exemplo: ATR $3 * 40 * $0.01 * 0.02 = $0.024 -> min $4
                #          ATR $10 * 40 * $0.01 * 0.02 = $0.08 -> min $4
                #          ATR $200 * 40 * $0.01 * 0.02 = $1.6 -> min $4
                # Para Gold funcionar precisamos multiplicador maior
                atr_multiplier = 150.0  # Ajustado para Gold
                sl_dollars_atr = atr_price * atr_multiplier * self.point_value * self.volume

                # LIMITES: min $4, max $10 (evita SL muito apertado ou muito largo)
                sl_dinheiro = max(4.0, min(10.0, sl_dollars_atr))

                print(f"\n[SL DINAMICO ATR]")
                print(f"  ATR M5: ${atr_price:.3f} (volatilidade)")
                print(f"  SL Calculado: ${sl_dollars_atr:.2f}")
                print(f"  SL Final: ${sl_dinheiro:.2f} (ATR * 150)")
                if sl_dinheiro != sl_dollars_atr:
                    if sl_dinheiro == 4.0:
                        print(f"  [LIMITADO MIN] ATR baixo, usando SL minimo $4")
                    else:
                        print(f"  [LIMITADO MAX] ATR alto, usando SL maximo $10")

            # Converter perda em USD para distância de preço
            pontos_para_sl = sl_dinheiro / (self.point_value * self.volume)
            sl_price_distance = pontos_para_sl * self.symbol_point

            # DEBUG: Mostrar calculos
            print(f"\n[DEBUG SL CALCULATION]")
            print(f"  SL target: ${sl_dinheiro:.2f}")
            print(f"  volume: {self.volume}")
            print(f"  point_value: ${self.point_value:.4f}")
            print(f"  pontos_para_sl: {pontos_para_sl:.1f}")
            print(f"  sl_price_distance: ${sl_price_distance:.3f}")

            if signal["type"] == "BUY":
                market_price = tick['ask']  # Preco de compra
                sl_price = market_price - sl_price_distance  # Subtrair variação de preço
                tp_price = 0  # SEM TP FIXO!
                print(f"  market_price (ASK): {market_price:.3f}")
                print(f"  sl_price: {market_price:.3f} - {sl_price_distance:.3f} = {sl_price:.3f}")
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
                print(f"  market_price (BID): {market_price:.3f}")
                print(f"  sl_price: {market_price:.3f} + {sl_price_distance:.3f} = {sl_price:.3f}")
                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,  # SEM TP!
                    comment="LossZero_Trailing"
                )

            # DEBUG: Verificar tipo do resultado
            print(f"[DEBUG ORDER RESULT] Tipo: {type(result)}, Valor: {result}")

            # Verificar se ordem foi executada (retcode 10009 = sucesso)
            if result and isinstance(result, dict):
                retcode = result.get('retcode', -1)
                order_id = result.get('order', 0)

                # Mapear códigos de erro MT5
                error_messages = {
                    10009: "TRADE_RETCODE_DONE (Sucesso)",
                    10016: "TRADE_RETCODE_INVALID_STOPS (SL/TP inválido)",
                    10030: "TRADE_RETCODE_INVALID_VOLUME (Volume inválido)",
                    10015: "TRADE_RETCODE_INVALID_PRICE (Preço inválido)",
                }

                error_msg = error_messages.get(retcode, f"Erro desconhecido ({retcode})")
                print(f"[ORDER RESULT] retcode: {retcode} - {error_msg}, order: {order_id}")

                if retcode != 10009:
                    logger.warning(f"ORDEM REJEITADA: {error_msg}")
                    logger.warning(f"  SL calculado: ${sl_dinheiro:.2f} = {self.current_sl_pontos:.0f} pts")
                    logger.warning(f"  SL preço: {sl_price:.4f}")
                    logger.warning(f"  Symbol point: {self.symbol_point}")
                    logger.warning(f"  Preço mercado: {market_price:.4f}")

            if result and isinstance(result, dict) and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                # Capturar ticket e magic number do MT5
                ticket = result.get('order', 0)
                self.last_position_ticket = ticket
                
                # Salvar para compatibilidade (última posição)
                self.entry_price = market_price
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                
                # NOVO: Rastrear posição específica
                self.positions_entry_price[ticket] = market_price
                self.positions_trailing_active[ticket] = False
                self.positions_trailing_stop[ticket] = 0.0

                # Extrair magic number do request (pode ser objeto ou dict)
                request_obj = result.get('request', None)
                if request_obj and hasattr(request_obj, 'magic'):
                    magic_number = request_obj.magic
                elif isinstance(request_obj, dict):
                    magic_number = request_obj.get('magic', 0)
                else:
                    magic_number = 0
                
                # Salvar último tipo de trade (evita alternar muito rápido)
                self.last_trade_type = signal["type"]
                
                # Calcular força do sinal
                signal_strength = self._calculate_signal_strength(signal)

                # Simplificar razão para exibição
                reason_display = signal['reason'].replace('_', ' ')

                print(f"")
                print(f"{'='*60}")
                print(f"[POSICAO ABERTA]: {signal['type']} ${market_price:.2f}")
                print(f"   Ticket: {self.last_position_ticket}")
                print(f"   Volume: {self.volume} lotes (FIXO)")
                print(f"   Motivo: {reason_display}")
                print(f"   SL: ${sl_price:.2f} (distância: ${sl_dinheiro:.2f})")
                print(f"   TP: SEM TP FIXO (lucro ilimitado!)")
                print(f"")
                print(f"   TRAILING STOP SIMPLIFICADO:")
                print(f"   Ativa com: ${self.trailing_activation_dollar:.2f} de lucro")
                print(f"   Protege inicialmente: ${self.trailing_distance_dollar:.2f}")
                print(f"   Sobe a cada: ${self.trailing_distance_dollar:.2f} adicional")
                print(f"{'='*60}")
                print(f"")

                # INICIAR WORKER DE MONITORAMENTO CONTINUO
                # Worker: Monitora posições a cada 20ms (50 checks/segundo)
                # Fallback: Loop principal a cada 1s se worker não iniciar
                try:
                    import os
                    USE_WORKER = os.getenv("GOLD_USE_WORKER", "true").lower() == "true"

                    if USE_WORKER and (not self.position_worker or not self.position_worker.is_running()):
                        try:
                            print(f"[WORKER] Iniciando monitoramento contínuo (20ms)...")
                            worker_interval = 0.02
                            self.position_worker = PositionMonitorWorker(
                                mt5_client=self.mt5,
                                symbol=self.symbol,
                                check_interval=worker_interval,
                                trailing_callback=self._trailing_worker_callback
                            )
                            self.position_worker.start()

                            # Verificar se worker iniciou corretamente
                            import time
                            time.sleep(0.1)

                            if self.position_worker.is_running():
                                print(f"[WORKER] ✓ ATIVO (20ms checks, 50/segundo)")
                            else:
                                print(f"[WORKER] ✗ Falha ao iniciar - caindo para FALLBACK (1s)")
                                self.position_worker = None
                        except Exception as worker_error:
                            print(f"[WORKER] Erro ao iniciar: {worker_error}")
                            print(f"[WORKER] Caindo para FALLBACK (1s)")
                            self.position_worker = None
                    else:
                        if USE_WORKER:
                            print(f"[WORKER] FALLBACK - Gerenciando trailing no loop principal (1s)")
                        else:
                            print(f"[WORKER] Desabilitado via GOLD_USE_WORKER=false - usando FALLBACK (1s)")

                except Exception as e:
                    print(f"[WORKER] Erro inesperado: {e}")
                    self.position_worker = None

                # Log do trade no banco de dados
                try:
                    trade_data = {
                        'ticket': ticket,
                        'magic_number': magic_number,
                        'strength': signal_strength,
                        'trade_type': signal["type"],
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': tp_price,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "2.0.0",
                        'reason': signal["reason"],
                        'status': "OPEN",
                        'comment': f"LossZero_{signal['type']}_{signal['reason']}"
                    }
                    # Log do trade e obter o trade_id
                    self.current_trade_id = self.btc_logger.log_trade(trade_data)
                    # IMPORTANTE: Linkar ticket com trade_id para trailing stops
                    self.positions_trade_id[ticket] = self.current_trade_id
                    print(f"   [DB] Trade registrado - ID: {self.current_trade_id} | Ticket: {ticket}")
                    print(f"        Magic: {magic_number} | Strength: {signal_strength}")
                except Exception as e:
                    print(f"   Erro ao logar trade: {e}")
            else:
                print(f"Erro ao abrir posicao: {result}")
                
                # FALLBACK: Tentar obter entry_price da posição já aberta no MT5
                try:
                    positions = self.mt5.positions_get(symbol=self.symbol)
                    if positions and len(positions) > 0:
                        pos = positions[-1]  # Última posição aberta
                        self.entry_price = pos.get('price_open', 0)
                        self.last_position_ticket = pos.get('ticket', 0)
                        print(f"[FALLBACK] Entry price recuperado do MT5: ${self.entry_price:.2f} (Ticket: {self.last_position_ticket})")
                except Exception as e:
                    print(f"[FALLBACK] Erro ao recuperar entry_price: {e}")

                # Log da tentativa falha
                try:
                    failed_strength = self._calculate_signal_strength(signal)
                    trade_data_failed = {
                        'ticket': None,
                        'magic_number': None,
                        'strength': failed_strength,
                        'trade_type': signal["type"],
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': tp_price,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "2.0.0",
                        'reason': signal["reason"],
                        'status': "FAILED",
                        'comment': f"Failed_{signal['type']}_{signal['reason']}"
                    }
                    self.btc_logger.log_trade(trade_data_failed)
                except Exception as e:
                    print(f"   Erro ao logar trade falha: {e}")
                
        except Exception as e:
            print(f"Erro ao abrir posicao: {e}")

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

            # CORREÇÃO: Processar TODAS as posições que temos no dicionário
            # Não apenas a última posição aberta
            if ticket not in self.positions_entry_price:
                # Posição externa, ignorar
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

            # Processar trailing para esta posição específica
            return self._update_trailing_from_worker(pos_dict, current_bid, current_ask)

        except Exception as e:
            print(f"[WORKER] Erro no callback: {e}")
            return False


    def _update_trailing_from_worker(self, pos, current_bid, current_ask):
        """
        v1.4.0 - PROTECAO PROGRESSIVA GOLD (Worker 20ms)

        MESMA LOGICA DO BTC v3.5.0:
        - $1.00 lucro -> SL em entry (break-even, protege $0)
        - $3.00 lucro -> SL protege $1.00 (sobe a cada $2)
        - $5.00 lucro -> SL protege $3.00 (sobe a cada $2)
        - Formula: protecao = lucro - $2.00

        CORRIGE BUG: Ordem atingia $7 mas protegia apenas $3.9
        SOLUCAO: Protecao progressiva simples e agressiva

        Returns:
            True se atualizou, False caso contrario
        """
        try:
            # Obter ticket da posição
            ticket = pos.get('ticket')
            if not ticket:
                return False

            # Verificar se esta posicao pertence a este agente
            entry_price = self.positions_entry_price.get(ticket, pos.get('price_open', 0))
            if entry_price <= 0:
                return False

            # Obter dados da posicao
            pos_type = pos.get('type', 0)
            current_price = current_bid if pos_type == 0 else current_ask

            # Lucro em dolares (MT5 retorna profit direto em dolares)
            profit_dollars = float(pos.get('profit', 0.0))
            current_sl = pos.get('sl', 0)

            # DEBUG: Mostrar lucro quando > $0.30
            if profit_dollars > 0.3:
                print(f"[WORKER] Gold #{ticket}: Lucro ${profit_dollars:.2f}")

            # PROTECAO PROGRESSIVA v1.4.0 (MESMA LOGICA DO BTC v3.5.0)
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
                    try:
                        result = self.mt5.modify_position(ticket=ticket, sl=new_sl, tp=None)

                        if result and result.get('retcode') == 10009:
                            print(f"")
                            print(f"[PROTECTION] Gold #{ticket}")
                            print(f"   Tipo: {protection_type}")
                            print(f"   Lucro atual: ${profit_dollars:.2f}")
                            print(f"   SL: ${current_sl:.2f} -> ${new_sl:.2f}")
                            print(f"")
                        else:
                            print(f"[PROTECTION] Falha ao mover SL: {result}")

                    except Exception as e:
                        print(f"[PROTECTION] Erro: {e}")

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
        TRAILING STOP SIMPLIFICADO - BASEADO EM DÓLARES
        - Ativa com $1 de lucro
        - Protege $0.50 inicialmente
        - Sobe $1 a cada $1 adicional de lucro
        """
        try:
            # Obter ticket da posição
            ticket = pos.get('ticket')
            if not ticket:
                print(f"   [TRAILING ERROR] Ticket inválido: {ticket}")
                return

            # Obter tipo de posição (0=BUY, 1=SELL)
            pos_type = pos.get('type', 0)

            # Obter preço atual do tick
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if tick:
                # Usar preço correto baseado no tipo de posição
                if pos_type == 0:  # BUY
                    current_price = tick.get('ask', 0)
                else:  # SELL
                    current_price = tick.get('bid', 0)

                if current_price <= 0:
                    current_price = tick.get('bid', 0) if tick.get('bid', 0) > 0 else tick.get('ask', 0)
            else:
                current_price = pos.get('price_open', 0)

            # Obter entry_price do dicionário
            entry_price = self.positions_entry_price.get(ticket, pos.get('price_open', 0))
            if entry_price <= 0:
                entry_price = pos.get('price_open', 0)
                if entry_price > 0:
                    self.positions_entry_price[ticket] = entry_price
                else:
                    return

            # USAR LUCRO DIRETO DO MT5 (mais preciso e confiável)
            mt5_profit_raw = pos.get('profit', 0.0)
            profit_dinheiro = float(mt5_profit_raw)

            # Obter estado de trailing desta posição
            trailing_active = self.positions_trailing_active.get(ticket, False)
            trailing_stop_price = self.positions_trailing_stop.get(ticket, 0.0)

            # ATIVAR TRAILING quando atingir $1 de lucro
            if not trailing_active and profit_dinheiro >= self.trailing_activation_dollar:
                # CORREÇÃO CRÍTICA: Usar o mesmo preço que o MT5 usa no _safe_modify_sl
                # Para BUY: usa ASK, para SELL: usa BID
                mt5_current_price = current_price  # Já está correto baseado no tipo de posição

                # Calcular trailing stop inicial: protege $0.50 de lucro
                # Para SELL: SL deve ficar ACIMA do preço atual para proteger lucro
                # Para BUY: SL deve ficar ABAIXO do preço atual para proteger lucro

                # Diferença de preço equivalente a $0.50 de lucro
                # $0.50 / (point_value * volume) = pontos necessários
                pontos_para_proteger = self.trailing_distance_dollar / (self.point_value * self.volume)
                trailing_price_distance = pontos_para_proteger * self.symbol_point

                print(f"   [TRAILING CALC] Protegendo ${self.trailing_distance_dollar:.2f}")
                print(f"   [TRAILING CALC] Pontos necessários: {pontos_para_proteger:.1f}")
                print(f"   [TRAILING CALC] Distância preço: {trailing_price_distance:.3f}")
                print(f"   [TRAILING CALC] Preço MT5 atual: ${mt5_current_price:.3f}")

                # Calcular trailing stop price
                # PARA BUY: SL deve ficar ABAIXO do preço atual (protege lucro)
                # PARA SELL: SL deve ficar ACIMA do preço atual (protege lucro)
                if pos_type == 0:  # BUY - SL ABAIXO do preço atual
                    trailing_stop_price = mt5_current_price - trailing_price_distance
                    print(f"   [TRAILING CALC] BUY: {mt5_current_price:.3f} - {trailing_price_distance:.3f} = {trailing_stop_price:.3f}")
                    print(f"   [TRAILING CALC] BUY SL deve ficar ABAIXO do preço atual: {mt5_current_price:.3f} > {trailing_stop_price:.3f}")
                    
                    # VALIDAÇÃO CRÍTICA: Para BUY, SL deve ser MENOR que preço atual
                    if trailing_stop_price >= mt5_current_price:
                        print(f"   [ERRO CRÍTICO] SL BUY inválido: {trailing_stop_price:.3f} >= preço atual {mt5_current_price:.3f}")
                        # Ajustar para garantir que SL < preço atual
                        trailing_stop_price = mt5_current_price - (self.symbol_point * 10)  # Mínimo 10 pontos abaixo
                        print(f"   [CORREÇÃO] SL BUY ajustado para: {trailing_stop_price:.3f}")
                        
                else:  # SELL - SL ACIMA do preço atual para proteger lucro
                    trailing_stop_price = mt5_current_price + trailing_price_distance
                    print(f"   [TRAILING CALC] SELL: {mt5_current_price:.3f} + {trailing_price_distance:.3f} = {trailing_stop_price:.3f}")
                    print(f"   [TRAILING CALC] SELL SL deve ficar ACIMA do preço atual: {trailing_stop_price:.3f} > {mt5_current_price:.3f}")
                    
                    # VALIDAÇÃO CRÍTICA: Para SELL, SL deve ser MAIOR que preço atual
                    if trailing_stop_price <= mt5_current_price:
                        print(f"   [ERRO CRÍTICO] SL SELL inválido: {trailing_stop_price:.3f} <= preço atual {mt5_current_price:.3f}")
                        # Ajustar para garantir que SL > preço atual
                        trailing_stop_price = mt5_current_price + (self.symbol_point * 10)  # Mínimo 10 pontos acima
                        print(f"   [CORREÇÃO] SL SELL ajustado para: {trailing_stop_price:.3f}")

                # Salvar no dicionário desta posição
                self.positions_trailing_active[ticket] = True
                self.positions_trailing_stop[ticket] = trailing_stop_price

                # Compatibilidade com variáveis únicas
                self.trailing_active = True
                self.trailing_stop_price = trailing_stop_price

                # Modificar SL no MT5
                success = self._safe_modify_sl(ticket, trailing_stop_price, "ATIVAR")
                if success:
                    print(f"   [TRAILING ATIVADO #{ticket}] Protege ${self.trailing_distance_dollar:.2f} de lucro!")

                    # LOG TRAILING STOP NO BANCO DE DADOS
                    try:
                        trailing_distance_dinheiro = self.trailing_distance_dollar
                        # Obter trade_id do dicionário (suporta múltiplas posições)
                        trade_id = self.positions_trade_id.get(ticket, self.current_trade_id)
                        trailing_data = {
                            'trade_id': trade_id,
                            'ticket': ticket,
                            'symbol': self.symbol,
                            'action': 'ACTIVATED',
                            'old_sl_price': None,
                            'new_sl_price': trailing_stop_price,
                            'current_price': current_price,
                            'profit_pontos': mt5_profit_raw,
                            'profit_dinheiro': profit_dinheiro,
                            'trailing_distance_pontos': (trailing_distance_dinheiro / self.point_value) / self.volume,
                            'trailing_distance_dinheiro': trailing_distance_dinheiro,
                            'reason': f'Trailing activated at ${profit_dinheiro:.2f} profit',
                            'agent_version': '1.3.0'
                        }
                        self.btc_logger.log_trailing_stop(trailing_data)
                    except Exception as db_e:
                        logger.error(f"[DB] Erro ao registrar trailing: {db_e}")

                print(f"")
                print(f"{'='*60}")
                print(f"[TRAILING ATIVADO - SIMPLIFICADO]")
                print(f"   Lucro atual: ${profit_dinheiro:.2f}")
                print(f"   Trailing ativou em: ${self.trailing_activation_dollar:.2f}")
                print(f"   Trailing Stop: ${trailing_stop_price:.2f}")
                print(f"   Protege: ${self.trailing_distance_dollar:.2f} de lucro")
                print(f"   A partir de agora: IMPOSSIVEL PERDER!")
                print(f"{'='*60}")
                print(f"")

            # ATUALIZAR TRAILING se já ativo
            if trailing_active:
                # Escalação 1:1 ratio: A cada $1 de lucro adicional, escala $1 de proteção
                # Exemplo:
                #   $1.00 lucro: protege $0.50 (base)
            #   $1.50 lucro: protege $1.00 (base)
            #   $3.00 lucro: protege $1.00 + 1.00 * 1.0 = $2.00 (1.50 additional profit / 1.50 step = 1 level * 1.00 increment)
                additional_profit = max(0, profit_dinheiro - self.trailing_activation_dollar)
                additional_levels = int(additional_profit // self.profit_step_for_increment_dollar)
                trailing_distance_dinheiro = self.trailing_distance_dollar + additional_levels * self.protection_increment_dollar

                # Garantir que não protege mais que o lucro atual (deixar margem segura)
                trailing_distance_dinheiro = min(trailing_distance_dinheiro, profit_dinheiro - 0.05)  # Deixar $0.05 de margem

                print(f"   [TRAILING CALC] Distância final: ${trailing_distance_dinheiro:.2f}")

                # Converter distância em dólares para variação de preço
                # CORREÇÃO CRÍTICA: Usar mesmo cálculo da ativação (linha 1636)
                pontos_para_proteger = trailing_distance_dinheiro / (self.point_value * self.volume)
                trailing_price_distance = pontos_para_proteger * self.symbol_point

                print(f"   [TRAILING CALC] Pontos para proteger: {pontos_para_proteger:.1f}")
                print(f"   [TRAILING CALC] Distância preço: ${trailing_price_distance:.3f}")

                # Calcular novo trailing stop
                if pos_type == 0:  # BUY
                    new_stop = current_price - trailing_price_distance
                    print(f"   [TRAILING CALC] BUY: {current_price:.3f} - {trailing_price_distance:.3f} = {new_stop:.3f}")
                    print(f"   [TRAILING CALC] Stop atual: {trailing_stop_price:.3f} | Novo: {new_stop:.3f}")

                    if new_stop > trailing_stop_price:
                        old_stop = trailing_stop_price
                        movimento = new_stop - old_stop

                        # Modificar SL no MT5 com retry logic
                        max_retries = 3
                        retry_delay = 0.5
                        success = False

                        for attempt in range(max_retries):
                            success = self._safe_modify_sl(ticket, new_stop, f"TRAILING_SUBIU_{movimento:.2f}")
                            if success:
                                break
                            if attempt < max_retries - 1:
                                print(f"   [TRAILING] Tentativa {attempt + 1}/{max_retries} falhou, aguardando {retry_delay}s...")
                                time.sleep(retry_delay)

                        if success:
                            print(f"   [TRAILING SUBIU #{ticket}]: ${old_stop:.2f} -> ${new_stop:.2f} (+${movimento:.2f}) | Protege: ${trailing_distance_dinheiro:.2f}")

                            # Atualizar dicionário
                            self.positions_trailing_stop[ticket] = new_stop
                            self.trailing_stop_price = new_stop
                        else:
                            print(f"   [ERRO CRITICO] Falha ao subir trailing após {max_retries} tentativas")
                            logger.error(f"[TRAILING ERROR] Não conseguiu modificar SL #{ticket} de ${old_stop:.2f} para ${new_stop:.2f}")
                    else:
                        print(f"   [TRAILING] Sem atualização BUY: novo SL ${new_stop:.2f} <= antigo ${trailing_stop_price:.2f}")

                else:  # SELL
                    new_stop = current_price + trailing_price_distance
                    print(f"   [TRAILING CALC] SELL: {current_price:.3f} + {trailing_price_distance:.3f} = {new_stop:.3f}")
                    print(f"   [TRAILING CALC] Stop atual: {trailing_stop_price:.3f} | Novo: {new_stop:.3f}")

                    if new_stop < trailing_stop_price:
                        old_stop = trailing_stop_price
                        movimento = old_stop - new_stop

                        # Modificar SL no MT5 com retry logic
                        max_retries = 3
                        retry_delay = 0.5
                        success = False

                        for attempt in range(max_retries):
                            success = self._safe_modify_sl(ticket, new_stop, f"TRAILING_DESCEU_{movimento:.2f}")
                            if success:
                                break
                            if attempt < max_retries - 1:
                                print(f"   [TRAILING] Tentativa {attempt + 1}/{max_retries} falhou, aguardando {retry_delay}s...")
                                time.sleep(retry_delay)

                        if success:
                            print(f"   [TRAILING DESCEU #{ticket}]: ${old_stop:.2f} -> ${new_stop:.2f} (-${movimento:.2f}) | Protege: ${trailing_distance_dinheiro:.2f}")

                            # Atualizar dicionário
                            self.positions_trailing_stop[ticket] = new_stop
                            self.trailing_stop_price = new_stop

                        else:
                            print(f"   [ERRO CRITICO] Falha ao descer trailing após {max_retries} tentativas")
                            logger.error(f"[TRAILING ERROR] Não conseguiu modificar SL #{ticket} de ${old_stop:.2f} para ${new_stop:.2f}")
                    else:
                        print(f"   [TRAILING] Sem atualização SELL: novo SL ${new_stop:.2f} >= antigo ${trailing_stop_price:.2f}")

                # Mostrar status atual
                lucro_protegido = profit_dinheiro - trailing_distance_dinheiro
                print(f"   [TRAILING ATIVO #{ticket}] Lucro: ${profit_dinheiro:.2f} | Protegido: ${lucro_protegido:.2f} | Stop: ${trailing_stop_price:.2f}")

        except Exception as e:
            print(f"Erro ao gerenciar posicao: {e}")

    def _get_trade_id_for_logging(self, ticket: int) -> int:
        """
        Obtém o trade_id para logging, buscando no banco se necessário.
        """
        # Prioridade 1: Usar o ID em memória se disponível
        if self.current_trade_id and self.last_position_ticket == ticket:
            return self.current_trade_id

        # Prioridade 2: Buscar no banco de dados pelo ticket
        try:
            from core.btc_logger import BTCLogger
            btc_logger = BTCLogger()
            trade_id = btc_logger.get_trade_id_by_ticket(ticket)

            if trade_id:
                # Atualiza o ID em memória para otimizar futuras chamadas
                self.current_trade_id = trade_id
                self.last_position_ticket = ticket
                print(f"   [DB] Trade ID {trade_id} recuperado para o ticket {ticket}")
                return trade_id
            else:
                print(f"   [DB] AVISO: Trade ID não encontrado no banco para o ticket {ticket}.")
                return None

        except Exception as e:
            print(f"   [DB] ERRO ao buscar trade_id pelo ticket {ticket}: {e}")
            return None

    def _safe_modify_sl(self, ticket: int, new_sl: float, action: str) -> bool:
        """
        Modifica Stop Loss de forma segura com logs detalhados e retry
        CORRIGIDO: Executa realmente no MT5
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
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                print(f"   [ERRO] Posição não encontrada - Ticket: {ticket}")
                return False
            
            position = positions[0]  # Pegar primeira posição
            
            # Usar lock para evitar conflitos entre threads
            with self._trailing_lock:
                # Obter preço atual para calcular distância
                tick = self.mt5.get_symbol_info_tick(self.symbol)
                if not tick:
                    print(f"   [ERRO] Não foi possível obter preço atual")
                    return False
                
                current_price = tick['bid'] if position['type'] == 0 else tick['ask']
                
                # Calcular distância do preço atual
                if position['type'] == 0:  # BUY
                    distance_pct = ((current_price - new_sl) / current_price) * 100
                    direction = "acima"
                else:  # SELL
                    distance_pct = ((new_sl - current_price) / current_price) * 100
                    direction = "abaixo"
                
                # Log da tentativa
                print(f"   [MT5] Tentando {action} SL - Ticket: {ticket}")
                print(f"   [MT5] Preço atual: ${current_price:.2f}")
                print(f"   [MT5] Novo SL: ${new_sl:.2f} ({distance_pct:.4f}% {direction})")
                print(f"   [MT5] Posição atual SL: ${position.get('sl', 'N/A')}")
                
                # CORREÇÃO: Pular verificação de distância pequena APENAS se NÃO for a ativação inicial.
                # A ativação inicial DEVE sempre ser executada.
                if action != "ATIVAR":
                    # Verificar se distância é muito pequena (evitar modificações desnecessárias)
                    if abs(new_sl - position.get('sl', 0)) < self.symbol_point:
                        print(f"   [INFO] Modificação de SL muito pequena, pulando.")
                        return False

                # MÚLTIPLAS TENTATIVAS com diferentes abordagens
                for attempt in range(3):
                    try:
                        print(f"   [MT5] Tentativa {attempt + 1}/3...")
                        
                        # MÉTODO 1: Modificação direta (mais comum)
                        result = self.mt5.order_send({
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": self.symbol,
                            "position": ticket,
                            "sl": new_sl,
                            "tp": position.get('tp', 0),  # Manter TP atual
                        })
                        
                        # Verificar resultado da tentativa
                        if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                            print(f"   [MT5] ✅ SUCESSO! SL modificado para ${new_sl:.2f}")
                            print(f"   [MT5] Ticket: {ticket} | Ação: {action}")
                            
                            # Atualizar timestamp da última modificação
                            self._last_sl_modification = time.time()
                            return True
                        else:
                            # Log do erro detalhado
                            error_code = result.get('retcode', 'Unknown') if result else 'No result'
                            error_desc = result.get('comment', 'No description') if result else 'No result'
                            
                            print(f"   [MT5] ❌ Tentativa {attempt + 1} falhou")
                            print(f"   [MT5] Erro: {error_code} - {error_desc}")
                            
                            # Se falhou por distância, tentar abordagem diferente
                            if error_code == 130:  # Invalid stops
                                print(f"   [MT5] Problema de distância, ajustando...")
                                # Manter distância mínima
                                if position['type'] == 0:  # BUY
                                    new_sl = current_price - 0.1  # Mínimo 0.1
                                else:  # SELL  
                                    new_sl = current_price + 0.1  # Mínimo 0.1
                                print(f"   [MT5] Novo SL ajustado para: ${new_sl:.2f}")
                    
                    except Exception as inner_e:
                        print(f"   [MT5] Exceção na tentativa {attempt + 1}: {inner_e}")
                    
                    # Aguardar antes da próxima tentativa (exceto na última)
                    if attempt < 2:
                        print(f"   [MT5] Aguardando 0.5s antes da próxima tentativa...")
                        time.sleep(0.5)
                
                # TODAS AS TENTATIVAS FALHARAM
                print(f"   [MT5] ❌ TODAS AS TENTATIVAS FALHARAM")
                print(f"   [MT5] Ticket: {ticket} | Novo SL: ${new_sl:.2f}")
                print(f"   [MT5] Ação: {action}")
                
                # TENTATIVA FINAL: Diretamente através do MT5 se disponível
                try:
                    print(f"   [MT5] Tentativa FINAL usando order_send...")

                    # Construir request manualmente (sem type_filling para SLTP)
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": self.symbol,
                        "position": ticket,
                        "sl": new_sl,
                        "tp": position.get('tp', 0),
                    }

                    result_final = self.mt5.order_send(request)
                    
                    if result_final and result_final.get('retcode') == 10009:
                        print(f"   [MT5] ✅ SUCESSO NA TENTATIVA FINAL!")
                        self._last_sl_modification = time.time()
                        return True
                    else:
                        error_final = result_final.get('comment', 'Unknown') if result_final else 'No result'
                        print(f"   [MT5] ❌ Tentativa final também falhou: {error_final}")
                        
                except Exception as final_e:
                    print(f"   [MT5] ❌ Erro na tentativa final: {final_e}")
                
                return False
                        
        except Exception as e:
            print(f"   [MT5] ❌ Exceção geral ao modificar SL: {e}")
            return False

    def _get_time(self):
        """
        Retorna hora atual
        """
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _calculate_signal_strength(self, signal: dict) -> str:
        """
        Calcula força do sinal baseado em confirmações
        
        Args:
            signal: Dicionário com informações do sinal
            
        Returns:
            "STRONG" | "MODERATE" | "WEAK"
        """
        confirmations = 0
        reason = signal.get('reason', '').lower()
        
        # Contar confirmações no reason
        if 'downtrend' in reason or 'uptrend' in reason:
            confirmations += 1
        
        if 'momentum' in reason:
            confirmations += 1
        
        if 'volume' in reason or 'volatility' in reason:
            confirmations += 1
        
        if 'm15_confirm' in reason or 'confirmed' in reason:
            confirmations += 1
        
        # Classificar força
        if confirmations >= 3:
            return "STRONG"
        elif confirmations >= 2:
            return "MODERATE"
        else:
            return "WEAK"
