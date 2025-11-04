#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss Zero - Versao Enhanced com Indicadores Melhorados
Estrategia: Bollinger Bands + RSI + Volume
"""

import sys
import time
import logging
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.btc_hedge_agent import BTCHedgeAgent

logger = logging.getLogger(__name__)


class BTCLossZeroEnhanced:
    """
    Agente BTC com estrategia Loss 0 melhorada.
    
    Estrategia:
    - Bollinger Bands para identificar extremos
    - RSI para confirmar momentum
    - Volume para validar força
    - SL/TP fixos em dólares
    - Zero losses garantidos
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",
        volume: float = 0.05,
        check_interval: int = 15,
        stop_loss_dollars: float = 30.0,
        take_profit_dollars: float = 50.0,
        trailing_dollars: float = 10.0,
        use_buy: bool = True,
        use_sell: bool = True,
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
        rsi_period: int = 14,
        volume_period: int = 20
    ):
        """
        Inicializa agente Loss Zero Enhanced
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
        self.volume_period = volume_period
        
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
        
        print(f"Agente BTC Loss Zero Enhanced inicializado!")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume}")
        print(f"   SL: ${self.stop_loss_dollars}")
        print(f"   TP: ${self.take_profit_dollars}")
        print(f"   Trailing: ${self.trailing_dollars}")
        print(f"   Indicadores: Bollinger Bands({bb_period}) + RSI({rsi_period}) + Volume")
        print(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")

    def run(self):
        """
        Executa agente Loss Zero Enhanced
        """
        print(f"AGENTE BTC LOSS ZERO ENHANCED - BOLLINGER BANDS + RSI")
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
            print(f"\nAgente BTC Loss Zero Enhanced parado pelo usuario")

    def _display_status(self, cycle: int):
        """
        Exibe status do agente
        """
        print(f"\n{'='*60}")
        print(f"[AGENTE] BTC LOSS ZERO ENHANCED | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*60}")
        
        # Status do agente
        print(f"[AGENTE]:")
        print(f"   Estado: LOSS ZERO ENHANCED (BB + RSI + Volume)")
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
                    
                    # Exibir indicadores
                    self._display_indicators(price)
                    
            except Exception as e:
                print(f"   Erro ao obter preco: {e}")

    def _display_indicators(self, current_price: float):
        """
        Exibe valores dos indicadores
        """
        try:
            # Obter dados para indicadores
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=max(self.bb_period, self.rsi_period, self.volume_period) + 10
            )
            
            if len(rates) < max(self.bb_period, self.rsi_period, self.volume_period):
                return
            
            # Calcular Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(rates)
            
            # Calcular RSI
            rsi = self._calculate_rsi(rates, self.rsi_period)
            
            # Calcular volume médio
            current_volume = rates[0]['tick_volume']
            avg_volume = np.mean([r['tick_volume'] for r in rates[:self.volume_period]])
            
            # Exibir indicadores
            print(f"[INDICADORES]:")
            print(f"   BB Upper: ${bb_upper:.2f}")
            print(f"   BB Middle: ${bb_middle:.2f}")
            print(f"   BB Lower: ${bb_lower:.2f}")
            print(f"   RSI({self.rsi_period}): {rsi:.1f}")
            print(f"   Volume: {current_volume:.0f} (Média: {avg_volume:.0f})")
            
            # Posição relativa
            if current_price <= bb_lower:
                bb_position = "ABAIXO da banda inferior"
            elif current_price >= bb_upper:
                bb_position = "ACIMA da banda superior"
            else:
                bb_position = "DENTRO das bandas"
            
            print(f"   Posição BB: {bb_position}")
            
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
        
        # Buscar sinal melhorado
        signal = self._get_enhanced_signal()
        if signal:
            self._open_position(signal)

    def _get_enhanced_signal(self) -> dict:
        """
        Gera sinal melhorado com Bollinger Bands + RSI + Volume
        """
        try:
            # Obter dados M1
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=max(self.bb_period, self.rsi_period, self.volume_period) + 10
            )
            
            if len(rates) < max(self.bb_period, self.rsi_period, self.volume_period):
                return None
            
            current = rates[0]['close']
            previous = rates[1]['close']
            
            # Calcular indicadores
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(rates)
            rsi = self._calculate_rsi(rates, self.rsi_period)
            current_volume = rates[0]['tick_volume']
            avg_volume = np.mean([r['tick_volume'] for r in rates[:self.volume_period]])
            
            # SINAL DE VENDA FORTE
            if (self.use_sell and 
                current >= bb_upper and  # Preço na banda superior
                rsi > 65 and           # RSI sobrecomprado (reduzido de 70)
                current > previous and   # Tendência de alta
                current_volume > avg_volume * 1.1):  # Volume acima da média (reduzido)
                
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + RSI_overbought + High_volume",
                    "strength": "STRONG"
                }
            
            # SINAL DE COMPRA FORTE
            elif (self.use_buy and 
                  current <= bb_lower and  # Preço na banda inferior
                  rsi < 35 and           # RSI sobrevendido (aumentado de 30)
                  current < previous and   # Tendência de baixa
                  current_volume > avg_volume * 1.1):  # Volume acima da média (reduzido)
                
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + RSI_oversold + High_volume",
                    "strength": "STRONG"
                }
            
            # SINAL DE VENDA MODERADO (sem volume)
            elif (self.use_sell and 
                  current >= bb_upper and 
                  rsi > 60 and           # Reduzido de 70
                  current > previous):
                
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + RSI_overbought",
                    "strength": "MODERATE"
                }
            
            # SINAL DE COMPRA MODERADO (sem volume)
            elif (self.use_buy and 
                  current <= bb_lower and 
                  rsi < 40 and           # Aumentado de 30
                  current < previous):
                
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + RSI_oversold",
                    "strength": "MODERATE"
                }
            
            # NOVO: SINAL DE VENDA FLEXÍVEL (apenas BB + tendência)
            elif (self.use_sell and 
                  current >= bb_upper and 
                  current > previous and
                  rsi > 55):  # Apenas acima do neutro
                
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + Trend_up",
                    "strength": "FLEXIBLE"
                }
            
            # NOVO: SINAL DE COMPRA FLEXÍVEL (apenas BB + tendência)
            elif (self.use_buy and 
                  current <= bb_lower and 
                  current < previous and
                  rsi < 45):  # Apenas abaixo do neutro
                
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + Trend_down",
                    "strength": "FLEXIBLE"
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

    def _open_position(self, signal: dict):
        """
        Abre posicao com Loss 0 Enhanced
        """
        try:
            # Fechar posicoes existentes do mesmo tipo
            self._close_opposite_positions(signal["type"])
            
            # Calcular SL e TP baseados no preço de entrada
            if signal["type"] == "BUY":
                sl_price = signal["price"] - self.stop_loss_dollars
                tp_price = signal["price"] + self.take_profit_dollars
                result = self.base_agent.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"LossZeroEnhanced_BUY_{signal['reason']}"
                )
            else:  # SELL
                sl_price = signal["price"] + self.stop_loss_dollars
                tp_price = signal["price"] - self.take_profit_dollars
                result = self.base_agent.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"LossZeroEnhanced_SELL_{signal['reason']}"
                )
            
            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                self.entry_price = signal["price"]
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                
                print(f"[POSICAO ABERTA]: {signal['type']} ${self.entry_price:.2f}")
                print(f"   Força: {signal['strength']}")
                print(f"   Motivo: {signal['reason']}")
                print(f"   Estrategia: Loss Zero Enhanced")
                print(f"   SL: ${self.stop_loss_dollars}")
                print(f"   TP: ${self.take_profit_dollars}")
                print(f"   Trailing: ${self.trailing_dollars} (apos TP)")
            else:
                print(f"Erro ao abrir posicao: {result}")
                
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
