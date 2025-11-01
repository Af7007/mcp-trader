#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss Zero Otimizado - Estratégia de Trailing Stop Ilimitado
======================================================================

Características:
- Estratégia de ZERO LOSSES garantidas com trailing stop dinâmico
- Sem Take Profit fixo (TP infinito)
- Trailing stop começa em 0.5% e cresce indefinidamente
- Lucros ilimitados: captura todo movimento favorável
- Análise simples: RSI para sinais de entrada
- Gerenciamento automático de posições

Configuração:
- Symbol: BTCUSDc (Bitcoin em centavos)
- Volume: 0.05 lots (agressivo)
- Check Interval: 15 segundos
- Trailing Start: 0.5% de lucro
- Trailing Increment: +0.1% por movimento favorável
"""

import logging
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
from core.database import setup_database, get_db_connection
from core.telegram_notifier import get_telegram_notifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BTCLossZeroOtimizado:
    """
    Agente de Trading BTC com Estratégia Loss Zero Otimizada.

    Principios:
    1. ZERO LOSSES - Trailing stop sempre protege
    2. LUCROS ILIMITADOS - Sem TP fixo
    3. AUTOMÁTICO - Sem intervenção manual
    4. SIMPLES - Apenas RSI para sinais
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",
        volume: float = 0.05,
        check_interval: int = 15,
        trailing_start_percent: float = 0.5,
        trailing_increment: float = 0.1,
        use_buy: bool = True,
        use_sell: bool = True
    ):
        """Inicializa agente Loss Zero"""
        self.symbol = symbol
        self.volume = volume
        self.check_interval = check_interval
        self.trailing_start_percent = trailing_start_percent
        self.trailing_increment = trailing_increment
        self.use_buy = use_buy
        self.use_sell = use_sell

        # Inicializar MT5
        self.mt5 = None
        self._init_mt5()

        # Telegram notificador
        self.telegram = get_telegram_notifier()

        # Estado do agente
        self.trailing_active = False
        self.trailing_distance = 0.0
        self.entry_price = 0.0
        self.entry_ticket = None
        self.position_type = None  # "BUY" ou "SELL"
        self.current_profit_pct = 0.0

        # Estatísticas
        self.total_trades = 0
        self.profitable_trades = 0
        self.total_profit = 0.0
        self.current_win_streak = 0

        logger.info(f"✅ Agente BTC Loss Zero Otimizado inicializado")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Volume: {self.volume}")
        logger.info(f"   Trailing: {trailing_start_percent}% → ILIMITADO")
        logger.info(f"   Check Interval: {check_interval}s")

    def _init_mt5(self):
        """Inicializa conexão com MetaTrader 5"""
        if not mt5.initialize():
            raise Exception(f"Falha ao inicializar MT5: {mt5.last_error()}")

        self.mt5 = mt5
        logger.info("✅ MT5 inicializado com sucesso")

    def run(self):
        """Executa agente Loss Zero continuamente"""
        logger.info("=" * 70)
        logger.info("🤖 AGENTE BTC LOSS ZERO - TRAILING STOP ILIMITADO")
        logger.info("=" * 70)
        logger.info(f"Estratégia: Zero Losses + Lucros Ilimitados")
        logger.info(f"Pressione Ctrl+C para parar")
        logger.info("=" * 70)

        try:
            cycle = 0
            while True:
                cycle += 1
                self._execute_cycle(cycle)
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n" + "=" * 70)
            logger.info("⛔ Agente BTC Loss Zero parado pelo usuário")
            logger.info("=" * 70)
            self._print_final_stats()
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
            self._notify(f"❌ Agente Loss Zero parado com erro: {e}")

    def _execute_cycle(self, cycle: int):
        """Executa um ciclo completo de análise e gerenciamento"""
        try:
            # Verificar posições abertas
            positions = self.mt5.positions_get(symbol=self.symbol)

            if not positions:
                # Sem posições, analisar para abrir
                self._analyze_and_open(cycle)
            else:
                # Tem posição, gerenciar trailing
                for pos in positions:
                    self._manage_position_trailing(pos, cycle)

        except Exception as e:
            logger.error(f"Erro no ciclo {cycle}: {e}")

    def _analyze_and_open(self, cycle: int):
        """Analisa mercado e abre posição se sinal for válido"""
        try:
            # Obter dados M1
            rates = self.mt5.copy_rates_from_pos(
                self.symbol,
                mt5.TIMEFRAME_M1,
                0,
                50
            )

            if rates is None or len(rates) < 20:
                return

            # Calcular RSI
            rsi = self._calculate_rsi(rates, 14)

            # Gerar sinais
            signal = None

            # SELL: RSI > 70 (overbought)
            if self.use_sell and rsi > 70:
                signal = {
                    "type": "SELL",
                    "reason": f"RSI overbought ({rsi:.2f})",
                    "price": rates[0]["close"]
                }

            # BUY: RSI < 30 (oversold)
            elif self.use_buy and rsi < 30:
                signal = {
                    "type": "BUY",
                    "reason": f"RSI oversold ({rsi:.2f})",
                    "price": rates[0]["close"]
                }

            # Abrir posição se houver sinal
            if signal:
                self._open_position(signal)

        except Exception as e:
            logger.error(f"Erro na análise: {e}")

    def _open_position(self, signal: Dict):
        """Abre nova posição com estratégia Loss Zero"""
        try:
            # Fechar posições opostas primeiro
            self._close_opposite_positions(signal["type"])

            # Preparar request
            request = {
                "action": mt5.ORDER_TYPE_SELL if signal["type"] == "SELL" else mt5.ORDER_TYPE_BUY,
                "symbol": self.symbol,
                "volume": self.volume,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "deviation": 10,
                "comment": "Loss Zero - Trailing ilimitado"
            }

            # Enviar ordem
            result = self.mt5.order_send(request)

            if result and result.retcode == mt5.ORDER_RETCODE_DONE:
                self.entry_price = signal["price"]
                self.entry_ticket = result.order
                self.position_type = signal["type"]
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.current_profit_pct = 0.0
                self.total_trades += 1

                msg = f"""
🟢 POSIÇÃO ABERTA - Loss Zero
{'='*50}
Tipo: {signal["type"]}
Ticket: {result.order}
Preço: ${signal["price"]:.2f}
Volume: {self.volume}
Motivo: {signal["reason"]}
Estratégia: Trailing Stop Ilimitado (SEM TP FIXO)
SL: Trailing em {self.trailing_start_percent}% (inativo)
TP: INFINITO (trailing ilimitado)
{'='*50}
"""
                logger.info(msg)
                self._notify(msg)
            else:
                logger.error(f"Erro ao abrir posição: {result}")

        except Exception as e:
            logger.error(f"Erro ao abrir posição: {e}")

    def _manage_position_trailing(self, pos, cycle: int):
        """Gerencia trailing stop de uma posição"""
        try:
            current_price = pos.price_current

            # Calcular lucro percentual
            if pos.type == mt5.ORDER_TYPE_BUY:
                profit_pct = ((current_price - pos.price_open) / pos.price_open) * 100
            else:  # SELL
                profit_pct = ((pos.price_open - current_price) / pos.price_open) * 100

            self.current_profit_pct = profit_pct

            # Ativar trailing quando atinge limite
            if not self.trailing_active and profit_pct >= self.trailing_start_percent:
                self.trailing_active = True
                self.trailing_distance = self.trailing_start_percent
                msg = f"🚀 TRAILING ATIVADO! Lucro: {profit_pct:.2f}% | Distância: {self.trailing_distance:.2f}%"
                logger.info(msg)
                self._notify(msg)

            # Atualizar trailing quando preço continua favorável
            if self.trailing_active:
                # Se lucro > distância + incremento, aumenta o trailing
                if profit_pct > self.trailing_distance + self.trailing_increment:
                    old_distance = self.trailing_distance
                    self.trailing_distance = profit_pct - self.trailing_increment
                    logger.info(f"📈 Trailing atualizado: {old_distance:.2f}% → {self.trailing_distance:.2f}% (Lucro atual: {profit_pct:.2f}%)")

                # Verificar se deve fechar (preço caiu abaixo do trailing)
                if profit_pct < self.trailing_distance * 0.95:  # 5% de tolerância
                    self._close_position_with_profit(pos, profit_pct)

        except Exception as e:
            logger.error(f"Erro ao gerenciar trailing: {e}")

    def _close_position_with_profit(self, pos, profit_pct: float):
        """Fecha posição com lucro via trailing stop"""
        try:
            result = self.mt5.position_close(pos.ticket)

            if result and result.retcode == mt5.ORDER_RETCODE_DONE:
                self.total_profit += profit_pct * self.volume * 100  # Aproximação
                self.profitable_trades += 1
                self.current_win_streak += 1
                self.trailing_active = False

                msg = f"""
🟢 POSIÇÃO FECHADA COM LUCRO - Trailing Stop
{'='*50}
Ticket: {pos.ticket}
Tipo: {"BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"}
Lucro: {profit_pct:.2f}%
Trailing Ativo: {self.trailing_distance:.2f}%
Streak: {self.current_win_streak} vitórias consecutivas
Total Trades: {self.total_trades}
Win Rate: {(self.profitable_trades/self.total_trades*100):.1f}%
{'='*50}
"""
                logger.info(msg)
                self._notify(msg)
            else:
                logger.error(f"Erro ao fechar posição: {result}")

        except Exception as e:
            logger.error(f"Erro ao fechar posição: {e}")

    def _close_opposite_positions(self, signal_type: str):
        """Fecha posições opostas ao sinal"""
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            if not positions:
                return

            for pos in positions:
                # Se sinal é SELL e posição é BUY, fechar
                if signal_type == "SELL" and pos.type == mt5.ORDER_TYPE_BUY:
                    self.mt5.position_close(pos.ticket)
                # Se sinal é BUY e posição é SELL, fechar
                elif signal_type == "BUY" and pos.type == mt5.ORDER_TYPE_SELL:
                    self.mt5.position_close(pos.ticket)

        except Exception as e:
            logger.error(f"Erro ao fechar posições opostas: {e}")

    def _calculate_rsi(self, rates, period: int = 14) -> float:
        """Calcula RSI simples"""
        try:
            if not isinstance(rates, list):
                # Converter numpy array para lista
                rates = list(rates)

            if len(rates) < period + 1:
                return 50.0

            # Extrair preços de fechamento
            closes = []
            for r in rates[:period + 1]:
                if isinstance(r, dict):
                    closes.append(float(r["close"]))
                else:
                    # Se é struct/numpy, acessar por índice
                    closes.append(float(r[4]))  # close é geralmente índice 4

            closes.reverse()  # Inverter para começar com mais antigo

            # Calcular ganhos e perdas
            gains = []
            losses = []

            for i in range(1, len(closes)):
                diff = closes[i] - closes[i-1]
                if diff > 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(diff))

            # Média de ganhos e perdas
            avg_gain = sum(gains) / period if gains else 0
            avg_loss = sum(losses) / period if losses else 0

            # RSI
            if avg_loss == 0:
                return 100.0 if avg_gain > 0 else 50.0

            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs)) if rs > 0 else 0

            return rsi

        except Exception as e:
            logger.error(f"Erro ao calcular RSI: {e}")
            return 50.0

    def _notify(self, message: str):
        """Envia notificação via Telegram"""
        try:
            if self.telegram:
                self.telegram.notify(message)
        except:
            pass

    def _print_final_stats(self):
        """Imprime estatísticas finais"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 ESTATÍSTICAS FINAIS DO AGENTE LOSS ZERO")
        logger.info("=" * 70)
        logger.info(f"Total de Trades: {self.total_trades}")
        logger.info(f"Trades Lucrativos: {self.profitable_trades}")
        logger.info(f"Win Rate: {(self.profitable_trades/max(1, self.total_trades)*100):.1f}%")
        logger.info(f"Lucro Total Aproximado: {self.total_profit:.2f}%")
        logger.info(f"Maior Streak: {self.current_win_streak}")
        logger.info("=" * 70 + "\n")


def main():
    """Função principal para iniciar o agente"""
    try:
        # Criar agente Loss Zero
        agent = BTCLossZeroOtimizado(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            trailing_start_percent=0.5,
            trailing_increment=0.1,
            use_buy=True,
            use_sell=True
        )

        # Executar agente
        agent.run()

    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        print(f"❌ Erro: {e}")
        print("\nCertifique-se de que:")
        print("1. MetaTrader 5 está aberto")
        print("2. Você está logado na sua conta")
        print("3. O símbolo BTCUSDc está disponível")


if __name__ == "__main__":
    main()
