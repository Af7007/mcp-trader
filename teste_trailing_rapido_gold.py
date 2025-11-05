#!/usr/bin/env python3
"""
TESTE DE TRAILING GOLD - VERSÃO CORRIGIDA
Foco em testar ativação e funcionamento do trailing sem problemas de execução
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class GoldTrailingTesteRapido(GoldLossZeroSimple):
    """
    Agente de teste otimizado para trailing - parâmetros conservadores
    """
    
    def __init__(self, *args, **kwargs):
        """
        Configurações conservadoras para evitar "Invalid stops"
        """
        # Configurações conservadoras para Gold
        kwargs.update({
            'trailing_activation_atr_multiplier': 0.05,  # 5% do ATR
            'trailing_distance_atr_multiplier': 0.02,   # 2% do ATR  
            'stop_loss_atr_multiplier': 3.0,  # SL conservador (3x ATR)
            'volume': 0.01,  # Volume pequeno
            'check_interval': 5,  # Check a cada 5s
            'use_buy': True,   # BUY permitido
            'use_sell': True   # SELL permitido
        })
        
        print("="*80)
        print("TESTE DE TRAILING GOLD - VERSÃO CORRIGIDA")
        print("="*80)
        print("OBJETIVO: Testar ativação e funcionamento do trailing")
        print("FOCO: Parâmetros conservadores para evitar erros")
        print("")
        print("CONFIGURAÇÕES CONSERVADORAS:")
        print("- SL: 3.0 × ATR (distância segura)")
        print("- Volume: 0.01 lotes (baixo risco)")
        print("- Trailing ativa: 5% do ATR")
        print("- Trailing distância: 2% do ATR")
        print("- BUY/SELL: Seletivo com sinais normais")
        print("")
        
        super().__init__(*args, **kwargs)
        
        # Controles de teste
        self.test_mode = True
        self.trailing_tests = 0
        self.trailing_activations = 0
        self.max_tests = 10  # Testar até 10 ciclos
        
        print(f"[TESTE] ATR calculado: {self.current_atr:.0f} pontos")
        print(f"[TESTE] SL: {self.current_sl_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
        print(f"[TESTE] Trailing ativa: {self.current_trailing_activation_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.3f}")
        print(f"[TESTE] Trailing distância: {self.current_trailing_distance_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_distance_pontos):.3f}")
        print("="*80)
        print("")
    
    def _display_status(self, cycle: int):
        """
        Display otimizado para teste de trailing
        """
        if not self.test_mode:
            return super()._display_status(cycle)
            
        print(f"\n[TESTE TRAILING GOLD] Ciclo #{cycle} | {self._get_time()}")
        print("="*60)
        
        # Status do MT5
        if not self.mt5:
            print("[ERRO] MT5 não conectado")
            return
            
        # Verificar posições abertas
        positions = self.mt5.positions_get(symbol=self.symbol)
        
        if positions:
            for pos in positions:
                ticket = pos.get('ticket')
                pos_type = "BUY" if pos.get('type') == 0 else "SELL"
                entry = pos.get('price_open', 0)
                current = pos.get('price_current', 0)
                profit = pos.get('profit', 0)
                
                # Calcular lucro em pontos
                if pos.get('type') == 0:  # BUY
                    profit_pontos = (current - entry) / self.symbol_point
                else:  # SELL
                    profit_pontos = (entry - current) / self.symbol_point
                    
                profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)
                
                print(f"#{ticket} {pos_type}:")
                print(f"  Entrada: ${entry:.2f} | Atual: ${current:.2f}")
                print(f"  Lucro: {profit_pontos:.1f} pts (${profit_dinheiro:.3f})")
                
                # Status do trailing
                trailing_active = self.positions_trailing_active.get(ticket, False)
                trailing_stop = self.positions_trailing_stop.get(ticket, 0)
                
                if trailing_active:
                    print(f"  STATUS: [TRAILING ATIVO] Stop: ${trailing_stop:.3f}")
                    self.trailing_activations += 1
                    print(f"  Total ativações: {self.trailing_activations}")
                else:
                    threshold = self.current_trailing_activation_pontos
                    falta = threshold - profit_pontos
                    falta_dinheiro = self._pontos_para_dinheiro(falta)
                    
                    if profit_pontos >= threshold:
                        print(f"  STATUS: [ATENÇÃO] Lucro {profit_pontos:.1f} ≥ {threshold:.1f} pts - Trailing deveria estar ativo!")
                    elif profit_pontos > 0:
                        print(f"  STATUS: [AGUARDANDO] Faltam {falta:.1f} pts (${falta_dinheiro:.3f})")
                        print(f"  Threshold: {threshold:.0f} pts = ${self._pontos_para_dinheiro(threshold):.3f}")
                    else:
                        print(f"  STATUS: [NEGATIVO] {profit_pontos:.1f} pts")
                        print(f"  SL: ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
                        
        else:
            print("Nenhuma posição aberta")
            
            # Verificar se está analisando
            signal = self._get_simple_signal()
            if signal:
                print(f"[ANALISE] Sinal: {signal['type']} - Força: {signal.get('strength', 'N/A')}")
            else:
                print("[ANALISE] Aguardando sinais...")
                
        # Resumo do teste
        self.trailing_tests += 1
        print(f"\n[RESUMO] Teste #{self.trailing_tests}/10")
        print(f"  Ativações de trailing: {self.trailing_activations}")
        print(f"  Status: {['OK', 'LIMITE ATINGIDO'][self.trailing_tests >= self.max_tests]}")
        
        # Parar teste se atingiu limite
        if self.trailing_tests >= self.max_tests:
            print(f"\n[TURMINO] Teste concluído após {self.max_tests} ciclos")
            print(f"[RESULTADO] Total de ativações de trailing: {self.trailing_activations}")
            
            if self.trailing_activations > 0:
                print(f"[SUCESSO] Trailing funcionando! {self.trailing_activations} ativações detectadas")
            else:
                print(f"[INFO] Nenhuma ativação - positions podem não ter atingido threshold")
                
            # Finalizar graciosamente
            print(f"\n[FINAL] Finalizando teste...")
            sys.exit(0)
            
        print("="*60)

def main():
    print("TESTE DE TRAILING GOLD - VERSÃO CORRIGIDA")
    print("OBJETIVO: Verificar funcionamento do trailing stop")
    print("MÉTODO: Agente normal com configurações conservadoras")
    print("")
    print("VANTAGENS:")
    print("- Sem forçar posições específicas")
    print("- Parâmetros conservadores para evitar erros")
    print("- Teste automático por 10 ciclos")
    print("- Foco na ativação do trailing")
    print("")
    print("CONFIGURAÇÕES:")
    print("- SL: 3.0 × ATR (distância segura)")
    print("- Volume: 0.01 lotes")
    print("- Trailing ativa: 5% do ATR")
    print("- Check: 5 segundos")
    print("")
    print("PARA PARAR: Ctrl+C")
    print("="*60)
    print("")
    
    # Criar agente de teste
    agent = GoldTrailingTesteRapido(
        symbol='XAUUSDc',
        volume=0.01,
        check_interval=5,
        trailing_activation_atr_multiplier=0.05,
        trailing_distance_atr_multiplier=0.02,
        stop_loss_atr_multiplier=3.0,
        use_buy=True,
        use_sell=True
    )
    
    print("")
    print("INICIANDO TESTE...")
    print("O que esperar:")
    print("1. Agente opera normalmente")
    print("2. Acompanha ativação do trailing")
    print("3. Mostra status a cada 5 segundos")
    print("4. Teste termina automaticamente em 10 ciclos")
    print("")
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print(f"\n[Teste] Parado pelo usuário")
        print(f"Resultados: {agent.trailing_activations} ativações de trailing")
    except SystemExit:
        print(f"\n[Teste] Finalizado normalmente")
        print(f"Resultados: {agent.trailing_activations} ativações de trailing")


if __name__ == "__main__":
    main()
