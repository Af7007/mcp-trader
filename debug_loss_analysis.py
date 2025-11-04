#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Loss Analysis
Investiga por que ocorreu perda maior que o SL configurado
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

# Database path
DB_PATH = Path(__file__).parent / 'trading.db'
GAME_MAGIC_NUMBER = 777777

def analyze_recent_loss():
    """Analisa a perda recente para entender o que aconteceu"""
    try:
        mt5 = get_mt5_client()
        
        # Get recent deals from MT5
        now = datetime.now()
        yesterday = now - timedelta(hours=6)  # Últimas 6 horas
        
        deals = mt5.history_deals_get(
            date_from=yesterday,
            date_to=now,
            symbol="XAUUSDc"
        )
        
        print("=" * 60)
        print("ANÁLISE DA PERDA RECENTE")
        print("=" * 60)
        
        # Filter by magic number
        game_deals = []
        for deal in deals:
            magic = deal.get('magic', 0)
            if magic == GAME_MAGIC_NUMBER:
                game_deals.append(deal)
        
        print(f"\n[MT5] Found {len(game_deals)} deals with magic {GAME_MAGIC_NUMBER}")
        
        # Group by position to find the problematic trade
        positions = {}
        
        for deal in game_deals:
            pos_id = deal.get('position_id')
            entry_type = deal.get('entry')
            deal_type = deal.get('type')
            deal_profit = deal.get('profit', 0)
            deal_price = deal.get('price', 0)
            deal_time = deal.get('time')
            
            if not pos_id:
                continue
                
            if pos_id not in positions:
                positions[pos_id] = {
                    'ticket': pos_id,
                    'type': None,
                    'volume': 0,
                    'open_price': 0,
                    'close_price': 0,
                    'profit': 0,
                    'open_time': None,
                    'close_time': None,
                    'deals': []
                }
            
            positions[pos_id]['deals'].append({
                'entry': entry_type,
                'type': deal_type,
                'price': deal_price,
                'profit': deal_profit,
                'time': deal_time
            })
            
            if entry_type == 0:  # IN deal
                positions[pos_id]['type'] = 'BUY' if deal_type == 0 else 'SELL'
                positions[pos_id]['volume'] = deal.get('volume', 0)
                positions[pos_id]['open_price'] = deal_price
                positions[pos_id]['open_time'] = deal_time
                
            elif entry_type == 1:  # OUT deal
                positions[pos_id]['profit'] = deal_profit
                positions[pos_id]['close_price'] = deal_price
                positions[pos_id]['close_time'] = deal_time
        
        # Find positions with high losses
        high_losses = []
        for pos_id, pos in positions.items():
            if pos['profit'] < -5:  # Perdas maiores que $5
                high_losses.append(pos)
        
        print(f"\n[ANALYSIS] Found {len(high_losses)} positions with high losses:")
        
        for pos in high_losses:
            print(f"\n[POSITION] Ticket: {pos['ticket']}")
            print(f"[POSITION] Type: {pos['type']}")
            print(f"[POSITION] Volume: {pos['volume']}")
            print(f"[POSITION] Open Price: {pos['open_price']}")
            print(f"[POSITION] Close Price: {pos['close_price']}")
            print(f"[POSITION] Profit: ${pos['profit']:.2f}")
            print(f"[POSITION] Open Time: {pos['open_time']}")
            print(f"[POSITION] Close Time: {pos['close_time']}")
            
            # Calculate price movement
            if pos['type'] == 'BUY':
                price_movement = pos['close_price'] - pos['open_price']
                expected_sl_movement = -5.50 / (pos['volume'] * 100)  # SL de $5.50
            else:  # SELL
                price_movement = pos['open_price'] - pos['close_price']
                expected_sl_movement = -5.50 / (pos['volume'] * 100)  # SL de $5.50
            
            print(f"[POSITION] Price Movement: {price_movement:.5f}")
            print(f"[POSITION] Expected SL Movement: {expected_sl_movement:.5f}")
            print(f"[POSITION] Actual Loss: ${abs(pos['profit']):.2f}")
            print(f"[POSITION] Expected Max Loss: $5.50")
            
            # Check all deals for this position
            print(f"[POSITION] All deals:")
            for deal in pos['deals']:
                print(f"  - Entry: {deal['entry']}, Type: {deal['type']}, Price: {deal['price']}, Profit: ${deal['profit']:.2f}, Time: {deal['time']}")
        
        # Check current positions for trailing issues
        print(f"\n[CURRENT] Checking current positions...")
        current_positions = mt5.positions_get(symbol="XAUUSDc", magic=GAME_MAGIC_NUMBER)
        
        if current_positions:
            for pos in current_positions:
                ticket = pos['ticket']
                pos_type = 'BUY' if pos['type'] == 0 else 'SELL'
                current_price = pos['price_current']
                entry_price = pos['price_open']
                sl = pos['sl']
                profit = (current_price - entry_price) * pos['volume'] * 100 if pos_type == 'BUY' else (entry_price - current_price) * pos['volume'] * 100
                
                print(f"\n[CURRENT] Ticket: {ticket}")
                print(f"[CURRENT] Type: {pos_type}")
                print(f"[CURRENT] Entry: {entry_price}")
                print(f"[CURRENT] Current: {current_price}")
                print(f"[CURRENT] SL: {sl}")
                print(f"[CURRENT] Profit: ${profit:.2f}")
                
                # Check if SL is being respected
                if sl:
                    if pos_type == 'BUY':
                        max_allowed_loss = (entry_price - sl) * pos['volume'] * 100
                    else:
                        max_allowed_loss = (sl - entry_price) * pos['volume'] * 100
                    
                    print(f"[CURRENT] Max Allowed Loss: ${max_allowed_loss:.2f}")
                    
                    if profit < -max_allowed_loss - 1:  # Tolerância de $1
                        print(f"[CURRENT] ⚠️  SL VIOLATION! Loss exceeds configured SL!")
                    else:
                        print(f"[CURRENT] ✅ SL being respected")
        else:
            print("[CURRENT] No open positions found")
        
        return high_losses
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []

