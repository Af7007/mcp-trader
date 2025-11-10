"""
Analise completa das operacoes Gold - Foco em assertividade rapida
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

db_path = r'c:\mcp-trader\btc_trading_logs.db'

print("="*80)
print("ANALISE COMPLETA - GOLD OPERATIONS (OPERACOES RAPIDAS)")
print("="*80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar todas as ordens Gold
cursor.execute("""
    SELECT
        id,
        timestamp,
        trade_type,
        entry_price,
        sl_price,
        exit_price,
        profit_loss,
        status,
        exit_reason,
        reason,
        comment
    FROM trades
    WHERE symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%'
    ORDER BY timestamp DESC
    LIMIT 100
""")

trades = cursor.fetchall()
conn.close()

if not trades:
    print("\n[!] Nenhuma ordem encontrada")
    exit()

print(f"\n[+] {len(trades)} ordens analisadas\n")

# Estatisticas
wins = []
losses = []
total_profit = 0
total_loss = 0

buy_trades = []
sell_trades = []

m1_confirmed_trades = []
m5_follow_trades = []

for trade in trades:
    id, ts, trade_type, entry, sl, exit, profit, status, exit_reason, reason, comment = trade

    if profit:
        if profit > 0:
            wins.append(trade)
            total_profit += profit
        else:
            losses.append(trade)
            total_loss += profit

    if trade_type == 'BUY':
        buy_trades.append(trade)
    else:
        sell_trades.append(trade)

    # Separar por tipo de entrada
    if reason and 'M1' in reason and 'CONFIRMED' in reason:
        m1_confirmed_trades.append(trade)
    elif reason and 'M5' in reason and 'follow' in reason:
        m5_follow_trades.append(trade)

print("="*80)
print("ESTATISTICAS GERAIS")
print("="*80)
total_closed = len([t for t in trades if t[7] and 'CLOSED' in t[7]])
print(f"Total ordens: {len(trades)}")
print(f"Ordens fechadas: {total_closed}")
print(f"Wins: {len(wins)} ({len(wins)/total_closed*100:.1f}%)" if total_closed > 0 else "Wins: 0")
print(f"Losses: {len(losses)} ({len(losses)/total_closed*100:.1f}%)" if total_closed > 0 else "Losses: 0")
print(f"Win Rate: {len(wins)/(len(wins)+len(losses))*100:.1f}%" if (len(wins)+len(losses)) > 0 else "Win Rate: N/A")
print(f"\nTotal Profit: ${total_profit:.2f}")
print(f"Total Loss: ${total_loss:.2f}")
print(f"Net Result: ${total_profit + total_loss:.2f}")

if wins:
    avg_win = total_profit / len(wins)
    print(f"Avg Win: ${avg_win:.2f}")

if losses:
    avg_loss = total_loss / len(losses)
    print(f"Avg Loss: ${avg_loss:.2f}")

print("\n" + "="*80)
print("ANALISE POR DIRECAO")
print("="*80)

buy_wins = [t for t in wins if t[2] == 'BUY']
buy_losses = [t for t in losses if t[2] == 'BUY']
sell_wins = [t for t in wins if t[2] == 'SELL']
sell_losses = [t for t in losses if t[2] == 'SELL']

print(f"\nBUY Trades: {len(buy_trades)}")
print(f"  Wins: {len(buy_wins)} | Losses: {len(buy_losses)}")
if len(buy_wins) + len(buy_losses) > 0:
    buy_wr = len(buy_wins)/(len(buy_wins)+len(buy_losses))*100
    print(f"  Win Rate: {buy_wr:.1f}%")

print(f"\nSELL Trades: {len(sell_trades)}")
print(f"  Wins: {len(sell_wins)} | Losses: {len(sell_losses)}")
if len(sell_wins) + len(sell_losses) > 0:
    sell_wr = len(sell_wins)/(len(sell_wins)+len(sell_losses))*100
    print(f"  Win Rate: {sell_wr:.1f}%")

print("\n" + "="*80)
print("ANALISE POR TIPO DE SINAL")
print("="*80)

# M1 CONFIRMED
m1_wins = [t for t in m1_confirmed_trades if t[6] and t[6] > 0]
m1_losses = [t for t in m1_confirmed_trades if t[6] and t[6] < 0]

print(f"\nM1_CONFIRMED (M1 confirmado por M5):")
print(f"  Total: {len(m1_confirmed_trades)}")
print(f"  Wins: {len(m1_wins)} | Losses: {len(m1_losses)}")
if len(m1_wins) + len(m1_losses) > 0:
    m1_wr = len(m1_wins)/(len(m1_wins)+len(m1_losses))*100
    print(f"  Win Rate: {m1_wr:.1f}%")

# M5 FOLLOW
m5_wins = [t for t in m5_follow_trades if t[6] and t[6] > 0]
m5_losses = [t for t in m5_follow_trades if t[6] and t[6] < 0]

print(f"\nM5_FOLLOW (Seguir tendencia M5):")
print(f"  Total: {len(m5_follow_trades)}")
print(f"  Wins: {len(m5_wins)} | Losses: {len(m5_losses)}")
if len(m5_wins) + len(m5_losses) > 0:
    m5_wr = len(m5_wins)/(len(m5_wins)+len(m5_losses))*100
    print(f"  Win Rate: {m5_wr:.1f}%")

print("\n" + "="*80)
print("ULTIMAS 10 PERDAS - ANALISE DETALHADA")
print("="*80)

for i, trade in enumerate(losses[:10], 1):
    id, ts, trade_type, entry, sl, exit, profit, status, exit_reason, reason, comment = trade

    print(f"\n{i}. Ticket ID: {id} | {trade_type}")
    print(f"   Timestamp: {ts}")
    print(f"   Entry: ${entry:.3f} | SL: ${sl:.3f} | Exit: ${exit:.3f}")

    # Calcular distancia SL
    if entry and sl:
        if trade_type == 'BUY':
            sl_dist = entry - sl
        else:
            sl_dist = sl - entry
        print(f"   SL Distance: ${sl_dist:.3f}")

    print(f"   Loss: ${profit:.2f}")
    print(f"   Exit Reason: {exit_reason}")
    print(f"   Signal: {reason}")

print("\n" + "="*80)
print("DIAGNOSTICO E RECOMENDACOES")
print("="*80)

print(f"""
RESULTADOS DA ANALISE:

