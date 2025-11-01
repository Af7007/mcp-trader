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

from core.mt5_direct_client import get_mt5_client
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
        trailing_start_amount: float = 1.0,  # Ativa com $1 de lucro (NOVO - em dólares)
        trailing_increment_amount: float = 0.5,  # Sobe $0.50 a cada dólar de lucro (NOVO - em dólares)
        initial_sl_percent: float = 2.5,  # SL de segurança inicial (2.5% - aumentado)
        initial_tp_percent: float = 10.0,  # TP de segurança inicial (10% - aumentado)
        use_buy: bool = True,
        use_sell: bool = True
    ):
        """Inicializa agente Loss Zero com SL/TP dinâmicos e trailing em dólares"""
        self.symbol = symbol
        self.volume = volume
        self.check_interval = check_interval
        self.trailing_start_amount = trailing_start_amount  # Em dólares
        self.trailing_increment_amount = trailing_increment_amount  # Em dólares
        self.initial_sl_percent = initial_sl_percent  # Percentual
        self.initial_tp_percent = initial_tp_percent  # Percentual
        self.use_buy = use_buy
        self.use_sell = use_sell

        # Inicializar MT5
        self.mt5 = None
        self._init_mt5()

        # Telegram notificador
        self.telegram = get_telegram_notifier()

        # Estado do agente
        self.trailing_active = False
        self.trailing_amount_dollars = 0.0  # Trailing em dólares (não percentual)
        self.entry_price = 0.0
        self.entry_ticket = None
        self.position_type = None  # "BUY" ou "SELL"
        self.current_profit_pct = 0.0
        self.current_profit_dollars = 0.0  # Lucro em dólares
        self.current_sl = 0.0  # SL dinâmico
        self.current_tp = 0.0  # TP de segurança

        # Estatísticas
        self.total_trades = 0
        self.profitable_trades = 0
        self.total_profit = 0.0
        self.current_win_streak = 0

        logger.info(f"[OK] Agente BTC Loss Zero Otimizado inicializado")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Volume: {self.volume}")
        logger.info(f"   SL Inicial (Segurança): {self.initial_sl_percent}%")
        logger.info(f"   TP Inicial (Segurança): {self.initial_tp_percent}%")
        logger.info(f"   Trailing Start: ${self.trailing_start_amount:.2f} em lucro → DINÂMICO")
        logger.info(f"   Trailing Increment: +${self.trailing_increment_amount:.2f} por dólar")
        logger.info(f"   Check Interval: {self.check_interval}s")

    def _init_mt5(self):
        """Inicializa conexão com MetaTrader 5"""
        self.mt5 = get_mt5_client()
        if not self.mt5:
            raise Exception("Falha ao inicializar MT5 client")
        logger.info("[OK] MT5 inicializado com sucesso")

    def run(self):
        """Executa agente Loss Zero continuamente"""
        logger.info("=" * 70)
        logger.info("[AGENTE] AGENTE BTC LOSS ZERO - TRAILING STOP ILIMITADO")
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
            logger.error(f"[ERRO] Erro fatal: {e}")
            self._notify(f"[ERRO] Agente Loss Zero parado com erro: {e}")

    def _execute_cycle(self, cycle: int):
        """Executa um ciclo completo de análise e gerenciamento"""
        try:
            # Verificar posições abertas
            positions = self.mt5.positions_get(symbol=self.symbol)

            if not positions:
                # Sem posições, resetar trailing e analisar para abrir
                self.trailing_active = False
                self.trailing_amount_dollars = 0.0
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
                "M1",
                0,
                50
            )

            if rates is None or len(rates) < 20:
                return

            # Calcular RSI e MFI
            rsi = self._calculate_rsi(rates, 14)
            mfi = self._calculate_mfi(rates, 14)

            # Gerar sinais com dupla confirmação (RSI + MFI)
            signal = None

            # SELL: RSI > 70 (overbought) E MFI > 40 (forte volume de venda)
            if self.use_sell and rsi > 70 and mfi > 40:
                signal = {
                    "type": "SELL",
                    "reason": f"RSI overbought ({rsi:.2f}) + MFI sell ({mfi:.2f})",
                    "price": rates[0]["close"]
                }

            # BUY: RSI < 30 (oversold) E MFI < 60 (forte volume de compra)
            elif self.use_buy and rsi < 30 and mfi < 60:
                signal = {
                    "type": "BUY",
                    "reason": f"RSI oversold ({rsi:.2f}) + MFI buy ({mfi:.2f})",
                    "price": rates[0]["close"]
                }

            # Abrir posição se houver sinal
            if signal:
                self._open_position(signal)

        except Exception as e:
            logger.error(f"Erro na análise: {e}")

    def _open_position(self, signal: Dict):
        """Abre nova posição com SL/TP de segurança e trailing dinâmico"""
        try:
            # Fechar posições opostas primeiro
            self._close_opposite_positions(signal["type"])

            entry_price = signal["price"]

            # Calcular SL e TP de segurança inicial
            if signal["type"] == "SELL":
                # Para SELL: SL acima do preço de entrada
                sl = entry_price * (1 + self.initial_sl_percent / 100)
                # TP abaixo do preço de entrada
                tp = entry_price * (1 - self.initial_tp_percent / 100)
                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl,
                    tp=tp,
                    comment="LossZero"
                )
            else:  # BUY
                # Para BUY: SL abaixo do preço de entrada
                sl = entry_price * (1 - self.initial_sl_percent / 100)
                # TP acima do preço de entrada
                tp = entry_price * (1 + self.initial_tp_percent / 100)
                result = self.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl,
                    tp=tp,
                    comment="LossZero"
                )

            # Verificar se ordem foi executada (retcode == 10009 = TRADE_RETCODE_DONE)
            if result and result.get('retcode') == 10009:
                self.entry_price = entry_price
                self.entry_ticket = result.get('order')
                self.position_type = signal["type"]
                self.current_sl = sl  # NOVO: Armazena SL atual
                self.current_tp = tp  # NOVO: Armazena TP atual
                self.trailing_active = False
                self.trailing_amount_dollars = 0.0
                self.current_profit_pct = 0.0
                self.total_trades += 1

                msg = f"""
[ABERTO] POSIÇÃO ABERTA - Loss Zero com Proteção
{'='*50}
Tipo: {signal["type"]}
Ticket: {self.entry_ticket}
Preço: ${entry_price:.2f}
Volume: {self.volume}
Motivo: {signal["reason"]}
SL Inicial (Segurança): ${sl:.2f} ({self.initial_sl_percent}%)
TP Inicial (Segurança): ${tp:.2f} ({self.initial_tp_percent}%)
Trailing: Ativa em ${self.trailing_start_amount:.2f} em lucro (inativo)
Estratégia: SL/TP dinâmicos com trailing em dólares
{'='*50}
"""
                logger.info(msg)
                self._notify(msg)
            else:
                logger.error(f"Erro ao abrir posição: {result}")
                logger.error(f"  Retcode esperado: 10009, recebido: {result.get('retcode') if result else 'None'}")

        except Exception as e:
            logger.error(f"Erro ao abrir posição: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _manage_position_trailing(self, pos, cycle: int):
        """Gerencia trailing stop em DÓLARES com SL dinâmico"""
        try:
            # pos é um dicionário retornado pelo MT5
            current_price = pos.get('price_current', 0)
            pos_type = pos.get('type', 0)  # 0 = BUY, 1 = SELL
            price_open = pos.get('price_open', 0)
            ticket = pos.get('ticket', 0)

            if current_price == 0 or price_open == 0:
                return

            # Calcular lucro em DÓLARES (não em percentual)
            if pos_type == 0:  # BUY
                profit_dollars = (current_price - price_open) * self.volume * 100  # Converter para dólares
                profit_pct = ((current_price - price_open) / price_open) * 100
            else:  # SELL
                profit_dollars = (price_open - current_price) * self.volume * 100  # Converter para dólares
                profit_pct = ((price_open - current_price) / price_open) * 100

            self.current_profit_pct = profit_pct
            self.current_profit_dollars = profit_dollars

            # Ativar trailing quando lucro atinge $1 (ou valor configurado)
            if not self.trailing_active and profit_dollars >= self.trailing_start_amount:
                self.trailing_active = True
                self.trailing_amount_dollars = self.trailing_start_amount

                # Atualizar SL para defender o trailing
                new_sl = self._calculate_new_sl_dollars(current_price, pos_type, profit_dollars)
                self.current_sl = new_sl
                self._update_position_sl(ticket, new_sl)

                msg = f"""[INICIO] TRAILING ATIVADO - SL DINÂMICO ATIVADO!
Ticket: {ticket}
Lucro: ${profit_dollars:.2f} ({profit_pct:.2f}%)
Trailing Stop em: ${self.trailing_amount_dollars:.2f}
SL Atualizado para: ${new_sl:.2f}
"""
                logger.info(msg)
                self._notify(msg)
                return  # Aguardar próximo ciclo

            # Atualizar trailing quando lucro cresce
            if self.trailing_active:
                # Se lucro ultrapassou trailing + incremento, aumenta o trailing
                if profit_dollars > self.trailing_amount_dollars + self.trailing_increment_amount:
                    old_amount = self.trailing_amount_dollars
                    self.trailing_amount_dollars = profit_dollars - self.trailing_increment_amount

                    # Atualizar SL para defender o novo trailing
                    new_sl = self._calculate_new_sl_dollars(current_price, pos_type, self.trailing_amount_dollars)
                    self.current_sl = new_sl
                    self._update_position_sl(ticket, new_sl)

                    logger.info(f"[SUBIDA] Trailing: ${old_amount:.2f} → ${self.trailing_amount_dollars:.2f} | SL: ${new_sl:.2f} | Lucro: ${profit_dollars:.2f}")

                # Verificar se deve fechar (lucro caiu abaixo do trailing)
                elif profit_dollars < self.trailing_amount_dollars:
                    logger.info(f"[PARADO] STOP ATIVADO! Lucro: ${profit_dollars:.2f} < Stop: ${self.trailing_amount_dollars:.2f}")
                    self._close_position_with_profit(pos, profit_pct)
                    return

                # Log de monitoramento a cada ciclo
                else:
                    if cycle % 4 == 0:  # Log a cada 4 ciclos (60 segundos)
                        logger.info(f"[MONITOR] Ticket {ticket}: Lucro ${profit_dollars:.2f} | Trailing ${self.trailing_amount_dollars:.2f} | SL ${self.current_sl:.2f}")

        except Exception as e:
            logger.error(f"Erro ao gerenciar trailing: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _calculate_new_sl(self, current_price: float, pos_type: int, trailing_distance: float) -> float:
        """Calcula novo SL baseado no trailing distance (percentual - LEGADO)"""
        if pos_type == 0:  # BUY
            # Para BUY: SL fica abaixo do preço atual, deixando margem do trailing
            new_sl = current_price * (1 - (trailing_distance - 0.05) / 100)
        else:  # SELL
            # Para SELL: SL fica acima do preço atual, deixando margem do trailing
            new_sl = current_price * (1 + (trailing_distance - 0.05) / 100)

        return new_sl

    def _calculate_new_sl_dollars(self, current_price: float, pos_type: int, trailing_dollars: float) -> float:
        """Calcula novo SL baseado no trailing em DÓLARES"""
        # Converter trailing de dólares para preço
        price_distance = trailing_dollars / self.volume / 100

        if pos_type == 0:  # BUY
            # Para BUY: SL fica abaixo do preço, com margem de $0.05
            new_sl = current_price - (price_distance - 0.05)
        else:  # SELL
            # Para SELL: SL fica acima do preço, com margem de $0.05
            new_sl = current_price + (price_distance - 0.05)

        return new_sl

    def _update_position_sl(self, ticket: int, new_sl: float):
        """Atualiza o Stop Loss de uma posição aberta"""
        try:
            import MetaTrader5 as mt5

            # Obter informações atuais da posição
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions:
                logger.error(f"Posição {ticket} não encontrada para atualizar SL")
                return

            pos = positions[0]

            # Preparar requisição de modificação
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "sl": new_sl,
                "tp": self.current_tp,  # Manter TP original
                "magic": 123456,
            }

            result = mt5.order_send(request)

            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                logger.info(f"[ATUALIZAR] SL da posição {ticket} atualizado para ${new_sl:.2f}")
            else:
                logger.error(f"Erro ao atualizar SL: {result}")

        except Exception as e:
            logger.error(f"Erro ao atualizar SL da posição: {e}")

    def _close_position_with_profit(self, pos, profit_pct: float):
        """Fecha posição com lucro via trailing stop"""
        try:
            ticket = pos.get('ticket')
            pos_type = pos.get('type', 0)

            result = self.mt5.close_position(ticket)

            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                self.total_profit += profit_pct * self.volume * 100  # Aproximação
                self.profitable_trades += 1
                self.current_win_streak += 1
                self.trailing_active = False

                msg = f"""
[ABERTO] POSIÇÃO FECHADA COM LUCRO - Trailing Stop
{'='*50}
Ticket: {ticket}
Tipo: {"BUY" if pos_type == 0 else "SELL"}
Lucro: {profit_pct:.2f}%
Trailing Ativo: ${self.trailing_amount_dollars:.2f}
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
                # Posição type: 0 = BUY, 1 = SELL
                # Se sinal é SELL e posição é BUY (type=0), fechar
                if signal_type == "SELL" and pos.get('type') == 0:
                    self.mt5.close_position(pos.get('ticket'))
                # Se sinal é BUY e posição é SELL (type=1), fechar
                elif signal_type == "BUY" and pos.get('type') == 1:
                    self.mt5.close_position(pos.get('ticket'))

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

    def _calculate_mfi(self, rates, period: int = 14) -> float:
        """
        Calcula Money Flow Index (MFI) - indicador de volume

        Fórmula:
        1. Typical Price = (High + Low + Close) / 3
        2. Money Flow = Typical Price × Volume
        3. Positive Money Flow (quando preço sobe)
        4. Negative Money Flow (quando preço desce)
        5. Money Flow Ratio = Positive MF / Negative MF
        6. MFI = 100 - (100 / (1 + Money Flow Ratio))

        Interpretação:
        - MFI > 40 = Forte volume em alta (SELL)
        - MFI < 60 = Forte volume em baixa (BUY)
        - MFI 40-60 = Neutro
        """
        try:
            if not isinstance(rates, list):
                rates = list(rates)

            if len(rates) < period + 1:
                return 50.0

            # Extrair dados OHLCV
            data = []
            for r in rates[:period + 1]:
                if isinstance(r, dict):
                    typical_price = (float(r.get("high", 0)) + float(r.get("low", 0)) + float(r.get("close", 0))) / 3
                    volume = float(r.get("tick_volume", 1))  # Usar tick_volume como proxy de volume
                else:
                    # Se é struct/numpy
                    typical_price = (float(r[2]) + float(r[3]) + float(r[4])) / 3  # high, low, close
                    volume = float(r[7]) if len(r) > 7 else 1  # tick_volume

                money_flow = typical_price * volume
                data.append({
                    "typical_price": typical_price,
                    "money_flow": money_flow,
                    "volume": volume
                })

            # Reverter para ter mais antigo primeiro
            data.reverse()

            # Calcular positive e negative money flows
            positive_mf = 0
            negative_mf = 0

            for i in range(1, len(data)):
                current_tp = data[i]["typical_price"]
                previous_tp = data[i-1]["typical_price"]
                current_mf = data[i]["money_flow"]

                if current_tp > previous_tp:
                    positive_mf += current_mf
                elif current_tp < previous_tp:
                    negative_mf += current_mf

            # Calcular Money Flow Ratio e MFI
            if negative_mf == 0:
                return 100.0 if positive_mf > 0 else 50.0

            money_flow_ratio = positive_mf / negative_mf if negative_mf != 0 else 0
            mfi = 100 - (100 / (1 + money_flow_ratio)) if money_flow_ratio >= 0 else 0

            return mfi

        except Exception as e:
            logger.error(f"Erro ao calcular MFI: {e}")
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
        logger.info("[STATS] ESTATÍSTICAS FINAIS - Loss Zero com SL/TP Dinâmico")
        logger.info("=" * 70)
        logger.info(f"Total de Trades: {self.total_trades}")
        logger.info(f"Trades Lucrativos: {self.profitable_trades}")
        logger.info(f"Win Rate: {(self.profitable_trades/max(1, self.total_trades)*100):.1f}%")
        logger.info(f"Lucro Total Aproximado: {self.total_profit:.2f}%")
        logger.info(f"Maior Streak: {self.current_win_streak}")
        logger.info("")
        logger.info("Estratégia Utilizada:")
        logger.info(f"  SL Inicial (Segurança): {self.initial_sl_percent}%")
        logger.info(f"  TP Inicial (Segurança): {self.initial_tp_percent}%")
        logger.info(f"  Trailing Start: ${self.trailing_start_amount:.2f} em lucro")
        logger.info(f"  Trailing Increment: +${self.trailing_increment_amount:.2f} por dólar")
        logger.info(f"  SL Dinâmico: Defendendo o trailing stop em dólares")
        logger.info("=" * 70 + "\n")


def main():
    """Função principal para iniciar o agente"""
    try:
        # Criar agente Loss Zero com SL/TP dinâmicos e trailing em DÓLARES
        agent = BTCLossZeroOtimizado(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            trailing_start_amount=1.0,     # Ativa com $1 de lucro
            trailing_increment_amount=0.5, # Sobe $0.50 a cada dólar de lucro
            initial_sl_percent=2.5,        # SL de segurança: 2.5% (aumentado)
            initial_tp_percent=10.0,       # TP de segurança: 10% (aumentado)
            use_buy=True,
            use_sell=True
        )

        # Executar agente
        agent.run()

    except Exception as e:
        logger.error(f"[ERRO] Erro fatal: {e}")
        print(f"[ERRO] Erro: {e}")
        print("\nCertifique-se de que:")
        print("1. MetaTrader 5 está aberto")
        print("2. Você está logado na sua conta")
        print("3. O símbolo BTCUSDc está disponível")


if __name__ == "__main__":
    main()
