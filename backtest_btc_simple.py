#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtester Simples para BTC v2.1.0
Testa estrategia usando dados historicos do MT5
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
from collections import defaultdict

class BTCBacktesterSimple:
    """
    Backtester simples que simula trades usando logica do agente BTC v2.1.0
    """

    def __init__(self, symbol="BTCUSDc", days=7):
        self.symbol = symbol
        self.days = days

        # Parametros do agente (mesmos do BTC v2.1.0)
        self.base_volume = 0.30
        self.min_score_m5 = 3.5
        self.max_atr_m5_dollars = 20.0
        self.max_spread_dollars = 20.0
        self.fixed_sl_dollars = 5.0
        self.trailing_activation_dollar = 2.0
        self.trailing_distance_dollar = 1.0
        self.point_value = 0.003  # BTC com volume 0.30

        # Resultados
        self.trades = []
        self.current_position = None

        # Inicializar MT5
        if not mt5.initialize():
            raise Exception("Falha ao inicializar MT5")

    def get_historical_data(self):
        """Busca dados historicos do MT5"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)

        print(f"[BACKTEST] Buscando dados de {start_date.date()} a {end_date.date()}")

        rates_m5 = mt5.copy_rates_range(
            self.symbol,
            mt5.TIMEFRAME_M5,
            start_date,
            end_date
        )

        rates_m1 = mt5.copy_rates_range(
            self.symbol,
            mt5.TIMEFRAME_M1,
            start_date,
            end_date
        )

        if rates_m5 is None or rates_m1 is None:
            raise Exception("Erro ao buscar dados historicos")

        print(f"[BACKTEST] {len(rates_m5)} velas M5, {len(rates_m1)} velas M1")

        return rates_m5, rates_m1

    def calculate_dynamic_volume(self, atr_dollars):
        """Calcula volume dinamico (v2.1.0)"""
        if atr_dollars < 5.0:
            return self.base_volume  # 0.30
        elif atr_dollars < 10.0:
            return self.base_volume * 0.67  # 0.20
        else:
            return self.base_volume * 0.33  # 0.10

    def calculate_atr(self, rates, period=14):
        """Calcula ATR"""
        atr_sum = 0
        for i in range(period):
            if i >= len(rates):
                break
            high = rates[i]['high']
            low = rates[i]['low']
            close_prev = rates[i+1]['close'] if i+1 < len(rates) else rates[i]['close']
            tr = max(high - low, abs(high - close_prev), abs(low - close_prev))
            atr_sum += tr
        return atr_sum / period if period > 0 else 0

    def calculate_rsi(self, closes, period=14):
        """Calcula RSI"""
        if len(closes) < period + 1:
            return 50.0

        gains = [max(0, closes[i] - closes[i+1]) for i in range(period)]
        losses = [max(0, closes[i+1] - closes[i]) for i in range(period)]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def analyze_m5_signal(self, rates_m5_window):
        """
        Analisa M5 para sinal (mesma logica do agente)
        """
        if len(rates_m5_window) < 50:
            return None

        closes = [r['close'] for r in rates_m5_window[:50]]
        current = closes[0]

        # Indicadores
        sma20 = sum(closes[:20]) / 20
        sma50 = sum(closes[:50]) / 50
        rsi = self.calculate_rsi(closes, 14)

        # Tendencia
        uptrend = sum(1 for i in range(4) if closes[i] > closes[i+1]) >= 3
        downtrend = sum(1 for i in range(4) if closes[i] < closes[i+1]) >= 3

        # Momentum
        momentum = (current - closes[9]) / closes[9] * 100

        # ATR
        atr_pontos = self.calculate_atr(rates_m5_window, 14)
        atr_dollars = atr_pontos * self.point_value * self.base_volume

        # Volume dinamico
        volume = self.calculate_dynamic_volume(atr_dollars)

        # Recalcular ATR com volume ajustado
        atr_dollars_adjusted = atr_pontos * self.point_value * volume

        # Filtro ATR
        if atr_dollars_adjusted > self.max_atr_m5_dollars:
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

        # Verificar score minimo
        if buy_score >= self.min_score_m5:
            return {
                'type': 'BUY',
                'score': buy_score,
                'price': current,
                'volume': volume,
                'atr': atr_dollars_adjusted
            }
        elif sell_score >= self.min_score_m5:
            return {
                'type': 'SELL',
                'score': sell_score,
                'price': current,
                'volume': volume,
                'atr': atr_dollars_adjusted
            }

        return None

    def confirm_m1_timing(self, rates_m1_window, signal_type):
        """
        Confirma timing em M1 (2 velas consecutivas)
        """
        if len(rates_m1_window) < 3:
            return False

        closes = [r['close'] for r in rates_m1_window[:3]]

        if signal_type == "BUY":
            return closes[0] > closes[1] > closes[2]
        else:  # SELL
            return closes[0] < closes[1] < closes[2]

    def open_position(self, signal, bar):
        """Abre posicao virtual"""
        entry_price = signal['price']
        volume = signal['volume']

        # Calcular SL
        pontos_para_sl = self.fixed_sl_dollars / (self.point_value * volume)
        sl_distance = pontos_para_sl * 0.01  # point = 0.01

        if signal['type'] == 'BUY':
            sl_price = entry_price - sl_distance
        else:
            sl_price = entry_price + sl_distance

        self.current_position = {
            'type': signal['type'],
            'entry_price': entry_price,
            'entry_time': bar['time'],
            'sl_price': sl_price,
            'volume': volume,
            'score': signal['score'],
            'atr': signal['atr'],
            'trailing_active': False,
            'trailing_stop': 0,
            'max_profit': 0
        }

    def manage_position(self, bar):
        """Gerencia posicao aberta (SL e Trailing)"""
        if not self.current_position:
            return None

        pos = self.current_position
        current_price = bar['close']

        # Calcular lucro atual
        if pos['type'] == 'BUY':
            profit_points = (current_price - pos['entry_price']) / 0.01
        else:
            profit_points = (pos['entry_price'] - current_price) / 0.01

        profit_dollars = profit_points * self.point_value * pos['volume']

        # Atualizar max profit
        if profit_dollars > pos['max_profit']:
            pos['max_profit'] = profit_dollars

        # Verificar SL
        if pos['type'] == 'BUY':
            if current_price <= pos['sl_price']:
                return self.close_position(bar, 'SL_HIT', profit_dollars)
        else:
            if current_price >= pos['sl_price']:
                return self.close_position(bar, 'SL_HIT', profit_dollars)

        # Ativar trailing
        if not pos['trailing_active'] and profit_dollars >= self.trailing_activation_dollar:
            pos['trailing_active'] = True

            # Calcular trailing stop inicial
            protection = self.trailing_distance_dollar
            protection_points = protection / (self.point_value * pos['volume'])
            protection_distance = protection_points * 0.01

            if pos['type'] == 'BUY':
                pos['trailing_stop'] = current_price - protection_distance
            else:
                pos['trailing_stop'] = current_price + protection_distance

        # Gerenciar trailing
        if pos['trailing_active']:
            protection = self.trailing_distance_dollar
            protection_points = protection / (self.point_value * pos['volume'])
            protection_distance = protection_points * 0.01

            if pos['type'] == 'BUY':
                new_trailing = current_price - protection_distance
                if new_trailing > pos['trailing_stop']:
                    pos['trailing_stop'] = new_trailing

                # Verificar se atingiu trailing
                if current_price <= pos['trailing_stop']:
                    return self.close_position(bar, 'TRAILING_HIT', profit_dollars)
            else:
                new_trailing = current_price + protection_distance
                if new_trailing < pos['trailing_stop']:
                    pos['trailing_stop'] = new_trailing

                # Verificar se atingiu trailing
                if current_price >= pos['trailing_stop']:
                    return self.close_position(bar, 'TRAILING_HIT', profit_dollars)

        return None

    def close_position(self, bar, reason, profit):
        """Fecha posicao e registra trade"""
        pos = self.current_position

        trade = {
            'type': pos['type'],
            'entry_price': pos['entry_price'],
            'entry_time': pos['entry_time'],
            'exit_price': bar['close'],
            'exit_time': bar['time'],
            'volume': pos['volume'],
            'score': pos['score'],
            'atr': pos['atr'],
            'profit': profit,
            'reason': reason,
            'max_profit': pos['max_profit']
        }

        self.trades.append(trade)
        self.current_position = None

        return trade

    def run_backtest(self):
        """Executa backtest"""
        print(f"\n{'='*60}")
        print(f"BACKTEST BTC v2.1.0 - Ultimos {self.days} dias")
        print(f"{'='*60}\n")

        # Buscar dados
        rates_m5, rates_m1 = self.get_historical_data()

        # Mapear indices M1 para M5
        m1_index = 0

        # Simular trades
        for i in range(50, len(rates_m5)):
            # Janela M5
            rates_m5_window = rates_m5[i-50:i+1]

            # Analisar M5
            signal = self.analyze_m5_signal(rates_m5_window)

            if signal and not self.current_position:
                # Buscar janela M1 correspondente
                # M5 bar = 5 velas M1
                m1_start = m1_index
                m1_end = min(m1_index + 5, len(rates_m1))
                rates_m1_window = rates_m1[m1_start:m1_end]

                # Confirmar M1
                if self.confirm_m1_timing(rates_m1_window, signal['type']):
                    self.open_position(signal, rates_m5[i])

            # Gerenciar posicao aberta
            if self.current_position:
                trade = self.manage_position(rates_m5[i])
                if trade:
                    # Mostrar trade fechado
                    result = "[WIN]" if trade['profit'] > 0 else "[LOSS]"
                    print(f"{result} {trade['type']} | Profit: ${trade['profit']:.2f} | Reason: {trade['reason']}")

            # Avançar indice M1 (5 velas M1 = 1 vela M5)
            m1_index += 5

        # Fechar posicao aberta se houver
        if self.current_position:
            self.close_position(rates_m5[-1], 'BACKTEST_END', 0)

        # Calcular metricas
        return self.calculate_metrics()

    def calculate_metrics(self):
        """Calcula metricas do backtest"""
        if not self.trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_profit': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }

        wins = [t for t in self.trades if t['profit'] > 0]
        losses = [t for t in self.trades if t['profit'] <= 0]

        total_wins = sum(t['profit'] for t in wins)
        total_losses = abs(sum(t['profit'] for t in losses))

        metrics = {
            'total_trades': len(self.trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': (len(wins) / len(self.trades) * 100) if self.trades else 0,
            'total_profit': sum(t['profit'] for t in self.trades),
            'avg_win': total_wins / len(wins) if wins else 0,
            'avg_loss': total_losses / len(losses) if losses else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else 0,
            'max_win': max((t['profit'] for t in wins), default=0),
            'max_loss': min((t['profit'] for t in losses), default=0)
        }

        return metrics

    def print_report(self, metrics):
        """Imprime relatorio"""
        print(f"\n{'='*60}")
        print(f"RELATORIO BACKTEST - BTC v2.1.0")
        print(f"{'='*60}\n")

        print(f"Periodo: Ultimos {self.days} dias")
        print(f"Symbol: {self.symbol}")
        print(f"Estrategia: M5 + M1 Timing (Score >= {self.min_score_m5})")
        print(f"Volume Dinamico: ATIVO (0.10-0.30)\n")

        print(f"{'='*60}")
        print(f"RESULTADOS")
        print(f"{'='*60}\n")

        print(f"Total de Trades: {metrics['total_trades']}")
        print(f"Wins: {metrics['wins']}")
        print(f"Losses: {metrics['losses']}")
        print(f"Win Rate: {metrics['win_rate']:.1f}%\n")

        print(f"Total Profit: ${metrics['total_profit']:.2f}")
        print(f"Avg Win: ${metrics['avg_win']:.2f}")
        print(f"Avg Loss: ${metrics['avg_loss']:.2f}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}\n")

        print(f"Max Win: ${metrics['max_win']:.2f}")
        print(f"Max Loss: ${metrics['max_loss']:.2f}\n")

        # Analise
        print(f"{'='*60}")
        print(f"ANALISE")
        print(f"{'='*60}\n")

        if metrics['win_rate'] >= 65:
            print("[EXCELENTE] Win rate >= 65%")
        elif metrics['win_rate'] >= 60:
            print("[BOM] Win rate >= 60%")
        elif metrics['win_rate'] >= 55:
            print("[ACEITAVEL] Win rate >= 55%")
        else:
            print("[BAIXO] Win rate < 55% - Ajustar parametros")

        if metrics['total_profit'] > 0:
            print(f"[LUCRO] Net profit positivo: ${metrics['total_profit']:.2f}")
        else:
            print(f"[PREJUIZO] Net profit negativo: ${metrics['total_profit']:.2f}")

        print(f"\n{'='*60}\n")


def main():
    """Executa backtest"""
    # Configurar periodo (ultimos 7 dias)
    backtester = BTCBacktesterSimple(
        symbol="BTCUSDc",
        days=7
    )

    # Executar
    metrics = backtester.run_backtest()

    # Mostrar relatorio
    backtester.print_report(metrics)

    # Fechar MT5
    mt5.shutdown()


if __name__ == '__main__':
    main()