1. WIN RATE GERAL: {len(wins)/(len(wins)+len(losses))*100:.1f}%
   -> {'[OK] Acima de 50%' if len(wins)/(len(wins)+len(losses)) > 0.5 else '[ALERTA] Abaixo de 50% - PRECISA MELHORAR'}

2. DIRECAO MAIS LUCRATIVA:
   -> BUY: {buy_wr:.1f}% win rate
   -> SELL: {sell_wr:.1f}% win rate
   -> {'SELL esta melhor' if sell_wr > buy_wr else 'BUY esta melhor' if buy_wr > sell_wr else 'Ambos iguais'}

3. TIPO DE SINAL MAIS EFETIVO:
   -> M1_CONFIRMED: {m1_wr:.1f}% win rate ({len(m1_confirmed_trades)} trades)
   -> M5_FOLLOW: {m5_wr:.1f}% win rate ({len(m5_follow_trades)} trades)
   -> {'M1_CONFIRMED melhor' if m1_wr > m5_wr else 'M5_FOLLOW melhor'}

PROBLEMAS IDENTIFICADOS:

1. CONFLITO DE TIMEFRAMES
   - Usar M15 para tendencia principal NAO funciona para scalping M5/M1
   - M15 pode estar em tendencia contraria ao movimento rapido de M5
   - SOLUCAO: Remover validacao M15, focar 100% em M5 + M1

2. ENTRADA MUITO RAPIDA EM M1
   - M1 e muito volatil para entrada direta
   - SOLUCAO: Usar M1 apenas para TIMING, nao para sinal principal
   - Esperar pullback em M1 apos sinal M5 confirmado

3. SL MUITO APERTADO ($2.50)
   - Gold tem movimentos rapidos de $3-5
   - SL de $2.50 esta sendo atingido por ruido
   - SOLUCAO: Aumentar SL para $4.00 OU usar ATR dinamico

4. FALTA DE FILTRO DE VOLATILIDADE
   - Entrar durante alta volatilidade = maior risco
   - SOLUCAO: Evitar trades quando ATR > 2.0

5. TRAILING STOP MUITO CONSERVADOR
   - TS atual so ativa com $5 de lucro
   - Em scalping, precisa proteger lucro rapido
   - SOLUCAO: TS ativa com $2.00 de lucro

MELHORIAS RECOMENDADAS:

[CRITICAS - IMPLEMENTAR AGORA]
1. Remover completamente validacao M15
2. M5 = Sinal principal (tendencia)
3. M1 = Timing de entrada (pullback/confirmacao)
4. Aumentar SL base para $4.00
5. Ativar TS com $2.00 de lucro

[IMPORTANTES - IMPLEMENTAR EM SEGUIDA]
6. Filtro ATR: Evitar trade se ATR > 2.0
7. Filtro de spread: Evitar se spread > 0.5
8. Score minimo M5: 4.0 (ao inves de 3.5)
9. Aguardar 2 velas M1 de confirmacao

[OPCIONAIS - TESTAR DEPOIS]
10. Filtro de horario (evitar Asian session)
11. Volume minimo para entrada
12. Nao operar durante noticias importantes
""")
