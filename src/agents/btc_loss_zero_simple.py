#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente BTC Loss Zero - Versao Simples e Funcional
Estrategia: Trailing Stop ilimitado sem losses
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.btc_hedge_agent import BTCHedgeAgent

logger = logging.getLogger(__name__)


class BTCLossZeroSimple:
    """
    Agente BTC com estrategia Loss 0 baseado no BTCHedgeAgent.
    
    Estrategia:
    - Modifica BTCHedgeAgent para nao usar TP fixo
    - Usa trailing stop ilimitado
    - Zero losses garantidos
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
        """
        Inicializa agente Loss Zero
        """
        self.symbol = symbol
        self.volume = volume
        self.check_interval = check_interval
        self.trailing_start_percent = trailing_start_percent
        self.trailing_increment = trailing_increment
        self.use_buy = use_buy
        self.use_sell = use_sell
        
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
        
        print(f"Agente BTC Loss Zero inicializado!")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing: {trailing_start_percent}% -> infinito")
        print(f"   BUY/SELL: {'Ativo' if use_buy and use_sell else 'Seletivo'}")

    def run(self):
        """
        Executa agente Loss Zero
        """
        print(f"AGENTE BTC LOSS ZERO - TRAILING ILIMITADO")
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
            print(f"\nAgente BTC Loss Zero parado pelo usuario")

    def _display_status(self, cycle: int):
        """
        Exibe status do agente
        """
        print(f"\n{'='*60}")
        print(f"🤖 AGENTE BTC LOSS ZERO | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*60}")
        
        # Status do agente
        print(f"📊 AGENTE:")
        print(f"   Estado: LOSS ZERO (Trailing ilimitado)")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing Ativo: {'SIM' if self.trailing_active else 'NAO'}")
        if self.trailing_active:
            print(f"   Distancia Trailing: {self.trailing_distance:.2f}%")
        
        # Mercado
        if self.base_agent.mt5:
            try:
                tick = self.base_agent.mt5.symbol_info_tick(self.symbol)
                if tick:
                    price = tick['bid'] if tick['bid'] > 0 else tick['ask']
                    print(f"📈 MERCADO ({self.symbol}):")
                    print(f"   Preco: ${price:.2f}")
                    
                    if self.trailing_active:
                        profit_pct = ((price - self.entry_price) / self.entry_price) * 100
                        if self.base_agent._is_buy_position():
                            direction = "LONG"
                        else:
                            direction = "SHORT"
                        print(f"   Posicao: {direction}")
                        print(f"   Lucro Atual: {profit_pct:.2f}%")
                        
            except Exception as e:
                print(f"   Erro ao obter preco: {e}")

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
        # Usar análise simples do agente base
        if not self.use_buy and not self.use_sell:
            return
        
        # Buscar sinal simples
        signal = self._get_simple_signal()
        if signal:
            self._open_position(signal)

    def _get_simple_signal(self) -> dict:
        """
        Gera sinal simples para Loss 0
        """
        try:
            # Obter dados M1
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=20
            )
            
            if len(rates) < 10:
                return None
            
            # Analise simples
            current = rates[0]['close']
            previous = rates[1]['close']
            
            # SELL: Preco subindo mas RSI alto
            if self.use_sell and current > previous:
                rsi = self._calculate_simple_rsi(rates, 14)
                if rsi > 70:
                    return {
                        "type": "SELL",
                        "price": current,
                        "reason": "RSI overbought"
                    }
            
            # BUY: Preco descendo mas RSI baixo
            if self.use_buy and current < previous:
                rsi = self._calculate_simple_rsi(rates, 14)
                if rsi < 30:
                    return {
                        "type": "BUY",
                        "price": current,
                        "reason": "RSI oversold"
                    }
            
            return None
            
        except Exception as e:
            print(f"Erro na analise: {e}")
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
            
        except:
            return 50.0

    def _open_position(self, signal: dict):
        """
        Abre posicao com Loss 0
        """
        try:
            # Fechar posicoes existentes do mesmo tipo
            self._close_opposite_positions(signal["type"])
            
            # Criar request
            request = {
                "action": self.base_agent.mt5.ORDER_TYPE_SELL if signal["type"] == "SELL" else self.base_agent.mt5.ORDER_TYPE_BUY,
                "symbol": self.symbol,
                "volume": self.volume,
                "type_filling": self.base_agent.mt5.ORDER_FILLING_FOK,
                "deviation": 10
            }
            
            result = self.base_agent.mt5.order_send(request)
            
            if result and result.retcode == self.base_agent.mt5.ORDER_RETCODE_DONE:
                self.entry_price = signal["price"]
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                
                print(f"📈 POSICAO ABERTA: {signal['type']} ${self.entry_price:.2f}")
                print(f"   Motivo: {signal['reason']}")
                print(f"   Estrategia: Loss Zero (Trailing ilimitado)")
                print(f"   SL: Trailing stop (inativo ate 0.5%)")
                print(f"   TP: Sem TP (trailing ilimitado)")
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
            current_price = pos.price_current
            profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
            
            # Verificar se deve ativar trailing
            if not self.trailing_active and profit_pct >= self.trailing_start_percent:
                self.trailing_active = True
                self.trailing_distance = profit_pct
                print(f"🚀 TRAILING ATIVADO em {profit_pct:.2f}%!")
                
            # Atualizar trailing
            if self.trailing_active:
                if profit_pct > self.trailing_distance + self.trailing_increment:
                    self.trailing_distance = profit_pct - self.trailing_increment
                    print(f"📈 TRAILING ATUALIZADO: {self.trailing_distance:.2f}%")
                
                # Verificar stop
                stop_level = self._calculate_stop_level(pos.type, current_price)
                if current_price <= stop_level:
                    print(f"🛑 TRAILING STOP ATIVADO! Lucro: {profit_pct:.2f}%")
                    self.base_agent.mt5.position_close(pos.ticket)
                    self.trailing_active = False
                    
        except Exception as e:
            print(f"Erro ao gerenciar posicao: {e}")

    def _calculate_stop_level(self, pos_type: int, current_price: float) -> float:
        """
        Calcula nivel do trailing stop
        """
        if pos_type == 0:  # BUY
            return current_price * (1 - self.trailing_distance / 100)
        else:  # SELL
            return current_price * (1 + self.trailing_distance / 100)

    def _get_time(self):
        """
        Retorna hora atual
        """
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
