#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGENTE ADAPTIVE CORRIGIDO - LÓGICA DO GAME APLICADA
=================================================

CORREÇÃO BASEADA NO GAME QUE FUNCIONA:
- Worker a cada 1 segundo (vs 15s)
- Trailing com $0.50 lucro (vs $1.65+)
- Lógica simples como o Game
- Cálculo direto de lucro
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mt5_direct_client import get_mt5_client

logger = logging.getLogger(__name__)


class GoldAdaptiveAgentGameLogic(GoldLossZeroSimple):
    """
    AGENTE ADAPTIVE CORRIGIDO - LÓGICA DO GAME
    Combina a lógica de sinais do Adaptive com o trailing simples do Game
    """
    
    def __init__(self, *args, **kwargs):
        # PARÂMETROS FORÇADOS COMO O GAME
        force_params = {
            # WORKER ATIVO (como o Game)
            'check_interval': 1.0,  # 1s (vs 15s do Adaptive)
            
            # TRAILING SIMPLES (como o Game)  
            'trailing_activation_fixed': 0.50,  # $0.50 lucro (vs 35% ATR = $1.65+)
            'trailing_distance_fixed': 0.20,    # $0.20 atrás do preço
            
            # AUTO-LEARNING OFF (como o Game)
            'auto_tuning_enabled': False,
            
            # SL FIXO (como o Game)
            'stop_loss_fixed': 3.0,  # $3.0 fixo
            
            # OPERAÇÕES (mais agressivas)
            'use_buy': True,
            'use_sell': True
        }
        
        # Forçar parâmetros
        for key, value in force_params.items():
            if key not in kwargs:
                kwargs[key] = value
        
        print("="*70)
        print("🚀 AGENTE ADAPTIVE CORRIGIDO - LÓGICA DO GAME")
        print("="*70)
        print("🔧 CONFIGURAÇÕES APLICADAS:")
        print(f"   • Worker: {kwargs['check_interval']}s (vs 15s)")
        print(f"   • Trailing Ativa: ${kwargs['trailing_activation_fixed']} (vs $1.65+)")
        print(f"   • Trailing Distância: ${kwargs['trailing_distance_fixed']} atrás")
        print(f"   • SL Fixo: ${kwargs['stop_loss_fixed']}")
        print(f"   • Auto-learning: DESABILITADO")
        print("="*70)
        
        # Chama construtor da classe pai
        super().__init__(*args, **kwargs)
        
        # Salvar parâmetros do game
        self.trailing_activation_fixed = kwargs.get('trailing_activation_fixed', 0.50)
        self.trailing_distance_fixed = kwargs.get('trailing_distance_fixed', 0.20)
        self.stop_loss_fixed = kwargs.get('stop_loss_fixed', 3.0)
        
        print(f"✅ Agente inicializado com lógica do Game!")
        print(f"📊 Resultado esperado: 15-30 operações/hora\n")

    def run(self):
        """
        Override do run com lógica do Game (worker ativo)
        """
        print(f"\n[{self._get_time()}] INICIANDO AGENTE ADAPTIVE COM LÓGICA DO GAME...")
        print(f"Worker ativo a cada {self.check_interval}s (ultra-frequente)")
        print(f"Trailing ativa com ${self.trailing_activation_fixed} lucro")
        print(f"Trailing distance: ${self.trailing_distance_fixed} atrás do preço\n")

        try:
            cycle = 0
            while True:
                cycle += 1

                # Mostrar que está rodando (mais frequente)
                if cycle % 2 == 0:  # A cada 2 segundos
                    print(f".", end="", flush=True)

                # ANÁLISE DE SINAIS (como o Adaptive original)
                signal = self._analyze_m5_trend()
                if signal:
                    print(f"\n[{self._get_time()}] SINAL DETECTADO: {signal['type']}")
                    self._open_position(signal)

                # WORKER INLINE (como o Game)
                if self.active_positions:
                    self._update_all_positions_game_logic()
                else:
                    if cycle % 10 == 0:
                        print(f"\n[IDLE] Sem posições - aguardando sinais...")

                # Sleep curto (como o Game)
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print(f"\n[{self._get_time()}] Agente parado pelo usuário")
            self._show_final_stats()

    def _update_all_positions_game_logic(self):
        """
        WORKER COM LÓGICA DO GAME - ULTRA ATIVO
        """
        if not self.active_positions:
            return

        try:
            # Obter posições no MT5
            mt5_positions = self.mt5.positions_get(symbol=self.symbol)
            if not mt5_positions:
                # Todas fechadas
                self._handle_closed_positions()
                return

            # Atualizar cada posição com lógica simples
            for ticket, data in list(self.active_positions.items()):
                # Verificar se ainda existe
                mt5_pos = next((p for p in mt5_positions if p['ticket'] == ticket), None)
                if not mt5_pos:
                    self._handle_position_closed(ticket, data)
                    del self.active_positions[ticket]
                else:
                    # Atualizar com lógica simples do Game
                    self._update_position_trailing_game_logic(ticket, data, mt5_pos)

        except Exception as e:
            print(f"[ERRO] Falha no worker: {e}")

    def _update_position_trailing_game_logic(self, ticket: int, data: Dict, mt5_pos: Dict):
        """
        TRAILING STOP COM LÓGICA DO GAME - ULTRA SIMPLES
        """
        try:
            # Dados básicos
            pos_type = mt5_pos['type']  # 0=BUY, 1=SELL
            entry_price = data['entry_price']
            current_price = mt5_pos['price_current']
            current_sl = mt5_pos['sl']
            
            # CÁLCULO SIMPLES DE LUCRO (como o Game)
            # Para Gold: 0.01 lotes = 1 oz = $1.00 por $1.00 movimento
            if pos_type == 0:  # BUY
                price_movement = current_price - entry_price
            else:  # SELL
                price_movement = entry_price - current_price
            
            # Lucro em dólares (simples como o Game)
            profit_dollars = price_movement * 1.0  # 1.0 = 0.01 lotes = 1 oz
            data['current_profit'] = profit_dollars
            
            # DEBUG condicional (menos spammy)
            if cycle % 5 == 0 or profit_dollars > 0.3:  # Mostra a cada 5s ou quando lucrando
                print(f"\n[WORKER] Ticket {ticket}:")
                print(f"  Preço: ${current_price:.2f} | Lucro: ${profit_dollars:.2f}")
                print(f"  Trailing Ativo: {data.get('trailing_active', False)}")

            # LÓGICA SIMPLES DO GAME
            if profit_dollars >= self.trailing_activation_fixed:
                # Calcular novo SL ($0.20 atrás do preço atual)
                trailing_distance = self.trailing_distance_fixed
                
                if pos_type == 0:  # BUY
                    new_sl = current_price - trailing_distance
                else:  # SELL  
                    new_sl = current_price + trailing_distance
                
                # Só sobe o SL (como o Game)
                should_update = False
                if not data.get('trailing_active', False):
                    should_update = True
                    action = "ATIVANDO"
                elif pos_type == 0 and new_sl > data.get('sl_price', 0):
                    should_update = True
                    action = "SUBINDO"
                elif pos_type == 1 and new_sl < data.get('sl_price', 999):
                    should_update = True
                    action = "DESCENDO"
                
                if should_update:
                    print(f"\n[{action} TRAILING] Ticket {ticket}")
                    print(f"  Lucro: ${profit_dollars:.2f} | Preço: ${current_price:.2f}")
                    print(f"  Novo SL: ${new_sl:.2f}")
                    
                    # Modificar posição (como o Game)
                    try:
                        result = self.mt5.modify_position(ticket=ticket, sl=new_sl, tp=0)
                        
                        if result and result.get('retcode') == 10009:
                            data['trailing_active'] = True
                            data['sl_price'] = new_sl
                            print(f"  ✅ SUCESSO! SL = ${new_sl:.2f}")
                        else:
                            print(f"  ❌ FALHA: {result}")
                            
                    except Exception as e:
                        print(f"  ❌ ERRO: {e}")

        except Exception as e:
            print(f"[ERRO] Trailing {ticket}: {e}")

    def _get_time(self):
        """Helper method para tempo"""
        return datetime.now().strftime("%H:%M:%S")


