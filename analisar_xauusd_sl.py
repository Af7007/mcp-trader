#!/usr/bin/env python3
"""
ANALISE ESPECIFICA DO CALCULO DE SL PARA XAUUSDc
Verifica como o SL está sendo calculado nos trades de XAUUSDc
"""

import sqlite3
import os

def analisar_xauusd_trades():
    """Analisa trades específicos de XAUUSDc"""
    if not os.path.exists('trading.db'):
        print("ERRO: Banco trading.db não encontrado")
        return

    try:
        conn = sqlite3.connect('trading.db')
        cursor = conn.cursor()

        # Buscar todos os trades de XAUUSDc
        cursor.execute("""
            SELECT id, ticket, symbol, type, volume, open_price, sl, tp, profit, open_time, close_time
            FROM game_history
            WHERE symbol = 'XAUUSDc'
            ORDER BY id DESC
            LIMIT 20
        """)

        trades = cursor.fetchall()

        print("ANALISE DE TRADES XAUUSDc")
        print("=" * 80)
        print(f"Total de trades encontrados: {len(trades)}")
        print()

        for trade in trades:
            id_trade, ticket, symbol, tipo, volume, open_price, sl, tp, profit, open_time, close_time = trade

            print(f"TRADE ID: {id_trade} | TICKET: {ticket}")
            print(f"  Tipo: {tipo} | Volume: {volume}")
            print(f"  Preço Abertura: {open_price}")
            print(f"  SL: {sl} | TP: {tp}")
            print(f"  Profit: {profit}")
            print(f"  Open Time: {open_time} | Close Time: {close_time}")

            # Calcular diferença esperada para SL de $6
            if open_price and sl:
                if tipo == 'BUY':
                    sl_esperado = open_price - 6.0  # Para BUY, SL deve ser preço - $6
                    diferenca = abs(sl - sl_esperado)
                    print(f"  SL ESPERADO (BUY): {sl_esperado:.2f} | DIFERENCA: {diferenca:.2f}")
                elif tipo == 'SELL':
                    sl_esperado = open_price + 6.0  # Para SELL, SL deve ser preço + $6
                    diferenca = abs(sl - sl_esperado)
                    print(f"  SL ESPERADO (SELL): {sl_esperado:.2f} | DIFERENCA: {diferenca:.2f}")

                if diferenca > 0.01:  # Tolerância de 1 cent
                    print(f"  ERRO: SL INCORRETO! Diferença de ${diferenca:.2f}")
                else:
                    print("  OK: SL CORRETO")
            print("-" * 50)

        # Estatísticas gerais
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                AVG(CASE WHEN sl IS NOT NULL THEN sl END) as avg_sl,
                MIN(CASE WHEN sl IS NOT NULL THEN sl END) as min_sl,
                MAX(CASE WHEN sl IS NOT NULL THEN sl END) as max_sl
            FROM game_history
            WHERE symbol = 'XAUUSDc'
        """)

        stats = cursor.fetchone()
        total, avg_sl, min_sl, max_sl = stats

        print("\nESTATISTICAS GERAIS XAUUSDc:")
        print(f"Total de trades: {total}")
        print(f"SL médio: {avg_sl:.2f}" if avg_sl else "SL médio: N/A")
        print(f"SL mínimo: {min_sl:.2f}" if min_sl else "SL mínimo: N/A")
        print(f"SL máximo: {max_sl:.2f}" if max_sl else "SL máximo: N/A")

        conn.close()

    except Exception as e:
        print(f"ERRO ao analisar trades: {e}")

def verificar_configuracao_gold():
    """Verifica configurações específicas para Gold"""
    print("\nVERIFICANDO CONFIGURACOES GOLD:")
    print("=" * 50)

    # Verificar arquivos de configuração
    config_files = [
        'src/core/config.py',
        'EXECUTAR_GOLD_AGRESSIVO.py',
        'EXECUTAR_GOLD_6USD_CORRIGIDO.py'
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\nAnalisando: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Procurar por configurações de SL
                    if 'SL' in content.upper() or 'stop' in content.lower():
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if ('sl' in line.lower() or 'stop' in line.lower()) and ('6' in line or 'gold' in line.lower() or 'xau' in line.lower()):
                                print(f"  Linha {i+1}: {line.strip()}")

            except Exception as e:
                print(f"  ERRO ao ler {config_file}: {e}")

if __name__ == "__main__":
    analisar_xauusd_trades()
    verificar_configuracao_gold()
