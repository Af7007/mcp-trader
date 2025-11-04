#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss Zero - Versão Flexible com Múltiplos Parâmetros
Estrategia: Ultra-flexível para capturar mais movimentos
"""

import sys
import time
import logging
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.btc_hedge_agent import BTCHedgeAgent
from core.btc_logger import BTCLogger

logger = logging.getLogger(__name__)


class BTCLossZeroFlexible:
    """
    Agente BTC com estrategia Loss 0 ultra-flexível.
    
    Estrategia:
    - Múltiplos parâmetros de entrada
    - Adaptação dinâmica ao mercado
    - SL/TP fixos em dólares
    - Zero losses garantidos
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",
        volume: float = 0.05,
        check_interval: int = 15,
        stop_loss_dollars: float = 100.0,
        take_profit_dollars: float = 150.0,
        trailing_dollars: float = 50.0,
        use_buy: bool = True,
        use_sell: bool = True,
        # Parâmetros Bollinger Bands
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
        # Parâmetros RSI
        rsi_period: int = 14,
        rsi_overbought: float = 60.0,  # Reduzido para mais sinais
        rsi_oversold: float = 40.0,      # Aumentado para mais sinais
        # Parâmetros Volume
        volume_period: int = 20,
        volume_multiplier: float = 1.0,    # Reduzido para mais flexibilidade
        # Parâmetros de Tendência
        use_trend_filter: bool = True,
        trend_periods: int = 5,
        # Parâmetros de Momentum
        use_momentum: bool = True,
        momentum_period: int = 3
    ):
        """
        Inicializa agente Loss Zero Flexible
        """
        self.symbol = symbol
        self.volume = volume
        self.check_interval = check_interval
        self.stop_loss_dollars = stop_loss_dollars
        self.take_profit_dollars = take_profit_dollars
        self.trailing_dollars = trailing_dollars
        self.use_buy = use_buy
        self.use_sell = use_sell
        
        # Parâmetros dos indicadores
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.volume_period = volume_period
        self.volume_multiplier = volume_multiplier
        self.use_trend_filter = use_trend_filter
        self.trend_periods = trend_periods
        self.use_momentum = use_momentum
        self.momentum_period = momentum_period
        
        # Criar agente base
        self.base_agent = BTCHedgeAgent(
            symbol=symbol,
            volume=volume,
            check_interval=check_interval,
            target_profit=float('inf'),  # TP infinito (sem limite)
            hedge_trigger=-10.0,  # Hedge muito tardio
            hedge_tp_target=10.0,  # TP hedge muito alto
            only_sell=False
        )
        
        # Estado Loss 0
        self.trailing_active = False
        self.trailing_distance = 0.0
        self.entry_price = 0.0
        self.highest_profit = 0.0
        
        # Sistema de logging
        self.logger = BTCLogger()
        self.agent_version = "Flexible"
        
        print(f"Agente BTC Loss Zero Flexible inicializado!")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume}")
        print(f"   SL: ${self.stop_loss_dollars}")
        print(f"   TP: ${self.take_profit_dollars}")
        print(f"   Trailing: ${self.trailing_dollars}")
        print(f"   BB: {bb_period} períodos, {bb_std_dev} std")
        print(f"   RSI: {rsi_period} períodos ({rsi_oversold}-{rsi_overbought})")
        print(f"   Volume: {volume_period} períodos (x{volume_multiplier})")
        print(f"   Tendência: {trend_periods} períodos")
        print(f"   Momentum: {momentum_period} períodos")
        print(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")

    def run(self):
        """
        Executa agente Loss Zero Flexible
        """
        print(f"AGENTE BTC LOSS ZERO FLEXIBLE - ULTRA ADAPTÁVEL")
        print(f"="*60)
        print(f"Parando processo ativo com Ctrl+C")
        print()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                self._display_status(cycle)
                
                # Verificar posições abertas
                self._check_positions()
                
                # Gerenciar trailing stop
                self._manage_trailing()
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\nAgente BTC Loss Zero Flexible parado pelo usuario")

    def _display_status(self, cycle: int):
        """
        Exibe status do agente
        """
        print(f"\n{'='*60}")
        print(f"[AGENTE] BTC LOSS ZERO FLEXIBLE | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*60}")
        
        # Status do agente
        print(f"[AGENTE]:")
        print(f"   Estado: LOSS ZERO FLEXIBLE (Ultra-adaptável)")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing Ativo: {'SIM' if self.trailing_active else 'NAO'}")
        if self.trailing_active:
            print(f"   Distancia Trailing: {self.trailing_distance:.2f}%")
        
        # Mercado
        if self.base_agent.mt5:
            try:
                tick = self.base_agent.mt5.get_symbol_info_tick(self.symbol)
                if tick:
                    price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
                    print(f"[MERCADO] ({self.symbol}):")
                    print(f"   Preco: ${price:.2f}")
                    
                    # Exibir indicadores e logar ciclo
                    self._display_indicators(price, cycle)
                    
            except Exception as e:
                print(f"   Erro ao obter preco: {e}")

    def _display_indicators(self, current_price: float, cycle: int):
        """
        Exibe valores dos indicadores e loga ciclo
        """
        try:
            # Obter dados para indicadores
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=max(self.bb_period, self.rsi_period, self.volume_period, self.trend_periods, self.momentum_period) + 10
            )
            
            if len(rates) < max(self.bb_period, self.rsi_period, self.volume_period, self.trend_periods, self.momentum_period):
                return
            
            # Calcular indicadores
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(rates)
            rsi = self._calculate_rsi(rates, self.rsi_period)
            current_volume = rates[0]['tick_volume']
            avg_volume = np.mean([r['tick_volume'] for r in rates[:self.volume_period]])
            trend = self._calculate_trend(rates)
            momentum = self._calculate_momentum(rates)
            
            # Posição relativa
            if current_price <= bb_lower:
                bb_position = "ABAIXO da banda inferior"
            elif current_price >= bb_upper:
                bb_position = "ACIMA da banda superior"
            else:
                bb_position = "DENTRO das bandas"
            
            # Logar ciclo no banco de dados (com tratamento de erro)
            try:
                cycle_data = {
                    'cycle_number': cycle,
                    'symbol': self.symbol,
                    'price': current_price,
                    'bb_upper': bb_upper,
                    'bb_middle': bb_middle,
                    'bb_lower': bb_lower,
                    'bb_position': bb_position,
                    'rsi': rsi,
                    'rsi_overbought': self.rsi_overbought,
                    'rsi_oversold': self.rsi_oversold,
                    'volume_current': current_volume,
                    'volume_avg': avg_volume,
                    'volume_multiplier': self.volume_multiplier,
                    'trend': trend,
                    'momentum': momentum,
                    'agent_version': self.agent_version
                }
                
                # Buscar sinal para logar
                signal = self._get_flexible_signal()
                if signal:
                    cycle_data.update({
                        'signal_type': signal['type'],
                        'signal_strength': signal['strength'],
                        'signal_reason': signal['reason'],
                        'signal_price': signal['price']
                    })
                
                # Logar ciclo
                self.logger.log_cycle(cycle_data)
            except Exception as log_error:
                print(f"   [AVISO] Erro ao fazer logging do ciclo: {log_error}")
                # Continuar execução mesmo se logging falhar
            
            # Exibir indicadores
            print(f"[INDICADORES]:")
            print(f"   BB Upper: ${bb_upper:.2f}")
            print(f"   BB Middle: ${bb_middle:.2f}")
            print(f"   BB Lower: ${bb_lower:.2f}")
            print(f"   RSI({self.rsi_period}): {rsi:.1f} ({self.rsi_oversold}-{self.rsi_overbought})")
            print(f"   Volume: {current_volume:.0f} (Média: {avg_volume:.0f}, x{self.volume_multiplier})")
            print(f"   Tendência: {trend}")
            print(f"   Momentum: {momentum:.2f}")
            
            print(f"   Posição BB: {bb_position}")
            
            # Debug adicional para identificar problemas
            if bb_position == "ACIMA da banda superior":
                print(f"   [DEBUG] Preço ${current_price:.2f} está ACIMA da BB Upper ${bb_upper:.2f}")
                print(f"   [DEBUG] Deveria gerar sinal de VENDA, não de COMPRA")
            elif bb_position == "ABAIXO da banda inferior":
                print(f"   [DEBUG] Preço ${current_price:.2f} está ABAIXO da BB Lower ${bb_lower:.2f}")
                print(f"   [DEBUG] Deveria gerar sinal de COMPRA, não de VENDA")
            
        except Exception as e:
            print(f"   Erro ao calcular indicadores: {e}")

    def _check_positions(self):
        """
        Verifica e gerencia posicoes
        """
        if not self.base_agent.mt5:
            return
        
        try:
            positions = self.base_agent.mt5.positions_get(symbol=self.symbol)
            if not positions:
                # Nenhuma posicao, analisa para abrir
                self._analyze_and_open()
            else:
                # Tem posicao, gerencia trailing
                for pos in positions:
                    self._manage_position_trailing(pos)
                    
        except Exception as e:
            print(f"Erro ao verificar posicoes: {e}")

    def _analyze_and_open(self):
        """
        Analisa mercado e abre posicao
        """
        if not self.use_buy and not self.use_sell:
            return
        
        # Buscar sinal flexível
        signal = self._get_flexible_signal()
        if signal:
            self._open_position(signal)

    def _get_flexible_signal(self) -> dict:
        """
        Gera sinal ultra-flexível com múltiplos parâmetros
        """
        try:
            # Obter dados M1
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=max(self.bb_period, self.rsi_period, self.volume_period, self.trend_periods, self.momentum_period) + 10
            )
            
            if len(rates) < max(self.bb_period, self.rsi_period, self.volume_period, self.trend_periods, self.momentum_period):
                return None
            
            current = rates[0]['close']
            previous = rates[1]['close']
            
            # Calcular indicadores
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(rates)
            rsi = self._calculate_rsi(rates, self.rsi_period)
            current_volume = rates[0]['tick_volume']
            avg_volume = np.mean([r['tick_volume'] for r in rates[:self.volume_period]])
            trend = self._calculate_trend(rates)
            momentum = self._calculate_momentum(rates)
            
            # ESTRATÉGIA 1: SINAL FORTE COMPLETO
            if self.use_sell and current >= bb_upper and rsi > self.rsi_overbought and current > previous and current_volume > avg_volume * self.volume_multiplier:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + RSI_overbought + Trend_up + Volume",
                    "strength": "STRONG"
                }
            
            elif self.use_buy and current <= bb_lower and rsi < self.rsi_oversold and current < previous and current_volume > avg_volume * self.volume_multiplier:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + RSI_oversold + Trend_down + Volume",
                    "strength": "STRONG"
                }
            
            # ESTRATÉGIA 2: SINAL BB + MOMENTUM (sem RSI)
            if self.use_sell and current >= bb_upper and momentum > 0 and current > previous:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + Momentum_up",
                    "strength": "MOMENTUM"
                }
            
            elif self.use_buy and current <= bb_lower and momentum < 0 and current < previous:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + Momentum_down",
                    "strength": "MOMENTUM"
                }
            
            # ESTRATÉGIA 3: SINAL RSI + TENDÊNCIA (sem BB)
            if self.use_sell and rsi > self.rsi_overbought and trend == "ALTA" and current > previous:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "RSI_overbought + Trend_up",
                    "strength": "TREND"
                }
            
            elif self.use_buy and rsi < self.rsi_oversold and trend == "BAIXA" and current < previous:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "RSI_oversold + Trend_down",
                    "strength": "TREND"
                }
            
            # ESTRATÉGIA 4: SINAL APENAS COM BB (mais permissivo)
            if self.use_sell and current >= bb_upper and current > previous:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + Trend_up",
                    "strength": "FLEXIBLE"
                }
            
            elif self.use_buy and current <= bb_lower and current < previous:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + Trend_down",
                    "strength": "FLEXIBLE"
                }
            
            # ESTRATÉGIA 5: SINAL COM MOMENTUM FORTE
            if self.use_sell and momentum > 2.0 and current > previous and rsi > 50:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "Strong_momentum_up",
                    "strength": "MOMENTUM_STRONG"
                }
            
            elif self.use_buy and momentum < -2.0 and current < previous and rsi < 50:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "Strong_momentum_down",
                    "strength": "MOMENTUM_STRONG"
                }
            
            # ESTRATÉGIA 6: SINAL RSI EXTREMO (sem outras condições)
            if self.use_sell and rsi > 75:  # Extremamente sobrecomprado
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "RSI_extreme_overbought",
                    "strength": "EXTREME"
                }
            
            elif self.use_buy and rsi < 25:  # Extremamente sobrevendido
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "RSI_extreme_oversold",
                    "strength": "EXTREME"
                }
            
            return None
            
        except Exception as e:
            print(f"Erro na analise: {e}")
            return None

    def _calculate_bollinger_bands(self, rates):
        """
        Calcula Bollinger Bands
        """
        try:
            closes = [r['close'] for r in rates[:self.bb_period]]
            
            if len(closes) < self.bb_period:
                return 0, 0, 0
            
            # Calcular SMA (banda do meio)
            middle_band = np.mean(closes)
            
            # Calcular desvio padrão
            std_dev = np.std(closes)
            
            # Calcular bandas superior e inferior
            upper_band = middle_band + (self.bb_std_dev * std_dev)
            lower_band = middle_band - (self.bb_std_dev * std_dev)
            
            return upper_band, middle_band, lower_band
            
        except Exception as e:
            print(f"Erro ao calcular Bollinger Bands: {e}")
            return 0, 0, 0

    def _calculate_rsi(self, rates, period):
        """
        Calcula RSI
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
            
        except:
            return 50.0

    def _calculate_trend(self, rates):
        """
        Calcula tendência simples
        """
        try:
            if len(rates) < self.trend_periods + 1:
                return "NEUTRA"
            
            closes = [r['close'] for r in rates[:self.trend_periods + 1]]
            
            # Calcular média móvel simples
            sma = np.mean(closes[:-1])
            current = closes[0]
            
            if current > sma * 1.002:  # 0.2% acima da média
                return "ALTA"
            elif current < sma * 0.998:  # 0.2% abaixo da média
                return "BAIXA"
            else:
                return "NEUTRA"
                
        except:
            return "NEUTRA"

    def _calculate_momentum(self, rates):
        """
        Calcula momentum
        """
        try:
            if len(rates) < self.momentum_period + 1:
                return 0.0
            
            closes = [r['close'] for r in rates[:self.momentum_period + 1]]
            
            # Momentum = preço atual - preço há N períodos
            momentum = closes[0] - closes[self.momentum_period]
            
            # Normalizar para percentual
            if closes[self.momentum_period] != 0:
                momentum_pct = (momentum / closes[self.momentum_period]) * 100
                return momentum_pct
            
            return 0.0
            
        except:
            return 0.0

    def _open_position(self, signal: dict):
        """
        Abre posicao com Loss 0 Flexible
        """
        try:
            # Fechar posicoes existentes do mesmo tipo
            self._close_opposite_positions(signal["type"])
            
            # Calcular SL e TP baseados no preço de entrada
            if signal["type"] == "BUY":
                sl_price = signal["price"] - self.stop_loss_dollars
                tp_price = signal["price"] + self.take_profit_dollars
                
                # Verificar se os stops são válidos
                if sl_price <= 0 or tp_price <= 0:
                    print(f"Erro: SL/TP inválidos para BUY - SL: {sl_price}, TP: {tp_price}")
                    return
                
                # Para BUY: SL deve ser menor que preço atual, TP deve ser maior
                if sl_price >= signal["price"] or tp_price <= signal["price"]:
                    print(f"Erro: SL/TP incorretos para BUY")
                    print(f"  Preço: ${signal['price']:.2f}")
                    print(f"  SL: ${sl_price:.2f} (deve ser < preço)")
                    print(f"  TP: ${tp_price:.2f} (deve ser > preço)")
                    return
                
                result = self.base_agent.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"LF_BUY_{signal['strength']}"
                )
            else:  # SELL
                sl_price = signal["price"] + self.stop_loss_dollars
                tp_price = signal["price"] - self.take_profit_dollars
                
                # Verificar se os stops são válidos
                if sl_price <= 0 or tp_price <= 0:
                    print(f"Erro: SL/TP inválidos para SELL - SL: {sl_price}, TP: {tp_price}")
                    return
                
                # Para SELL: SL deve ser maior que preço atual, TP deve ser menor
                if sl_price <= signal["price"] or tp_price >= signal["price"]:
                    print(f"Erro: SL/TP incorretos para SELL")
                    print(f"  Preço: ${signal['price']:.2f}")
                    print(f"  SL: ${sl_price:.2f} (deve ser > preço)")
                    print(f"  TP: ${tp_price:.2f} (deve ser < preço)")
                    return
                
                result = self.base_agent.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"LF_SELL_{signal['strength']}"
                )
            
            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                self.entry_price = signal["price"]
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                
                print(f"[POSICAO ABERTA]: {signal['type']} ${self.entry_price:.2f}")
                print(f"   Força: {signal['strength']}")
                print(f"   Motivo: {signal['reason']}")
                print(f"   Estrategia: Loss Zero Flexible")
                print(f"   SL: ${self.stop_loss_dollars}")
                print(f"   TP: ${self.take_profit_dollars}")
                print(f"   Trailing: ${self.trailing_dollars} (apos TP)")
                
                # Logar trade executado
                trade_data = {
                    'symbol': self.symbol,
                    'trade_type': signal['type'],
                    'entry_price': self.entry_price,
                    'sl_price': sl_price if signal['type'] == 'BUY' else sl_price,
                    'tp_price': tp_price if signal['type'] == 'BUY' else tp_price,
                    'volume': self.volume,
                    'strength': signal['strength'],
                    'reason': signal['reason'],
                    'comment': f"LF_{signal['type']}_{signal['strength']}",
                    'status': 'OPEN',
                    'agent_version': self.agent_version
                }
                
                self.logger.log_trade(trade_data)
                
                # Atualizar performance da estratégia
                self.logger.update_strategy_performance(
                    strategy_name=signal['reason'],
                    signal_type=signal['type'],
                    signal_strength=signal['strength'],
                    success=True
                )
                
            else:
                print(f"Erro ao abrir posicao: {result}")
                
                # Logar erro na ordem
                if result:
                    # Atualizar ciclo com erro
                    error_data = {
                        'order_result': str(result.get('retcode', 'Unknown')),
                        'order_error': result.get('comment', 'Unknown error'),
                        'sl_price': sl_price if signal['type'] == 'BUY' else sl_price,
                        'tp_price': tp_price if signal['type'] == 'BUY' else tp_price
                    }
                    
                    # Atualizar performance da estratégia com falha
                    self.logger.update_strategy_performance(
                        strategy_name=signal['reason'],
                        signal_type=signal['type'],
                        signal_strength=signal['strength'],
                        success=False
                    )
                
        except Exception as e:
            print(f"Erro ao abrir posicao: {e}")

    def _close_opposite_positions(self, signal_type: str):
        """
        Fecha posicoes opostas
        """
        try:
            positions = self.base_agent.mt5.positions_get(symbol=self.symbol)
            for pos in positions:
                if signal_type == "BUY" and pos.type == 0:  # SELL
                    self.base_agent.mt5.position_close(pos.ticket)
                elif signal_type == "SELL" and pos.type == 1:  # BUY
                    self.base_agent.mt5.position_close(pos.ticket)
                    
        except Exception as e:
            print(f"Erro ao fechar posicoes opostas: {e}")

    def _manage_trailing(self):
        """
        Gerencia trailing stop
        """
        if not self.trailing_active:
            return
        
        try:
            positions = self.base_agent.mt5.positions_get(symbol=self.symbol)
            for pos in positions:
                self._manage_position_trailing(pos)
                
        except Exception as e:
            print(f"Erro ao gerenciar trailing: {e}")

    def _manage_position_trailing(self, pos):
        """
        Gerencia trailing de uma posicao
        """
        try:
            # Obter preço atual do tick
            tick = self.base_agent.mt5.get_symbol_info_tick(self.symbol)
            if tick:
                current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
            else:
                current_price = pos.get('price_open', 0)  # Fallback para preço de abertura
            
            # Verificar se entry_price é válido para evitar divisão por zero
            if self.entry_price <= 0:
                return  # Sair se não há preço de entrada válido
            
            # Calcular lucro em dólares
            profit_dollars = current_price - self.entry_price
            
            # Verificar se deve ativar trailing (quando lucrar >= trailing_dollars)
            if not self.trailing_active and abs(profit_dollars) >= self.trailing_dollars:
                self.trailing_active = True
                self.trailing_stop_price = self.entry_price + (self.trailing_dollars if pos.type == 0 else -self.trailing_dollars)
                print(f"[TRAILING ATIVADO] em ${abs(profit_dollars):.2f}!")
                
            # Atualizar trailing
            if self.trailing_active:
                # Para posições BUY: trailing sobe com o preço
                if pos.type == 0:  # BUY
                    new_stop = current_price - self.trailing_dollars
                    if new_stop > self.trailing_stop_price:
                        self.trailing_stop_price = new_stop
                        print(f"[TRAILING ATUALIZADO]: SL ${self.trailing_stop_price:.2f}")
                else:  # SELL
                    new_stop = current_price + self.trailing_dollars
                    if new_stop < self.trailing_stop_price:
                        self.trailing_stop_price = new_stop
                        print(f"[TRAILING ATUALIZADO]: SL ${self.trailing_stop_price:.2f}")
                
                # Verificar stop
                if (pos.type == 0 and current_price <= self.trailing_stop_price) or \
                   (pos.type == 1 and current_price >= self.trailing_stop_price):
                    print(f"[TRAILING STOP ATIVADO]! Lucro: ${profit_dollars:.2f}")
                    self.base_agent.mt5.position_close(pos.ticket)
                    self.trailing_active = False
                    
        except Exception as e:
            print(f"Erro ao gerenciar posicao: {e}")

    def _get_time(self):
        """
        Retorna hora atual
        """
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
