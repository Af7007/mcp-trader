"""
Analisa se as entradas Gold estão contra a tendência M5
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import sqlite3
import MetaTrader5 as mt5
from datetime import datetime, timedelta

def init_mt5():
    """Inicializa MT5"""
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        return False
    print("[OK] MT5 inicializado")
    return True

def get_recent_gold_trades():
    """Busca trades Gold recentes do banco"""
    conn = sqlite3.connect('btc_trading_logs.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket, symbol, trade_type, volume, entry_price, exit_price,
               sl_price, tp_price, profit_loss, timestamp, status
        FROM trades
        WHERE (symbol LIKE '%XAU%' OR symbol LIKE '%GOLD%')
        AND timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp DESC
    """)

    trades = []
    for row in cursor.fetchall():
        trades.append({
            'ticket': row[0],
            'symbol': row[1],
            'type': row[2],
            'volume': row[3],
            'entry': row[4],
            'exit': row[5],
            'sl': row[6],
            'tp': row[7],
            'profit': row[8],
            'time': row[9],
            'status': row[10]
        })

    conn.close()
    return trades

def get_m5_trend_at_time(entry_time_str):
    """
    Verifica tendência M5 no momento da entrada
    """
    try:
        # Converter timestamp string para datetime
        entry_time = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')

        # Buscar candles M5 do momento da entrada
        rates = mt5.copy_rates_range(
            "XAUUSDc",
            mt5.TIMEFRAME_M5,
            entry_time - timedelta(hours=2),  # 2 horas antes
            entry_time + timedelta(minutes=5)  # até o momento da entrada
        )

        if not rates or len(rates) < 10:
            return {"trend": "UNKNOWN", "reason": "Dados insuficientes"}

        # Pegar últimos 15 candles antes da entrada
        closes = [r['close'] for r in rates[-15:]]

        # Calcular tendência (5/8 velas subindo/descendo)
        uptrend = sum(1 for i in range(7) if closes[i] < closes[i+1]) >= 5
        downtrend = sum(1 for i in range(7) if closes[i] > closes[i+1]) >= 5

        # Micro trend (3 velas consecutivas)
        micro_uptrend = any(
            closes[i] < closes[i+1] < closes[i+2]
            for i in range(len(closes) - 2)
        )
        micro_downtrend = any(
            closes[i] > closes[i+1] > closes[i+2]
            for i in range(len(closes) - 2)
        )

        # Determinar tendência
        if uptrend and micro_uptrend:
            return {
                "trend": "UPTREND",
                "micro": "UP",
                "strength": "STRONG",
                "uptrend": uptrend,
                "micro_uptrend": micro_uptrend
            }
        elif downtrend and micro_downtrend:
            return {
                "trend": "DOWNTREND",
                "micro": "DOWN",
                "strength": "STRONG",
                "downtrend": downtrend,
                "micro_downtrend": micro_downtrend
            }
        elif uptrend:
            return {
                "trend": "UPTREND",
                "micro": "WEAK",
                "strength": "WEAK",
                "uptrend": uptrend,
                "micro_uptrend": micro_uptrend
            }
        elif downtrend:
            return {
                "trend": "DOWNTREND",
                "micro": "WEAK",
                "strength": "WEAK",
                "downtrend": downtrend,
                "micro_downtrend": micro_downtrend
            }
        else:
            return {
                "trend": "NEUTRAL",
                "micro": "NEUTRAL",
                "strength": "NEUTRAL"
            }

    except Exception as e:
        return {"trend": "ERROR", "reason": str(e)}

