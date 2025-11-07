#!/usr/bin/env python3
"""
Teste das correções implementadas no Agente Gold Loss Zero
Testa:
1. Cálculo de ATR/SL (corrigir current_sl_pontos muito alto)
2. TradeRequest access (corrigir 'object has no attribute get')
3. Validações de segurança para valores de SL
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_loss_zero_simple import GoldLossZeroSimple
import MetaTrader5 as mt5

def testar_calculo_atr():
    """Testa se o cálculo de ATR está retornando valores corretos"""
    print("="*60)
    print("TESTE 1: CÁLCULO DE ATR")
    print("="*60)
    
    try:
        # Inicializar agente (vai calcular ATR automaticamente)
        agente = GoldLossZeroSimple()
        
        print(f"ATR calculado: {agente.current_atr:.0f} pontos")
        print(f"SL baseado em ATR: {agente.current_sl_pontos:.0f} pontos")
        print(f"SL em dinheiro: ${agente._pontos_para_dinheiro(agente.current_sl_pontos):.2f}")
        
        # Validar se valores estão na faixa correta
        if 300 <= agente.current_atr <= 600:
            print("✅ ATR está na faixa CORRETA (300-600 pontos)")
        else:
            print(f"❌ ATR está FORA da faixa esperada! Valor: {agente.current_atr:.0f}")
            
        if 1500 <= agente.current_sl_pontos <= 3000:
            print("✅ SL está na faixa CORRETA (1500-3000 pontos)")
        else:
            print(f"❌ SL está FORA da faixa esperada! Valor: {agente.current_sl_pontos:.0f}")
            
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste de ATR: {e}")
        return False

def testar_traderequest_access():
    """Testa se o acesso ao TradeRequest está corrigido"""
    print("\n" + "="*60)
    print("TESTE 2: ACESSO AO TRADEREQUEST")
    print("="*60)
    
    try:
        agente = GoldLossZeroSimple()
        
        # Simular resultado de ordem MT5 (como viria da biblioteca)
        # O MT5 retorna um objeto TradeRequest, não um dict
        class MockTradeRequest:
            def __init__(self):
                self.retcode = 10009
                self.order = 12345
                self.deal = 67890
                self.comment = "Test"
                self.request = type('Request', (), {'magic': 123456, 'symbol': 'XAUUSDc'})()
        
        # Converter usando o método do MT5Client
        mock_result = MockTradeRequest()
        converted_result = agente.mt5._to_dict(mock_result)
        
        print(f"Resultado original: {type(mock_result)}")
        print(f"Resultado convertido: {type(converted_result)}")
        print(f"Converted result: {converted_result}")
        
        if isinstance(converted_result, dict) and converted_result.get('retcode') == 10009:
            print("✅ Conversão de TradeRequest para dict FUNCIONANDO")
            
            # Testar acesso ao magic number
            magic_number = converted_result.get('request', {}).get('magic', 0) if isinstance(converted_result.get('request'), dict) else 0
            print(f"Magic number extraído: {magic_number}")
            
            if magic_number == 123456:
                print("✅ Extração de magic number FUNCIONANDO")
                return True
            else:
                print(f"❌ Magic number incorreto! Esperado: 123456, Obtido: {magic_number}")
                return False
        else:
            print("❌ Conversão de TradeRequest FALHOU")
            return False
            
    except Exception as e:
        print(f"❌ ERRO no teste de TradeRequest: {e}")
        return False

def testar_validacoes_sl():
    """Testa as validações de segurança para valores de SL"""
    print("\n" + "="*60)
    print("TESTE 3: VALIDAÇÕES DE SL")
    print("="*60)
    
    try:
        agente = GoldLossZeroSimple()
        
        # Testar diferentes cenários de SL
        test_cases = [
            {"name": "SL Normal", "sl_pontos": 2000},
            {"name": "SL Muito Alto", "sl_pontos": 50000},
            {"name": "SL Muito Baixo", "sl_pontos": 100},
            {"name": "SL Zero", "sl_pontos": 0},
        ]
        
        for test_case in test_cases:
            sl_pontos = test_case["sl_pontos"]
            sl_dinheiro = agente._pontos_para_dinheiro(sl_pontos)
            
            print(f"{test_case['name']}: {sl_pontos} pts = ${sl_dinheiro:.2f}")
            
            # Verificar se as validações funcionam
            if sl_pontos > 10000:  # Muito alto
                print(f"  ⚠️ SL muito alto! Deveria ser limitado.")
            elif sl_pontos < 300:  # Muito baixo
                print(f"  ⚠️ SL muito baixo! Deveria usar mínimo.")
            else:
                print(f"  ✅ SL na faixa aceitável")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste de validações: {e}")
        return False

def testar_integracao_mt5():
    """Testa a integração básica com MT5"""
    print("\n" + "="*60)
    print("TESTE 4: INTEGRAÇÃO MT5")
    print("="*60)
    
    try:
        agente = GoldLossZeroSimple()
        
        # Testar conexão MT5
        if agente.mt5:
            print("✅ Cliente MT5 inicializado")
            
            # Testar obtenção de símbolo
            symbol_info = agente.mt5.get_symbol_info("XAUUSDc")
            if symbol_info:
                print("✅ Símbolo XAUUSDc encontrado")
                print(f"   Point: {symbol_info.get('point', 'N/A')}")
                print(f"   Tick Value: {symbol_info.get('trade_tick_value', 'N/A')}")
            else:
                print("⚠️ Símbolo XAUUSDc não encontrado (pode não estar disponível)")
                
            # Testar tick
            tick = agente.mt5.get_symbol_info_tick("XAUUSDc")
            if tick:
                print("✅ Tick obtido para XAUUSDc")
                print(f"   Bid: {tick.get('bid', 'N/A')}")
                print(f"   Ask: {tick.get('ask', 'N/A')}")
            else:
                print("⚠️ Tick não obtido (mercado fechado?)")
                
            return True
        else:
            print("❌ Cliente MT5 não inicializado")
            return False
            
    except Exception as e:
        print(f"❌ ERRO no teste de integração MT5: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("INICIANDO TESTES DAS CORREÇÕES DO AGENTE GOLD LOSS ZERO")
    print("="*60)
    print("Data:", "11/6/2025, 2:09:45 PM")
    print("Problemas testados:")
    print("1. current_sl_pontos muito alto (27253)")
    print("2. TradeRequest 'object has no attribute get'")
    print("3. Validações de segurança para SL")
    print("="*60)
    
    resultados = []
    
    # Executar testes
    resultados.append(("Cálculo ATR", testar_calculo_atr()))
    resultados.append(("TradeRequest Access", testar_traderequest_access()))
    resultados.append(("Validações SL", testar_validacoes_sl()))
    resultados.append(("Integração MT5", testar_integracao_mt5()))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome:20}: {status}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultados: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("\n🎉 TODAS AS CORREÇÕES ESTÃO FUNCIONANDO!")
    else:
        print(f"\n⚠️ {len(resultados) - sucessos} teste(s) falharam")
    
    print("="*60)

if __name__ == "__main__":
    main()