def check_trailing_logic():
    """Verifica a lógica do trailing implementada"""
    try:
        print("\n" + "=" * 60)
        print("VERIFICAÇÃO DA LÓGICA DE TRAILING")
        print("=" * 60)
        
        # Simulação do cálculo de trailing
        volume = 0.02
        sl_dollars = 5.50
        entry_price = 4000.0
        
        # Cálculo atual implementado
        sl_price_movement = sl_dollars / (volume * 100)
        
        print(f"[TRAILING] Volume: {volume}")
        print(f"[TRAILING] SL Dollars: ${sl_dollars}")
        print(f"[TRAILING] Entry Price: {entry_price}")
        print(f"[TRAILING] SL Price Movement: {sl_price_movement:.5f}")
        
        # Para BUY
        buy_sl = entry_price - sl_price_movement
        print(f"[TRAILING] BUY SL Price: {buy_sl}")
        
        # Para SELL
        sell_sl = entry_price + sl_price_movement
        print(f"[TRAILING] SELL SL Price: {sell_sl}")
        
        # Verificação
        print(f"[TRAILING] Verificação:")
        print(f"[TRAILING] - Se preço cair {sl_price_movement:.5f} pontos, stop é acionado")
        print(f"[TRAILING] - Loss máxima: ${sl_dollars}")
        
        # Teste com perda de $10.70
        actual_loss = 10.70
        required_movement = actual_loss / (volume * 100)
        print(f"[TRAILING] Para loss de ${actual_loss:.2f}:")
        print(f"[TRAILING] - Movement necessário: {required_movement:.5f}")
        print(f"[TRAILING] - Isso excede o SL de ${sl_dollars} em ${(actual_loss - sl_dollars):.2f}")
        
    except Exception as e:
        print(f"[TRAILING ERROR] {e}")

def main():
    """Função principal"""
    # Analisar perdas recentes
    high_losses = analyze_recent_loss()
    
    # Verificar lógica do trailing
    check_trailing_logic()
    
    print("\n" + "=" * 60)
    print("RECOMENDAÇÕES")
    print("=" * 60)
    
    if high_losses:
        print("\n1. VERIFICAR TRAILING STOP:")
        print("   - O trailing pode não estar funcionando corretamente")
        print("   - Verificar se modify_position está atualizando SL corretamente")
        print("   - Considerar usar close_position em vez de modify_position")
        
        print("\n2. VERIFICAR LÓGICA DE CÁLCULO:")
        print("   - Confirmar fórmula: sl_dollars / (volume * 100)")
        print("   - Verificar se volume está correto")
        print("   - Validar cálculo de profit/loss")
        
        print("\n3. VERIFICAR TIMING:")
        print("   - Pode haver delay na execução do trailing")
        print("   - Mercado pode ter se movido rapidamente")
        print("   - SL pode não ter sido atualizado a tempo")
    
    print("\n4. AÇÕES CORRETIVAS:")
    print("   - Implementar validação de distância mínima")
    print("   - Adicionar logs detalhados do trailing")
    print("   - Testar com diferentes valores de SL")

if __name__ == "__main__":
    main()
