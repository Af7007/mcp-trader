#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOLD Loss Zero GAME - Sistema de Predição M1 com Trailing Agressivo

CONCEITO:
- Timeframe: M1 (1 minuto)
- Foco: PREDIÇÃO do próximo candle (não indicadores)
- Trailing: Agressivo a cada $0.10 após positivação
- Múltiplas ordens: Permitido quando todas estão com trailing positivo
- SL inicial: $2 fixo
- Volume: 0.02 lotes
- Worker: MUITO ATIVO (1-2 segundos)

ESTRATÉGIA:
1. Sistema de predição indica direção (BUY/SELL)
2. Abre com SL de $2
3. Assim que positiva (qualquer valor > $0), ativa trailing
4. Trailing sobe a cada $0.10 de lucro
5. Pode abrir nova ordem se TODAS as anteriores têm trailing positivo
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client

logger = logging.getLogger(__name__)


class GoldLossZeroGame:
    """
    Sistema Gold Loss Zero Game - Predição M1 + Trailing Agressivo + Múltiplas Posições
    """

    def __init__(
        self,
        symbol: str = "XAUUSDc",
        volume: float = 0.02,
        sl_initial_dollars: float = 5.0,  # SL fixo em dólares (AUMENTADO de $2 para $5)
        trailing_step_dollars: float = 0.20,  # Sobe trailing a cada $0.20 (AUMENTADO de $0.10)
        worker_interval: float = 0.5,  # Worker check a cada 0.5 segundo (ACELERADO de 1s)
        max_positions: int = 1,  # Máximo de posições simultâneas (REDUZIDO de 3 para 1)
        magic_number: int = None,  # Magic number único para identificar este agente
    ):
        """
        Inicializa Gold Loss Zero Game

        Args:
            symbol: Símbolo (XAUUSDc para Gold)
            volume: Volume fixo (0.02 lotes)
            sl_initial_dollars: SL inicial em dólares ($2)
            trailing_step_dollars: Step do trailing ($0.10)
            worker_interval: Intervalo do worker em segundos (1-2s)
            max_positions: Máximo de posições simultâneas
            magic_number: Identificador único deste agente (padrão: baseado em timestamp)
        """
        self.symbol = symbol
        self.volume = volume
        self.sl_initial_dollars = sl_initial_dollars
        self.trailing_step_dollars = trailing_step_dollars
        self.worker_interval = worker_interval
        self.max_positions = max_positions

        # Magic number único para este agente
        # Se não fornecido, gera baseado em timestamp
        import time
        if magic_number is None:
            # Gera magic number único baseado em timestamp (últimos 6 dígitos)
            self.magic_number = int(time.time() * 1000) % 1000000
        else:
            self.magic_number = magic_number

        # GOLD Contract Specs
        # 1 lote = 100 oz
        # 0.02 lotes = 2 oz
        # Se preço move $1.00 → Lucro = $1.00 × 2 oz = $2.00
        self.contract_size = 100  # oz por lote
        self.point_value = self.contract_size * self.volume  # Valor em $ por $1 de movimento

        # MT5 Connection
        self.mt5 = get_mt5_client()

        # Rastreamento de posições
        self.active_positions: Dict[int, Dict] = {}  # ticket -> position_data

        # Estatísticas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0

        # Cooldown para evitar múltiplas aberturas
        self.last_open_time = 0
        self.open_cooldown = 5.0  # 5 segundos entre aberturas

        print(f"\n{'='*60}")
        print(f"GOLD LOSS ZERO GAME - Sistema de Predição M1")
        print(f"{'='*60}")
        print(f"Symbol: {self.symbol}")
        print(f"Volume: {self.volume} lotes")
        print(f"Magic Number: {self.magic_number} (ID único deste agente)")
        print(f"Contract Size: {self.contract_size} oz/lote")
        print(f"Point Value: ${self.point_value:.2f} por $1 de movimento")
        print(f"SL Inicial: ${self.sl_initial_dollars:.2f}")
        print(f"Trailing Step: ${self.trailing_step_dollars:.2f}")
        print(f"Worker Interval: {self.worker_interval}s (MUITO ATIVO)")
        print(f"Max Posições Simultâneas: {self.max_positions}")
        print(f"\nESTRATÉGIA:")
        print(f"1. Predição do próximo candle M1")
        print(f"2. SL fixo de ${self.sl_initial_dollars}")
        print(f"3. Trailing ativa quando positiva")
        print(f"4. Trailing sobe a cada ${self.trailing_step_dollars}")
        print(f"5. Nova ordem só se todas têm trailing positivo")
        print(f"{'='*60}\n")

    def run(self):
        """
        Loop principal do agente
        """
        print(f"[{self._get_time()}] INICIANDO Gold Loss Zero Game...")
        print(f"Worker ativo a cada {self.worker_interval}s")
        print(f"Max posições: {self.max_positions}")
        print(f"Cooldown abertura: {self.open_cooldown}s")
        print(f"Trailing threshold: $0.10")
        print(f"Trailing distance: $0.10 (preço)\n")

        try:
            cycle = 0
            while True:
                cycle += 1

                # Mostrar que está rodando
                if cycle % 2 == 0:  # A cada 1 segundo
                    print(f".", end="", flush=True)

                self._display_status(cycle)

                # Atualizar posições existentes (worker inline)
                if self.active_positions:
                    print(f"\n[WORKER EXECUTANDO] {len(self.active_positions)} posição(ões) para atualizar")
                    self._update_all_positions()
                else:
                    if cycle % 10 == 0:
                        print(f"\n[IDLE] Sem posições abertas")

                # Verificar se pode abrir nova posição
                self._check_and_open_position()

                # Sleep do worker (muito ativo!)
                time.sleep(self.worker_interval)

        except KeyboardInterrupt:
            print(f"\n[{self._get_time()}] Agente parado pelo usuário")
            self._show_final_stats()

    def _display_status(self, cycle: int):
        """
        Exibe status resumido
        """
        positions_count = len(self.active_positions)

        # Se tem posições, mostrar a cada 5 ciclos, senão a cada 10
        show_interval = 5 if positions_count > 0 else 10

        if cycle % show_interval == 0:
            print(f"\n[{self._get_time()}] Ciclo #{cycle} | Posições: {positions_count}/{self.max_positions} | P&L: ${self.total_profit:.2f}")

            if self.active_positions:
                for ticket, data in self.active_positions.items():
                    profit = data.get('current_profit', 0)
                    trailing_active = data.get('trailing_active', False)
                    sl_price = data.get('sl_price', 0)
                    status_icon = 'OK' if trailing_active else '...'
                    sl_info = f"SL: ${sl_price:.2f}" if trailing_active else ""
                    print(f"  Ticket {ticket}: [{status_icon}] Lucro: ${profit:.2f} {sl_info}")

    def _update_all_positions(self):
        """
        Atualiza trailing de TODAS as posições abertas (worker inline)
        """
        if not self.active_positions:
            return

        print(f"\n>>> UPDATE_ALL_POSITIONS CHAMADO <<<")
        print(f">>> Posições rastreadas: {list(self.active_positions.keys())}")

        try:
            # Obter apenas as posições DESTE agente (filtradas por magic number)
            mt5_positions = self.mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
            print(f">>> Posições no MT5 (magic {self.magic_number}): {len(mt5_positions) if mt5_positions else 0}")

            if not mt5_positions:
                # Todas as posições foram fechadas
                print(f">>> TODAS FECHADAS - chamando handle_closed_positions")
                self._handle_closed_positions()
                return

            # Criar dict de tickets MT5
            mt5_tickets = {pos['ticket']: pos for pos in mt5_positions}
            print(f">>> Tickets MT5: {list(mt5_tickets.keys())}")

            # Atualizar cada posição rastreada
            tickets_to_remove = []
            for ticket, data in list(self.active_positions.items()):
                if ticket not in mt5_tickets:
                    # Posição foi fechada
                    tickets_to_remove.append(ticket)
                    self._handle_position_closed(ticket, data)
                else:
                    # Atualizar trailing
                    mt5_pos = mt5_tickets[ticket]
                    self._update_position_trailing(ticket, data, mt5_pos)

            # Remover posições fechadas
            for ticket in tickets_to_remove:
                del self.active_positions[ticket]

        except Exception as e:
            print(f"[ERRO] Falha ao atualizar posições: {e}")

    def _update_position_trailing(self, ticket: int, data: Dict, mt5_pos: Dict):
        """
        Atualiza trailing de uma posição específica
        """
        try:
            # Obter dados
            pos_type = mt5_pos['type']  # 0=BUY, 1=SELL
            entry_price = data['entry_price']
            current_sl = mt5_pos['sl']

            # Obter preço atual
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                return

            current_price = tick['bid'] if pos_type == 0 else tick['ask']

            # Calcular lucro em dólares (CORRIGIDO!)
            # Para Gold: 1 lote = 100 oz, 0.02 lotes = 2 oz
            # Se preço move $1.00 → Lucro = $1.00 × point_value
            if pos_type == 0:  # BUY
                price_movement = current_price - entry_price
            else:  # SELL
                price_movement = entry_price - current_price

            profit_dollars = price_movement * self.point_value
            data['current_profit'] = profit_dollars

            # DEBUG: SEMPRE mostrar quando tem posição aberta
            print(f"\n[WORKER] Ticket {ticket} @ {self._get_time()}:")
            print(f"  Entry: ${entry_price:.2f} | Current: ${current_price:.2f}")
            print(f"  Movement: ${price_movement:.2f} (price change)")
            print(f"  Point Value: ${self.point_value:.2f}")
            print(f"  Profit Calculado: ${profit_dollars:.2f}")
            print(f"  Trailing Active: {data['trailing_active']}")
            print(f"  Current SL: ${current_sl:.2f}")

            # Status
            if profit_dollars >= 0.10 and not data['trailing_active']:
                print(f"  >>> LUCRO >= $0.10! Vai ativar trailing...")
            elif data['trailing_active']:
                print(f"  >>> TRAILING ATIVO")

            # === TRAILING STOP SIMPLIFICADO ===
            # REGRA: SL fica $0.10 atrás do preço atual

            # Ativa quando lucro >= $0.10
            if profit_dollars >= 0.10:
                # Calcular novo SL ($0.10 atrás do preço)
                trailing_distance = 0.10  # $0.10 em movimento de preço

                if pos_type == 0:  # BUY
                    new_sl = current_price - trailing_distance
                else:  # SELL
                    new_sl = current_price + trailing_distance

                # Calcular proteção
                if pos_type == 0:
                    protected = (new_sl - entry_price) * self.point_value
                else:
                    protected = (entry_price - new_sl) * self.point_value

                # Decidir se atualiza
                should_update = False
                action = ""

                if not data['trailing_active']:
                    should_update = True
                    action = "ATIVANDO"
                else:
                    # Só sobe, nunca desce
                    if pos_type == 0 and new_sl > data['sl_price']:
                        should_update = True
                        action = "SUBINDO"
                    elif pos_type == 1 and new_sl < data['sl_price']:
                        should_update = True
                        action = "DESCENDO"

                if should_update:
                    print(f"\n{'='*70}")
                    print(f"[{action} TRAILING] Ticket {ticket} @ {self._get_time()}")
                    print(f"{'='*70}")
                    print(f"  Lucro: ${profit_dollars:.2f}")
                    print(f"  Current: ${current_price:.2f}")
                    print(f"  Novo SL: ${new_sl:.2f} (${trailing_distance:.2f} atrás)")
                    print(f"  Proteção: ${protected:.2f}")
                    print(f"  Executando modify_position...")

                    try:
                        result = self.mt5.modify_position(ticket=ticket, sl=new_sl, tp=0)
                        print(f"  Retcode: {result.get('retcode') if result else 'None'}")

                        if result and result.get('retcode') == 10009:
                            data['trailing_active'] = True
                            data['sl_price'] = new_sl
                            print(f"  ✓✓✓ SUCESSO! SL = ${new_sl:.2f}, Protege ${protected:.2f}")
                        else:
                            print(f"  XXX FALHOU! Result: {result}")
                        print(f"{'='*70}\n")
                    except Exception as e:
                        print(f"  XXX EXCEÇÃO: {e}\n")
                        import traceback
                        traceback.print_exc()

        except Exception as e:
            print(f"[ERRO] Erro ao processar trailing {ticket}: {e}")

    def _handle_position_closed(self, ticket: int, data: Dict):
        """
        Trata fechamento de posição
        """
        profit = data.get('current_profit', 0)
        self.total_trades += 1
        self.total_profit += profit

        if profit > 0:
            self.winning_trades += 1
            print(f"\n[{self._get_time()}] ✅ POSIÇÃO FECHADA COM LUCRO - Ticket {ticket}")
        else:
            self.losing_trades += 1
            print(f"\n[{self._get_time()}] ❌ POSIÇÃO FECHADA COM PERDA - Ticket {ticket}")

        print(f"  Resultado: ${profit:.2f}")
        print(f"  Total P&L: ${self.total_profit:.2f}\n")

    def _handle_closed_positions(self):
        """
        Todas as posições foram fechadas
        """
        for ticket in list(self.active_positions.keys()):
            data = self.active_positions[ticket]
            self._handle_position_closed(ticket, data)

        self.active_positions.clear()

    def _check_and_open_position(self):
        """
        Verifica se pode abrir nova posição
        """
        # VERIFICAÇÃO 1: Posições no rastreamento
        if len(self.active_positions) >= self.max_positions:
            return

        # VERIFICAÇÃO 2: Posições REAIS no MT5 (dupla checagem) - filtra por magic
        try:
            mt5_positions = self.mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
            if mt5_positions and len(mt5_positions) >= self.max_positions:
                print(f"  [BLOQUEIO] Já tem {len(mt5_positions)} posição(ões) deste agente (magic {self.magic_number})")
                return
        except Exception as e:
            print(f"  [ERRO] Falha ao verificar posições MT5: {e}")
            return

        # VERIFICAÇÃO 3: Cooldown entre aberturas
        current_time = time.time()
        time_since_last_open = current_time - self.last_open_time
        if self.last_open_time > 0 and time_since_last_open < self.open_cooldown:
            remaining = self.open_cooldown - time_since_last_open
            if int(remaining) == int(self.open_cooldown - 1):  # Mostrar 1x
                print(f"  [COOLDOWN] Aguardando {remaining:.1f}s antes de nova abertura")
            return

        # VERIFICAÇÃO 4: Só abre se TODAS as posições têm trailing positivo
        if self.active_positions:
            all_have_positive_trailing = all(
                data['trailing_active'] for data in self.active_positions.values()
            )
            if not all_have_positive_trailing:
                print(f"  [BLOQUEIO] Aguardando trailing positivo na(s) posição(ões) existente(s)")
                return

        # Obter predição
        signal = self._predict_next_candle()
        if signal:
            self._open_position(signal)

    def _predict_next_candle(self) -> Dict:
        """
        Sistema de PREDIÇÃO AVANÇADO - 20 Candles M1 + Score de Qualidade

        Análise profunda baseada em:
        - Últimos 20 candles M1 (padrão real)
        - Médias móveis (SMA 5, 10, 20)
        - Força da tendência (consistência)
        - Aceleração/desaceleração
        - Confirmação M5 obrigatória
        - Score de qualidade (mínimo 70/100)

        Returns:
            {"type": "BUY"/"SELL", "confidence": 0-100, "score": 0-100} ou None
        """
        try:
            # === PASSO 1: CONFIRMAR TENDÊNCIA M5 (OBRIGATÓRIO) ===
            rates_m5 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M5",
                start_pos=0,
                count=10
            )

            if len(rates_m5) < 10:
                return None

            # M5: Precisa de tendência FORTE (4 de 5 candles)
            closes_m5 = [r['close'] for r in rates_m5[:6]]
            m5_ups = sum([1 for i in range(5) if closes_m5[i] > closes_m5[i+1]])
            m5_downs = sum([1 for i in range(5) if closes_m5[i] < closes_m5[i+1]])

            m5_uptrend = m5_ups >= 4  # RIGOROSO: 4 de 5
            m5_downtrend = m5_downs >= 4

            # M5 DEVE ter tendência clara
            if not m5_uptrend and not m5_downtrend:
                return None

            # === PASSO 2: ANÁLISE PROFUNDA DOS ÚLTIMOS 20 CANDLES M1 ===
            rates_m1 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=25  # Pegar 25 para calcular médias
            )

            if len(rates_m1) < 25:
                return None

            # Extrair dados
            closes = [r['close'] for r in rates_m1[:21]]  # 0-20
            highs = [r['high'] for r in rates_m1[:21]]
            lows = [r['low'] for r in rates_m1[:21]]
            volumes = [r['tick_volume'] for r in rates_m1[:21]]

            current = closes[0]

            # === ANÁLISE 1: MÉDIAS MÓVEIS ===
            sma_5 = sum(closes[:5]) / 5
            sma_10 = sum(closes[:10]) / 10
            sma_20 = sum(closes[:20]) / 20

            # === ANÁLISE 2: FORÇA DA TENDÊNCIA (últimos 20 candles) ===
            ups_20 = sum([1 for i in range(20) if closes[i] > closes[i+1]])
            downs_20 = sum([1 for i in range(20) if closes[i] < closes[i+1]])

            # === ANÁLISE 3: TENDÊNCIA RECENTE (últimos 10 candles) ===
            ups_10 = sum([1 for i in range(10) if closes[i] > closes[i+1]])
            downs_10 = sum([1 for i in range(10) if closes[i] < closes[i+1]])

            # === ANÁLISE 4: TENDÊNCIA IMEDIATA (últimos 5 candles) ===
            ups_5 = sum([1 for i in range(5) if closes[i] > closes[i+1]])
            downs_5 = sum([1 for i in range(5) if closes[i] < closes[i+1]])

            # === ANÁLISE 5: MOMENTUM GRADUAL ===
            # Verificar se está acelerando ou desacelerando
            momentum_recent = ((closes[0] - closes[5]) / closes[5]) * 100  # Últimos 5
            momentum_medium = ((closes[0] - closes[10]) / closes[10]) * 100  # Últimos 10
            momentum_long = ((closes[0] - closes[20]) / closes[20]) * 100  # Últimos 20

            # === ANÁLISE 6: VOLATILIDADE CONTROLADA ===
            avg_range = sum([highs[i] - lows[i] for i in range(10)]) / 10
            current_range = highs[0] - lows[0]

            # Evitar volatilidade extrema
            if current_range > avg_range * 2.5:
                return None

            # === ANÁLISE 7: VOLUME ===
            avg_volume = sum(volumes[:10]) / 10
            volume_ratio = volumes[0] / avg_volume if avg_volume > 0 else 1

            # === SISTEMA DE SCORE PARA BUY ===
            if m5_uptrend:
                score = 0

                # 1. Consistência de 20 candles (0-25 pontos)
                if ups_20 >= 15:  # 15 de 20 subindo
                    score += 25
                elif ups_20 >= 12:  # 12 de 20 subindo
                    score += 15

                # 2. Tendência recente forte (0-20 pontos)
                if ups_10 >= 7:  # 7 de 10
                    score += 20
                elif ups_10 >= 6:
                    score += 10

                # 3. Tendência imediata (0-20 pontos)
                if ups_5 >= 4:  # 4 de 5
                    score += 20
                elif ups_5 >= 3:
                    score += 10

                # 4. Preço acima das médias (0-15 pontos)
                if current > sma_5 > sma_10 > sma_20:  # Alinhamento perfeito
                    score += 15
                elif current > sma_5 and current > sma_10:
                    score += 10
                elif current > sma_5:
                    score += 5

                # 5. Momentum positivo e acelerando (0-10 pontos)
                if momentum_recent > 0.01 and momentum_recent > momentum_medium:
                    score += 10  # Acelerando
                elif momentum_recent > 0.01:
                    score += 5  # Positivo

                # 6. Volume confirmando (0-10 pontos)
                if volume_ratio > 1.2:  # Volume 20% acima da média
                    score += 10
                elif volume_ratio > 1.0:
                    score += 5

                # DECISÃO: Score mínimo 70
                if score >= 70:
                    confidence = min(abs(momentum_recent) * 1000, 100)
                    return {
                        "type": "BUY",
                        "confidence": confidence,
                        "score": score,
                        "reason": f"Score:{score} Up20:{ups_20}/20 Up10:{ups_10}/10"
                    }

            # === SISTEMA DE SCORE PARA SELL ===
            elif m5_downtrend:
                score = 0

                # 1. Consistência de 20 candles (0-25 pontos)
                if downs_20 >= 15:  # 15 de 20 caindo
                    score += 25
                elif downs_20 >= 12:
                    score += 15

                # 2. Tendência recente forte (0-20 pontos)
                if downs_10 >= 7:  # 7 de 10
                    score += 20
                elif downs_10 >= 6:
                    score += 10

                # 3. Tendência imediata (0-20 pontos)
                if downs_5 >= 4:  # 4 de 5
                    score += 20
                elif downs_5 >= 3:
                    score += 10

                # 4. Preço abaixo das médias (0-15 pontos)
                if current < sma_5 < sma_10 < sma_20:  # Alinhamento perfeito
                    score += 15
                elif current < sma_5 and current < sma_10:
                    score += 10
                elif current < sma_5:
                    score += 5

                # 5. Momentum negativo e acelerando (0-10 pontos)
                if momentum_recent < -0.01 and momentum_recent < momentum_medium:
                    score += 10  # Acelerando para baixo
                elif momentum_recent < -0.01:
                    score += 5  # Negativo

                # 6. Volume confirmando (0-10 pontos)
                if volume_ratio > 1.2:
                    score += 10
                elif volume_ratio > 1.0:
                    score += 5

                # DECISÃO: Score mínimo 70
                if score >= 70:
                    confidence = min(abs(momentum_recent) * 1000, 100)
                    return {
                        "type": "SELL",
                        "confidence": confidence,
                        "score": score,
                        "reason": f"Score:{score} Down20:{downs_20}/20 Down10:{downs_10}/10"
                    }

            return None

        except Exception as e:
            print(f"[ERRO] Falha na predição: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _open_position(self, signal: Dict):
        """
        Abre nova posição
        """
        try:
            # Obter preço
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                print("[ERRO] Não foi possível obter preço de mercado")
                return

            signal_type = signal['type']
            confidence = signal.get('confidence', 0)

            # Calcular SL em movimento de preço (CORRIGIDO!)
            # Para Gold: Se quero perder $2.00 com 0.02 lotes (point_value = 2)
            # Preciso de: $2.00 / 2 = $1.00 de movimento
            sl_price_movement = self.sl_initial_dollars / self.point_value

            if signal_type == "BUY":
                entry_price = tick['ask']
                sl_price = entry_price - sl_price_movement

                result = self.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment=f"GoldGame_{self.magic_number}",
                    magic=self.magic_number
                )
            else:  # SELL
                entry_price = tick['bid']
                sl_price = entry_price + sl_price_movement

                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment=f"GoldGame_{self.magic_number}",
                    magic=self.magic_number
                )

            if result and result.get('retcode') == 10009:
                ticket = result.get('order', 0)

                # Registrar tempo de abertura
                self.last_open_time = time.time()

                # Adicionar ao rastreamento
                self.active_positions[ticket] = {
                    'ticket': ticket,
                    'type': signal_type,
                    'entry_price': entry_price,
                    'sl_price': sl_price,  # SL inicial
                    'volume': self.volume,
                    'open_time': datetime.now(),
                    'trailing_active': False,
                    'current_profit': 0
                }

                # Extrair score e reason
                score = signal.get('score', 0)
                reason = signal.get('reason', 'N/A')

                print(f"\n{'='*70}")
                print(f"[{self._get_time()}] NOVA POSIÇÃO ABERTA")
                print(f"{'='*70}")
                print(f"Ticket: {ticket}")
                print(f"Tipo: {signal_type}")
                print(f"Preço Entrada: ${entry_price:.2f}")
                print(f"Volume: {self.volume} lotes")
                print(f"SL Preço: ${sl_price:.2f} (Perda Máx: ${self.sl_initial_dollars:.2f})")
                print(f"\nQUALIDADE DO SINAL:")
                print(f"  Score: {score}/100 ★★★")
                print(f"  Confiança: {confidence:.1f}%")
                print(f"  Detalhes: {reason}")
                print(f"\nTRAILING:")
                print(f"  Ativa: Lucro >= $0.10")
                print(f"  Distância: $0.10 atrás do preço")
                print(f"\nPosições: {len(self.active_positions)}/{self.max_positions}")
                print(f"{'='*70}\n")

            else:
                print(f"[ERRO] Falha ao abrir posição: {result}")

        except Exception as e:
            print(f"[ERRO] Erro ao abrir posição: {e}")

    def _show_final_stats(self):
        """
        Mostra estatísticas finais
        """
        print(f"\n{'='*60}")
        print(f"ESTATÍSTICAS FINAIS - Gold Loss Zero Game")
        print(f"{'='*60}")
        print(f"Total de Trades: {self.total_trades}")
        print(f"Vitórias: {self.winning_trades}")
        print(f"Perdas: {self.losing_trades}")
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${self.total_profit:.2f}")
        print(f"{'='*60}\n")

    def _get_time(self):
        """
        Retorna hora atual
        """
        return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    # CONFIGURAÇÃO OTIMIZADA PARA M1
    agent = GoldLossZeroGame(
        symbol="XAUUSDc",
        volume=0.02,
        sl_initial_dollars=5.0,        # $5 SL (volatilidade M1)
        trailing_step_dollars=0.20,    # $0.20 step (mais robusto)
        worker_interval=0.5,           # 0.5s worker (captura rápida)
        max_positions=1                # 1 posição (evita catástrofe)
    )
    agent.run()
