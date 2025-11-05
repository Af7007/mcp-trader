#!/usr/bin/env python3
"""
Verifica última ordem no MT5 e no banco
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import MetaTrader5 as mt5
    if not mt5.initialize():
        print("[ERRO] Falha ao conectar MT5")
        sys.exit(1)
except Exception as e:
    print(f"[ERRO] Nao conseguiu importar MetaTrader5: {e}")
    sys.exit(1)

print("="*80)
print("VERIFICACAO DA ULTIMA ORDEM - MT5 vs BANCO")
print("="*80)

print("\n[1] POSICOES ABERTAS NO MT5:")
print("-"*80)

positions = mt5.positions_get(symbol="XAUUSDc")
if positions:
    for pos in positions:
        print(f"\n  Ticket: {pos.get('ticket')}")
        print(f"  Symbol: {pos.get('symbol')}")
        print(f"  Type: {'BUY' if pos.get('type') == 0 else 'SELL'}")
        print(f"  Volume: {pos.get('volume')}")
        print(f"  Entry Price: ${pos.get('price_open'):.2f}")
        print(f"  Current Price: ${pos.get('price_current'):.2f}")
        print(f"  SL Price: ${pos.get('sl'):.2f}" if pos.get('sl') else "  SL Price: N/A")
        print(f"  TP Price: ${pos.get('tp'):.2f}" if pos.get('tp') else "  TP Price: N/A")
        print(f"  Profit: ${pos.get('profit'):.2f}")
        print(f"  Comment: {pos.get('comment')}")
        
        # Calcular distância SL
        if pos.get('sl'):
            if pos.get('type') == 0:  # BUY
                sl_distance = pos.get('price_open') - pos.get('sl')
            else:  # SELL
                sl_distance = pos.get('sl') - pos.get('price_open')
            print(f"  SL Distance: ${sl_distance:.2f}")
else:
    print("  Nenhuma posição aberta")

print("\n[2] HISTORICO RECENTE DE DEALS (últimas 24h):")
print("-"*80)

date_from = datetime.now() - timedelta(hours=24)
deals = mt5.history_deals_get(date_from=date_from, date_to=datetime.now())

if deals:
    print(f"\nTotal de deals: {len(deals)}")
    print("\nUltimos 5 deals:")
    for deal in reversed(deals[-5:]):
        print(f"\n  Position ID: {deal.get('position_id')}")
        print(f"  Deal ID: {deal.get('deal')}")
        print(f"  Symbol: {deal.get('symbol')}")
        print(f"  Type: {deal.get('type')} (0=BUY, 1=SELL)")
        print(f"  Entry: {deal.get('entry')} (0=IN, 1=OUT)")
        print(f"  Price: ${deal.get('price'):.2f}")
        print(f"  Volume: {deal.get('volume')}")
        print(f"  Profit: ${deal.get('profit'):.2f}")
        print(f"  Comment: {deal.get('comment')}")
        print(f"  Time: {datetime.fromtimestamp(deal.get('time')).strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("  Nenhum deal encontrado")

print("\n[3] ULTIMAS ORDENS NO BANCO:")
print("-"*80)

conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, ticket, symbol, trade_type, entry_price, sl_price, tp_price, 
           volume, strength, status, timestamp
    FROM trades 
    WHERE symbol = 'XAUUSDc'
    ORDER BY id DESC 
    LIMIT 3;
""")

trades = cursor.fetchall()
if trades:
    print(f"\nUltimos 3 trades:")
    for trade in trades:
        trade_id, ticket, symbol, trade_type, entry_price, sl_price, tp_price, volume, strength, status, timestamp = trade
        print(f"\n  ID: {trade_id} | Ticket: {ticket}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Type: {trade_type} | Volume: {volume}")
        print(f"  Entry: ${entry_price:.2f}")
        print(f"  SL: ${sl_price:.2f}" if sl_price else "  SL: N/A")
        print(f"  TP: ${tp_price:.2f}" if tp_price else "  TP: N/A")
        print(f"  Strength: {strength} | Status: {status}")
        
        # Calcular distância
        if sl_price and entry_price:
            if trade_type == "SELL":
                sl_distance = sl_price - entry_price
            else:
                sl_distance = entry_price - sl_price
            print(f"  SL Distance (calculado): ${sl_distance:.2f}")
else:
    print("  Nenhum trade encontrado")

conn.close()

print("\n" + "="*80)
print("ANALISE DE CALCULO")
print("="*80)

if positions and trades:
    pos = positions[0]
    trade = trades[0]
    
    print(f"\nUltima posicao MT5: Ticket {pos.get('ticket')}")
    print(f"Ultimo trade Banco: Ticket {trade[1]}")
    
    if pos.get('ticket') == trade[1]:
        print("\n[OK] Tickets correspondem!")
        
        print(f"\nComparacao de SL:")
        print(f"  MT5 SL: ${pos.get('sl'):.2f}")
        print(f"  Banco SL: ${trade[5]:.2f}")
        
        if abs(pos.get('sl') - trade[5]) < 0.01:
            print(f"  [OK] SL correspondem!")
        else:
            print(f"  [ERRO] SL diferem por ${abs(pos.get('sl') - trade[5]):.2f}")
        
        # Analisar calculo
        entry = trade[4]
        sl = trade[5]
        
        print(f"\nDetalhes do calculo:")
        print(f"  Entry price (banco): ${entry:.2f}")
        print(f"  SL price (banco): ${sl:.2f}")
        
        if trade[2] == "SELL":
            sl_distance_pontos = (sl - entry) / 0.001  # symbol_point
            sl_distance_dinheiro = (sl - entry) * 0.1 * trade[7]  # point_value * volume
            print(f"  Tipo: SELL")
            print(f"  SL Distance: {sl_distance_pontos:.0f} pontos")
            print(f"  SL Distance Dinheiro: ${sl_distance_dinheiro:.2f}")
        else:
            sl_distance_pontos = (entry - sl) / 0.001
            sl_distance_dinheiro = (entry - sl) * 0.1 * trade[7]
            print(f"  Tipo: BUY")
            print(f"  SL Distance: {sl_distance_pontos:.0f} pontos")
            print(f"  SL Distance Dinheiro: ${sl_distance_dinheiro:.2f}")

print("\n" + "="*80)
