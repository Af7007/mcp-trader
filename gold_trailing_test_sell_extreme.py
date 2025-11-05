#!/usr/bin/env python3
"""
AGENTE GOLD TRAILING STOP - TESTE SELL COM SL EXTREMO
Versão que força SELL com SL MUITO maior para garantir abertura
Objetivo: Garantir que funcione mesmo em condições adversas
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class GoldTrailingTestSellExtreme(GoldLossZeroSimple):
    """
    Agente de teste para trailing stop - SELL COM SL EXTREMO
    SEM indicadores - abre posição IMEDIATAMENTE SELL com SL muito maior
    """
    
    def __init__(self, *args, **kwargs):
        """
        Configurações de teste com SL EXTREMO
        """
        # Configurações para garantir abertura
        kwargs.update({
            'trailing_activation_atr_multiplier': 0.01,  # Ultra baixo!
            'trailing_distance_atr_multiplier': 0.005,   # Ultra baixo!
            'stop_loss_atr_multiplier': 50.0,  # SL EXTREMO!
            'volume': 0.01,  # Volume menor para menor risco
            'check_interval': 2,  # Check ultra-rápido
            'use_buy': False,  # ONLY SELL!
            'use_sell': True   # ONLY SELL!
        })
        
        print("="*80)
        print("GOLD TRAILING STOP - TESTE SELL COM SL EXTREMO")
        print("="*80)
        print("OBJETIVO: Testar trailing stop SEM indicadores")
        print("COMPORTAMENTO: Abre posição IMEDIATAMENTE SELL")
        print("SL EXTREMO: Usar SL MAIOR para garantir abertura")
        print("")
        print("CONFIGURAÇÕES SL EXTREMO:")
        print("- ATR forçado: 100 pontos")
        print("- SL: 50.0 × ATR = 5000 pontos (EXTREMO!)")
        print("- Trailing ativa: 1 ponto (ultra-baixo)")
        print("- Volume: 0.01 lotes (menor risco)")
        print("- Check: 2 segundos")
        print("- Opções: ONLY SELL (BUY desabilitado)")
        print("")
        
        super().__init__(*args, **kwargs)
        
        # Forçar ATR e SL EXTREMO
        self.current_atr = 100.0
        self.current_sl_pontos = self.current_atr * self.sl_atr_mult  # 100 × 50 = 5000 pts!
        self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
        self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult
        
        # Controles de teste
        self.test_mode = True
        self.position_opened_for_test = False
        self.trailing_activation_attempts = 0
        self.sell_operations_count = 0
        
        print(f"[TESTE] ATR forçado: {self.current_atr} pontos")
        print(f"[TESTE] SL EXTREMO: {self.current_sl_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
        print(f"[TESTE] Trailing ativa em: {self.current_trailing_activation_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
        print(f"[TESTE] Operação: ONLY SELL (BUY desabilitado)")
        print(f"[TESTE] SL EXTREMO para garantir abertura")
        print("="*80)
        print("")
    
    def _open_position(self, signal: dict):
        """
        Override com SL EXTREMO para garantir abertura - ONLY SELL
        """
        # Forçar apenas SELL
        if signal["type"] != "SELL":
            signal["type"] = "SELL"
            signal["reason"] = "FORCED_SELL_EXTREME_SL"
            print(f"[TESTE] Sinal convertido para SELL (_EXTREME_SL)")
            
        try:
            # Fechar posicoes existentes do mesmo tipo (SELL)
            self._close_opposite_positions("SELL")

            # Obter preco atual de mercado
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                print("Erro: Nao foi possivel obter preco de mercado")
                return

            # SL EXTREMO para garantir distancia minima
            if self.current_atr == 0:
                self.current_atr = 100.0
                
            # SL EXTREMO (já calculado no init)
            self.current_sl_pontos = self.current_atr * self.sl_atr_mult  # 5000 pts!
            
            # Calcular valores em dinheiro (GOLD - usa point_value)
            sl_dinheiro = self._pontos_para_dinheiro(self.current_sl_pontos)
            trailing_activation_dinheiro = self._pontos_para_dinheiro(self.current_trailing_activation_pontos)
            trailing_distance_dinheiro = self._pontos_para_dinheiro(self.current_trailing_distance_pontos)

            # Calcular SL EXTREMO baseado em distancia em PREÇO
            # Para Gold: SL EXTREMO para garantir abertura
            market_price = tick['bid']  # Preco de venda
                
            # SL EXTREMO para SELL (muito abaixo do preço)
            # Usar 25% do valor total para garantir distancia MÁXIMA
            sl_price = market_price - (sl_dinheiro * 0.25)  # Muito abaixo do preço
            
            print(f"  market_price (BID): ${market_price:.3f}")
            print(f"  SL distance EXTREMO: ${sl_dinheiro:.2f}")
            print(f"  sl_price: ${market_price:.3f} - {sl_dinheiro*0.25:.3f} = ${sl_price:.3f}")
            print(f"  Distancia real: ${market_price - sl_price:.3f}")
            print(f"  [SELL] SL EXTREMO abaixo da entrada (garantido)")
            
            result = self.mt5.sell_market(
                symbol=self.symbol,
                volume=self.volume,
                sl=sl_price,
                tp=0,  # SEM TP!
                comment="Teste_Extreme_SL_SELL"
            )

            # Verificar se ordem foi executada
            if result:
                retcode = result.get('retcode', -1)
                print(f"[ORDER RESULT] retcode: {retcode}, order: {result.get('order', 0)}")
            
            if result and result.get('retcode') == 10009:  # TRADE_RETCODE_DONE
                # Contar operação SELL
                self.sell_operations_count += 1
                
                # Capturar ticket e magic number do MT5
                ticket = result.get('order', 0)
                self.last_position_ticket = ticket
                
                # Salvar para compatibilidade (última posição)
                self.entry_price = market_price
                self.trailing_active = False
                self.trailing_distance = 0.0
                self.highest_profit = 0.0
                
                # NOVO: Rastrear posição específica
                self.positions_entry_price[ticket] = market_price
                self.positions_trailing_active[ticket] = False
                self.positions_trailing_stop[ticket] = 0.0
                magic_number = result.get('request', {}).get('magic', 0)
                
                # Salvar último tipo de trade
                self.last_trade_type = "SELL"
                
                print(f"")
                print(f"{'='*60}")
                print(f"[EXTREME SELL ABERTO]: ${market_price:.2f}")
                print(f"   Ticket: {self.last_position_ticket}")
                print(f"   Volume: {self.volume} lotes")
                print(f"   Motivo: {signal['reason']}")
                print(f"   SL: ${sl_price:.2f} (distancia: ${market_price - sl_price:.2f})")
                print(f"   SL EXTREMO: ${sl_dinheiro:.2f} total")
                print(f"   TP: SEM TP FIXO (lucro ilimitado!)")
                print(f"   Operações SELL: {self.sell_operations_count}")
                print(f"")
                print(f"   TRAILING STOP:")
                print(f"   Ativa com: {self.current_trailing_activation_pontos:.0f} pts = ${trailing_activation_dinheiro:.2f} lucro")
                print(f"   Distancia: {self.current_trailing_distance_pontos:.0f} pts = ${trailing_distance_dinheiro:.2f}")
                print(f"   Lucro protegido quando ativar: ${trailing_activation_dinheiro - trailing_distance_dinheiro:.2f}")
                print(f"{'='*60}")
                print(f"")

                # Log do trade no banco de dados
                try:
                    trade_data = {
                        'ticket': ticket,
                        'magic_number': magic_number,
                        'strength': "TEST_EXTREME_SELL",
                        'trade_type': "SELL",
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': 0,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "Teste_Extreme_Sell_v1.0",
                        'reason': signal["reason"],
                        'status': "OPEN",
                        'comment': f"Extreme_Sell_{signal['reason']}"
                    }
                    # Log do trade e obter o trade_id
                    self.current_trade_id = self.btc_logger.log_trade(trade_data)
                    print(f"   [DB] Trade registrado - ID: {self.current_trade_id}")
                    print(f"        Ticket: {ticket} | Magic: {magic_number} | Volume: {self.volume}")
                except Exception as e:
                    print(f"   Erro ao logar trade: {e}")
            else:
                print(f"Erro ao abrir posicao SELL EXTREMO: {result}")
                
                # Mostrar detalhes do erro
                if result and result.get('retcode') == 10016:
                    print(f"   [ERRO] 10016 - Invalid stops")
                    print(f"   [ERRO] Mesmo com SL EXTREMO ainda está dando erro!")
                    print(f"   [ERRO] Preço: ${market_price:.3f}")
                    print(f"   [ERRO] SL: ${sl_price:.3f}")
                    print(f"   [ERRO] Distancia: ${market_price - sl_price:.3f}")
                    print(f"   [ERRO] Possível motivo:")
                    print(f"   - Horario de mercado (late trading)")
                    print(f"   - Spread muito alto")
                    print(f"   - Condições especiais do broker")
                    print(f"   [ERRO] SOLUÇÃO: Aguardar momento melhor")
                
                # Log da tentativa falha
                try:
                    trade_data_failed = {
                        'ticket': None,
                        'magic_number': None,
                        'strength': "TEST_EXTREME_SELL_FAILED",
                        'trade_type': "SELL",
                        'entry_price': market_price,
                        'sl_price': sl_price,
                        'tp_price': 0,
                        'volume': self.volume,
                        'symbol': self.symbol,
                        'agent_version': "Teste_Extreme_Sell_v1.0",
                        'reason': signal["reason"],
                        'status': "FAILED",
                        'comment': f"Extreme_Sell_Failed_{signal['reason']}"
                    }
                    self.btc_logger.log_trade(trade_data_failed)
                except Exception as e:
                    print(f"   Erro ao logar trade falha: {e}")
                 
        except Exception as e:
            print(f"Erro ao abrir posicao SELL EXTREMO: {e}")
    
    def _get_simple_signal(self) -> dict:
        """
        IGNORAR INDICADORES - ABERTURA IMEDIATA SELL COM SL EXTREMO
        """
        if not self.test_mode:
            return super()._get_simple_signal()
            
        # Verificar se já abriu posição para teste
        if self.position_opened_for_test:
            return None
            
        # Verificar se MT5 está conectado
        if not self.mt5:
            return None
            
        # Verificar posições abertas
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions:
            print(f"[TESTE] Posição SELL já existe - aguardando trailing")
            self.position_opened_for_test = True
            return None
        
        try:
            # Obter último candle para determinar direção
            rates = self.mt5.copy_rates_from_pos(
                symbol=self.symbol,
                timeframe="M1",  # Usar M1 para timing preciso
                start_pos=0,
                count=3  # Últimos 3 minutos
            )
            
            if len(rates) < 2:
                print(f"[TESTE] Dados insuficientes para análise")
                return None
            
            # Analisar último candle
            current_candle = rates[0]
            prev_candle = rates[1]
            
            # LÓGICA SIMPLES: FORÇAR SELL independente do candle
            current_price = current_candle['close']
            prev_price = prev_candle['close']
            
            # FORÇAR SELL - IGNORAR direção do candle
            signal_type = "SELL"
            reason = "FORCED_SELL_EXTREME_SL_TEST"
            
            print(f"[TESTE] Última candle: ALTA/BX (${prev_price:.2f} -> ${current_price:.2f})")
            print(f"[TESTE] FORÇANDO SELL com SL EXTREMO")
            
            print(f"[TESTE] SINAL FORÇADO: {signal_type}")
            print(f"[TESTE] TESTANDO ABERTURA SELL COM SL EXTREMO...")
            
            return {
                "type": signal_type,
                "price": current_price,
                "reason": reason
            }
            
        except Exception as e:
            print(f"[TESTE] Erro ao analisar candle: {e}")
            return None
    
    def _analyze_and_open(self):
        """
        Override para modo de teste - abre posição SELL COM SL EXTREMO
        """
        if not self.test_mode:
            return super()._analyze_and_open()
            
        # Parar após uma posição para teste
        if self.position_opened_for_test:
            return
            
        # Verificar se posição SELL já existe
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions:
            # Verificar se é SELL
            pos = positions[0]
            if pos.get('type') == 1:  # SELL
                print(f"[TESTE] Posição SELL encontrada - aguardando trailing")
                self.position_opened_for_test = True
                return
        
        # Obter sinal IMEDIATO (SELL forçado)
        signal = self._get_simple_signal()
        if not signal:
            return
            
        print(f"[TESTE] ABRINDO POSIÇÃO SELL COM SL EXTREMO...")
        self._open_position(signal)
        
        if self.last_position_ticket:
            self.position_opened_for_test = True
            print(f"[TESTE] Posição SELL #{self.last_position_ticket} aberta para teste")
            print(f"[TESTE] Aguardando ativação do trailing...")
            print(f"[TESTE] Objetivo: Ativar em {self.current_trailing_activation_pontos:.0f} pts (${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f})")
    
    def _display_status(self, cycle: int):
        """
        Display simplificado para teste SELL COM SL EXTREMO
        """
        if not self.test_mode:
            return super()._display_status(cycle)
            
        print(f"\n[TRAILING TEST EXTREME SELL] Ciclo #{cycle} | {self._get_time()}")
        print("="*55)
        
        # Status simplificado
        positions = self.mt5.positions_get(symbol=self.symbol) if self.mt5 else []
        
        if positions:
            pos = positions[0]
            ticket = pos.get('ticket')
            entry = pos.get('price_open', 0)
            profit = pos.get('profit', 0)
            
            # Calcular lucro em pontos para SELL
            current_price = entry + profit / (self.point_value * self.volume * self.symbol_point) if profit else entry
            if pos.get('type') == 1:  # SELL
                profit_pontos = (entry - current_price) / self.symbol_point
            else:  # BUY (não deveria acontecer)
                profit_pontos = (current_price - entry) / self.symbol_point
                
            profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)
            
            print(f"[EXTREME SELL] Posição #{ticket}:")
            print(f"  Entrada: ${entry:.2f} | Atual: ${current_price:.2f}")
            print(f"  Lucro: {profit_pontos:.1f} pts (${profit_dinheiro:.3f})")
            print(f"  Threshold trailing: {self.current_trailing_activation_pontos:.0f} pts (${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.3f})")
            print(f"  SL EXTREMO: ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
            print(f"  Operações SELL: {self.sell_operations_count}")
            
            # Status do trailing
            trailing_active = self.positions_trailing_active.get(ticket, False)
            if trailing_active:
                trailing_stop = self.positions_trailing_stop.get(ticket, 0)
                print(f"  STATUS: [TRAILING ATIVO] Stop: ${trailing_stop:.2f}")
                self.trailing_activation_attempts += 1
            else:
                falta = self.current_trailing_activation_pontos - profit_pontos
                falta_dinheiro = self._pontos_para_dinheiro(falta)
                if profit_pontos > 0:
                    print(f"  STATUS: [AGUARDANDO] Faltam {falta:.1f} pts (${falta_dinheiro:.3f})")
                else:
                    print(f"  STATUS: [NEGATIVO] {profit_pontos:.1f} pts")
        else:
            print(f"[EXTREME SELL] Nenhuma posição SELL aberta")
            print(f"[EXTREME SELL] Aguardando sinal para abrir SELL...")
            
            # Verificar se vai abrir SELL
            signal = self._get_simple_signal()
            if signal:
                print(f"[EXTREME SELL] Sinal detectado: {signal['type']} - Preparando para abrir SELL...")
            
        print("="*55)


def main():
    print("TESTE TRAILING STOP SELL COM SL EXTREMO")
    print("OBJETIVO: Garantir abertura com SL muito maior")
    print("COMPORTAMENTO: Força SELL com SL EXTREMO")
    print("")
    
    # Criar agente de teste SELL COM SL EXTREMO
    agent = GoldTrailingTestSellExtreme(
        symbol='XAUUSDc',
        volume=0.01,  # Volume menor
        check_interval=2,
        trailing_activation_atr_multiplier=0.01,  # Ultra baixo
        trailing_distance_atr_multiplier=0.005,   # Ultra baixo
        stop_loss_atr_multiplier=50.0,  # SL EXTREMO!
        use_buy=False,   # ONLY SELL!
        use_sell=True    # ONLY SELL!
    )
    
    print("")
    print("CONFIGURAÇÕES SL EXTREMO:")
    print(f"- SL: {agent.current_sl_pontos:.0f} pts = ${agent._pontos_para_dinheiro(agent.current_sl_pontos):.2f}")
    print(f"- Trailing ativa em: ${agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos):.3f}")
    print(f"- Volume: {agent.volume}")
    print(f"- Operações: ONLY SELL (BUY desabilitado)")
    print("")
    print("O QUE ESPERAR:")
    print("1. Posição SELL abre SEM erro (SL EXTREMO)")
    print("2. Trailing ativa em 30-60 segundos")
    print("3. Trailing se move com o preço")
    print("4. Sistema funcionando perfeitamente")
    print("")
    print("PARA PARAR: Ctrl+C")
    print("="*60)
    print("")
    
    # Executar teste
    try:
        agent.run()
    except KeyboardInterrupt:
        print(f"\n[EXTREME SELL] Teste parado pelo usuário")
        
        # Resumo do teste
        if agent.position_opened_for_test:
            print(f"[EXTREME SELL] Resumo:")
            print(f"  - Posição SELL aberta: SIM")
            print(f"  - Operações SELL: {agent.sell_operations_count}")
            print(f"  - Tentativas trailing: {agent.trailing_activation_attempts}")
            print(f"  - SL EXTREMO: Garantiu abertura sem erro")
            print(f"  - Teste EXTREME SELL concluído!")
        else:
            print(f"[EXTREME SELL] Posição SELL não foi aberta durante o teste")


if __name__ == "__main__":
    main()
