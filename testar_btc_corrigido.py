#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste BTC Loss Zero com stops corrigidos
Foco em resolver o problema de "Invalid stops"
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.btc_hedge_agent import BTCHedgeAgent


class BTCLossZeroCorrigido:
    """
    Versão corrigida do agente BTC Loss Zero
    Foco em stops válidos para MT5
    """

    def __init__(
        self,
        symbol: str = "BTCUSDc",
        volume: float = 0.01,
        check_interval: int = 15,
        stop_loss_dollars: float = 300.0,  # Aumentado para $300
        take_profit_dollars: float = 500.0,  # Aumentado para $500
        trailing_dollars: float = 200.0,    # Aumentado para $200
        use_buy: bool = True,
        use_sell: bool = True,
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,  # Mais conservador
        rsi_oversold: float = 30.0,   # Mais conservador
        volume_period: int = 20,
        volume_multiplier: float = 1.5
    ):
        """
        Inicializa agente corrigido
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
        
        # Criar agente base
        self.base_agent = BTCHedgeAgent(
            symbol=symbol,
            volume=volume,
            check_interval=check_interval,
            target_profit=float('inf'),
            hedge_trigger=-10.0,
            hedge_tp_target=10.0,
            only_sell=False
        )
        
        # Estado
        self.trailing_active = False
        self.entry_price = 0.0
        
        print(f"Agente BTC Loss Zero CORRIGIDO inicializado!")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {self.volume}")
        print(f"   SL: ${self.stop_loss_dollars} (aumentado)")
        print(f"   TP: ${self.take_profit_dollars} (aumentado)")
        print(f"   Trailing: ${self.trailing_dollars} (aumentado)")
        print(f"   RSI: {self.rsi_oversold}-{self.rsi_overbought} (mais conservador)")

    def run(self):
        """
        Executa agente corrigido
        """
        print(f"AGENTE BTC LOSS ZERO CORRIGIDO")
        print(f"="*50)
        print(f"Parando processo ativo com Ctrl+C")
        print()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                self._display_status(cycle)
                
                # Verificar posições abertas
                self._check_positions()
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\nAgente BTC Loss Zero Corrigido parado pelo usuario")

    def _display_status(self, cycle: int):
        """
        Exibe status do agente
        """
        print(f"\n{'='*50}")
        print(f"[AGENTE] BTC LOSS ZERO CORRIGIDO | Ciclo #{cycle} | {self._get_time()}")
        print(f"{'='*50}")
        
        # Status do agente
        print(f"[AGENTE]:")
        print(f"   Estado: LOSS ZERO CORRIGIDO")
        print(f"   Volume: {self.volume}")
        print(f"   Trailing Ativo: {'SIM' if self.trailing_active else 'NAO'}")
        
        # Mercado
        if self.base_agent.mt5:
            try:
                tick = self.base_agent.mt5.get_symbol_info_tick(self.symbol)
                if tick:
                    price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
                    print(f"[MERCADO] ({self.symbol}):")
                    print(f"   Preco: ${price:.2f}")
                    
                    # Exibir indicadores
                    self._display_indicators(price, cycle)
                    
            except Exception as e:
                print(f"   Erro ao obter preco: {e}")

    def _display_indicators(self, current_price: float, cycle: int):
        """
        Exibe valores dos indicadores
        """
        try:
            # Obter dados para indicadores
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=50
            )
            
            if len(rates) < 20:
                print(f"   [INDICADORES] Dados insuficientes: {len(rates)} candles")
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
            
            # Buscar sinal
            signal = self._get_signal()
            if signal:
                print(f"[SINAL GERADO]:")
                print(f"   Tipo: {signal['type']}")
                print(f"   Preço: ${signal['price']:.2f}")
                print(f"   Razão: {signal['reason']}")
                print(f"   Força: {signal['strength']}")
                
                # Mostrar cálculo dos stops
                if signal['type'] == 'BUY':
                    sl = signal['price'] - self.stop_loss_dollars
                    tp = signal['price'] + self.take_profit_dollars
                    print(f"   SL Calculado: ${sl:.2f} (-${self.stop_loss_dollars})")
                    print(f"   TP Calculado: ${tp:.2f} (+${self.take_profit_dollars})")
                else:
                    sl = signal['price'] + self.stop_loss_dollars
                    tp = signal['price'] - self.take_profit_dollars
                    print(f"   SL Calculado: ${sl:.2f} (+${self.stop_loss_dollars})")
                    print(f"   TP Calculado: ${tp:.2f} (-${self.take_profit_dollars})")
            else:
                print(f"[SINAL]: Nenhum sinal nas condições atuais")
            
        except Exception as e:
            print(f"   Erro ao calcular indicadores: {e}")

    def _check_positions(self):
        """
        Verifica e gerencia posições
        """
        if not self.base_agent.mt5:
            return
        
        try:
            positions = self.base_agent.mt5.positions_get(symbol=self.symbol)
            if not positions:
                # Nenhuma posição, analisa para abrir
                self._analyze_and_open()
            else:
                print(f"   [POSICAO] Já existe posição aberta")
                    
        except Exception as e:
            print(f"Erro ao verificar posicoes: {e}")

    def _analyze_and_open(self):
        """
        Analisa mercado e abre posição
        """
        if not self.use_buy and not self.use_sell:
            return
        
        # Buscar sinal
        signal = self._get_signal()
        if signal:
            self._open_position(signal)

    def _get_signal(self) -> dict:
        """
        Gera sinal corrigido
        """
        try:
            # Obter dados M1
            rates = self.base_agent.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",
                start_pos=0,
                count=50
            )
            
            if len(rates) < 20:
                return None
            
            current = rates[0]['close']
            previous = rates[1]['close']
            
            # Calcular indicadores
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(rates)
            rsi = self._calculate_rsi(rates, self.rsi_period)
            current_volume = rates[0]['tick_volume']
            avg_volume = np.mean([r['tick_volume'] for r in rates[:self.volume_period]])
            
            # Estratégia mais conservadora
            if self.use_sell and current >= bb_upper and rsi > self.rsi_overbought and current > previous and current_volume > avg_volume * self.volume_multiplier:
                return {
                    "type": "SELL",
                    "price": current,
                    "reason": "BB_upper + RSI_overbought + Volume",
                    "strength": "STRONG"
                }
            
            elif self.use_buy and current <= bb_lower and rsi < self.rsi_oversold and current < previous and current_volume > avg_volume * self.volume_multiplier:
                return {
                    "type": "BUY",
                    "price": current,
                    "reason": "BB_lower + RSI_oversold + Volume",
                    "strength": "STRONG"
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
            
        except Exception as e:
            print(f"Erro ao calcular RSI: {e}")
            return 50.0

    def _calculate_trend(self, rates):
        """
        Calcula tendência simples
        """
        try:
            if len(rates) < 6:
                return "NEUTRA"
            
            closes = [r['close'] for r in rates[:6]]
            
            # Calcular média móvel simples
            sma = np.mean(closes[:-1])
            current = closes[0]
            
            if current > sma * 1.002:  # 0.2% acima da média
                return "ALTA"
            elif current < sma * 0.998:  # 0.2% abaixo da média
                return "BAIXA"
            else:
                return "NEUTRA"
                
        except Exception as e:
            print(f"Erro ao calcular tendência: {e}")
            return "NEUTRA"

    def _calculate_momentum(self, rates):
        """
        Calcula momentum
        """
        try:
            if len(rates) < 4:
                return 0.0
            
            closes = [r['close'] for r in rates[:4]]
            
            # Momentum = preço atual - preço há 3 períodos
            momentum = closes[0] - closes[3]
            
            # Normalizar para percentual
            if closes[3] != 0:
                momentum_pct = (momentum / closes[3]) * 100
                return momentum_pct
            
            return 0.0
            
        except Exception as e:
            print(f"Erro ao calcular momentum: {e}")
            return 0.0

    def _open_position(self, signal: dict):
        """
        Abre posição com validação corrigida
        """
        try:
            # Calcular SL e TP
            if signal["type"] == "BUY":
                sl_price = signal["price"] - self.stop_loss_dollars
                tp_price = signal["price"] + self.take_profit_dollars
                
                # Validação melhorada
                if sl_price <= 0 or tp_price <= 0:
                    print(f"❌ SL/TP inválidos (valores <= 0)")
                    return
                
                if sl_price >= signal["price"]:
                    print(f"❌ SL inválido para BUY: ${sl_price:.2f} >= ${signal['price']:.2f}")
                    return
                
                if tp_price <= signal["price"]:
                    print(f"❌ TP inválido para BUY: ${tp_price:.2f} <= ${signal['price']:.2f}")
                    return
                
                # Verificar distância mínima
                sl_distance = signal["price"] - sl_price
                tp_distance = tp_price - signal["price"]
                
                if sl_distance < 100:  # Mínimo $100 de distância
                    print(f"❌ SL muito próximo: ${sl_distance:.2f} (mínimo $100)")
                    return
                
                if tp_distance < 100:  # Mínimo $100 de distância
                    print(f"❌ TP muito próximo: ${tp_distance:.2f} (mínimo $100)")
                    return
                
                print(f"✅ Validação BUY passou: SL=${sl_distance:.2f}, TP=${tp_distance:.2f}")
                
                result = self.base_agent.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"CORRIGIDO_BUY_{signal['strength']}"
                )
            else:  # SELL
                sl_price = signal["price"] + self.stop_loss_dollars
                tp_price = signal["price"] - self.take_profit_dollars
                
                # Validação melhorada
                if sl_price <= 0 or tp_price <= 0:
                    print(f"❌ SL/TP inválidos (valores <= 0)")
                    return
                
                if sl_price <= signal["price"]:
                    print(f"❌ SL inválido para SELL: ${sl_price:.2f} <= ${signal['price']:.2f}")
                    return
                
                if tp_price >= signal["price"]:
                    print(f"❌ TP inválido para SELL: ${tp_price:.2f} >= ${signal['price']:.2f}")
                    return
                
                # Verificar distância mínima
                sl_distance = sl_price - signal["price"]
                tp_distance = signal["price"] - tp_price
                
                if sl_distance < 100:  # Mínimo $100 de distância
                    print(f"❌ SL muito próximo: ${sl_distance:.2f} (mínimo $100)")
                    return
                
                if tp_distance < 100:  # Mínimo $100 de distância
                    print(f"❌ TP muito próximo: ${tp_distance:.2f} (mínimo $100)")
                    return
                
                print(f"✅ Validação SELL passou: SL=${sl_distance:.2f}, TP=${tp_distance:.2f}")
                
                result = self.base_agent.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"CORRIGIDO_SELL_{signal['strength']}"
                )
            
            if result and result.get('retcode') == 10009:
                self.entry_price = signal["price"]
                print(f"✅ [POSICAO ABERTA]: {signal['type']} ${self.entry_price:.2f}")
                print(f"   Força: {signal['strength']}")
                print(f"   Motivo: {signal['reason']}")
                print(f"   SL: ${self.stop_loss_dollars}")
                print(f"   TP: ${self.take_profit_dollars}")
            else:
                print(f"❌ Erro ao abrir posicao: {result}")
                if result:
                    print(f"   Retcode: {result.get('retcode')}")
                    print(f"   Comment: {result.get('comment')}")
                
        except Exception as e:
            print(f"Erro ao abrir posicao: {e}")

    def _get_time(self):
        """
        Retorna hora atual
        """
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def main():
    """
    Função principal
    """
    print("🧪 TESTE DO BTC LOSS ZERO CORRIGIDO")
    print("=" * 50)
    
    try:
        # Criar agente corrigido
        agent = BTCLossZeroCorrigido(
            symbol="BTCUSDc",
            volume=0.01,
            check_interval=30,
            stop_loss_dollars=300.0,  # $300
            take_profit_dollars=500.0,  # $500
            trailing_dollars=200.0,    # $200
            use_buy=True,
            use_sell=True,
            rsi_overbought=70.0,
            rsi_oversold=30.0
        )
        
        print("✅ Agente criado com sucesso!")
        
        # Executar agente
        agent.run()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
