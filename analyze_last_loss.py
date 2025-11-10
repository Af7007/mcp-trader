"""
Analisa a última ordem que fechou negativa com detalhes completos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.mt5_mcp_client import get_mt5_client
from core.mt5_direct_client import get_mt5_client as get_direct_client
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_last_losses():
    """Analisa últimas ordens com loss"""
    mt5 = get_mt5_client()
    mt5_direct = get_direct_client()

    # Buscar histórico das últimas 24h
    from_date = int((datetime.now() - timedelta(hours=24)).timestamp())
    to_date = int(datetime.now().timestamp())

    print("=" * 100)
    print("ANALISE DE ORDENS COM LOSS - ULTIMAS 24H")
    print("=" * 100)
    print()

    history = mt5.history_deals_get(from_date, to_date)

    if not history or 'deals' not in history:
        print("Nenhum deal encontrado")
        return

    deals = history['deals']
    print(f"Total de deals: {len(deals)}")
    print()

    # Agrupar por order
    orders = defaultdict(list)
    for deal in deals:
        order_id = deal.get('order', 0)
        orders[order_id].append(deal)

    # Encontrar últimas ordens com loss
    print("[ANALISE] Ultimas 3 ordens com LOSS:")
    print("=" * 100)

    loss_count = 0
    for order_id in sorted(orders.keys(), reverse=True):
        deals_list = orders[order_id]

        # Calcular profit total da ordem
        total_profit = sum(d.get('profit', 0) for d in deals_list)

        if total_profit < -0.1 and loss_count < 3:  # Loss maior que $0.10
            loss_count += 1

            # Separar IN e OUT
            in_deals = [d for d in deals_list if d.get('entry') == 0]
            out_deals = [d for d in deals_list if d.get('entry') == 1]

            print(f"\nORDER {order_id}: LOSS ${total_profit:.2f}")
            print("-" * 100)

            # Deal de entrada
            if in_deals:
                deal_in = in_deals[0]
                entry_time = datetime.fromtimestamp(deal_in.get('time', 0))
                deal_type = 'BUY' if deal_in.get('type') == 0 else 'SELL'
                symbol = deal_in.get('symbol', 'XAUUSDc')

                print(f"[ENTRADA]")
                print(f"  Deal ID: {deal_in.get('ticket')}")
                print(f"  Symbol: {symbol}")
                print(f"  Tipo: {deal_type}")
                print(f"  Preco: {deal_in.get('price', 0):.3f}")
                print(f"  Volume: {deal_in.get('volume', 0):.2f}")
                print(f"  Time: {entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

            # Deal de saída
            if out_deals:
                deal_out = out_deals[0]
                exit_time = datetime.fromtimestamp(deal_out.get('time', 0))

                print(f"[SAIDA]")
                print(f"  Deal ID: {deal_out.get('ticket')}")
                print(f"  Preco: {deal_out.get('price', 0):.3f}")
                print(f"  Volume: {deal_out.get('volume', 0):.2f}")
                print(f"  Profit: ${deal_out.get('profit', 0):.2f}")
                print(f"  Time: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

                # Calcular métricas detalhadas
                if in_deals:
                    entry_price = in_deals[0].get('price', 0)
                    exit_price = deal_out.get('price', 0)
                    price_diff = abs(exit_price - entry_price)
                    duration = (exit_time - entry_time).total_seconds() / 60
                    volume = in_deals[0].get('volume', 0)

                    print(f"[METRICAS]")
                    print(f"  Distancia percorrida: ${price_diff:.3f}")
                    print(f"  Duracao: {duration:.1f} minutos")
                    print(f"  Profit real: ${total_profit:.2f}")
                    print()

                    # Buscar informações do símbolo para calcular SL esperado
                    symbol_info = mt5_direct.symbol_info(symbol)

                    if symbol_info and volume > 0:
                        point = symbol_info.point
                        tick_value = symbol_info.trade_tick_value
                        tick_size = symbol_info.trade_tick_size

                        print(f"[PARAMETROS DO SIMBOLO]")
                        print(f"  Point: {point}")
                        print(f"  Tick value: ${tick_value:.4f}")
                        print(f"  Tick size: {tick_size}")
                        print()

                        # Calcular quantos pontos a ordem percorreu
                        pontos_percorridos = price_diff / point

                        # Calcular o valor por ponto para este volume
                        valor_por_ponto = tick_value * volume

                        # Calcular loss esperado com a fórmula ANTIGA (volume * 100)
                        # Formula antiga: price_distance = loss / (volume * 100)
                        # Invertendo: loss = price_distance * volume * 100
                        loss_formula_antiga = price_diff * volume * 100

                        # Calcular loss esperado com a fórmula NOVA (point_value)
                        # Formula nova: pontos = loss / (point_value * volume)
                        # Invertendo: loss = pontos * point_value * volume
                        loss_formula_nova = pontos_percorridos * tick_value * volume

                        print(f"[COMPARACAO DE FORMULAS]")
                        print(f"  Pontos percorridos: {pontos_percorridos:.1f}")
                        print(f"  Valor por ponto: ${valor_por_ponto:.4f}")
                        print()
                        print(f"  LOSS REAL (MT5): ${abs(total_profit):.2f}")
                        print(f"  LOSS FORMULA ANTIGA (vol*100): ${loss_formula_antiga:.2f}")
                        print(f"  LOSS FORMULA NOVA (point_value): ${loss_formula_nova:.2f}")
                        print()

                        # Verificar qual fórmula está mais próxima
                        diff_antiga = abs(abs(total_profit) - loss_formula_antiga)
                        diff_nova = abs(abs(total_profit) - loss_formula_nova)

                        print(f"[PRECISAO]")
                        print(f"  Diferenca formula ANTIGA: ${diff_antiga:.2f}")
                        print(f"  Diferenca formula NOVA: ${diff_nova:.2f}")

                        if diff_nova < diff_antiga:
                            print(f"  [OK] Formula NOVA eh mais precisa!")
                        else:
                            print(f"  [ALERTA] Formula ANTIGA eh mais precisa - verificar configuracao")
                        print()

                        # Mostrar o SL price
                        if deal_type == 'BUY':
                            sl_price = entry_price - price_diff
                            print(f"[SL CALCULADO]")
                            print(f"  Entry: {entry_price:.3f}")
                            print(f"  Exit: {exit_price:.3f}")
                            print(f"  SL deve estar em: {sl_price:.3f} (BUY - abaixo do entry)")
                        else:
                            sl_price = entry_price + price_diff
                            print(f"[SL CALCULADO]")
                            print(f"  Entry: {entry_price:.3f}")
                            print(f"  Exit: {exit_price:.3f}")
                            print(f"  SL deve estar em: {sl_price:.3f} (SELL - acima do entry)")

                    print()

            print("=" * 100)

    if loss_count == 0:
        print("\n[OK] Nenhuma ordem com loss significativo nas ultimas 24h")
        print("=" * 100)

if __name__ == "__main__":
    analyze_last_losses()
