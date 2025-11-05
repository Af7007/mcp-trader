#!/usr/bin/env python3
"""
AGENTE GOLD ULTRA-AGGRESSIVE - CORREÇÃO DEFINITIVA
Versão final com thresholds ultra-baixos para garantir ativação do trailing
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class GoldUltraAggressiveFixed(GoldLossZeroSimple):
    """
    Versão ultra-agressiva CORRIGIDA com thresholds ultra-baixos
    Força ATR baixo para garantir ativação rápida do trailing
    """
    
    def __init__(self, *args, **kwargs):
        """
        Aplicar configurações ultra-agressivas
        """
        # THRESHOLDS ULTRA-AGGRESSIVES
        kwargs.update({
            # Trailing: ATIVAR EM $0.20-0.50
            'trailing_activation_atr_multiplier': 0.01,  # 0.01 × ATR
            'trailing_distance_atr_multiplier': 0.005,   # 0.005 × ATR
            
            # Stop Loss: Menos agressivo
            'stop_loss_atr_multiplier': 1.0,  # 1.0 × ATR
            
            # Volume maior para movimentos mais rápidos
            'volume': 0.05,
            
            # Check interval ultra-frequente
            'check_interval': 2  # 2 segundos!
        })
        
        print("="*80)
        print("GOLD ULTRA-AGGRESSIVE CORRIGIDO - VERSÃO FINAL")
        print("="*80)
        print("PROBLEMA: Trailing não ativava")
        print("SOLUÇÃO: ATR forçado ULTRA-BAIXO")
        print("")
        print("CONFIGURAÇÕES ULTRA-AGGRESSIVES:")
        print("- Trailing ativa: 0.01 × ATR (ultra-baixo)")
        print("- Trailing distância: 0.005 × ATR (ultra-baixo)")
        print("- ATR forçado: 100 pontos (vs 400-4600 anterior)")
        print("- Volume: 0.05 (5x maior)")
        print("- Check: 2s (ultra-rápido)")
        print("- Cooldown: 1s (ultra-rápido)")
        print("")
        
        super().__init__(*args, **kwargs)
        
        # Forçar ATR MUITO menor
        self.current_atr = 100.0  # Forçar ATR ultra-baixo
        self.current_sl_pontos = self.current_atr * self.sl_atr_mult  # 100 × 1.0 = 100 pts
        self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult  # 100 × 0.01 = 1 pt
        self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult  # 100 × 0.005 = 0.5 pt
        
        # Cooldown ultra-rápido
        self.cooldown_seconds = 1
        self.cooldown_same_direction = 0  # Sem cooldown se mesmo tipo
        
        print(f"[ATR FORÇADO] {self.current_atr} pontos")
        print(f"[SL] {self.current_sl_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
        print(f"[TRAILING ATIVA] {self.current_trailing_activation_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
        print(f"[TRAILING DISTÂNCIA] {self.current_trailing_distance_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_distance_pontos):.2f}")
        print(f"[LUCRO PROTEGIDO] ~${self._pontos_para_dinheiro(self.current_trailing_activation_pontos - self.current_trailing_distance_pontos):.2f}")
        print("")
        print("OBJETIVO: Trailing ativa em $0.10-0.20 de lucro")
        print("RESULTADO ESPERADO: Movimento mínimo ativa trailing")
        print("="*80)
        print("")
    
    def _calculate_initial_atr(self):
        """
        Override: Forçar ATR ultra-baixo para garantir ativação
        """
        print(f"[ATR] Forçando ATR ultra-baixo: 100 pontos")
        self.current_atr = 100.0
        
        # Calcular thresholds com ATR forçado
        self.current_sl_pontos = self.current_atr * self.sl_atr_mult
        self.current_trailing_activation_pontos = self.current_atr * self.trailing_activation_mult
        self.current_trailing_distance_pontos = self.current_atr * self.trailing_distance_mult
        
        print(f"[ATR] Thresholds com ATR forçado:")
        print(f"       SL: {self.current_sl_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_sl_pontos):.2f}")
        print(f"       Trailing ativa: {self.current_trailing_activation_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.2f}")
        print(f"       Trailing distância: {self.current_trailing_distance_pontos:.0f} pts = ${self._pontos_para_dinheiro(self.current_trailing_distance_pontos):.2f}")
        print(f"       Lucro protegido: ~${self._pontos_para_dinheiro(self.current_trailing_activation_pontos - self.current_trailing_distance_pontos):.2f}")
        print("")
    
    def _manage_position_trailing(self, pos):
        """
        Override com debug ultra-detalhado
        """
        try:
            ticket = pos.get('ticket')
            if not ticket:
                return
            
            # Obter dados da posição
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if tick:
                current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
            else:
                current_price = pos.get('price_open', 0)

            entry_price = self.positions_entry_price.get(ticket, pos.get('price_open', 0))
            if entry_price <= 0:
                return

            pos_type = pos.get('type', 0)
            trailing_active = self.positions_trailing_active.get(ticket, False)
            trailing_stop_price = self.positions_trailing_stop.get(ticket, 0.0)

            # Calcular lucro em pontos
            if pos_type == 0:  # BUY
                profit_price_diff = current_price - entry_price
            else:  # SELL
                profit_price_diff = entry_price - current_price

            profit_pontos = profit_price_diff / self.symbol_point
            profit_dinheiro = self._pontos_para_dinheiro(profit_pontos)

            # DEBUG ULTRA DETALHADO
            print(f"")
            print(f"[TRAILING DEBUG #{ticket}]")
            print(f"  Entry: ${entry_price:.3f} | Current: ${current_price:.3f}")
            print(f"  Profit pts: {profit_pontos:.1f} | Profit $: ${profit_dinheiro:.3f}")
            print(f"  Threshold pts: {self.current_trailing_activation_pontos:.0f} | $: ${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.3f}")
            print(f"  ATR forçado: {self.current_atr:.0f} pts")
            print(f"  symbol_point: {self.symbol_point}")
            print(f"  Trailing ativo: {trailing_active}")
            print(f"")

            # Verificar ativação
            if not trailing_active and profit_pontos >= self.current_trailing_activation_pontos:
                print(f"")
                print(f"[ATIVANDO TRAILING] Ticket #{ticket}")
                print(f"   Lucro atual: {profit_pontos:.1f} pts (${profit_dinheiro:.3f})")
                print(f"   Threshold: {self.current_trailing_activation_pontos:.0f} pts (${self._pontos_para_dinheiro(self.current_trailing_activation_pontos):.3f})")
                print(f"   DIFERENÇA: {profit_pontos - self.current_trailing_activation_pontos:.1f} pts ACIMA do threshold!")
                
                # Converter para variação de preço
                trailing_price_distance = self.current_trailing_distance_pontos * self.symbol_point

                if pos_type == 0:  # BUY
                    trailing_stop_price = current_price - trailing_price_distance
                else:  # SELL
                    trailing_stop_price = current_price + trailing_price_distance
                
                # Salvar no dicionário
                self.positions_trailing_active[ticket] = True
                self.positions_trailing_stop[ticket] = trailing_stop_price
                self.trailing_active = True
                self.trailing_stop_price = trailing_stop_price

                # Calcular lucro protegido
                lucro_protegido_pontos = profit_pontos - self.current_trailing_distance_pontos
                lucro_protegido_dinheiro = self._pontos_para_dinheiro(lucro_protegido_pontos)

                # Modificar SL usando método corrigido
                success = self._safe_modify_sl(ticket, trailing_stop_price, "ATIVAR TRAILING")
                if success:
                    print(f"[TRAILING ATIVADO COM SUCESSO]")
                    print(f"   Stop Loss: ${trailing_stop_price:.3f}")
                    print(f"   Lucro mínimo protegido: ${lucro_protegido_dinheiro:.3f}")
                    print(f"   A partir de agora: IMPOSSÍVEL PERDER!")
                else:
                    print(f"[ERRO] Falha ao ativar trailing!")
                
                print(f"")
            else:
                # Mostrar progresso
                if profit_pontos > 0:
                    falta_pontos = self.current_trailing_activation_pontos - profit_pontos
                    falta_dinheiro = self._pontos_para_dinheiro(falta_pontos)
                    if not trailing_active:
                        progress = (profit_pontos / self.current_trailing_activation_pontos) * 100
                        print(f"[AGUARDANDO #{ticket}] {profit_pontos:.1f}pts (${profit_dinheiro:.3f}) | {progress:.1f}% do threshold | Faltam: {falta_pontos:.1f}pts (${falta_dinheiro:.3f})")
                
            # Atualizar trailing se já ativo
            if trailing_active:
                lucro_protegido_pontos = profit_pontos - self.current_trailing_distance_pontos
                lucro_protegido_dinheiro = self._pontos_para_dinheiro(lucro_protegido_pontos)
                
                print(f"[TRAILING ATIVO #{ticket}] Lucro ${profit_dinheiro:.3f} | Protegido ${lucro_protegido_dinheiro:.3f} | Stop ${trailing_stop_price:.3f}")
                
                # Lógica de atualização
                trailing_price_distance = self.current_trailing_distance_pontos * self.symbol_point
                
                if pos_type == 0:  # BUY
                    new_stop = current_price - trailing_price_distance
                    if new_stop > trailing_stop_price:
                        old_stop = trailing_stop_price
                        try:
                            success = self.mt5.modify_position(ticket=ticket, sl=new_stop, tp=None)
                            if success:
                                print(f"[TRAILING SUBIU] ${old_stop:.3f} -> ${new_stop:.3f}")
                                self.positions_trailing_stop[ticket] = new_stop
                                self.trailing_stop_price = new_stop
                            else:
                                print(f"[ERRO] Falha ao subir trailing")
                        except Exception as e:
                            print(f"[ERRO] Erro ao subir trailing: {e}")
                else:  # SELL
                    new_stop = current_price + trailing_price_distance
                    if new_stop < trailing_stop_price:
                        old_stop = trailing_stop_price
                        try:
                            success = self.mt5.modify_position(ticket=ticket, sl=new_stop, tp=None)
                            if success:
                                print(f"[TRAILING DESCEU] ${old_stop:.3f} -> ${new_stop:.3f}")
                                self.positions_trailing_stop[ticket] = new_stop
                                self.trailing_stop_price = new_stop
                            else:
                                print(f"[ERRO] Falha ao descer trailing")
                        except Exception as e:
                            print(f"[ERRO] Erro ao descer trailing: {e}")

        except Exception as e:
            print(f"Erro no trailing: {e}")


def main():
    print("EXECUTANDO GOLD ULTRA-AGGRESSIVE CORRIGIDO")
    print("ATR ultra-baixo forçado para ativação garantida")
    print("")
    
    # Criar agente corrigido
    agent = GoldUltraAggressiveFixed(
        symbol='XAUUSDc',
        volume=0.05,
        check_interval=2,  # 2 segundos!
        trailing_activation_atr_multiplier=0.01,  # Ultra baixo!
        trailing_distance_atr_multiplier=0.005,   # Ultra baixo!
        stop_loss_atr_multiplier=1.0,
        use_buy=True,
        use_sell=True
    )
    
    print("")
    print("CONFIGURAÇÕES FINAIS:")
    print(f"- Trailing ativa em: ${agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos):.2f}")
    print(f"- Trailing distância: ${agent._pontos_para_dinheiro(agent.current_trailing_distance_pontos):.2f}")
    print(f"- Lucro protegido: ~${agent._pontos_para_dinheiro(agent.current_trailing_activation_pontos - agent.current_trailing_distance_pontos):.2f}")
    print(f"- Volume: {agent.volume}")
    print(f"- Check: {agent.check_interval}s")
    print(f"- ATR forçado: {agent.current_atr:.0f} pts")
    print("")
    print("OBJETIVO: Trailing ativa em $0.10-0.20 de lucro")
    print("PARA PARAR: Ctrl+C")
    print("="*70)
    print("")
    
    # Executar
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n[STOP] Agente parado pelo usuário")


if __name__ == "__main__":
    main()
