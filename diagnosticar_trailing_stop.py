#!/usr/bin/env python3
"""
Script para diagnosticar o problema do trailing stop do BTC LOSS ZERO.
"""

import sys
import time
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_direct_client import get_mt5_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_modify_position():
    """
    Testa a função modify_position diretamente
    """
    print("=== TESTE DIRETO DO modify_position ===")
    
    mt5 = get_mt5_client()
    
    # Verificar conexão
    if not mt5.is_connected():
        print("[ERRO] Nao esta conectado ao MT5")
        return False
    
    print("[OK] Conectado ao MT5")
    
    # Verificar posições abertas do BTC
    positions = mt5.positions_get(symbol="BTCUSDc")
    print(f"[INFO] Posicoes encontradas: {len(positions) if positions else 0}")
    
    if positions:
        for pos in positions:
            print(f"   Ticket: {pos['ticket']}")
            print(f"   Tipo: {'BUY' if pos['type'] == 0 else 'SELL'}")
            print(f"   Preco: ${pos['price_open']:.2f}")
            print(f"   SL atual: ${pos['sl']:.2f}")
            print(f"   TP atual: ${pos['tp']:.2f}")
            print(f"   Profit: ${pos['profit']:.2f}")
            
            # Testar modificação simples do SL
            current_sl = pos['sl']
            new_sl = current_sl - 10.0 if pos['type'] == 0 else current_sl + 10.0
            
            print(f"   [TESTE] Modificacao:")
            print(f"      SL atual: ${current_sl:.2f}")
            print(f"      Novo SL: ${new_sl:.2f}")
            
            result = mt5.modify_position(
                ticket=pos['ticket'],
                sl=new_sl,
                tp=pos['tp']  # Manter TP
            )
            
            if result:
                print(f"   [OK] Modificacao bem-sucedida!")
                print(f"      Retcode: {result.get('retcode')}")
                print(f"      Comment: {result.get('comment', '')}")
            else:
                print(f"   [ERRO] Falha na modificacao")
                error = mt5.last_error()
                print(f"      Erro: {error}")
            
            print()
    else:
        print("[INFO] Nenhuma posicao BTCUSDc encontrada para teste")
    
    return True

def analyze_trailing_calculation():
    """
    Analisa o cálculo do trailing no código do agente
    """
    print("=== ANALISE DO CALCULO DE TRAILING ===")
    
    # Simular cenário real
    symbol = "BTCUSDc"
    mt5 = get_mt5_client()
    
    # Obter tick atual
    tick = mt5.get_symbol_info_tick(symbol)
    if not tick:
        print("[ERRO] Nao foi possivel obter preco atual")
        return False
    
    current_price = tick['bid'] if tick.get('bid', 0) > 0 else tick.get('ask', 0)
    print(f"[INFO] Preco atual: ${current_price:.2f}")
    
    # Simular uma posição BUY fictícia
    entry_price = current_price - 50.0  # $50 abaixo do preço atual (lucro fictício)
    volume = 0.02  # Volume mencionado no log
    
    # Calcular lucro em pontos
    profit_pontos = current_price - entry_price
    profit_dinheiro = profit_pontos * volume  # Aproximação
    
    print(f"[SIMULACAO] Posicao BUY ficticia:")
    print(f"   Preco de entrada: ${entry_price:.2f}")
    print(f"   Lucro atual: {profit_pontos:.1f} pontos")
    print(f"   Lucro aproximado: ${profit_dinheiro:.2f}")
    
    # Simular cálculos do agente
    # trailing_activation_atr_multiplier = 0.3 (do código)
    # trailing_distance_atr_multiplier = 0.2 (do código)
    
    # Simular ATR (valor típico para BTC)
    simulated_atr = 120.0  # pontos
    
    activation_pontos = simulated_atr * 0.3  # 36 pontos
    distance_pontos = simulated_atr * 0.2    # 24 pontos
    
    print(f"[CALCULOS] Trailing:")
    print(f"   ATR simulado: {simulated_atr} pontos")
    print(f"   Ativacao em: {activation_pontos:.0f} pontos")
    print(f"   Distancia: {distance_pontos:.0f} pontos")
    print(f"   Lucro para ativar: ${activation_pontos * volume:.2f}")
    
    # Verificar se ativaria
    trailing_active = profit_pontos >= activation_pontos
    print(f"   Trailing ativo: {'SIM' if trailing_active else 'NAO'}")
    
    if trailing_active:
        # Calcular novo SL
        new_sl = current_price - distance_pontos
        lucro_protegido = profit_pontos - distance_pontos
        
        print(f"   [ATIVADO] Trailing ativado:")
        print(f"      Novo SL: ${new_sl:.2f}")
        print(f"      Lucro protegido: {lucro_protegido:.1f} pontos")
        
        # Mostrar como percentual
        distancia_pct = (distance_pontos / current_price) * 100
        print(f"      Distancia do trailing: {distancia_pct:.3f}%")
    
    print()
    return True

def identify_root_cause():
    """
    Identifica a causa raiz do problema
    """
    print("=== IDENTIFICACAO DA CAUSA RAIZ ===")
    
    print("POSSIVEIS causas do problema:")
    print()
    
    print("1. CALCULO DE DISTANCIA:")
    print("   - No log mostra 'Distancia Trailing: 0.00%'")
    print("   - Isso sugere que self.trailing_distance esta zerado")
    print("   - O calculo pode estar usando percentual em vez de pontos")
    print()
    
    print("2. LOGICA DE ATIVACAO:")
    print("   - Trailing ativa em pontos, nao percentual")
    print("   - Log mostra 'Trailing Ativo: SIM' mas 'Distancia: 0.00%'")
    print("   - Contradicao: se ativo, deveria ter distancia > 0")
    print()
    
    print("3. PROBLEMA NO MODIFY_POSITION:")
    print("   - modify_position pode estar falhando silenciosamente")
    print("   - Erro nao esta sendo mostrado no log")
    print("   - MT5 pode estar rejeitando a ordem")
    print()
    
    print("4. TIMING DE ATUALIZACAO:")
    print("   - Worker pode nao estar executando a cada 2s")
    print("   - Callback pode nao estar sendo chamado")
    print("   - Thread pode ter parado")
    print()
    
    print("PROXIMOS PASSOS:")
    print("1. Verificar se modify_position funciona diretamente")
    print("2. Adicionar mais logging ao agente")
    print("3. Verificar se worker esta ativo")
    print("4. Testar em situacao real")
    
    print()

def main():
    print("DIAGNOSTICO DO PROBLEMA DE TRAILING STOP - BTC LOSS ZERO")
    print("=" * 60)
    print()
    
    try:
        # Teste 1: modify_position direto
        test_modify_position()
        
        # Teste 2: Análise do cálculo
        analyze_trailing_calculation()
        
        # Teste 3: Identificação da causa
        identify_root_cause()
        
    except Exception as e:
        print(f"[ERRO] Erro durante diagnostico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
