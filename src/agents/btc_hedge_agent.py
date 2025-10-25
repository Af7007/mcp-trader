#!/usr/bin/env python3
"""
Agente de Trading BTCUSD com Estratégia de Hedge
- Operações consecutivas em tendência lucrativa
- Hedge automático em reversão
- SL dinâmico baseado em ATR
- Limite de 20 operações por dia
"""

import logging
import time
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client
from core.database import setup_database, get_db_connection
from core.telegram_notifier import get_telegram_notifier

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Estados do agente"""
    ANALYZING = "analyzing"
    TRADING = "trading"
    HEDGING = "hedging"
    PAUSED = "paused"
    STOPPED = "stopped"


class BTCHedgeAgent:
    """
    Agente de Trading para BTCUSD com estratégia de hedge.

    Características:
    - Lote fixo: 0.02
    - TP: ~$2 por operação
    - SL dinâmico baseado em ATR
    - Operações consecutivas em tendência
    - Hedge em reversão
    - Limite: 20 operações/dia
    """

    def __init__(
        self,
        symbol: str = "BTCUSDm",
        volume: float = 0.02,
        target_profit: float = 2.0,
        max_daily_trades: int = 20,
        check_interval: int = 30
    ):
        """
        Inicializa o agente.

        Args:
            symbol: Símbolo para negociar
            volume: Volume em lotes
            target_profit: Lucro alvo por operação ($)
            max_daily_trades: Máximo de operações por dia
            check_interval: Intervalo de verificação (segundos)
        """
        self.symbol = symbol
        self.volume = volume
        self.target_profit = target_profit
        self.max_daily_trades = max_daily_trades
        self.check_interval = check_interval

        self.mt5 = get_mt5_client()
        self.state = AgentState.ANALYZING
        self.telegram = get_telegram_notifier()

        # Contadores
        self.daily_trades = 0
        self.total_profit = 0.0
        self.winning_streak = 0
        self.last_trade_time = None
        self.trades_today = []
        self.open_tickets = set()  # Rastreia tickets de posições abertas
        self.cycle_count = 0  # Para controlar resumos periódicos
        self.startup_notified = False  # Flag para enviar notificação de inicialização uma vez

        # Configurações de hedge
        self.hedge_active = False
        self.original_position_ticket = None
        self.hedge_position_ticket = None

        # SL dinâmico
        self.atr_multiplier = 1.5

        logger.info(f"🤖 Agente BTCUSD inicializado")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Volume: {volume}")
        logger.info(f"   Target Profit: ${target_profit}")
        logger.info(f"   Max Daily Trades: {max_daily_trades}")

    def calculate_atr(self, periods: int = 14) -> float:
        """Calcula ATR para SL dinâmico."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M5",
            start_pos=0,
            count=periods + 1
        )

        # ATR padrão por tipo de símbolo
        symbol_upper = self.symbol.upper()
        if 'BTC' in symbol_upper:
            default_atr = 150.0
        elif 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            default_atr = 1.0
        elif 'JPY' in symbol_upper:
            default_atr = 0.10
        else:
            # Forex padrão
            default_atr = 0.0008

        if not rates or len(rates) < periods:
            logger.warning(f"⚠️ Dados insuficientes para ATR. Usando padrão: {default_atr}")
            return default_atr

        # Calcular True Range
        trs = []
        for i in range(1, len(rates)):
            high_low = rates[i]['high'] - rates[i]['low']
            high_close = abs(rates[i]['high'] - rates[i-1]['close'])
            low_close = abs(rates[i]['low'] - rates[i-1]['close'])
            tr = max(high_low, high_close, low_close)
            trs.append(tr)

        # ATR é a média dos True Ranges
        atr = sum(trs) / len(trs) if trs else default_atr

        # Se ATR calculado for muito pequeno ou zero, usar padrão
        if atr < 0.0001:
            logger.warning(f"⚠️ ATR muito pequeno ({atr:.8f}). Usando padrão: {default_atr}")
            atr = default_atr

        return atr

    def calculate_indicators(self) -> Dict[str, float]:
        """Calcula todos os indicadores disponíveis."""
        rates = self.mt5.copy_rates_from_pos(
            symbol=self.symbol,
            timeframe="M5",
            start_pos=0,
            count=50
        )

        if not rates:
            return {}

        closes = [r['close'] for r in rates]
        highs = [r['high'] for r in rates]
        lows = [r['low'] for r in rates]

        # RSI
        rsi = self._calculate_rsi(closes, 14)

        # Médias Móveis
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50

        # MACD
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        macd = ema_12 - ema_26

        # Bollinger Bands
        bb_middle = sma_20
        std = (sum((c - bb_middle) ** 2 for c in closes[-20:]) / 20) ** 0.5
        bb_upper = bb_middle + (2 * std)
        bb_lower = bb_middle - (2 * std)

        # ATR
        atr = self.calculate_atr()

        current_price = closes[-1]

        return {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'macd': macd,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'atr': atr,
            'current_price': current_price,
            'trend': 'UP' if sma_20 > sma_50 else 'DOWN'
        }

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcula RSI."""
        if len(prices) < period + 1:
            return 50

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calcula EMA."""
        if len(prices) < period:
            return sum(prices) / len(prices)

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def analyze_signal(self, indicators: Dict) -> str:
        """
        Analisa indicadores e retorna sinal.

        Returns:
            'BUY', 'SELL' ou 'NEUTRAL'
        """
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        current_price = indicators.get('current_price', 0)
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        trend = indicators.get('trend', 'NEUTRAL')

        buy_signals = 0
        sell_signals = 0

        # RSI
        if rsi < 30:
            buy_signals += 2
        elif rsi > 70:
            sell_signals += 2
        elif rsi < 45:
            buy_signals += 1
        elif rsi > 55:
            sell_signals += 1

        # MACD
        if macd > 0:
            buy_signals += 1
        else:
            sell_signals += 1

        # Bollinger Bands
        if current_price < bb_lower:
            buy_signals += 1
        elif current_price > bb_upper:
            sell_signals += 1

        # Trend
        if trend == 'UP':
            buy_signals += 1
        elif trend == 'DOWN':
            sell_signals += 1

        # Decisão
        if buy_signals >= 3 and buy_signals > sell_signals:
            return 'BUY'
        elif sell_signals >= 3 and sell_signals > buy_signals:
            return 'SELL'
        else:
            return 'NEUTRAL'

    def get_minimum_sl_distance(self, symbol_info: Dict, current_price: float) -> float:
        """Calcula distância mínima de SL baseada nas regras do broker."""
        # Pegar stops_level do broker (distância mínima em pontos)
        stops_level = symbol_info.get('trade_stops_level', 0)
        point = symbol_info.get('point', 0.00001)

        # Converter stops_level para preço
        min_distance_broker = stops_level * point

        # Valores mínimos padrão por tipo de símbolo (como fallback)
        symbol = self.symbol.upper()
        if 'BTC' in symbol:
            min_distance_default = 100.0  # Bitcoin
        elif 'XAU' in symbol or 'GOLD' in symbol:
            min_distance_default = 0.50   # Ouro
        elif 'JPY' in symbol:
            min_distance_default = 0.10   # Yen (cotação em 3 dígitos)
        else:
            # Forex padrão (EUR, GBP, etc)
            min_distance_default = 0.0010  # 10 pips

        # Usar o maior entre o mínimo do broker e o padrão
        min_distance = max(min_distance_broker, min_distance_default)

        # Garantir pelo menos 0.1% do preço como SL
        min_percentage = current_price * 0.001

        return max(min_distance, min_percentage)

    def open_position(self, signal: str, indicators: Dict) -> Optional[int]:
        """Abre uma posição."""
        if self.daily_trades >= self.max_daily_trades:
            logger.warning(f"⚠️ Limite diário atingido: {self.daily_trades}/{self.max_daily_trades}")
            return None

        # Obter informações do símbolo
        symbol_info = self.mt5.get_symbol_info(self.symbol)
        if not symbol_info:
            logger.error("Não foi possível obter informações do símbolo")
            return None

        # Calcular SL e TP
        atr = indicators.get('atr', 0)
        current_price = indicators.get('current_price', 0)

        if current_price == 0:
            logger.error("Preço atual é 0, impossível abrir posição")
            return None

        # Calcular distância do SL baseada no ATR
        sl_distance = atr * self.atr_multiplier if atr > 0 else 0

        # Garantir distância mínima de SL
        min_sl_distance = self.get_minimum_sl_distance(symbol_info, current_price)
        sl_distance = max(sl_distance, min_sl_distance)

        logger.info(f"📏 SL Distance: ATR={atr:.5f}, Calculado={sl_distance:.5f}, Mínimo={min_sl_distance:.5f}")

        tick_value = symbol_info.get('trade_tick_value', 1)
        tick_size = symbol_info.get('trade_tick_size', 0.00001)

        # TP em pontos para atingir target profit
        if tick_value == 0 or self.volume == 0:
            logger.error(f"Valores inválidos: tick_value={tick_value}, volume={self.volume}")
            return None

        tp_points = (self.target_profit / (tick_value * self.volume)) * tick_size

        # Garantir TP mínimo também
        tp_points = max(tp_points, min_sl_distance)

        if signal == 'BUY':
            sl = current_price - sl_distance
            tp = current_price + tp_points

            logger.info(f"🔵 Preparando COMPRA:")
            logger.info(f"   Preço: {current_price:.5f}")
            logger.info(f"   SL: {sl:.5f} (distância: {sl_distance:.5f})")
            logger.info(f"   TP: {tp:.5f} (distância: {tp_points:.5f})")

            result = self.mt5.buy_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"Hedge_Agent_{self.daily_trades+1}"
            )
        else:  # SELL
            sl = current_price + sl_distance
            tp = current_price - tp_points

            logger.info(f"🔴 Preparando VENDA:")
            logger.info(f"   Preço: {current_price:.5f}")
            logger.info(f"   SL: {sl:.5f} (distância: {sl_distance:.5f})")
            logger.info(f"   TP: {tp:.5f} (distância: {tp_points:.5f})")

            result = self.mt5.sell_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl,
                tp=tp,
                comment=f"Hedge_Agent_{self.daily_trades+1}"
            )

        if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
            ticket = result.get('order')
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            self.open_tickets.add(ticket)
            self.trades_today.append({
                'ticket': ticket,
                'type': signal,
                'time': datetime.now(),
                'price': current_price,
                'sl': sl,
                'tp': tp
            })

            logger.info(f"✅ Posição aberta: {signal} | Ticket: {ticket} | SL: {sl:.2f} | TP: {tp:.2f}")

            # 🔔 Notificação Telegram
            try:
                self.telegram.send_trade_opened(
                    ticket=ticket,
                    symbol=self.symbol,
                    trade_type=signal,
                    volume=self.volume,
                    entry_price=current_price,
                    tp=tp,
                    sl=sl,
                    indicators={
                        'rsi': indicators.get('rsi', 0),
                        'macd': indicators.get('macd', 0),
                        'trend': indicators.get('trend', 'N/A'),
                        'atr': atr
                    }
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar notificação Telegram: {e}")

            return ticket
        else:
            error = result.get('comment', 'Unknown error') if result else 'No result'
            logger.error(f"❌ Erro ao abrir posição: {error}")

            # 🔔 Notificação de erro no Telegram
            try:
                self.telegram.send_error_alert(
                    error_message=f"Erro ao abrir posição {signal}",
                    context=error
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar alerta Telegram: {e}")

            return None

    def activate_hedge(self, original_ticket: int) -> Optional[int]:
        """Ativa estratégia de hedge."""
        positions = self.mt5.positions_get(ticket=original_ticket)
        if not positions or len(positions) == 0:
            return None

        position = positions[0]

        # Abrir posição oposta
        opposite_signal = 'SELL' if position['type'] == 0 else 'BUY'

        logger.info(f"🔄 Ativando HEDGE para posição {original_ticket}")

        # Hedge com mesmo volume
        hedge_ticket = self.open_position(opposite_signal, self.calculate_indicators())

        if hedge_ticket:
            self.hedge_active = True
            self.original_position_ticket = original_ticket
            self.hedge_position_ticket = hedge_ticket
            logger.info(f"✅ Hedge ativado: Original={original_ticket}, Hedge={hedge_ticket}")

            # 🔔 Notificação Telegram - Hedge Ativado
            try:
                self.telegram.send_critical_alert(
                    alert_type="HEDGE",
                    title="Hedge Ativado",
                    description=f"Posição em prejuízo. Hedge ativado para defender a posição.",
                    details={
                        'Ticket Original': str(original_ticket),
                        'Ticket Hedge': str(hedge_ticket),
                        'Prejuízo Atual': f"${position.get('profit', 0):+.2f}",
                        'Sinal Contrário': opposite_signal,
                        'Símbolo': self.symbol
                    }
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar alerta de hedge Telegram: {e}")

        return hedge_ticket

    def check_and_reset_daily_counter(self):
        """Reseta contador diário à meia-noite."""
        now = datetime.now()

        if self.trades_today:
            first_trade_today = self.trades_today[0]['time']
            if first_trade_today.date() < now.date():
                logger.info(f"🔄 Novo dia! Resetando contador. Trades ontem: {self.daily_trades}")
                self.daily_trades = 0
                self.trades_today = []
                self.open_tickets.clear()
                self.total_profit = 0.0
                self.winning_streak = 0

    def check_closed_positions(self):
        """
        Verifica se alguma posição foi fechada e atualiza métricas.
        Retorna lista de posições fechadas.
        """
        if not self.open_tickets:
            return []

        # Obter posições atualmente abertas
        current_positions = self.mt5.positions_get(symbol=self.symbol)
        current_tickets = set()
        if current_positions:
            current_tickets = {pos['ticket'] for pos in current_positions}

        # Detectar posições que foram fechadas
        closed_tickets = self.open_tickets - current_tickets

        if not closed_tickets:
            return []

        closed_positions = []

        for ticket in closed_tickets:
            # Buscar informações da posição fechada
            # Usar histórico de deals para obter resultado final
            deals = self.mt5.history_deals_get(ticket=ticket)

            if deals and len(deals) >= 2:  # Abertura + Fechamento
                close_deal = deals[-1]  # Último deal é o fechamento
                profit = close_deal.get('profit', 0)

                # Encontrar trade original na lista
                trade_info = None
                for trade in self.trades_today:
                    if trade['ticket'] == ticket:
                        trade_info = trade
                        break

                closed_positions.append({
                    'ticket': ticket,
                    'profit': profit,
                    'trade_info': trade_info
                })

                # Atualizar métricas
                self.total_profit += profit

                if profit > 0:
                    self.winning_streak += 1
                    logger.info(f"✅ Posição #{ticket} fechada com LUCRO: ${profit:+.2f} | Streak: {self.winning_streak}")
                else:
                    self.winning_streak = 0
                    logger.info(f"❌ Posição #{ticket} fechada com PREJUÍZO: ${profit:+.2f} | Streak resetado")

                # Salvar no banco
                self.save_trade_to_db(ticket, profit, trade_info)

                # 🔔 Notificação Telegram - Posição fechada
                try:
                    if trade_info:
                        self.telegram.send_trade_closed(
                            ticket=ticket,
                            symbol=self.symbol,
                            trade_type=trade_info.get('type', 'UNKNOWN'),
                            entry_price=trade_info.get('price', 0),
                            close_price=close_deal.get('price', 0),
                            profit=profit,
                            duration_seconds=int((close_deal.get('time', 0) - open_deal.get('time', 0))),
                            daily_stats={
                                'total_profit': self.total_profit,
                                'win_rate': (sum(1 for t in self.trades_today if t.get('profit', 0) > 0) / len(self.trades_today) * 100) if self.trades_today else 0,
                                'winning_streak': self.winning_streak,
                                'trades_count': self.daily_trades,
                                'wins': sum(1 for t in self.trades_today if t.get('profit', 0) > 0),
                                'losses': sum(1 for t in self.trades_today if t.get('profit', 0) <= 0)
                            }
                        )
                except Exception as e:
                    logger.error(f"⚠️ Erro ao enviar notificação de fechamento Telegram: {e}")

                # Remover do tracking
                self.open_tickets.discard(ticket)

        return closed_positions

    def save_trade_to_db(self, ticket: int, profit: float, trade_info: dict):
        """Salva trade no banco de dados."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Buscar histórico completo do deal
            deals = self.mt5.history_deals_get(ticket=ticket)

            if not deals or len(deals) < 2:
                logger.warning(f"Não foi possível obter histórico completo do ticket {ticket}")
                return

            open_deal = deals[0]
            close_deal = deals[-1]

            cursor.execute("""
                INSERT INTO trades (
                    ticket, symbol, type, volume,
                    open_price, close_price, open_time, close_time,
                    sl, tp, profit, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket,
                self.symbol,
                trade_info.get('type', 'BUY') if trade_info else 'UNKNOWN',
                open_deal.get('volume', 0),
                open_deal.get('price', 0),
                close_deal.get('price', 0),
                datetime.fromtimestamp(open_deal.get('time', 0)).isoformat(),
                datetime.fromtimestamp(close_deal.get('time', 0)).isoformat(),
                trade_info.get('sl', 0) if trade_info else 0,
                trade_info.get('tp', 0) if trade_info else 0,
                profit,
                f"BTC_Hedge_Agent"
            ))

            conn.commit()
            conn.close()
            logger.info(f"💾 Trade #{ticket} salvo no banco de dados")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar trade no banco: {e}", exc_info=True)

    def get_status(self) -> Dict:
        """Retorna status atual do agente."""
        positions = self.mt5.positions_get(symbol=self.symbol)
        indicators = self.calculate_indicators()

        return {
            'agent': 'BTC_Hedge_Agent',
            'state': self.state.value,
            'symbol': self.symbol,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'total_profit': self.total_profit,
            'winning_streak': self.winning_streak,
            'hedge_active': self.hedge_active,
            'positions_count': len(positions) if positions else 0,
            'positions': positions if positions else [],
            'indicators': indicators,
            'last_trade': self.last_trade_time.isoformat() if self.last_trade_time else None
        }

    def export_to_json(self, indicators: Dict, positions: List):
        """
        Exporta dados do agente para JSON (lido pelo MT5 dashboard).

        Arquivo: C:\\mcp-trader\\agent_data.json
        """
        try:
            # Calcular lucro total das posições
            total_positions_profit = 0.0
            if positions:
                for pos in positions:
                    total_positions_profit += pos.get('profit', 0)

            data = {
                "agent": "BTC_Hedge_Agent",
                "state": self.state.value,
                "symbol": self.symbol,
                "daily_trades": self.daily_trades,
                "max_daily_trades": self.max_daily_trades,
                "total_profit": round(total_positions_profit, 2),
                "winning_streak": self.winning_streak,
                "hedge_active": self.hedge_active,
                "positions_count": len(positions) if positions else 0,
                "timestamp": datetime.now().isoformat(),
                # Indicadores
                "current_price": round(indicators.get('current_price', 0), 2),
                "trend": indicators.get('trend', 'NEUTRAL'),
                "rsi": round(indicators.get('rsi', 50), 1),
                "macd": round(indicators.get('macd', 0), 2),
                "atr": round(indicators.get('atr', 0), 2),
                "sma_20": round(indicators.get('sma_20', 0), 2),
                "sma_50": round(indicators.get('sma_50', 0), 2),
                "bb_upper": round(indicators.get('bb_upper', 0), 2),
                "bb_middle": round(indicators.get('bb_middle', 0), 2),
                "bb_lower": round(indicators.get('bb_lower', 0), 2)
            }

            json_path = Path('C:/mcp-trader/agent_data.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")

    def run(self):
        """Loop principal do agente."""
        logger.info("🚀 Iniciando agente de trading BTCUSD...")

        cycle = 0

        try:
            while self.state != AgentState.STOPPED:
                cycle += 1
                self.cycle_count += 1

                # Reset diário
                self.check_and_reset_daily_counter()

                # Calcular indicadores
                indicators = self.calculate_indicators()

                if not indicators:
                    logger.error("❌ Erro ao calcular indicadores")
                    time.sleep(self.check_interval)
                    continue

                # Verificar posições fechadas e atualizar métricas
                closed = self.check_closed_positions()

                # Obter posições abertas
                positions = self.mt5.positions_get(symbol=self.symbol)
                positions_count = len(positions) if positions else 0

                # LOG A CADA CICLO
                self.print_status(cycle, indicators, positions)

                # EXPORTAR DADOS PARA MT5 DASHBOARD
                self.export_to_json(indicators, positions)

                # 🔔 Enviar notificação de inicialização do agente (apenas uma vez)
                if not self.startup_notified:
                    try:
                        signal = self.analyze_signal(indicators)
                        self.telegram.send_critical_alert(
                            alert_type="STARTUP",
                            title=f"🚀 Agente Iniciado - {self.symbol}",
                            description="Agente de trading iniciado e analisando mercado",
                            details={
                                'Volume': f"{self.volume} lots",
                                'Target Profit': f"${self.target_profit:.2f}",
                                'Stop Loss': f"1.5× ATR",
                                'Limite Diário': f"{self.max_daily_trades} operações",
                                'Preço Atual': f"${indicators.get('current_price', 0):.2f}",
                                'Tendência': indicators.get('trend', 'N/A'),
                                'RSI': f"{indicators.get('rsi', 0):.1f}",
                                'MACD': f"{indicators.get('macd', 0):+.2f}",
                                'ATR': f"{indicators.get('atr', 0):.2f}",
                                'Sinal Inicial': signal
                            }
                        )
                        self.startup_notified = True
                        logger.info("✅ Notificação de inicialização enviada ao Telegram")
                    except Exception as e:
                        logger.error(f"⚠️ Erro ao enviar notificação de inicialização: {e}")

                # 🔔 Enviar resumo periódico a cada 10 ciclos (~5 minutos com check_interval=30s)
                if self.cycle_count % 10 == 0:
                    try:
                        wins = sum(1 for trade in self.trades_today if trade.get('profit', 0) > 0)
                        self.telegram.send_periodic_summary(
                            symbol=self.symbol,
                            state=self.state.value,
                            daily_stats={
                                'total_profit': self.total_profit,
                                'win_rate': (wins / self.daily_trades * 100) if self.daily_trades > 0 else 0,
                                'winning_streak': self.winning_streak,
                                'trades_count': self.daily_trades,
                                'wins': wins,
                                'losses': self.daily_trades - wins
                            },
                            positions_open=positions_count,
                            indicators={
                                'current_price': indicators.get('current_price', 0),
                                'trend': indicators.get('trend', 'N/A'),
                                'rsi': indicators.get('rsi', 0),
                                'macd': indicators.get('macd', 0),
                                'atr': indicators.get('atr', 0),
                                'sma_20': indicators.get('sma_20', 0),
                                'sma_50': indicators.get('sma_50', 0),
                                'bb_upper': indicators.get('bb_upper', 0),
                                'bb_middle': indicators.get('bb_middle', 0),
                                'bb_lower': indicators.get('bb_lower', 0)
                            },
                            time_period="últimos 5 minutos"
                        )
                    except Exception as e:
                        logger.error(f"⚠️ Erro ao enviar resumo periódico Telegram: {e}")

                # Verificar se pode operar
                if self.daily_trades >= self.max_daily_trades:
                    logger.warning(f"⚠️  Limite diário atingido. Pausando...")
                    self.state = AgentState.PAUSED
                    time.sleep(self.check_interval)
                    continue

                # Analisar sinal
                signal = self.analyze_signal(indicators)

                # Verificar posições existentes
                if positions_count > 0:
                    # Verificar se precisa de hedge
                    for pos in positions:
                        profit = pos.get('profit', 0)

                        # Se estiver em prejuízo significativo e não tem hedge
                        if profit < -10 and not self.hedge_active:
                            logger.warning(f"⚠️  Posição em prejuízo: ${profit:.2f}")
                            self.activate_hedge(pos['ticket'])

                # Abrir nova posição se sinal válido e sem muitas posições
                if signal != 'NEUTRAL' and positions_count < 5:
                    if self.winning_streak >= 2:  # Operações consecutivas em winning streak
                        logger.info(f"📈 Winning streak: {self.winning_streak} - Abrindo nova posição")
                        self.open_position(signal, indicators)
                    elif positions_count == 0:  # Primeira posição
                        self.open_position(signal, indicators)

                # Aguardar próximo ciclo
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n⚠️  Agente interrompido pelo usuário")
            self.state = AgentState.STOPPED

            # 🔔 Notificação final no Telegram
            try:
                self.telegram.send_critical_alert(
                    alert_type="STOP",
                    title="Agente Parado",
                    description=f"Agente de trading {self.symbol} foi parado.",
                    details={
                        'Operações Hoje': str(self.daily_trades),
                        'Lucro Total': f"${self.total_profit:+.2f}",
                        'Streak': str(self.winning_streak),
                        'Posições Abertas': str(positions_count) if positions else "0"
                    }
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar notificação final Telegram: {e}")

        except Exception as e:
            logger.error(f"❌ Erro no agente: {e}", exc_info=True)
            self.state = AgentState.STOPPED

            # 🔔 Notificação de erro crítico
            try:
                self.telegram.send_error_alert(
                    error_message=f"Erro crítico no agente {self.symbol}",
                    context=str(e)
                )
            except Exception as e:
                logger.error(f"⚠️ Erro ao enviar alerta de erro Telegram: {e}")

    def print_status(self, cycle: int, indicators: Dict, positions: List):
        """Imprime status detalhado."""
        print("\n" + "="*80)
        print(f"🤖 AGENTE BTC HEDGE | Ciclo #{cycle} | {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)

        # Agente
        print(f"\n📊 AGENTE:")
        print(f"   Estado: {self.state.value.upper()}")
        print(f"   Operações Hoje: {self.daily_trades}/{self.max_daily_trades}")
        print(f"   Lucro Total: ${self.total_profit:+.2f}")
        print(f"   Winning Streak: {self.winning_streak}")
        print(f"   Hedge Ativo: {'SIM' if self.hedge_active else 'NÃO'}")

        # Mercado
        print(f"\n📈 MERCADO ({self.symbol}):")
        print(f"   Preço: ${indicators.get('current_price', 0):.2f}")
        print(f"   Tendência: {indicators.get('trend', 'N/A')}")
        print(f"   RSI: {indicators.get('rsi', 0):.1f}")
        print(f"   MACD: {indicators.get('macd', 0):+.2f}")
        print(f"   ATR: {indicators.get('atr', 0):.2f}")
        print(f"   SMA20: ${indicators.get('sma_20', 0):.2f}")
        print(f"   SMA50: ${indicators.get('sma_50', 0):.2f}")

        # Posições
        print(f"\n💼 POSIÇÕES ABERTAS: {len(positions) if positions else 0}")
        if positions:
            total_profit = 0
            for i, pos in enumerate(positions, 1):
                profit = pos.get('profit', 0)
                total_profit += profit
                tipo = "COMPRA" if pos.get('type') == 0 else "VENDA"
                print(f"   {i}. Ticket {pos.get('ticket')} | {tipo} | {pos.get('volume')} lots | Lucro: ${profit:+.2f}")
            print(f"   💰 TOTAL: ${total_profit:+.2f}")

        print("="*80 + "\n")


def main():
    """Função principal."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup database
    setup_database()

    # Criar e iniciar agente
    import sys

    # Permitir passar símbolo, volume e limite diário como argumentos
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDm"
    volume = float(sys.argv[2]) if len(sys.argv) > 2 else 0.02
    max_daily_trades = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    # Target profit padrão por símbolo
    target_profit_map = {
        'BTCUSDm': 2.0,
        'XAUUSDm': 2.0,  # Ouro
        'XAUUSDc': 2.0,  # Ouro (alternativa)
        'GBPUSDc': 2.0,  # Libra
        'EURUSDc': 2.0,  # Euro
        'USDJPYc': 2.0,  # Iene
    }
    target_profit = target_profit_map.get(symbol, 2.0)

    logger.info(f"Iniciando com símbolo: {symbol}, volume: {volume}, target_profit: ${target_profit}, max_daily_trades: {max_daily_trades}")

    agent = BTCHedgeAgent(
        symbol=symbol,
        volume=volume,
        target_profit=target_profit,
        max_daily_trades=max_daily_trades,
        check_interval=30
    )

    # Executar
    agent.run()


if __name__ == "__main__":
    main()
