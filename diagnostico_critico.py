# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import sys

# Forçar encoding UTF-8 no output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('btc_trading_logs.db')

print("=" * 60)
print("DIAGNOSTICO CRITICO - BTC LOSS ZERO AGENT")
print("=" * 60)

# Buscar todas operações
df = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC LIMIT 50", conn)

print(f"\nTotal de operacoes registradas: {len(df)}")

# Contar por status
status_counts = df['status'].value_counts()
print(f"\nPor status:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")

# Análise das posições abertas
df_open = df[df['status'] == 'OPEN']
print(f"\n{'='*60}")
print(f"PROBLEMA IDENTIFICADO: {len(df_open)} POSICOES ABERTAS!")
print(f"{'='*60}")

if len(df_open) > 0:
    # Contar BUY vs SELL
    buy_count = len(df_open[df_open['trade_type'] == 'BUY'])
    sell_count = len(df_open[df_open['trade_type'] == 'SELL'])

    print(f"\nPosicoes BUY: {buy_count}")
    print(f"Posicoes SELL: {sell_count}")

    # Análise de SL
    print(f"\n{'-'*60}")
    print("CONFIGURACAO DE STOP LOSS (primeiras 10):")
    print(f"{'-'*60}")

    for idx, row in df_open.head(10).iterrows():
        sl_dist = abs(row['entry_price'] - row['sl_price'])
        sl_pct = (sl_dist / row['entry_price']) * 100

        print(f"\nID: {row['id']} | {row['trade_type']} | Vol: {row['volume']}")
        print(f"  Entry: ${row['entry_price']:.2f}")
        print(f"  SL:    ${row['sl_price']:.2f}")
        print(f"  TP:    ${row['tp_price']:.2f}")
        print(f"  SL Distance: ${sl_dist:.2f} ({sl_pct:.3f}%)")

        # Calcular perda potencial
        # BTC: cada ponto = $10 por 0.01 lote
        # 0.3 lotes = 30x esse valor = $300 por ponto
        potential_loss = sl_dist * 10 * (row['volume'] / 0.01)
        print(f"  Perda potencial: ${potential_loss:.2f}")

    # Análise temporal
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"\n{'-'*60}")
    print("ANALISE TEMPORAL:")
    print(f"{'-'*60}")
    print(f"Primeira operacao: {df['timestamp'].min()}")
    print(f"Ultima operacao: {df['timestamp'].max()}")

    # Últimas 2 horas
    recent = df[df['timestamp'] > (pd.Timestamp.now() - pd.Timedelta(hours=2))]
    print(f"Operacoes nas ultimas 2h: {len(recent)}")

# Buscar TODAS as operações para estatísticas completas
df_all = pd.read_sql_query("SELECT COUNT(*) as total FROM trades", conn)
print(f"\nTotal ABSOLUTO no banco: {df_all['total'][0]}")

conn.close()

print(f"\n{'='*60}")
print("DIAGNOSTICO E RECOMENDACOES")
print(f"{'='*60}")

print("\n1. PROBLEMA PRINCIPAL:")
print("   - Agente abre posicoes mas NAO fecha")
print("   - 189+ posicoes abertas simultaneamente")
print("   - SL muito apertado: 50 pontos (~0.045%)")
print("   - Volume MUITO ALTO: 0.3 lotes por trade")
print("   - Exposicao total: ~57 lotes (189 x 0.3)")

print("\n2. IMPACTO FINANCEIRO:")
print("   - Cada SL pode gerar ~$1,500 de perda")
print("   - 189 SLs = perda potencial de ~$283,500")
print("   - Risco de margin call IMINENTE")

print("\n3. CAUSA RAIZ:")
print("   - Logica de fechamento nao implementada")
print("   - Agente so tem codigo para ABRIR posicoes")
print("   - Falta monitoramento de posicoes abertas")

print("\n4. ACAO IMEDIATA NECESSARIA:")
print("   >>> PARAR O AGENTE AGORA <<<")
print("   >>> FECHAR TODAS AS POSICOES MANUALMENTE <<<")
print("   >>> NAO REINICIAR ATE CORRIGIR <<<")

print("\n5. CORRECOES NECESSARIAS:")
print("   a) Implementar logica de fechamento de posicoes")
print("   b) Adicionar limite de posicoes simultaneas (max 1-2)")
print("   c) Reduzir volume para 0.01 lotes")
print("   d) Aumentar SL para 100-200 pontos")
print("   e) Adicionar trailing stop")
print("   f) Testar em demo ANTES de producao")
