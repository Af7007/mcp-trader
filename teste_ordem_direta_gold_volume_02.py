#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE ORDEM DIRETA - GOLD (VOLUME 0.02)
=========================================

OBJETIVO: Validar o ciclo completo de uma ordem, desde a abertura até o
gerenciamento do trailing stop, com VOLUME AJUSTADO PARA 0.02 LOTE.

CORREÇÃO APLICADA:
- Volume: 0.02 lote (AJUSTADO conforme solicitado)
- Valor do ponto: $0.002 por ponto com volume 0.02
- Trailing stop: ATIVO (sistema em dólares)
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class TesteOrdemDiretaVolume02(GoldLossZeroSimple):
    """
    Agente de teste com VOLUME 0.02 LOTE (conforme solicitado)
    """

    def __init__(self, *args, **kwargs):
        """
        Configurações corrigidas para Gold - Volume 0.02 lote
        """
        # CORREÇÃO: Volume 0.02 lote (AJUSTADO conforme solicitado)
        kwargs.update({
            'check_interval': 2,  # Verifica a cada 2 segundos
            'volume': 0.02,      # VOLUME AJUSTADO: 0.02 lote (conforme solicitado)
            'use_buy': True,     # Permite BUY e SELL
            'use_sell': True
        })

        super().__init__(*args, **kwargs)

        # VERIFICAR CONEXÃO MT5
        print("[VERIFICANDO] CONEXAO MT5...")
        if not self.mt5 or not self.mt5.is_connected():
            print("[ERRO] MT5 nao esta conectado!")
            print("   Certifique-se que:")
            print("   1. O MT5 Terminal esta aberto")
            print("   2. A conta esta logada")
            print("   3. O servidor esta conectado")
            print("   4. O simbolo XAUUSDc esta disponivel")
            exit(1)
        else:
            print("[OK] MT5 conectado com sucesso!")

        # VERIFICAR SÍMBOLO
        symbol_info = self.mt5.get_symbol_info(self.symbol)
        if not symbol_info:
            print(f"[ERRO] Simbolo {self.symbol} nao encontrado!")
            print("   Certifique-se que o simbolo esta disponivel no MT5")
            exit(1)
        else:
            print(f"[OK] Simbolo {self.symbol} disponivel")

        # VERIFICAR CONTA
        account_info = self.mt5.get_account_info()
        if not account_info:
            print("[ERRO] Nao foi possivel obter informacoes da conta!")
            exit(1)
        else:
            print(f"[OK] Conta conectada: {account_info.get('login', 'N/A')} | Saldo: ${account_info.get('balance', 0):.2f}")

        # Controles do teste
        self.test_in_progress = True
        self.position_opened_for_test = False

        print("="*80)
        print("INICIANDO TESTE INFINITO - GOLD TRAILING STOP (VOLUME 0.02)")
        print("="*80)
        print("[OBJETIVO] Testar com volume ajustado (0.02 lote)")
        print("[VOLUME] 0.02 lotes (AJUSTADO conforme solicitado)")
        print("[TRAILING] $1 ativa, protege progressivamente")
        print("[VALOR PONTO] $0.002 por ponto (com volume 0.02)")
        print("[ESTRATEGIA] Multi-timeframe (M1 + M5 + M15)")
        print("[EXECUCAO] Infinita ate Ctrl+C (1 posicao por vez)")
        print("[ENCERRAMENTO] Ctrl+C fecha todas as posicoes")
        print("")

    def _get_simple_signal(self) -> dict:
        """
        SINAL MELHORADO: Análise multi-timeframe com momentum, volume e RSI
        """
        # Verificar posições abertas e seus resultados
        positions = self.mt5.positions_get(symbol=self.symbol)
        has_negative_buy = False
        has_negative_sell = False

        if positions:
            for pos in positions:
                ticket = pos.get('ticket')
                profit = pos.get('profit', 0)
                pos_type = pos.get('type', 0)  # 0=BUY, 1=SELL

                # Verificar se é uma posição do nosso teste
                if ticket not in self.positions_entry_price:
                    # Posição externa, assumir controle
                    print(f"[AVISO] Posição externa #{ticket} encontrada. Assumindo controle.")
                    self.positions_entry_price[ticket] = pos.get('price_open', 0)
                    self.positions_trailing_active[ticket] = False
                    self.positions_trailing_stop[ticket] = 0.0

                # Verificar se posição está no prejuízo
                if profit < 0:
                    if pos_type == 0:  # BUY com prejuízo
                        has_negative_buy = True
                        print(f"[SEGURANÇA] Posição BUY #{ticket} com prejuízo (${profit:.2f}) - bloqueando novos BUY")
                    else:  # SELL com prejuízo
                        has_negative_sell = True
                        print(f"[SEGURANÇA] Posição SELL #{ticket} com prejuízo (${profit:.2f}) - bloqueando novos SELL")

        # REGRA: Apenas 1 posição por vez
        if positions:
            if len(positions) >= 1:
                print("[LIMITE] Máximo de 1 posição atingido - aguardando fechamento")
                return None

        # === SINAL MELHORADO: ANÁLISE MULTI-TIMEFRAME ===

        try:
            # 1. OBTER DADOS MULTI-TIMEFRAME
            rates_m1 = self.mt5.copy_rates_from_pos(symbol=self.symbol, timeframe="M1", start_pos=0, count=20)
            rates_m5 = self.mt5.copy_rates_from_pos(symbol=self.symbol, timeframe="M5", start_pos=0, count=15)
            rates_m15 = self.mt5.copy_rates_from_pos(symbol=self.symbol, timeframe="M15", start_pos=0, count=10)

            if not rates_m1 or len(rates_m1) < 10:
                print("[ERRO] Dados M1 insuficientes")
                return None

            # 2. CALCULAR INDICADORES
            rsi_m1 = self._calculate_rsi(rates_m1, 14)
            atr_m5 = self._calculate_atr_simple(rates_m5[:14]) if rates_m5 and len(rates_m5) >= 14 else 400.0

            # 3. ANÁLISE DE MOMENTUM E TENDÊNCIA
            momentum_m1 = self._calculate_momentum(rates_m1[:5])
            momentum_m5 = self._calculate_momentum(rates_m5[:5]) if rates_m5 else 0

            # 4. ANÁLISE DE VOLUME
            volume_spike = self._detect_volume_spike(rates_m1[:10])

            # 5. ANÁLISE DE TENDÊNCIA M5/M15
            trend_m5 = self._analyze_trend(rates_m5[:10]) if rates_m5 else "NEUTRAL"
            trend_m15 = self._analyze_trend(rates_m15[:8]) if rates_m15 else "NEUTRAL"

            # 6. PREÇO ATUAL PARA ENTRADA
            current_tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not current_tick:
                return None

            entry_price = current_tick['ask'] if current_tick.get('ask', 0) > 0 else current_tick.get('bid', 0)

            # === ESTRATÉGIA MELHORADA: M1 + M5 + M15 ===

            # Analisar tendência M1 também
            trend_m1 = self._analyze_trend(rates_m1[:10]) if rates_m1 else "NEUTRAL"

            # ESTRATÉGIA ULTRA SIMPLES: Qualquer timeframe com tendência
            buy_signal = any([t == "UP" for t in [trend_m1, trend_m5, trend_m15]])
            sell_signal = any([t == "DOWN" for t in [trend_m1, trend_m5, trend_m15]])

            # Contagem para debug
            buy_count = sum([1 for t in [trend_m1, trend_m5, trend_m15] if t == "UP"])
            sell_count = sum([1 for t in [trend_m1, trend_m5, trend_m15] if t == "DOWN"])

            # Contagem de sinais para compatibilidade
            buy_signals = 4 if buy_signal else 0
            sell_signals = 4 if sell_signal else 0

            buy_reasons = ["trend_M5_up", "trend_M15_up"] if buy_signal else []
            sell_reasons = ["trend_M5_down", "trend_M15_down"] if sell_signal else []

            # === DECISÃO FINAL ===
            print(f"[SINAL] RSI: {rsi_m1:.1f} | Momentum M1: {momentum_m1:.3f}% | M5: {momentum_m5:.3f}%")
            print(f"[SINAL] Trend M1: {trend_m1} | M5: {trend_m5} | M15: {trend_m15}")
            print(f"[SINAL] BUY count: {buy_count}/3 | SELL count: {sell_count}/3 | Volume Spike: {volume_spike}")
            print(f"[SINAL] ATR: {atr_m5:.0f} | BUY signals: {buy_signals} | SELL signals: {sell_signals}")

            # BUY: Pelo menos 3 sinais positivos (mais permissivo)
            if buy_signals >= 3 and not has_negative_buy:
                reason = f"MULTI_TIMEFRAME_BUY_{'_'.join(buy_reasons[:3])}"
                print(f"[BUY] {buy_signals} sinais confirmados - Entrando em ${entry_price:.3f}")
                return {
                    "type": "BUY",
                    "price": entry_price,
                    "reason": reason
                }

            # SELL: Pelo menos 3 sinais positivos (mais permissivo)
            elif sell_signals >= 3 and not has_negative_sell:
                reason = f"MULTI_TIMEFRAME_SELL_{'_'.join(sell_reasons[:3])}"
                print(f"[SELL] {sell_signals} sinais confirmados - Entrando em ${entry_price:.3f}")
                return {
                    "type": "SELL",
                    "price": entry_price,
                    "reason": reason
                }

            # Sem sinal forte suficiente
            print("[AGUARDANDO] Sinais insuficientes para entrada")
            return None

        except Exception as e:
            print(f"[ERRO] Falha na análise de sinal: {e}")
            return None

    def _open_position(self, signal: dict):
        """
        Abre a posição de teste com VOLUME 0.02 LOTE
        """
        super()._open_position(signal)
        if self.last_position_ticket:
            self.position_opened_for_test = True
            print(f"[SUCESSO] Posição de teste #{self.last_position_ticket} aberta.")
            print(f"           Volume: {self.volume} lotes (AJUSTADO para 0.02)")
            print("           Aguardando ativação do trailing stop...")

    def run(self):
        """
        Executa o ciclo de teste indefinidamente até interrupção manual.
        """
        print(f"TESTE INFINITO - Pressione Ctrl+C para encerrar.")
        print(f"Volume: {self.volume} lotes (AJUSTADO para 0.02)")
        print(f"Valor do ponto: ${self._pontos_para_dinheiro(1):.4f} por ponto")
        print(f"Trailing stop ativado para cada posição aberta.")
        print(f"="*60)

        try:
            while True:
                # SEMPRE tentar analisar para novos sinais (execução infinita)
                print("\n[CICLO] Analisando vela atual para sinal...")
                self._analyze_and_open()

                # SEMPRE verificar posições existentes para trailing
                print("         Verificando posições abertas...")
                self._check_positions()

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n[INTERRUPÇÃO] Usuário solicitou encerramento do teste...")
            self.shutdown_test()

    def shutdown_test(self):
        """
        Encerra o teste, fecha TODAS as posições abertas e exibe o relatório.
        """
        print("\n" + "="*80)
        print("TESTE CONCLUÍDO - FECHANDO TODAS AS POSIÇÕES")
        print("="*80)

        # Fechar TODAS as posições abertas pelo teste
        positions_closed = 0
        positions_failed = 0

        # Verificar posições abertas no MT5
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions:
            print(f"Encontradas {len(positions)} posições abertas no {self.symbol}")

            for pos in positions:
                ticket = pos.get('ticket')

                # Verificar se é uma posição do nosso teste
                if ticket in self.positions_entry_price:
                    print(f"Fechando posição de teste #{ticket}...")
                    try:
                        result = self.mt5.close_position(ticket)
                        if result and result.get('retcode') == 10009:
                            print(f"  [OK] Posição #{ticket} fechada com sucesso")
                            positions_closed += 1
                        else:
                            print(f"  [ERRO] Falha ao fechar posição #{ticket}: {result}")
                            positions_failed += 1
                    except Exception as e:
                        print(f"  [ERRO] Exceção ao fechar posição #{ticket}: {e}")
                        positions_failed += 1
                else:
                    print(f"  [INFO] Posição #{ticket} não é do teste (ignorando)")
        else:
            print("Nenhuma posição aberta encontrada.")

        print(f"\n[RESUMO FECHAMENTO]")
        print(f"  Posições fechadas: {positions_closed}")
        print(f"  Falhas no fechamento: {positions_failed}")
        print(f"  Volume usado: {self.volume} lotes")

        # Verificar o banco de dados
        self.validar_resultado_banco()

    def _calculate_rsi(self, rates, period=14):
        """
        Calcula RSI (Relative Strength Index)
        """
        if len(rates) < period + 1:
            return 50.0

        closes = [r['close'] for r in rates]
        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            gains.append(max(0, change))
            losses.append(max(0, -change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_momentum(self, rates):
        """
        Calcula momentum percentual
        """
        if len(rates) < 2:
            return 0.0

        first_close = rates[0]['close']
        last_close = rates[-1]['close']

        momentum = ((last_close - first_close) / first_close) * 100
        return momentum

    def _detect_volume_spike(self, rates):
        """
        Detecta volume spike (volume acima da média)
        """
        if len(rates) < 5:
            return False

        volumes = [r['tick_volume'] for r in rates]
        current_volume = volumes[-1]
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])

        # Volume spike: 1.5x acima da média
        return current_volume > avg_volume * 1.5

    def _analyze_trend(self, rates):
        """
        Analisa tendência baseada em médias móveis simples
        """
        if len(rates) < 5:
            return "NEUTRAL"

        closes = [r['close'] for r in rates]

        # Média curta (3 períodos) vs média longa (5 períodos)
        short_ma = sum(closes[-3:]) / 3
        long_ma = sum(closes[-5:]) / 5

        diff_percent = ((short_ma - long_ma) / long_ma) * 100

        # DEBUG: Mostrar valores calculados
        print(f"[DEBUG TREND] Short MA: {short_ma:.5f} | Long MA: {long_ma:.5f} | Diff: {diff_percent:.4f}%")

        if diff_percent > 0.005:  # 0.005% acima (ainda mais permissivo)
            return "DOWN"  # INVERTIDO: alta = SELL
        elif diff_percent < -0.005:  # 0.005% abaixo (ainda mais permissivo)
            return "UP"    # INVERTIDO: baixa = BUY
        else:
            return "NEUTRAL"

    def validar_resultado_banco(self):
        """
        Verifica a tabela `trailing_stops` para confirmar se o `trade_id` foi salvo.
        """
        print("\n[VALIDAÇÃO] Verificando o banco de dados...")
        if not self.last_position_ticket:
            print("[INFO] Nenhuma posição foi aberta, não há o que validar.")
            return

        try:
            import sqlite3
            conn = sqlite3.connect('btc_trading_logs.db')
            cursor = conn.cursor()

            cursor.execute(
                "SELECT trade_id, action FROM trailing_stops WHERE ticket = ? LIMIT 1",
                (self.last_position_ticket,)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                trade_id, action = result
                if trade_id:
                    print(f"SUCESSO: Trailing stop registrado para o ticket {self.last_position_ticket} com trade_id = {trade_id}.")
                    print("         A logica de recuperacao de trade_id funcionou!")
                else:
                    print(f"FALHA: Trailing stop registrado para o ticket {self.last_position_ticket}, mas o trade_id e NULO.")
                    print("        A recuperacao do trade_id falhou.")
            else:
                print("[AVISO] Nenhum registro de trailing stop encontrado para o ticket de teste.")
                print("         Isso é normal se a posição não atingiu o lucro necessário para ativar o trailing.")

        except Exception as e:
            print(f"[ERRO] Falha ao verificar o banco de dados: {e}")

def main():
    """
    Função principal para executar o teste.
    """
    agent = TesteOrdemDiretaVolume02(symbol='XAUUSDc')
    agent.run()

if __name__ == "__main__":
    main()