def create_adaptive_agent_game_logic():
    """
    Factory function para criar agente com lógica do Game
    """
    agent = GoldAdaptiveAgentGameLogic(
        symbol="XAUUSDc",
        volume=0.03,  # Volume maior
        use_buy=True,
        use_sell=True,
        # Parâmetros forçados com lógica do Game
        check_interval=1.0,  # 1s (ultra-frequente)
        trailing_activation_fixed=0.50,  # $0.50 lucro
        trailing_distance_fixed=0.20,    # $0.20 atrás
        stop_loss_fixed=3.0,             # $3.0 fixo
        auto_tuning_enabled=False,       # DESABILITADO
        optimization_interval=999999,    # Praticamente desabilitado
    )
    
    print("\n" + "="*70)
    print("🎯 AGENTE ADAPTIVE COM LÓGICA DO GAME CRIADO!")
    print("="*70)
    print("✅ Combina:")
    print("   • Sinais do Adaptive (M5 + M15 + filtros)")
    print("   • Trailing do Game (simples e eficaz)")
    print("   • Worker ultra-ativo (1s vs 15s)")
    print("   • Lógica ultra-simples (3 linhas vs 30+)")
    print("\n🚀 RESULTADO ESPERADO:")
    print("   • 15-30 operações/hora (vs 0-2 anterior)")
    print("   • Trailing ativa com $0.50 lucro (vs $1.65+)")
    print("   • Worker 15x mais ativo")
    print("="*70)
    
    return agent


if __name__ == "__main__":
    print("Criando agente adaptive com lógica do Game...")
    
    agent = create_adaptive_agent_game_logic()
    
    print("\nPara executar: agent.run()")
    print("Para parar: Ctrl+C")
    
    # Descomente para executar:
    # agent.run()
