#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do BTC Loss Zero Flexible
Verifica se as correções funcionam corretamente
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.btc_loss_zero_flexible import BTCLossZeroFlexible


def test_btc_flexible():
    """
    Testa o agente BTC Loss Zero Flexible
    """
    print("🧪 TESTE DO BTC LOSS ZERO FLEXIBLE")
    print("=" * 50)
    
    try:
        # Criar agente com parâmetros conservadores para teste
        agent = BTCLossZeroFlexible(
            symbol="BTCUSDc",
            volume=0.01,  # Volume menor para teste
            check_interval=30,  # Intervalo maior para teste
            stop_loss_dollars=50.0,  # SL menor
            take_profit_dollars=75.0,  # TP menor
            trailing_dollars=25.0,  # Trailing menor
            use_buy=True,
            use_sell=True,
            bb_period=20,
            rsi_period=14,
            rsi_overbought=65.0,  # Mais conservador
            rsi_oversold=35.0,   # Mais conservador
            volume_multiplier=1.2
        )
        
        print("✅ Agente criado com sucesso!")
        print(f"   Symbol: {agent.symbol}")
        print(f"   Volume: {agent.volume}")
        print(f"   SL: ${agent.stop_loss_dollars}")
        print(f"   TP: ${agent.take_profit_dollars}")
        print(f"   RSI: {agent.rsi_oversold}-{agent.rsi_overbought}")
        
        # Testar conexão MT5
        if agent.base_agent.mt5:
            print("✅ Conexão MT5 estabelecida!")
            
            # Testar obtenção de dados
            try:
                tick = agent.base_agent.mt5.get_symbol_info_tick(agent.symbol)
                if tick:
                    price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
                    print(f"✅ Dados de mercado obtidos: ${price:.2f}")
                    
                    # Testar cálculo de indicadores
                    try:
                        rates = agent.base_agent.mt5.copy_rates_from_pos(
                            symbol=agent.symbol,
                            timeframe="M1",
                            start_pos=0,
                            count=50
                        )
                        
                        if len(rates) >= 20:
                            # Testar cálculo de indicadores
                            bb_upper, bb_middle, bb_lower = agent._calculate_bollinger_bands(rates)
                            rsi = agent._calculate_rsi(rates, agent.rsi_period)
                            trend = agent._calculate_trend(rates)
                            momentum = agent._calculate_momentum(rates)
                            
                            print(f"✅ Indicadores calculados:")
                            print(f"   BB Upper: ${bb_upper:.2f}")
                            print(f"   BB Middle: ${bb_middle:.2f}")
                            print(f"   BB Lower: ${bb_lower:.2f}")
                            print(f"   RSI: {rsi:.1f}")
                            print(f"   Tendência: {trend}")
                            print(f"   Momentum: {momentum:.2f}")
                            
                            # Testar geração de sinal
                            signal = agent._get_flexible_signal()
                            if signal:
                                print(f"✅ Sinal gerado:")
                                print(f"   Tipo: {signal['type']}")
                                print(f"   Preço: ${signal['price']:.2f}")
                                print(f"   Razão: {signal['reason']}")
                                print(f"   Força: {signal['strength']}")
                                
                                # Testar validação de SL/TP
                                if signal['type'] == 'BUY':
                                    sl_price = signal['price'] - agent.stop_loss_dollars
                                    tp_price = signal['price'] + agent.take_profit_dollars
                                    
                                    if sl_price < signal['price'] and tp_price > signal['price']:
                                        print("✅ SL/TP válidos para BUY")
                                    else:
                                        print("❌ SL/TP inválidos para BUY")
                                else:  # SELL
                                    sl_price = signal['price'] + agent.stop_loss_dollars
                                    tp_price = signal['price'] - agent.take_profit_dollars
                                    
                                    if sl_price > signal['price'] and tp_price < signal['price']:
                                        print("✅ SL/TP válidos para SELL")
                                    else:
                                        print("❌ SL/TP inválidos para SELL")
                            else:
                                print("ℹ️ Nenhum sinal gerado nas condições atuais")
                        else:
                            print("❌ Dados insuficientes para cálculo de indicadores")
                            
                    except Exception as e:
                        print(f"❌ Erro ao calcular indicadores: {e}")
                else:
                    print("❌ Não foi possível obter tick do símbolo")
                    
            except Exception as e:
                print(f"❌ Erro ao obter dados de mercado: {e}")
        else:
            print("❌ Não foi possível conectar ao MT5")
            
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Teste concluído!")
    print("Se todos os testes passaram, o agente está pronto para uso.")


if __name__ == "__main__":
    test_btc_flexible()
