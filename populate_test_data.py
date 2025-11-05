#!/usr/bin/env python3
"""
Popula banco de dados com trades de exemplo para testar sistema de otimizacao
"""

import sqlite3
import random
from datetime import datetime, timedelta

def populate_test_trades():
    """
    Cria trades de exemplo com profit_loss preenchido
    """
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()
    
    print("="*70)
    print("POPULANDO BANCO COM TRADES DE TESTE")
    print("="*70)
    
    # Parametros para simulacao realista de Gold
    base_price = 3950.0
    win_rate = 0.72  # 72% de acerto
    avg_win = 4.5
    avg_loss = -6.0
    
    trades_created = 0
    total_profit = 0
    
    # Criar 100 trades simulados
    for i in range(100):
        # Timestamp retroativo
        timestamp = datetime.now() - timedelta(days=100-i, hours=random.randint(0, 23))
        
        # Preco de entrada (variacao aleatoria)
        entry_price = base_price + random.uniform(-50, 50)
        
        # Determinar se ganhou ou perdeu
        is_win = random.random() < win_rate
        
        if is_win:
            profit_loss = random.gauss(avg_win, 1.5)  # Distribuicao normal
            status = "CLOSED_WIN"
            exit_reason = "TP_HIT"
            exit_price = entry_price - profit_loss / 0.02  # Aproximacao
        else:
            profit_loss = random.gauss(avg_loss, 2.0)
            status = "CLOSED_LOSS"
            exit_reason = "SL_HIT"
            exit_price = entry_price + abs(profit_loss) / 0.02
        
        total_profit += profit_loss
        
        # Trade type (SELL only para Gold)
        trade_type = "SELL"
        
        # SL e TP
        sl_price = entry_price + 3.0  # SL 3 dollars acima
        tp_price = 0  # Sem TP fixo (trailing)
        
        # Inserir trade
        try:
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, symbol, trade_type, entry_price, sl_price, tp_price,
                    volume, status, exit_price, exit_reason, profit_loss,
                    reason, comment, agent_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                'XAUUSDc',
                trade_type,
                entry_price,
                sl_price,
                tp_price,
                0.02,
                status,
                exit_price,
                exit_reason,
                profit_loss,
                'simulated_test_data',
                'Test trade for optimization',
                '2.0_test'
            ))
            trades_created += 1
            
            if (i + 1) % 20 == 0:
                print(f"  Criados {i+1} trades... Profit total: ${total_profit:.2f}")
        
        except Exception as e:
            print(f"  Erro ao criar trade {i}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*70}")
    print(f"CONCLUIDO!")
    print(f"{'='*70}")
    print(f"  Trades criados: {trades_created}")
    print(f"  Win rate simulado: {win_rate*100:.0f}%")
    print(f"  Profit total: ${total_profit:.2f}")
    print(f"  Profit medio: ${total_profit/trades_created:.2f}")
    print(f"\nAgora execute: python demo_auto_learning.py")
    print(f"{'='*70}")


if __name__ == "__main__":
    import sys
    
    print("\nATENCAO: Este script vai criar 100 trades de TESTE no banco.")
    print("Estes trades sao SIMULADOS e nao representam trades reais.")
    print("\nContinuar? (s/n): ", end='')
    
    response = input().lower()
    
    if response == 's':
        populate_test_trades()
    else:
        print("Operacao cancelada.")
