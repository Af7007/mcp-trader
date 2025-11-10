"""
Analisa tendência M5 atual do Gold e mostra se deveria abrir trades
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import MetaTrader5 as mt5
from datetime import datetime

def init_mt5():
    """Inicializa MT5"""
    if not mt5.initialize():
        print("ERRO: Falha ao inicializar MT5")
        return False
    print("[OK] MT5 inicializado")
    return True

def analyze_m5_trend():
    """Analisa tendência M5 atual"""
    # Buscar últimos 15 candles M5
    rates = mt5.copy_rates_from_pos(
        "XAUUSDc",
        mt5.TIMEFRAME_M5,
        0,
        15
    )

    if rates is None or len(rates) < 10:
        print("ERRO: Não foi possível obter dados M5")
        return None

    # Reverter ordem (MT5 retorna newest first)
    closes = [r['close'] for r in rates][::-1]
    highs = [r['high'] for r in rates][::-1]
    lows = [r['low'] for r in rates][::-1]

    # Mostrar últimas velas
    print("\nULTIMAS 15 VELAS M5:")
    print("-" * 80)
    for i in range(len(closes)):
        direction = "UP" if i < len(closes)-1 and closes[i] < closes[i+1] else "DOWN" if i < len(closes)-1 and closes[i] > closes[i+1] else "FLAT"
        print(f"  Vela {i}: Close {closes[i]:.3f} ({direction})")

    # Calcular tendência (5/8 velas subindo/descendo)
    ups = sum(1 for i in range(7) if closes[i] < closes[i+1])
    downs = sum(1 for i in range(7) if closes[i] > closes[i+1])

    uptrend = ups >= 5
    downtrend = downs >= 5

    print(f"\nUPS: {ups}/8 velas | DOWNS: {downs}/8 velas")
    print(f"UPTREND: {uptrend} | DOWNTREND: {downtrend}")

    # Micro trend (3 velas consecutivas)
    micro_uptrend = False
    micro_downtrend = False

    for i in range(len(closes) - 2):
        if closes[i] < closes[i+1] < closes[i+2]:
            micro_uptrend = True
            print(f"  Micro UPTREND detectado nas velas {i}-{i+2}")
        if closes[i] > closes[i+1] > closes[i+2]:
            micro_downtrend = True
            print(f"  Micro DOWNTREND detectado nas velas {i}-{i+2}")

    # Análise de momentum
    momentum = (closes[-1] - closes[0]) / closes[0] * 100
    print(f"\nMOMENTUM 15 velas: {momentum:.2f}%")

    # Volatilidade
    avg_range = sum(highs[i] - lows[i] for i in range(len(highs))) / len(highs)
    print(f"VOLATILIDADE média: ${avg_range:.2f}")

    return {
        "uptrend": uptrend,
        "downtrend": downtrend,
        "micro_uptrend": micro_uptrend,
        "micro_downtrend": micro_downtrend,
        "ups": ups,
        "downs": downs,
        "momentum": momentum,
        "current_price": closes[-1],
        "volatility": avg_range
    }

def main():
    print("=" * 100)
    print("ANALISE GOLD - TENDENCIA M5 ATUAL")
    print("=" * 100)

    if not init_mt5():
        return

    # Análise
    trend = analyze_m5_trend()

    if not trend:
        mt5.shutdown()
        return

    print("\n" + "=" * 100)
    print("DECISAO DE TRADING (baseado na validação do código):")
    print("=" * 100)

    # Verificar BUY
    print("\n[BUY]")
    if trend["uptrend"] and trend["micro_uptrend"]:
        print("  [OK] APROVADO - M5 uptrend + micro confirmados")
        print(f"    Uptrend: {trend['uptrend']} ({trend['ups']}/8 velas)")
        print(f"    Micro uptrend: {trend['micro_uptrend']}")
        print(f"    Momentum: {trend['momentum']:.2f}%")
    else:
        print("  [X] REJEITADO - Requer uptrend E micro-uptrend")
        print(f"    Uptrend: {trend['uptrend']} ({trend['ups']}/8 velas)")
        print(f"    Micro uptrend: {trend['micro_uptrend']}")

    # Verificar SELL
    print("\n[SELL]")
    if trend["downtrend"] and trend["micro_downtrend"]:
        print("  [OK] APROVADO - M5 downtrend + micro confirmados")
        print(f"    Downtrend: {trend['downtrend']} ({trend['downs']}/8 velas)")
        print(f"    Micro downtrend: {trend['micro_downtrend']}")
        print(f"    Momentum: {trend['momentum']:.2f}%")
    else:
        print("  [X] REJEITADO - Requer downtrend E micro-downtrend")
        print(f"    Downtrend: {trend['downtrend']} ({trend['downs']}/8 velas)")
        print(f"    Micro downtrend: {trend['micro_downtrend']}")

    # Recomendação final
    print("\n" + "=" * 100)
    print("RECOMENDACAO:")
    print("=" * 100)

    if trend["uptrend"] and trend["micro_uptrend"]:
        print("OPERAR: BUY apenas")
        print("EVITAR: SELL (contra a tendência)")
    elif trend["downtrend"] and trend["micro_downtrend"]:
        print("OPERAR: SELL apenas")
        print("EVITAR: BUY (contra a tendência)")
    else:
        print("AGUARDAR: Mercado sem tendência clara M5")
        print("O agente NÃO deve abrir posições neste momento")

    print("=" * 100)

    mt5.shutdown()

if __name__ == "__main__":
    main()
