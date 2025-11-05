#!/usr/bin/env python3
"""
AGENTE GOLD TRAILING STOP - TESTE DIRETO
Versão simplificada SEM indicadores para testar trailing stop
Objetivo: Abrir posição IMEDIATAMENTE e ativar trailing
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class GoldTrailingTest(GoldLossZeroSimple):
    """
    Agente de teste para trailing stop
    SEM indicadores - abre posição IMEDIATAMENTE
    """
    
    def __init__(self, *args, **kwargs):
        """
        Configurações de teste ultra-agressivas
        """
        # Configurações ultra-agressivas para teste
        kwargs.update({
            'trailing_activation_atr_multiplier': 0.01,  # Ultra baixo!
            'trailing_distance_atr_multiplier': 0.005,   # Ultra baixo!
            'stop_loss_atr_multiplier': 1.0,
            'volume': 0.05,
            'check_interval': 2  # Check ultra-rápido
        })
        
        print("="*80)
        print("GOLD TRAILING STOP - TESTE DIRETO")
        print("="*80)
        print("OBJETIVO: Testar trailing stop SEM indicadores")
        print("COMPORTAMENTO: Abre posição IMEDIATAMENTE")
        print("TESTE: Tentar ativar trailing em 30-60 segundos")
        print("")
        print("CONFIGURAÇÕES ULTRA-AGGRESSIVES:")
        print("- ATR forçado: 100 pontos (ultra-baixo)")
        print("- Trailing ativa: 1 ponto (ultra-baixo)")
        print("- Volume: 0.05 lotes")
        print("- Check: 2 segundos")
        print("- Teste: Uma posição por vez")
        print("")
        
        super().__init__(*args, **kwargs)
        
        # Forçar ATR ultra-baixo
        self.current_atr = 100.0
        self.current_sl_pontos = self.current_atr * self.sl_atr_mult
        self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
        self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult
        
        # Controles de teste
        self.test_mode = True
        self.position_opened_for_test = False
        self.trailing_activation_attempts = 0
        self.max_test_attempts = 1  # Só uma posição para teste
        
        print(f"[TESTE] ATR forçado: {self.current_atr} pontos")
        print(f"[TESTE] Trailing ativa em: {self.current_trailing_activation_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
        print(f"[TESTE] Teste executar até: 1 posição")
        print("="*80)
        print("")
    
    def _get_simple_signal(self) -> dict:
        """
        IGNORAR INDICADORES - ABERTURA IMEDIATA
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
            print(f"[TESTE] Posição já existe - aguardando trailing")
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
            
            # LÓGICA SIMPLES: Seguir direção do último candle
            current_price = current_candle['close']
            prev_price = prev_candle['close']
            high_price = current_candle['high']
            low_price = current_candle['low']
            
            # Determinar direção baseado no candle
            if current_price > prev_price:
                signal_type = "BUY"
                reason = "CANDLE_UPWARD_TEST"
                print(f"[TESTE] Última candle: ALTA (${prev_price:.2f} -> ${current_price:.2f})")
            else:
                signal_type = "SELL"
                reason = "CANDLE_DOWNWARD_TEST"
                print(f"[TESTE] Última candle: BAIXA (${prev_price:.2f} -> ${current_price:.2f})")
            
            print(f"[TESTE] SINAL DETECTADO: {signal_type}")
            print(f"[TESTE] Testando ABERTURA IMEDIATA em ${current_price:.2f}")
            
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
        Override para modo de teste - abre posição IMEDIATAMENTE
        """
        if not self.test_mode:
            return super()._analyze_and_open()
            
        # Parar após uma posição para teste
        if self.position_opened_for_test:
            return
            
        # Verificar se posição já existe
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions:
            print(f"[TESTE] Posição encontrada - aguardando trailing")
            self.position_opened_for_test = True
            return
            
        # Obter sinal IMEDIATO (sem indicadores)
        signal = self._get_simple_signal()
        if not signal:
            return
            
        print(f"[TESTE] ABINDO POSIÇÃO DE TESTE...")
        self._open_position(signal)
        
        if self.last_position_ticket:
            self.position_opened_for_test = True
            print(f"[TESTE] Posição #{self.last_position_ticket} aberta para teste")
            print(f"[TESTE] Aguardando ativação do trailing...")
            print(f"[TESTE] Objetivo: Ativar em {self.current_trailing_activation_pontos:.0f} pts (${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f})")
    
    def _display_status(self, cycle: int):
        """
        Display simplificado para teste
        """
        if not self.test_mode:
            return super()._display_status(cycle)
            
        print(f"\n[TRAILING TEST] Ciclo #{cycle} | {self._get_time()}")
        print("="*50)
        
        # Status simplificado
        positions = self.mt5.positions_get(symbol=self.symbol) if self.mt5 else []
        
        if positions:
            pos = positions[0]
            ticket = pos.get('ticket')
            entry = pos.get('price_open', 0)
            profit = pos.get('profit', 0)
            
            # Calcular lucro em pontos
            current_price = entry + profit / (self.point_value * self.volume * self.symbol_point) if profit else entry
            if pos.get('type') == 1:  # SELL
                profit_pontos = (entry - current_price) / self.symbol_point
            else:  # BUY
                profit_pontos = (current_price - entry) / self.symbol_point
                
            profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)
            
            print(f"[TESTE] Posição #{ticket}:")
            print(f"  Entrada: ${entry:.2f} | Atual: ${current_price:.2f}")
            print(f"  Lucro: {profit_pontos:.1f} pts (${profit_dinheiro:.3f})")
            print(f"  Threshold trailing: {self.current_trailing_activation_pontos:.0f} pts (${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.3f})")
            
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
            print(f"[TESTE] Nenhuma posição aberta")
            print(f"[TESTE] Aguardando sinal para abrir posição...")
            
            # Verificar se vai abrir posição
            signal = self._get_simple_signal()
            if signal:
                print(f"[TESTE] Sinal detectado: {signal['type']} - Preparando para abrir...")
            
        print("="*50)


def main():
    print("TESTE DE TRAILING STOP SEM INDICADORES")
    print("OBJETIVO: Testar ativação do trailing")
    print("COMPORTAMENTO: Abre posição imediata")
    print("")
    
    # Criar agente de teste
    agent = GoldTrailingTest(
        symbol='XAUUSDc',
        volume=0.05,
        check_interval=2,
        trailing_activation_atr_multiplier=0.01,  # Ultra baixo
        trailing_distance_atr_multiplier=0.005,   # Ultra baixo
        stop_loss_atr_multiplier=1.0,
        use_buy=True,
        use_sell=True
    )
    
    print("")
    print("CONFIGURAÇÕES DO TESTE:")
    print(f"- ATR forçado: {agent.current_atr:.0f} pts")
    print(f"- Trailing ativa em: {agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos):.3f}")
    print(f"- Trailing distância: {agent._pontos_para_dinheiro(agent.current_trailing_distance_pontos):.3f}")
    print(f"- Volume: {agent.volume}")
    print("")
    print("O QUE ESPERAR:")
    print("1. Posição abre em 5-10 segundos")
    print("2. Trailing ativa em 30-60 segundos")
    print("3. Trailing se move com o preço")
    print("4. Logs detalhados de tudo")
    print("")
    print("PARA PARAR: Ctrl+C")
    print("="*60)
    print("")
    
    # Executar teste
    try:
        agent.run()
    except KeyboardInterrupt:
        print(f"\n[TESTE] Teste parado pelo usuário")
        
        # Resumo do teste
        if agent.position_opened_for_test:
            print(f"[TESTE] Resumo:")
            print(f"  - Posição aberta: SIM")
            print(f"  - Tentativas trailing: {agent.trailing_activation_attempts}")
            print(f"  - Teste concluído com sucesso!")
        else:
            print(f"[TESTE] Posição não foi aberta durante o teste")


if __name__ == "__main__":
    main()
