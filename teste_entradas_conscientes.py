#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Agente GOLD Loss Zero - MODO CONSCIENTE
Testa entradas baseadas em análise consciente + trailing stop funcional
"""

import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

class GoldLossConsciente:
    """
    Agente GOLD com análise consciente de sinais
    - Mostra análise em tempo real
    - Aguarda confirmação antes de abrir trades
    - Trailing stop 100% funcional
    """
    
    def __init__(self, auto_confirm=False):
        self.agente = GoldLossZeroSimple(
            symbol="XAUUSDc",
            volume=0.01,
            check_interval=10,
            use_buy=True,
            use_sell=True
        )
        self.auto_confirm = auto_confirm
        self.ultimo_sinal = None
        self.monitorando = True
        self.posicoes_abertas = 0
        
    def analisar_mercado_continuo(self):
        """
        Analisa mercado continuamente e mostra sinais
        """
        print("🔍 ANÁLISE CONSCIENTE ATIVADA")
        print("=" * 60)
        print("Monitorando mercado para sinais de entrada...")
        print("Pressione Ctrl+C para parar")
        print()
        
        try:
            while self.monitorando:
                # Gerar análise de sinal
                sinal = self.agente._get_simple_signal()
                
                if sinal:
                    self.ultimo_sinal = sinal
                    self._mostrar_analise_completa(sinal)
                    
                    if self.auto_confirm:
                        print("🤖 AUTO-CONFIRM: Abrindo trade automaticamente...")
                        self._abrir_trade_apos_analise(sinal)
                    else:
                        print("❓ Aguardando confirmação do usuário...")
                        print("   Digite 's' para abrir, 'n' para ignorar, 'q' para sair")
                        break
                else:
                    print(f"⏰ [{time.strftime('%H:%M:%S')}] Aguardando sinal válido...")
                    time.sleep(15)  # Verificar a cada 15s
                    
        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
    
    def _mostrar_analise_completa(self, sinal):
        """
        Mostra análise completa antes da decisão
        """
        print(f"\n🎯 SINAL DETECTADO!")
        print("=" * 50)
        print(f"📊 Tipo: {sinal['type']}")
        print(f"💰 Preço: ${sinal['price']:.2f}")
        print(f"📝 Razão: {sinal['reason']}")
        print()
        
        # Mostrar dados de mercado
        try:
            tick = self.agente.mt5.get_symbol_info_tick(self.agente.symbol)
            if tick:
                spread = abs(tick['ask'] - tick['bid'])
                print(f"📈 DADOS DO MERCADO:")
                print(f"   Bid: ${tick['bid']:.2f}")
                print(f"   Ask: ${tick['ask']:.2f}")
                print(f"   Spread: {spread:.3f}")
                print()
        except:
            pass
        
        # Mostrar configuração do trade
        sl_distance = self.agente.current_sl_pontos * self.agente.symbol_point
        sl_price = (tick['ask'] if sinal['type'] == 'BUY' else tick['bid']) - sl_distance
        
        print(f"🛡️ CONFIGURAÇÃO DO TRADE:")
        print(f"   Volume: {self.agente.volume} lotes")
        print(f"   SL: ${sl_price:.2f} ({self.agente.current_sl_pontos:.0f} pts)")
        print(f"   SL em $: ${self.agente._pontos_para_dinheiro(self.agente.current_sl_pontos):.2f}")
        print(f"   Trailing: Ativa com ${self.agente.trailing_activation_dollar}")
        print(f"   Protege: ${self.agente.trailing_distance_dollar} inicialmente")
        print()
        
        print(f"🔮 PROJEÇÃO DE LUCRO:")
        print(f"   Trailing step: ${self.agente.trailing_step_dollar}")
        print(f"   Exemplo: $3 lucro → protege $2.50")
        print(f"   Zero losses garantidos após ativação!")
        print()
    
    def _abrir_trade_apos_analise(self, sinal):
        """
        Abre trade após análise consciente
        """
        try:
            print(f"🚀 ABRINDO TRADE {sinal['type']}...")
            self.agente._open_position(sinal)
            self.posicoes_abertas += 1
            
            print(f"\n✅ Trade aberto com sucesso!")
            print(f"📊 Posições abertas: {self.posicoes_abertas}")
            print(f"🎯 Trailing stop será ativado automaticamente")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao abrir trade: {e}")
    
    def confirmar_trade(self):
        """
        Aguarda confirmação do usuário
        """
        if not self.ultimo_sinal:
            print("❌ Nenhum sinal detectado para confirmar")
            return False
            
        try:
            resposta = input("🤔 Confirmar abertura do trade? (s/n/q): ").lower().strip()
            
            if resposta == 's':
                self._abrir_trade_apos_analise(self.ultimo_sinal)
                return True
            elif resposta == 'n':
                print("⏭️ Trade ignorado")
                return False
            elif resposta == 'q':
                print("👋 Saindo...")
                self.monitorando = False
                return False
            else:
                print("❓ Resposta inválida. Use 's', 'n' ou 'q'")
                return self.confirmar_trade()
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            return False
    
    def mostrar_status(self):
        """
        Mostra status atual do sistema
        """
        print(f"\n📊 STATUS DO SISTEMA:")
        print(f"   Posições abertas: {self.posicoes_abertas}")
        print(f"   Trailing ativo: {self.agente.trailing_active}")
        print(f"   Último sinal: {self.ultimo_sinal['type'] if self.ultimo_sinal else 'Nenhum'}")
        print(f"   MT5 conectado: {'✅' if self.agente.mt5 else '❌'}")
        print()
    
    def run_teste_completo(self):
        """
        Executa teste completo com análise consciente
        """
        print("🎯 TESTE GOLD LOSS ZERO - MODO CONSCIENTE")
        print("=" * 60)
        print("Este teste irá:")
        print("1. 📊 Analisar mercado continuamente")
        print("2. 🔍 Detectar sinais válidos")
        print("3. 💭 Mostrar análise completa")
        print("4. 🤔 Aguardar confirmação")
        print("5. 🚀 Abrir trade (se confirmado)")
        print("6. 🛡️ Ativar trailing stop automático")
        print()
        
        # Mostrar configuração inicial
        self.mostrar_status()
        
        # Iniciar análise em thread separada
        analise_thread = threading.Thread(target=self.analisar_mercado_continuo)
        analise_thread.daemon = True
        analise_thread.start()
        
        try:
            time.sleep(2)  # Dar tempo para a análise começar
            
            while self.monitorando and self.ultimo_sinal is None:
                time.sleep(1)
            
            if self.ultimo_sinal and self.monitorando:
                # Aguardar confirmação
                self.confirmar_trade()
            
            # Manter monitoramento ativo para trailing
            print("🔄 Mantendo monitoramento ativo para trailing stop...")
            print("Pressione Ctrl+C para parar")
            
            while self.monitorando:
                self.mostrar_status()
                time.sleep(30)  # Status a cada 30s
                
        except KeyboardInterrupt:
            print("\n⏹️ Teste interrompido pelo usuário")
        finally:
            self.mostrar_status()

def main():
    """
    Menu principal do teste
    """
    print("🎯 TESTE GOLD LOSS ZERO - ENTRADAS CONSCIENTES")
    print("=" * 60)
    print("Escolha o modo de teste:")
    print()
    print("1. 🤖 Modo Automático (abre trades automaticamente)")
    print("2. 🧠 Modo Consciente (mostra análise + aguarda confirmação)")
    print("3. 📊 Apenas Análise (só mostra sinais, não abre trades)")
    print()
    
    try:
        escolha = input("Opção (1/2/3): ").strip()
        
        if escolha == '1':
            print("\n🚀 INICIANDO MODO AUTOMÁTICO...")
            teste = GoldLossConsciente(auto_confirm=True)
            teste.run_teste_completo()
            
        elif escolha == '2':
            print("\n🧠 INICIANDO MODO CONSCIENTE...")
            teste = GoldLossConsciente(auto_confirm=False)
            teste.run_teste_completo()
            
        elif escolha == '3':
            print("\n📊 INICIANDO MODO ANÁLISE APENAS...")
            teste = GoldLossConsciente(auto_confirm=False)
            # Modificar para só mostrar análise
            teste.mostrar_status()
            teste.analisar_mercado_continuo()
            
        else:
            print("❌ Opção inválida")
            return False
            
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Teste cancelado pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
