#!/usr/bin/env python3
"""
Diagnóstico do Problema de Trailing Stop no Gold
Problema: Ordem chegou a $5 de lucro mas trailing não ativa
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.mt5_direct_client import get_mt5_client

def diagnosticar_trailing():
    """
    Diagnostica por que o trailing não ativa em $5 de lucro
    """
    print("🔍 DIAGNÓSTICO DE TRAILING STOP - GOLD")
    print("="*60)
    
    mt5 = get_mt5_client()
    symbol = "XAUUSDc"
    
    try:
        # 1. Verificar ATR atual
        print("\n1. 📊 ATR ATUAL:")
        rates = mt5.copy_rates_from_pos(
            symbol=symbol,
            timeframe="M5",
            start_pos=0,
            count=20
        )
        
        if rates and len(rates) >= 14:
            atr = calcular_atr(rates[:14])
            print(f"   ATR calculado: {atr:.0f} pontos")
            
            # Thresholds baseados em ATR
            trailing_activation_pontos = atr * 0.35  # padrão 0.35
            trailing_distance_pontos = atr * 0.13    # padrão 0.13
            
            print(f"   Trailing activation: {trailing_activation_pontos:.0f} pontos")
            print(f"   Trailing distance: {trailing_distance_pontos:.0f} pontos")
            
            # Verificar ponto value
            symbol_info = mt5.get_symbol_info(symbol)
            if symbol_info:
                symbol_point = symbol_info.get('point', 0.001)
                tick_value = symbol_info.get('trade_tick_value', 0.1)
                print(f"   Symbol point: {symbol_point}")
                print(f"   Tick value: ${tick_value:.4f}")
                print(f"   Com volume 0.02: 1 ponto = ${tick_value * 0.02:.4f}")
                
                # Converter thresholds para dinheiro
                trailing_activation_dinheiro = trailing_activation_pontos * tick_value * 0.02
                trailing_distance_dinheiro = trailing_distance_pontos * tick_value * 0.02
                
                print(f"\n   💰 THRESHOLDS EM DINHEIRO (volume 0.02):")
                print(f"   Trailing ativa em: ${trailing_activation_dinheiro:.2f}")
                print(f"   Trailing distância: ${trailing_distance_dinheiro:.2f}")
                
                # PROBLEMA IDENTIFICADO?
                if trailing_activation_dinheiro > 5.0:
                    print(f"\n   ❌ PROBLEMA ENCONTRADO!")
                    print(f"   Threshold ${trailing_activation_dinheiro:.2f} > $5.00")
                    print(f"   Por isso não ativa com $5 de lucro!")
                else:
                    print(f"\n   ✅ Threshold OK - deveria ativar com $5")
        
        # 2. Verificar posições abertas
        print("\n2. 📈 POSIÇÕES ABERTAS:")
        positions = mt5.positions_get(symbol=symbol)
        
        if positions:
            for pos in positions:
                ticket = pos.get('ticket')
                entry_price = pos.get('price_open')
                current_price = pos.get('price_current')
                profit = pos.get('profit')
                pos_type = pos.get('type')
                
                print(f"   Ticket: {ticket}")
                print(f"   Entry: ${entry_price:.2f}")
                print(f"   Current: ${current_price:.2f}")
                print(f"   Profit: ${profit:.2f}")
                
                if pos_type == 0:
                    direction = "BUY"
                    price_diff = current_price - entry_price
                else:
                    direction = "SELL"  
                    price_diff = entry_price - current_price
                    
                print(f"   Direction: {direction}")
                print(f"   Price diff: ${price_diff:.4f}")
                
                # Converter diferença para pontos
                if 'symbol_info' in locals():
                    pontos = price_diff / symbol_point
                    print(f"   Em pontos: {pontos:.0f} pts")
                    
                    # Verificar se deveria ativar
                    should_activate = pontos >= trailing_activation_pontos
                    print(f"   Deveria ativar trailing? {'SIM' if should_activate else 'NÃO'}")
                    
                    if should_activate:
                        print(f"   ❌ URGENTE: Deveria ter ativado mas não ativou!")
                    else:
                        print(f"   ✅ OK: Ainda não atingiu threshold")
                        
        else:
            print("   Nenhuma posição aberta")
        
        # 3. Verificar histórico recente
        print("\n3. 📜 HISTÓRICO RECENTE:")
        from datetime import datetime, timedelta
        
        date_from = datetime.now() - timedelta(hours=2)
        deals = mt5.history_deals_get(date_from=date_from, date_to=datetime.now())
        
        if deals:
            recent_deals = deals[-3:]  # últimos 3 deals
            for deal in recent_deals:
                entry_type = deal.get('entry', 0)
                if entry_type == 1:  # DEAL_ENTRY_OUT = fechamento
                    ticket = deal.get('position_id')
                    profit = deal.get('profit', 0)
                    reason = deal.get('comment', '')
                    print(f"   Ticket {ticket}: ${profit:.2f} - {reason}")
        else:
            print("   Nenhum deal recente")
            
        # 4. Recomendações
        print("\n4. 🔧 RECOMENDAÇÕES:")
        
        if 'trailing_activation_dinheiro' in locals() and trailing_activation_dinheiro > 5.0:
            print("   SOLUÇÃO 1: Reduzir threshold de ativação")
            print(f"   Atual: {trailing_activation_pontos:.0f} pts (${trailing_activation_dinheiro:.2f})")
            novo_threshold_pontos = 200  # ~$2-3 de ativação
            novo_threshold_dinheiro = novo_threshold_pontos * tick_value * 0.02
            print(f"   Novo: {novo_threshold_pontos:.0f} pts (${novo_threshold_dinheiro:.2f})")
            
            print("\n   SOLUÇÃO 2: Usar modo agressivo")
            print("   aggressive_profit_mode=True ativa trailing em ~$2.40")
            
        else:
            print("   ✅ Threshold parece correto")
            print("   Verificar lógica de ativação no código")
            print("   Pode ser problema de thread/concurrency")
            
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

def calcular_atr(rates):
    """Calcula ATR simples"""
    try:
        true_ranges = []
        for i in range(1, min(14, len(rates))):
            high = rates[i-1]['high']
            low = rates[i-1]['low']
            prev_close = rates[i]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        atr_preco = sum(true_ranges) / len(true_ranges)
        atr_pontos = atr_preco / 0.001  # symbol_point Gold
        
        return max(atr_pontos, 400.0)  # mínimo 400 pontos
    except:
        return 400.0

if __name__ == "__main__":
    diagnosticar_trailing()
