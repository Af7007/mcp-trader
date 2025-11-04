#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise detalhada de perdas nas últimas ordens
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def analise_perdas():
    """
    Analisa perdas significativas nas últimas ordens
    """
    db_path = Path('btc_trading_logs.db')
    if not db_path.exists():
        print("Banco de dados não encontrado!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("ANALISE DETALHADA DE PERDAS - BTC TRADING")
    print("=" * 80)

    # 1. Trades fechados com lucro/prejuízo
    print("\n[RESUMO] TRADES FECHADOS:")
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as losses,
            COUNT(CASE WHEN profit_loss = 0 THEN 1 END) as breakeven,
            SUM(profit_loss) as total_profit,
            AVG(profit_loss) as avg_profit,
            MIN(profit_loss) as maior_perda,
            MAX(profit_loss) as maior_ganho
        FROM trades
        WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
    ''')

    result = cursor.fetchone()
    if result and result[0] > 0:
        total, wins, losses, breakeven, total_profit, avg_profit, maior_perda, maior_ganho = result
        winrate = (wins / total * 100) if total > 0 else 0

        print(f"   Total de trades fechados: {total}")
        print(f"   Vitórias: {wins} ({winrate:.1f}%)")
        print(f"   Perdas: {losses} ({(losses/total*100) if total > 0 else 0:.1f}%)")
        print(f"   Breakeven: {breakeven}")
        print(f"   Lucro/Prejuízo total: ${total_profit:.2f}")
        print(f"   Média por trade: ${avg_profit:.2f}")
        print(f"   Maior perda: ${maior_perda:.2f}")
        print(f"   Maior ganho: ${maior_ganho:.2f}")
    else:
        print("   ALERTA: Nenhum trade fechado encontrado!")

    # 2. Top 10 maiores perdas
    print("\n[PERDAS] TOP 10 MAIORES PERDAS:")
    cursor.execute('''
        SELECT
            timestamp,
            trade_type,
            entry_price,
            exit_price,
            profit_loss,
            reason,
            exit_reason,
            strength
        FROM trades
        WHERE status = 'CLOSED'
        AND profit_loss < 0
        ORDER BY profit_loss ASC
        LIMIT 10
    ''')

    perdas = cursor.fetchall()
    if perdas:
        for i, (ts, tipo, entry, exit_p, pl, reason, exit_reason, strength) in enumerate(perdas, 1):
            print(f"\n   {i}. Perda: ${pl:.2f}")
            print(f"      Tipo: {tipo} | Força: {strength}")
            print(f"      Entrada: ${entry:.2f} → Saída: ${exit_p:.2f}")
            print(f"      Razão entrada: {reason}")
            print(f"      Razão saída: {exit_reason}")
            print(f"      Timestamp: {ts}")
    else:
        print("   Nenhuma perda registrada.")

    # 3. Análise por tipo de trade (BUY vs SELL)
    print("\n[TIPO] PERFORMANCE POR TIPO DE TRADE:")
    cursor.execute('''
        SELECT
            trade_type,
            COUNT(*) as total,
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as losses,
            SUM(profit_loss) as total_pl,
            AVG(profit_loss) as avg_pl
        FROM trades
        WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
        GROUP BY trade_type
    ''')

    for tipo, total, wins, losses, total_pl, avg_pl in cursor.fetchall():
        winrate = (wins / total * 100) if total > 0 else 0
        print(f"\n   {tipo}:")
        print(f"      Total: {total} | Wins: {wins} ({winrate:.1f}%) | Losses: {losses}")
        print(f"      P&L Total: ${total_pl:.2f} | Média: ${avg_pl:.2f}")

    # 4. Análise por razão de entrada
    print("\n[RAZAO] PERFORMANCE POR RAZAO DE ENTRADA:")
    cursor.execute('''
        SELECT
            reason,
            COUNT(*) as total,
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as losses,
            SUM(profit_loss) as total_pl,
            AVG(profit_loss) as avg_pl
        FROM trades
        WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
        GROUP BY reason
        ORDER BY total_pl ASC
        LIMIT 10
    ''')

    razoes = cursor.fetchall()
    if razoes:
        for reason, total, wins, losses, total_pl, avg_pl in razoes:
            winrate = (wins / total * 100) if total > 0 else 0
            print(f"\n   {reason}:")
            print(f"      Total: {total} | Wins: {wins} ({winrate:.1f}%) | Losses: {losses}")
            print(f"      P&L: ${total_pl:.2f} | Média: ${avg_pl:.2f}")

    # 5. Análise por força do sinal
    print("\n[FORCA] PERFORMANCE POR FORCA DO SINAL:")
    cursor.execute('''
        SELECT
            strength,
            COUNT(*) as total,
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as losses,
            SUM(profit_loss) as total_pl,
            AVG(profit_loss) as avg_pl
        FROM trades
        WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
        GROUP BY strength
        ORDER BY avg_pl DESC
    ''')

    for strength, total, wins, losses, total_pl, avg_pl in cursor.fetchall():
        winrate = (wins / total * 100) if total > 0 else 0
        print(f"\n   {strength}:")
        print(f"      Total: {total} | Wins: {wins} ({winrate:.1f}%) | Losses: {losses}")
        print(f"      P&L: ${total_pl:.2f} | Média: ${avg_pl:.2f}")

    # 6. Trades em aberto (possíveis perdas futuras)
    print("\n[ABERTOS] TRADES ATUALMENTE EM ABERTO:")
    cursor.execute('''
        SELECT
            timestamp,
            trade_type,
            entry_price,
            sl_price,
            tp_price,
            reason,
            strength
        FROM trades
        WHERE status = 'OPEN'
        ORDER BY timestamp DESC
    ''')

    abertos = cursor.fetchall()
    if abertos:
        print(f"   Total de trades abertos: {len(abertos)}")
        for i, (ts, tipo, entry, sl, tp, reason, strength) in enumerate(abertos, 1):
            print(f"\n   {i}. {tipo} | {strength}")
            print(f"      Entrada: ${entry:.2f}")
            print(f"      SL: ${sl:.2f} | TP: ${tp:.2f}")
            print(f"      Razão: {reason}")
            print(f"      Aberto desde: {ts}")
    else:
        print("   OK - Nenhum trade aberto no momento.")

    # 7. Análise temporal (últimas 24h vs total)
    print("\n[TEMPO] ANALISE TEMPORAL - ULTIMAS 24 HORAS:")
    ontem = datetime.now() - timedelta(hours=24)

    cursor.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as losses,
            SUM(profit_loss) as total_pl
        FROM trades
        WHERE status = 'CLOSED'
        AND profit_loss IS NOT NULL
        AND timestamp > ?
    ''', (ontem.strftime('%Y-%m-%d %H:%M:%S'),))

    result = cursor.fetchone()
    if result and result[0] > 0:
        total, wins, losses, total_pl = result
        winrate = (wins / total * 100) if total > 0 else 0
        print(f"   Trades fechados (24h): {total}")
        print(f"   Wins: {wins} ({winrate:.1f}%) | Losses: {losses}")
        print(f"   P&L (24h): ${total_pl:.2f}")
    else:
        print("   Nenhum trade fechado nas últimas 24h")

    # 8. Identificar problemas comuns
    print("\n[ALERTA] PROBLEMAS IDENTIFICADOS:")

    # Problema 1: Taxa de conversão de sinais baixa
    cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL')
    total_sinais = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]

    if total_sinais > 0:
        taxa_conversao = (total_trades / total_sinais * 100)
        print(f"   1. Taxa de conversao: {taxa_conversao:.1f}% ({total_trades}/{total_sinais})")
        if taxa_conversao < 30:
            print(f"      ALERTA: Taxa muito baixa! Muitos sinais nao viraram trades.")

    # Problema 2: Predominância de SELL signals
    cursor.execute('''
        SELECT signal_type, COUNT(*)
        FROM cycles
        WHERE signal_type IS NOT NULL
        GROUP BY signal_type
    ''')
    distribuicao = dict(cursor.fetchall())

    if 'SELL' in distribuicao and 'BUY' in distribuicao:
        ratio = distribuicao['SELL'] / distribuicao['BUY']
        print(f"   2. Proporcao SELL/BUY: {ratio:.2f}x")
        if ratio > 2:
            print(f"      ALERTA: Muito mais sinais de SELL! Pode indicar vies de mercado.")

    # Problema 3: Winrate geral
    cursor.execute('''
        SELECT
            COUNT(CASE WHEN profit_loss > 0 THEN 1 END) * 1.0 / COUNT(*) * 100
        FROM trades
        WHERE status = 'CLOSED' AND profit_loss IS NOT NULL
    ''')

    winrate_geral = cursor.fetchone()[0]
    if winrate_geral:
        print(f"   3. Winrate geral: {winrate_geral:.1f}%")
        if winrate_geral < 50:
            print(f"      ALERTA: Winrate abaixo de 50%! Estrategia pode precisar ajustes.")

    conn.close()

    print("\n" + "=" * 80)
    print("[RECOMENDACOES]:")
    print("=" * 80)
    print("""
   1. Analisar razões de entrada com pior performance e ajustar condições
   2. Verificar se Stop Loss está muito próximo (muitas perdas pequenas)
   3. Considerar aumentar Take Profit se winrate for alto mas lucro baixo
   4. Avaliar se força do sinal está sendo respeitada nas decisões
   5. Investigar por que tantos sinais não viraram trades (283 sinais sem trades)
   6. Considerar adicionar filtros de confirmação para sinais
   7. Revisar proporção SELL/BUY - pode ser viés de mercado ou bug na lógica
    """)

    print("=" * 80)

if __name__ == "__main__":
    analise_perdas()