def main():
    print("=" * 100)
    print("ANALISE DE ENTRADAS GOLD - VERIFICACAO DE TENDENCIA M5")
    print("=" * 100)
    print()

    if not init_mt5():
        return

    # Buscar trades recentes
    trades = get_recent_gold_trades()
    print(f"Trades Gold nas ultimas 24h: {len(trades)}")
    print()

    if not trades:
        print("Nenhum trade encontrado nas ultimas 24h")
        mt5.shutdown()
        return

    # Análise estatística
    total = 0
    aligned_with_trend = 0
    against_trend = 0
    neutral = 0
    wins = 0
    losses = 0

    print("ANALISE DETALHADA:")
    print("-" * 100)

    for trade in trades:
        total += 1

        # Verificar se foi win ou loss
        is_win = trade['profit'] and trade['profit'] > 0
        if is_win:
            wins += 1
        elif trade['profit'] and trade['profit'] < 0:
            losses += 1

        # Verificar tendência M5 no momento da entrada
        m5_trend = get_m5_trend_at_time(trade['time'])

        # Verificar alinhamento
        trade_type = trade['type']
        trend = m5_trend.get('trend', 'UNKNOWN')

        if trend == "UPTREND" and trade_type == "BUY":
            alignment = "ALIGNED"
            aligned_with_trend += 1
        elif trend == "DOWNTREND" and trade_type == "SELL":
            alignment = "ALIGNED"
            aligned_with_trend += 1
        elif trend == "NEUTRAL":
            alignment = "NEUTRAL"
            neutral += 1
        elif trend in ["UNKNOWN", "ERROR"]:
            alignment = "UNKNOWN"
        else:
            alignment = "AGAINST"
            against_trend += 1

        # Mostrar resultado
        profit_str = f"${trade['profit']:.2f}" if trade['profit'] else "N/A"
        result_str = "WIN" if is_win else "LOSS" if trade['profit'] and trade['profit'] < 0 else "OPEN"

        print(f"\nTicket {trade['ticket']}: {trade['type']} @ {trade['entry']:.3f}")
        print(f"  Time: {trade['time']}")
        print(f"  M5 Trend: {trend} ({m5_trend.get('strength', 'N/A')})")
        print(f"  Alignment: {alignment}")
        print(f"  Result: {result_str} ({profit_str})")

        # Mostrar detalhes se CONTRA a tendência
        if alignment == "AGAINST":
            print(f"  [ALERTA] Entrada CONTRA a tendência M5!")
            print(f"    Trend: {trend}")
            print(f"    Trade: {trade_type}")
            if 'uptrend' in m5_trend:
                print(f"    Uptrend: {m5_trend.get('uptrend')}, Micro: {m5_trend.get('micro_uptrend')}")
            if 'downtrend' in m5_trend:
                print(f"    Downtrend: {m5_trend.get('downtrend')}, Micro: {m5_trend.get('micro_downtrend')}")

    # Resumo estatístico
    print()
    print("=" * 100)
    print("RESUMO ESTATISTICO:")
    print("=" * 100)
    print(f"Total de trades: {total}")
    print(f"Alinhados com tendencia: {aligned_with_trend} ({aligned_with_trend/total*100:.1f}%)")
    print(f"Contra tendencia: {against_trend} ({against_trend/total*100:.1f}%)")
    print(f"Neutro: {neutral} ({neutral/total*100:.1f}%)")
    print()
    print(f"Wins: {wins} ({wins/(wins+losses)*100:.1f}%)" if wins+losses > 0 else "Wins: 0")
    print(f"Losses: {losses} ({losses/(wins+losses)*100:.1f}%)" if wins+losses > 0 else "Losses: 0")
    print()

    # Análise por tipo de alinhamento
    if against_trend > 0:
        print(f"\n[DIAGNOSTICO] {against_trend} entradas CONTRA a tendencia detectadas!")
        print("Possíveis causas:")
        print("  1. IA está ignorando a validação M5")
        print("  2. Validação M5 está desabilitada ou com bug")
        print("  3. Fallback tradicional está abrindo sem validação")
        print("  4. Dados M5 mudaram após a entrada")
    else:
        print("\n[OK] Todas as entradas estao ALINHADAS com a tendencia M5!")
        print("O sistema de validação está funcionando corretamente.")

    print("=" * 100)

    mt5.shutdown()

if __name__ == "__main__":
    main()
