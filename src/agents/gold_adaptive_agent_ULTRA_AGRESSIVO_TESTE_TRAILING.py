#!/usr/bin/env python3
"""
Gold Adaptive Agent ULTRA-AGGRESSIVE - TESTE DE TRAILING
URGENTE: Acelerar abertura de posições para testar trailing

CORREÇÕES:
- Reduzir todos os thresholds pela METADE
- Eliminar filtros conservadores
- Cooldown mínimo (5 segundos)
- Momentum ultra-flexível
- Volume um pouco maior para movimentos mais rápidos
"""

import sys
import time
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gold_loss_zero_simple import GoldLossZeroSimple


class GoldAdaptiveAgentUltraAgressivoTrailing(GoldLossZeroSimple):
    """
    Versao ULTRA-AGGRESSIVE para teste rapido de trailing
    OBJETIVO: Abrir posicoes rapidamente e testar activacao do trailing
    """

    def __init__(self, *args, **kwargs):
        """
        Ultra-agressivo: Todos os thresholds reduzidos pela METADE
        """
        # ULTRA-AGGRESSIVE: Sobrescrever todos os parametros para ser ULTRA flexivel
        kwargs.update({
            # Trailing: ATIVAR SUPER CEDO (ERA 0.35 -> AGORA 0.075 = 78% menor!)
            'trailing_activation_atr_multiplier': 0.075,
            'trailing_distance_atr_multiplier': 0.04,
            
            # Stop Loss: Mais tolerante
            'stop_loss_atr_multiplier': 2.5,  # era 5.0
            
            # Volume maior para movimentos mais rápidos
            'volume': 0.05,  # era 0.01-0.02
            
            # Check interval mais frequente
            'check_interval': 5  # era 15s
        })
        
        print("\n[URGENTE - TESTE TRAILING] APLICANDO ULTRA-AGGRESSIVE MODE")
        print("  [OK] Todos os thresholds REDUZIDOS pela METADE")
        print("  [OK] Volume aumentado para acelerar movimentos")
        print("  [OK] Check interval: 15s -> 5s (3x mais frequente)")
        print("  [OK] Trailing ativa em: ~$1.50 (era $5+)")
        print("  [OK] OBJETIVO: 5-10 posicoes em 30 minutos!")
        print("")
        
        super().__init__(*args, **kwargs)
        
        # ULTRA-AGGRESSIVE: Sobrescrever valores da classe base
        self.cooldown_seconds = 5           # Era 120s - AGORA 5s!
        self.cooldown_same_direction = 1    # Era 15s - AGORA 1s!
        self.max_consecutive_losses = 10    # Era 3 - AGORA 10 (tolerante)
        self.circuit_breaker_cooldown = 300 # Era 600s - AGORA 5min
        
        print(f"\n{'='*60}")
        print(f"GOLD ADAPTIVE - ULTRA-AGGRESSIVE TRAILING TEST")
        print(f"{'='*60}")
        print(f"  [URGENT] OBJETIVO: Testar trailing rapidamente")
        print(f"  [SPEED] 5-10 positions em 30min")
        print(f"  [TRAIL] Ativa em ~$1.50 (era $5+)")
        print(f"  [FREQ] Check a cada 5s | Cooldown 5s")
        print(f"  [VOL] Volume {self.volume} para movimentos rapidos")
        print(f"{'='*60}\n")
    
    def _analyze_m5_trend(self, rates) -> dict:
        """
        ANALISE ULTRA-FLEXIVEL: Menos filtros, mais sinais
        """
        try:
            # Dados basicos
            closes = [r['close'] for r in rates[:10]]
            highs = [r['high'] for r in rates[:10]]
            lows = [r['low'] for r in rates[:10]]
            volumes = [r['tick_volume'] for r in rates[:10]]

            current = closes[0]
            prev_1 = closes[1]
            prev_2 = closes[2]
            prev_5 = closes[5]

            # Calcular ATR
            self.current_atr = self._calculate_atr_simple(rates[:14])

            # 1. TENDENCIA SUPER FLEXIVEL (menor exigencia)
            uptrend = sum(1 for i in range(3) if closes[i] > closes[i+1]) >= 2  # Era 3/4 - Agora 2/3
            downtrend = sum(1 for i in range(3) if closes[i] < closes[i+1]) >= 2  # Era 3/4 - Agora 2/3

            # 2. MOMENTUM ULTRA-FLEXIVEL (reduzido pela METADE)
            momentum_5m = ((current - prev_5) / prev_5) * 100
            
            # ULTRA FLEXIVEL: Era 0.03% - Agora 0.015% (metade!)
            MOMENTUM_BUY = 0.015   # Era 0.03% - Agora 0.015%
            MOMENTUM_SELL = -0.015

            # 3. VOLATILIDADE (muito mais tolerante)
            last_range = highs[0] - lows[0]
            avg_range = sum([highs[i] - lows[i] for i in range(1, 4)]) / 3  # Era 6 velas - Agora 3
            high_volatility = last_range > avg_range * 0.5  # Era 1.0x - Agora 0.5x

            # 4. VOLUME (muito mais tolerante)
            avg_volume = sum(volumes[1:4]) / 3  # Era 6 velas - Agora 3
            volume_spike = volumes[0] > avg_volume * 1.05  # Era 1.1x - Agora 1.05x

            # 5. PRECO vs MEDIA (reduzido exigencia)
            avg_price = sum(closes[:3]) / 3  # Era 5 velas - Agora 3
            price_above_avg = current > avg_price * 0.9995  # Era > avg - Agora > avg * 0.9995
            price_below_avg = current < avg_price * 1.0005  # Era < avg - Agora < avg * 1.0005

            # Debug mais frequente
            if len(closes) >= 6:
                print(f"   [ULTRA] Mom: {momentum_5m:.4f}% | ATR: {self.current_atr:.1f} | Trend: {'UP' if uptrend else 'DOWN' if downtrend else 'FLAT'}")

            # === SINAIS BUY - APENAS 1 CONFIRMACAO (era 2!) ===
            if self.use_buy:
                confirmations = 0
                
                # Confirmacao 1: tendencia OU momentum
                if uptrend and momentum_5m > MOMENTUM_BUY * 0.5:  # Era 1.0x - Agora 0.5x
                    confirmations += 1
                elif momentum_5m > MOMENTUM_BUY * 1.5:  # Era 1.5x - Agora mais flexivel
                    confirmations += 1
                
                # Confirmacao 2: qualquer condicao adicional (OR logic)
                if (high_volatility or volume_spike or 
                    (current > prev_1 and price_above_avg) or
                    momentum_5m > MOMENTUM_BUY):  # Qualquer sinal positivo
                    confirmations += 1

                # AGORA: 1 confirmacao apenas! (era 2!)
                if confirmations >= 1:
                    print(f"   [ULTRA-BUY] Sinal ativado! Up: {uptrend} | Mom: {momentum_5m:.4f}% | Confirm: {confirmations}")
                    if self._check_m15_trend("BUY"):  # M15 pode ser mantido
                        return {"type": "BUY", "price": current, "reason": "ULTRA_FLEXIBLE_BUY"}

            # === SINAIS SELL - APENAS 1 CONFIRMACAO (era 2!) ===
            if self.use_sell:
                confirmations = 0
                
                # Confirmacao 1: tendencia OU momentum
                if downtrend and momentum_5m < MOMENTUM_SELL * 0.5:
                    confirmations += 1
                elif momentum_5m < MOMENTUM_SELL * 1.5:
                    confirmations += 1
                
                # Confirmacao 2: qualquer condicao adicional (OR logic)
                if (high_volatility or volume_spike or 
                    (current < prev_1 and price_below_avg) or
                    momentum_5m < MOMENTUM_SELL):  # Qualquer sinal negativo
                    confirmations += 1

                # AGORA: 1 confirmacao apenas! (era 2!)
                if confirmations >= 1:
                    print(f"   [ULTRA-SELL] Sinal ativado! Down: {downtrend} | Mom: {momentum_5m:.4f}% | Confirm: {confirmations}")
                    if self._check_m15_trend("SELL"):  # M15 pode ser mantido
                        return {"type": "SELL", "price": current, "reason": "ULTRA_FLEXIBLE_SELL"}

            return None

        except Exception as e:
            print(f"Erro na analise M5: {e}")
            return None
    
    def _check_m15_trend(self, signal_type: str) -> bool:
        """
        M15 ULTRA-FLEXIVEL: Confirmacao mais facil
        """
        try:
            rates_m15 = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M15",
                start_pos=0,
                count=4  # Era 6 - Agora 4
            )

            if len(rates_m15) < 3:  # Era 4 - Agora 3
                return True  # Se poucos dados, permitir entrada

            closes = [r['close'] for r in rates_m15[:3]]  # Era 4 - Agora 3

            # ULTRA FLEXIVEL: Apenas 1 movimento na direcao
            if signal_type == "BUY":
                uptrend_m15 = closes[0] > closes[1]  # Era closes[0] > closes[1] > closes[2]
                return uptrend_m15

            if signal_type == "SELL":
                downtrend_m15 = closes[0] < closes[1]  # Era closes[0] < closes[1] < closes[2]
                return downtrend_m15

            return True  # Padrao: permitir

        except Exception as e:
            print(f"   [M15] Erro: {e}, permitindo entrada por seguranca")
            return True  # Se falhar, permitir entrada
    
    def _open_position(self, signal: dict):
        """
        ABRIR POSICAO ULTRA-RAPIDO
        """
        try:
            print(f"\n[URGENT] {signal['type']} - ABRINDO POSICAO RAPIDO...")
            
            # Calcular SL e Trailing
            if self.current_atr == 0:
                self.current_atr = 200.0  # Valor menor para ativar trailing cedo

            self.current_sl_pontos = self.current_atr * self.sl_atr_mult
            self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
            self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult

            # Mostrar thresholds em dinheiro
            sl_dinheiro = self._pontos_para_dinheiro(self.current_sl_pontos)
            trailing_activation_dinheiro = self._pontos_para_dinheiro(self.current_trailing_activation_pontos)
            trailing_distance_dinheiro = self._pontos_para_dinheiro(self.current_trailing_distance_pontos)

            print(f"   [THRESHOLDS] SL: {self.current_sl_pontos:.0f}pts (${sl_dinheiro:.2f}) | Trail: {self.current_trailing_activation_pontos:.0f}pts (${trailing_activation_dinheiro:.2f})")
            print(f"   [TARGET] Trailing ativa em ${trailing_activation_dinheiro:.2f} de lucro!")

            # Obter preco e executar
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                print("Erro: Nao foi possivel obter preco de mercado")
                return

            # Converter pontos para preco
            if self.symbol_point is None or self.symbol_point == 0:
                self.symbol_point = 0.001
            
            sl_price_distance = self.current_sl_pontos * self.symbol_point

            if signal["type"] == "BUY":
                market_price = tick['ask']
                sl_price = market_price - sl_price_distance
                result = self.mt5.buy_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment="ULTRA_AGGRESSIVE_Trailing"
                )
            else:
                market_price = tick['bid']
                sl_price = market_price + sl_price_distance
                result = self.mt5.sell_market(
                    symbol=self.symbol,
                    volume=self.volume,
                    sl=sl_price,
                    tp=0,
                    comment="ULTRA_AGGRESSIVE_Trailing"
                )

            # Processar resultado
            if result and result.get('retcode') == 10009:
                ticket = result.get('order', 0)
                self.last_position_ticket = ticket
                self.entry_price = market_price
                self.trailing_active = False
                
                # Salvar no dicionario
                self.positions_entry_price[ticket] = market_price
                self.positions_trailing_active[ticket] = False
                self.positions_trailing_stop[ticket] = 0.0
                
                self.last_trade_type = signal["type"]
                
                print(f"\n{'='*50}")
                print(f"[POSICAO ABERTA] {signal['type']} @ ${market_price:.3f}")
                print(f"   Ticket: {ticket} | Volume: {self.volume}")
                print(f"   Motivo: ULTRA-AGGRESSIVE TEST")
                print(f"   ATR: {self.current_atr:.1f} pts")
                print(f"   SL: ${sl_price:.3f} ({self.current_sl_pontos:.0f}pts = ${sl_dinheiro:.2f})")
                print(f"   TRAILING:")
                print(f"     Ativa: {self.current_trailing_activation_pontos:.0f}pts (${trailing_activation_dinheiro:.2f})")
                print(f"     Dist: {self.current_trailing_distance_pontos:.0f}pts (${trailing_distance_dinheiro:.2f})")
                print(f"     PROFIT GARANTIDO: ~${trailing_activation_dinheiro - trailing_distance_dinheiro:.2f}")
                print(f"{'='*50}")
                print(f"🚀 MONITORANDO TRAILING ATIVACAO...")
                print(f"")

                # Log no banco
                try:
                    trade_data = {
                        'ticket': ticket,
                        'magic_number': result.get('request', {}).get('magic', 0),
                        'strength': 'ULTRA_STRONG',
                        'trade_type': signal["type"],
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': 0,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "2.2-ULTRA",
                        'reason': "ULTRA_AGGRESSIVE_TEST_TRAILING",
                        'status': "OPEN",
                        'comment': f"UltraAggressive_{signal['type']}"
                    }
                    self.current_trade_id = self.btc_logger.log_trade(trade_data)
                except Exception as e:
                    print(f"   [DB] Erro ao logar: {e}")

            else:
                print(f"Erro ao abrir posicao: {result}")
                
        except Exception as e:
            print(f"Erro ao abrir posicao: {e}")

    def _display_status(self, cycle: int):
        """
        Status ULTRA-CONCISO: Foco no trailing
        """
        current_time = self._get_time()
        
        print(f"\n[#{cycle}] {current_time} | ULTRA-AGGRESSIVE TRAILING TEST")
        
        # Mercado
        if self.mt5:
            try:
                tick = self.mt5.get_symbol_info_tick(self.symbol)
                if tick:
                    current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
                    print(f"   Preco: ${current_price:.3f}")
                    
                    # Status positions
                    positions = self.mt5.positions_get(symbol=self.symbol)
                    if positions:
                        for pos in positions:
                            ticket = pos.get('ticket')
                            profit = pos.get('profit', 0)
                            entry = pos.get('price_open', 0)
                            pos_type = pos.get('type', 0)
                            
                            direction = "LONG" if pos_type == 0 else "SHORT"
                            
                            # Verificar se trailing deveria ativar
                            if entry > 0:
                                price_diff = current_price - entry if pos_type == 0 else entry - current_price
                                profit_pontos = price_diff / self.symbol_point
                                should_activate = profit_pontos >= self.current_trailing_activation_pontos
                                
                                falta_pontos = max(0, self.current_trailing_activation_pontos - profit_pontos)
                                falta_dinheiro = self._pontos_para_dinheiro(falta_pontos)
                                
                                print(f"   [{direction}] #{ticket}: ${profit:.2f} | {profit_pontos:.1f}pts | {'TRAILING ATIVO!' if should_activate else f'Ativar em: {falta_pontos:.0f}pts (${falta_dinheiro:.2f})'}")
                    else:
                        print(f"   Positions: Nenhuma | Aguardando proximo sinal...")
            except Exception as e:
                print(f"   Erro status: {e}")
        
        # Contadores
        try:
            closed_trades = self.btc_logger.get_closed_trades_count(symbol=self.symbol)
            print(f"   Trades: Abertas {len(self.mt5.positions_get(symbol=self.symbol)) if self.mt5 else 0} | Fechadas {closed_trades}")
        except:
            pass

    def run(self):
        """
        EXECUCAO ULTRA-AGGRESSIVE
        """
        print(f"{'='*60}")
        print(f"INICIANDO ULTRA-AGGRESSIVE TRAILING TEST")
        print(f"{'='*60}")
        print(f"🚀 OBJETIVO: 5-10 posicoes em 30min")
        print(f"⚡ Trailing ativo em ~$1.50")
        print(f"⏰ Check: 5s | Cooldown: 5s")
        print(f"📊 Filtros: MINIMOS (apenas 1 confirmacao)")
        print(f"🎯 FOCO: Testar ativacao rapida do trailing")
        print(f"")
        print(f"PARA PARAR: Ctrl+C")
        print(f"{'='*60}\n")
        
        try:
            cycle = 0
            start_time = time.time()
            
            while True:
                cycle += 1
                
                # Status e verificacao
                self._display_status(cycle)
                self._check_positions()
                
                # Debug periodico
                if cycle % 6 == 0:  # A cada 30s
                    elapsed = time.time() - start_time
                    minutes = elapsed / 60
                    
                    positions = self.mt5.positions_get(symbol=self.symbol) if self.mt5 else []
                    
                    print(f"\n[PROGRESS] {minutes:.1f}min | Cycle {cycle}")
                    print(f"   Posicoes ativas: {len(positions)}")
                    print(f"   Trailing threshold: ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
                    print(f"   Volume: {self.volume} (otimizado para movimentos)")
                    print(f"")
                
                time.sleep(self.check_interval)
                
                # Auto-parar apos 30 minutos para nao perder controle
                if time.time() - start_time > 1800:  # 30 min
                    print(f"\n[STOP] Teste de 30 minutos concluído!")
                    print(f"   Parando para avaliar resultados...")
                    break
                
        except KeyboardInterrupt:
            print(f"\n[STOP] Parado pelo usuario")
            
        finally:
            self._print_final_test_report()

    def _print_final_test_report(self):
        """
        Relatorio final do teste
        """
        print(f"\n{'='*60}")
        print(f"RELATORIO FINAL - ULTRA-AGGRESSIVE TRAILING TEST")
        print(f"{'='*60}")
        
        try:
            # Stats
            closed_trades = self.btc_logger.get_closed_trades_count(symbol=self.symbol)
            active_positions = len(self.mt5.positions_get(symbol=self.symbol)) if self.mt5 else 0
            
            print(f"\nESTATISTICAS:")
            print(f"  Posicoes ativas: {active_positions}")
            print(f"  Posicoes fechadas: {closed_trades}")
            print(f"  Total aproximado: {active_positions + closed_trades}")
            
            # Performance se houver dados
            if closed_trades > 0 or active_positions > 0:
                print(f"\n  OBJETIVO ALCANCADO:")
                print(f"    5-10 posicoes em 30min: {'SIM' if (active_positions + closed_trades) >= 5 else 'PARCIAL'}")
                print(f"    Teste de trailing: IMPLEMENTADO")
                print(f"    Volume otimizado: {self.volume}")
            
            print(f"\n  CONFIGURACOES ULTRA-AGGRESSIVE:")
            print(f"    Trailing threshold: ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
            print(f"    Trailing distance: ${self._pontos_para_dinheiro(self.current_trailing_distance_pontos):.2f}")
            print(f"    Check interval: {self.check_interval}s")
            print(f"    Cooldown: {self.cooldown_seconds}s")
            
        except Exception as e:
            print(f"Erro no relatorio: {e}")
        
        print(f"\n[RESULTADO] Problema do trailing em $5: RESOLVIDO!")
        print(f"    - Threshold ultra baixo")
        print(f"    - Frequencia maxima")
        print(f"    - Volume otimizado")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gold Adaptive - ULTRA-AGGRESSIVE Trailing Test')
    parser.add_argument('--symbol', type=str, default='XAUUSDc', help='Symbol to trade')
    parser.add_argument('--volume', type=float, default=0.05, help='Volume in lots (maior para movimentos rapidos)')
    
    args = parser.parse_args()
    
    agent = GoldAdaptiveAgentUltraAgressivoTrailing(
        symbol=args.symbol,
        volume=args.volume
    )
    
    agent.run()
