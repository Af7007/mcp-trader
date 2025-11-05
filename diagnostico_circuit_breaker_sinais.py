#!/usr/bin/env python3
"""
Diagnostico completo: Circuit Breaker + Sinais de Mercado
Analisa por que o agente ultra-agressivo nao abre posicoes
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path('.') / 'src'))

from core.mt5_direct_client import get_mt5_client
from core.btc_logger import BTCLogger
import sqlite3
from datetime import datetime, timedelta
import time

def main():
    print('DIAGNOSTICO COMPLETO: CIRCUIT BREAKER + SINAIS MERCADO')
    print('=' * 60)

    # Conexao MT5 (mesma do agente)
    mt5 = get_mt5_client()
    btc_logger = BTCLogger()

    # Inicializar variaveis
    consecutive_losses = 0
    last_close_time = None
    signal_valid = False
    signal_type = None
    time_since_last_close = None
    positions = None
    account = None

    # 1. VERIFICAR CIRCUIT BREAKER NO BANCO
    print('\n1. CIRCUIT BREAKER:')
    try:
        conn = sqlite3.connect('btc_trading_logs.db')
        cursor = conn.cursor()
        
        # Buscar ultimas operacoes
        cursor.execute('''
            SELECT id, status, trade_type, profit_loss, exit_reason, timestamp
            FROM trades 
            WHERE symbol = ? 
            ORDER BY id DESC LIMIT 10
        ''', ('XAUUSDc',))
        
        trades = cursor.fetchall()
        print(f'   Ultimas 10 operacoes XAUUSDc:')
        
        for trade in trades:
            trade_id, status, trade_type, profit_loss, exit_reason, timestamp = trade
            is_win = 'WIN' in status
            profit_str = f'${profit_loss:.2f}' if profit_loss else 'N/A'
            time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S') if timestamp else 'N/A'
            
            status_icon = 'WIN' if is_win else 'LOSS'
            print(f'   [{status_icon}] #{trade_id}: {trade_type} @ {time_str} - Profit: {profit_str}')
            
            if not is_win and status not in ['OPEN', 'FAILED']:
                consecutive_losses += 1
            elif is_win:
                consecutive_losses = 0  # Reset no win
                
            if status in ['CLOSED_WIN', 'CLOSED_LOSS'] and timestamp:
                if not last_close_time or timestamp > last_close_time:
                    last_close_time = timestamp
        
        print(f'   Perdas consecutivas: {consecutive_losses}/5')
        
        if consecutive_losses >= 5:
            print('   ALERTA: Circuit breaker ATIVO! (5+ perdas)')
            if last_close_time:
                elapsed = time.time() - last_close_time
                print(f'   Ultima operacao: {elapsed:.0f}s atras')
        else:
            print('   OK: Circuit breaker inativo')
            
        conn.close()
        
    except Exception as e:
        print(f'   Erro ao verificar circuito: {e}')

    print()

    # 2. VERIFICAR POSICOES ATIVAS
    print('2. POSICOES ATIVAS:')
    try:
        positions = mt5.positions_get(symbol='XAUUSDc')
        if positions:
            for pos in positions:
                comment = pos.get('comment', 'N/A')
                profit = pos.get('profit', 0)
                print(f'   Ticket #{pos.get("ticket")}: {pos.get("type", 0) and "SELL" or "BUY"} - Profit: ${profit:.2f} - Comment: {comment}')
        else:
            print('   Nenhuma posicao ativa')
    except Exception as e:
        print(f'   Erro ao verificar posicoes: {e}')

    print()

    # 3. ANALISAR SINAIS DE MERCADO
    print('3. ANALISE SINAIS MERCADO:')
    try:
        # Dados M5
        rates_m5 = mt5.copy_rates_from_pos(
            symbol='XAUUSDc',
            timeframe=5,
            start_pos=0,
            count=10
        )
        
        # Dados M15
        rates_m15 = mt5.copy_rates_from_pos(
            symbol='XAUUSDc',
            timeframe=15,
            start_pos=0,
            count=6
        )
        
        if len(rates_m5) >= 6 and len(rates_m15) >= 4:
            # Analise M5
            closes_m5 = [r['close'] for r in rates_m5[:6]]
            current_price = closes_m5[0]
            prev_5 = closes_m5[5]
            momentum = ((current_price - prev_5) / prev_5) * 100
            
            # Uptrend/downtrend
            uptrend = sum(1 for i in range(4) if closes_m5[i] > closes_m5[i+1]) >= 3
            downtrend = sum(1 for i in range(4) if closes_m5[i] < closes_m5[i+1]) >= 3
            
            # Analise M15
            closes_m15 = [r['close'] for r in rates_m15[:4]]
            uptrend_m15 = closes_m15[0] > closes_m15[1] > closes_m15[2]
            downtrend_m15 = closes_m15[0] < closes_m15[1] < closes_m15[2]
            
            print(f'   Preco atual: ${current_price:.2f}')
            print(f'   Momentum 5min: {momentum:.3f}%')
            print(f'   M5 Trend: UP={uptrend}, DOWN={downtrend}')
            print(f'   M15 Trend: UP={uptrend_m15}, DOWN={downtrend_m15}')
            
            # THRESHOLDS ULTRA-AGGRESSIVE
            MOMENTUM_BUY = 0.015
            MOMENTUM_SELL = -0.015
            
            print(f'   Thresholds ULTRA-AGGRESSIVE: BUY>{MOMENTUM_BUY}%, SELL<{MOMENTUM_SELL}%')
            
            # Verificar sinais
            signal_valid = False
            signal_type = None
            
            if uptrend_m15 and momentum > MOMENTUM_BUY:
                signal_valid = True
                signal_type = 'BUY'
                print(f'   >> SINAL BUY VALIDO: M15 uptrend + momentum {momentum:.3f}%')
                
            if downtrend_m15 and momentum < MOMENTUM_SELL:
                signal_valid = True  
                signal_type = 'SELL'
                print(f'   >> SINAL SELL VALIDO: M15 downtrend + momentum {momentum:.3f}%')
            
            if not signal_valid:
                print(f'   >> NENHUM SINAL VALIDO com filtros ULTRA-AGGRESSIVE')
                if not uptrend_m15 and not downtrend_m15:
                    print(f'      Motivo: M15 lateral (sem tendencia definida)')
                elif momentum >= MOMENTUM_BUY and momentum <= MOMENTUM_SELL:
                    print(f'      Motivo: Momentum {momentum:.3f}% insuficiente')
            
        else:
            print(f'   Erro: Dados insuficientes (M5: {len(rates_m5)}, M15: {len(rates_m15)})')
            
    except Exception as e:
        print(f'   Erro na analise: {e}')

    print()

    # 4. VERIFICAR CONEXAO MT5
    print('4. CONEXAO MT5:')
    try:
        account = mt5.get_account_info()
        if account:
            print(f'   Conta: {account.get("login")}')
            print(f'   Servidor: {account.get("server")}')
            print(f'   Balance: ${account.get("balance", 0):.2f}')
            print(f'   Equity: ${account.get("equity", 0):.2f}')
        else:
            print('   ERRO: Nao conectado ao MT5')
    except Exception as e:
        print(f'   Erro na conexao: {e}')

    print()

    # 5. ANALISE DE COOLDOWN
    print('5. COOLDOWN:')
    try:
        if last_close_time:
            time_since_last_close = time.time() - last_close_time
            print(f'   Tempo desde ultima operacao: {time_since_last_close:.0f}s')
            
            if time_since_last_close < 120:  # 2 minutos
                remaining = 120 - time_since_last_close
                print(f'   Cooldown ativo: {remaining:.0f}s restantes')
            else:
                print('   Cooldown expirado')
        else:
            print('   Nenhuma operacao recente')
    except Exception as e:
        print(f'   Erro ao verificar cooldown: {e}')

    print()

    # 6. RESUMO FINAL
    print('6. RESUMO DIAGNOSTICO:')
    print('-' * 30)
    
    issues = []
    
    if consecutive_losses >= 5:
        issues.append('Circuit breaker ATIVO')
    
    if not signal_valid:
        issues.append('Nenhum sinal valido encontrado')
    
    if time_since_last_close and time_since_last_close < 120:
        issues.append('Cooldown ativo')
    
    if not positions:
        issues.append('Nenhuma posicao ativa')
    
    if not account:
        issues.append('Sem conexao MT5')
    
    if not issues:
        print('   OK: Todos os sistemas funcionais')
        print('   RAZAO: Agent funcionando normalmente, aguardando sinais')
    else:
        print('   PROBLEMAS IDENTIFICADOS:')
        for issue in issues:
            print(f'   - {issue}')
    
    print()
    print('=' * 60)
    print('DIAGNOSTICO CONCLUIDO')

if __name__ == "__main__":
    main()
