#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise BUY vs SELL para BTC - Avaliar se vale a pena ativar BUY
"""

import sys
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import statistics

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def conectar_banco():
    """Conecta ao banco de dados."""
    try:
        db_path = Path(__file__).parent / "src" / "trading_system.db"
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return None

def analisar_buy_vs_sell_btc():
    """
    Analisa performance histórica de BUY vs SELL para BTC
    """
    print("=== ANÁLISE BUY vs SELL - BTC USD ===")
    
    conn = conectar_banco()
    if not conn:
        return False, [], []
    
    try:
        cursor = conn.cursor()
        
        # Buscar todos os trades de BTC do banco
        cursor.execute("""
            SELECT 
                symbol,
                type,
                volume,
                open_price,
                close_price,
                open_time,
                close_time,
                sl,
                tp,
                profit,
                comment
            FROM trades 
            WHERE symbol LIKE '%BTC%'
            ORDER BY open_time DESC
        """)
        
        trades_btc = cursor.fetchall()
        
        if not trades_btc:
            print("Nenhum trade de BTC encontrado no banco")
            return False, [], []
        
        print(f"Total de trades BTC encontrados: {len(trades_btc)}")
        
        # Analisar por tipo
        buy_trades = []
        sell_trades = []
        
        for trade in trades_btc:
            symbol, type_trade, volume, open_price, close_price, open_time, close_time, sl, tp, profit, comment = trade
            
            trade_info = {
                'type': type_trade,
                'volume': volume,
                'profit': profit,
                'open_price': open_price,
                'close_price': close_price,
                'open_time': open_time,
                'close_time': close_time,
                'sl': sl,
                'tp': tp,
                'comment': comment
            }
            
            if type_trade in ['BUY', 'COMPRA']:
                buy_trades.append(trade_info)
            elif type_trade in ['SELL', 'VENDA']:
                sell_trades.append(trade_info)
        
        print(f"\nTrades BUY: {len(buy_trades)}")
        print(f"Trades SELL: {len(sell_trades)}")
        
        # Análise detalhada BUY
        if buy_trades:
            buy_profits = [t['profit'] for t in buy_trades if t['profit'] != 0]
            buy_wins = [p for p in buy_profits if p > 0]
            buy_losses = [p for p in buy_profits if p <= 0]
            
            buy_win_rate = len(buy_wins) / len(buy_profits) * 100 if buy_profits else 0
            buy_avg_win = statistics.mean(buy_wins) if buy_wins else 0
            buy_avg_loss = statistics.mean(buy_losses) if buy_losses else 0
            buy_total = sum(buy_profits)
            
            print(f"\n=== ANÁLISE BUY ===")
            print(f"Trades BUY: {len(buy_trades)}")
            print(f"Trades com profit: {len(buy_profits)}")
            print(f"Wins: {len(buy_wins)} | Losses: {len(buy_losses)}")
            print(f"Win Rate: {buy_win_rate:.1f}%")
            print(f"Avg Win: ${buy_avg_win:.2f}")
            print(f"Avg Loss: ${buy_avg_loss:.2f}")
            print(f"Total Profit: ${buy_total:.2f}")
            
            # Ratio risk/reward BUY
            if buy_avg_loss != 0:
                buy_rr = abs(buy_avg_win / buy_avg_loss) if buy_avg_loss != 0 else 0
                print(f"Risk/Reward Ratio: 1:{buy_rr:.2f}")
        else:
            buy_win_rate = 0
            buy_avg_win = 0
            buy_avg_loss = 0
            buy_total = 0
        
        # Análise detalhada SELL
        if sell_trades:
            sell_profits = [t['profit'] for t in sell_trades if t['profit'] != 0]
            sell_wins = [p for p in sell_profits if p > 0]
            sell_losses = [p for p in sell_profits if p <= 0]
            
            sell_win_rate = len(sell_wins) / len(sell_profits) * 100 if sell_profits else 0
            sell_avg_win = statistics.mean(sell_wins) if sell_wins else 0
            sell_avg_loss = statistics.mean(sell_losses) if sell_losses else 0
            sell_total = sum(sell_profits)
            
            print(f"\n=== ANÁLISE SELL ===")
            print(f"Trades SELL: {len(sell_trades)}")
            print(f"Trades com profit: {len(sell_profits)}")
            print(f"Wins: {len(sell_wins)} | Losses: {len(sell_losses)}")
            print(f"Win Rate: {sell_win_rate:.1f}%")
            print(f"Avg Win: ${sell_avg_win:.2f}")
            print(f"Avg Loss: ${sell_avg_loss:.2f}")
            print(f"Total Profit: ${sell_total:.2f}")
            
            # Ratio risk/reward SELL
            if sell_avg_loss != 0:
                sell_rr = abs(sell_avg_win / sell_avg_loss) if sell_avg_loss != 0 else 0
                print(f"Risk/Reward Ratio: 1:{sell_rr:.2f}")
        else:
            sell_win_rate = 0
            sell_avg_win = 0
            sell_avg_loss = 0
            sell_total = 0
        
        # Análise comparativa
        print(f"\n=== COMPARAÇÃO BUY vs SELL ===")
        
        if buy_trades and sell_trades:
            # Comparar win rates
            if buy_win_rate > sell_win_rate:
                print(f"Melhor Win Rate: BUY ({buy_win_rate:.1f}% vs {sell_win_rate:.1f}%)")
            elif sell_win_rate > buy_win_rate:
                print(f"Melhor Win Rate: SELL ({sell_win_rate:.1f}% vs {buy_win_rate:.1f}%)")
            else:
                print(f"Win Rates iguais: {buy_win_rate:.1f}%")
            
            # Comparar performance total
            if buy_total > sell_total:
                print(f"Melhor Performance Total: BUY (${buy_total:.2f} vs ${sell_total:.2f})")
            elif sell_total > buy_total:
                print(f"Melhor Performance Total: SELL (${sell_total:.2f} vs ${buy_total:.2f})")
            else:
                print(f"Performance total igual")
        
        return True, buy_trades, sell_trades
        
    except Exception as e:
        print(f"Erro na análise: {e}")
        return False, [], []
    finally:
        conn.close()

def recommendation_buy_activation():
    """
    Gera recomendação sobre ativar BUY ou manter SELL-ONLY
    """
    print(f"\n=== RECOMENDAÇÃO: ATIVAR BUY? ===")
    
    sucesso, buy_trades, sell_trades = analisar_buy_vs_sell_btc()
    
    if not sucesso:
        return
    
    # Critérios para recomendação
    reasons_buy = []
    reasons_sell = []
    
    if buy_trades and sell_trades:
        # Análise detalhada
        buy_profits = [t['profit'] for t in buy_trades if t['profit'] != 0]
        sell_profits = [t['profit'] for t in sell_trades if t['profit'] != 0]
        
        buy_wins = [p for p in buy_profits if p > 0]
        sell_wins = [p for p in sell_profits if p > 0]
        
        buy_win_rate = len(buy_wins) / len(buy_profits) * 100 if buy_profits else 0
        sell_win_rate = len(sell_wins) / len(sell_profits) * 100 if sell_profits else 0
        
        buy_total = sum(buy_profits)
        sell_total = sum(sell_profits)
        
        # Avaliar se BUY vale a pena
        print(f"\nAVALIAÇÃO PARA ATIVAÇÃO DE BUY:")
        
        # 1. Win Rate
        if buy_win_rate >= 60:
            reasons_buy.append(f"BUY tem bom win rate: {buy_win_rate:.1f}%")
        elif buy_win_rate >= 40:
            reasons_buy.append(f"BUY tem win rate moderado: {buy_win_rate:.1f}%")
        else:
            reasons_sell.append(f"BUY tem baixo win rate: {buy_win_rate:.1f}%")
        
        # 2. Performance total
        if buy_total > 0:
            reasons_buy.append(f"BUY é profitable: ${buy_total:.2f}")
        else:
            reasons_sell.append(f"BUY não é profitable: ${buy_total:.2f}")
        
        # 3. Comparação com SELL
        if buy_win_rate > sell_win_rate + 10:
            reasons_buy.append(f"BUY supera SELL em win rate por {buy_win_rate - sell_win_rate:.1f}%")
        elif sell_win_rate > buy_win_rate + 10:
            reasons_sell.append(f"SELL supera BUY em win rate por {sell_win_rate - buy_win_rate:.1f}%")
        
        if buy_total > sell_total:
            reasons_buy.append(f"BUY supera SELL em profit por ${buy_total - sell_total:.2f}")
        elif sell_total > buy_total:
            reasons_sell.append(f"SELL supera BUY em profit por ${sell_total - buy_total:.2f}")
        
        # 4. Volume de trades
        if len(buy_trades) >= 10:
            reasons_buy.append(f"Amostra significativa de BUY trades: {len(buy_trades)}")
        else:
            reasons_sell.append(f"Poucos trades BUY para análise: {len(buy_trades)}")
    
    # Recomendação final
    print(f"\nMOTIVOS PARA ATIVAR BUY:")
    for reason in reasons_buy:
        print(f"  + {reason}")
    
    print(f"\nMOTIVOS PARA MANTER SELL-ONLY:")
    for reason in reasons_sell:
        print(f"  - {reason}")
    
    # Decisão final
    score_buy = len(reasons_buy)
    score_sell = len(reasons_sell)
    
    print(f"\n=== DECISÃO FINAL ===")
    if score_buy > score_sell:
        print(f"RECOMENDAÇÃO: ATIVAR BUY")
        print(f"Score BUY: {score_buy} vs SELL: {score_sell}")
        print(f"的理由: BUY tem melhor performance histórica")
    elif score_sell > score_buy:
        print(f"RECOMENDAÇÃO: MANTER SELL-ONLY")
        print(f"Score SELL: {score_sell} vs BUY: {score_buy}")
        print(f"的理由: SELL tem melhor performance histórica")
    else:
        print(f"RECOMENDAÇÃO: TESTE GRADUAL")
        print(f"Score empatado: {score_buy} vs {score_sell}")
        print(f"的理由: Performance similar, testar ativação gradual")

if __name__ == "__main__":
    print("ANÁLISE BUY vs SELL PARA BTC")
    print("="*50)
    
    recommendation_buy_activation()
    
    print(f"\n" + "="*50)
    print(f"CONCLUSÃO BASEADA EM DADOS HISTÓRICOS")
