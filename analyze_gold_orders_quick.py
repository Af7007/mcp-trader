"""
Analise detalhada das ordens Gold para identificar melhorias em operacoes rapidas
Foco: M5 e M1 vs M15
"""

import sqlite3
from datetime import datetime, timedelta

db_path = r'c:\mcp-trader\btc_trading_logs.db'

print("="*80)
print("ANALISE DE ORDENS GOLD - FOCO EM OPERACOES RAPIDAS")
print("="*80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar todas as ordens Gold das ultimas 24h
cursor.execute("""
    SELECT
        ticket,
        type,
        open_time,
        close_time,
        entry_price,
        sl_price,
        tp_price,
        result,
        comment,
        status
    FROM trades
    WHERE symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%'
    ORDER BY close_time DESC
    LIMIT 50
""")

trades = cursor.fetchall()

if not trades:
    print("\n[!] Nenhuma ordem encontrada")
    conn.close()
    exit()

print(f"\n[+] {len(trades)} ordens encontradas\n")

wins = []
losses = []
total_profit = 0
total_loss = 0

for trade in trades:
    ticket, typ, open_t, close_t, entry, sl, tp, result, comment, status = trade

    if result and result > 0:
        wins.append(trade)
        total_profit += result
    elif result and result < 0:
        losses.append(trade)
        total_loss += result

    # Calcular duracao
    if open_t and close_t:
        try:
            open_dt = datetime.strptime(open_t, '%Y-%m-%d %H:%M:%S')
            close_dt = datetime.strptime(close_t, '%Y-%m-%d %H:%M:%S')
            duration = (close_dt - open_dt).total_seconds() / 60  # minutos
        except:
            duration = 0
    else:
        duration = 0

    result_str = f"${result:.2f}" if result else "N/A"
    status_str = "[WIN]" if result and result > 0 else "[LOSS]" if result and result < 0 else "[OPEN]"

    print(f"{status_str} Ticket {ticket} | {typ}")
    print(f"  Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f if tp else 'N/A'}")
    print(f"  Result: {result_str} | Duration: {duration:.1f}min")
    if comment:
        print(f"  Comment: {comment}")
    print()

print("="*80)
print("ESTATISTICAS")
print("="*80)
print(f"Total trades: {len(trades)}")
print(f"Wins: {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
print(f"Losses: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")
print(f"Total Profit: ${total_profit:.2f}")
print(f"Total Loss: ${total_loss:.2f}")
print(f"Net Result: ${total_profit + total_loss:.2f}")

if wins:
    avg_win = total_profit / len(wins)
    print(f"Avg Win: ${avg_win:.2f}")

if losses:
    avg_loss = total_loss / len(losses)
    print(f"Avg Loss: ${avg_loss:.2f}")

print("\n" + "="*80)
print("ANALISE DE PADROES - PERDAS")
print("="*80)

# Analisar perdas por tipo de entrada
buy_losses = [t for t in losses if 'BUY' in t[1].upper()]
sell_losses = [t for t in losses if 'SELL' in t[1].upper()]

print(f"\nPerdas BUY: {len(buy_losses)}")
print(f"Perdas SELL: {len(sell_losses)}")

# Analisar comentarios das perdas
print("\n[!] Comentarios das ultimas perdas:")
for trade in losses[:10]:
    ticket, typ, open_t, close_t, entry, sl, tp, result, comment, status = trade
    print(f"  Ticket {ticket} ({typ}): {comment or 'Sem comentario'} | Loss: ${result:.2f}")

conn.close()

print("\n" + "="*80)
print("RECOMENDACOES PARA OPERACOES RAPIDAS (M5/M1)")
print("="*80)
print("""
1. REMOVER CONFIRMACAO M15 - Esta causando conflito com M5/M1
   -> M15 pode estar em tendencia oposta ao scalping em M5

2. FOCAR APENAS EM M5 + M1
   -> M5: Tendencia principal
   -> M1: Confirmacao rapida de entrada

3. ADICIONAR FILTRO DE VOLATILIDADE
   -> Evitar entradas durante noticias/alta volatilidade
   -> ATR muito alto = evitar trade

4. MELHORAR TIMING DE ENTRADA
   -> Esperar pullback em M1 apos sinal M5
   -> Nao entrar no topo/fundo de vela

5. TRAILING STOP MAIS AGRESSIVO
   -> Proteger lucros rapido em scalping
   -> TS ativa com $2.00 de lucro

6. FILTRO DE HORARIO
   -> Evitar Asian session (baixa volatilidade)
   -> Focar London/NY session (alta liquidez)
""")
