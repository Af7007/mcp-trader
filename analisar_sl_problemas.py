import sqlite3
import pandas as pd
from datetime import datetime

# Conectar ao banco
conn = sqlite3.connect('btc_trading_logs.db')

print("=== ANÁLISE DE OPERAÇÕES - BTC LOSS ZERO ===\n")

# Buscar TODAS as operações
df_all = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC", conn)
print(f"Total de operações registradas: {len(df_all)}")

# Separar por status
df_open = df_all[df_all['status'] == 'OPEN']
df_closed = df_all[df_all['status'] == 'CLOSED']

print(f"Operações ABERTAS: {len(df_open)}")
print(f"Operações FECHADAS: {len(df_closed)}")

print("\n=== PROBLEMA IDENTIFICADO ===")
if len(df_open) > 20:
    print(f"⚠️ CRÍTICO: Há {len(df_open)} posições ABERTAS simultaneamente!")
    print("Isso indica que:")
    print("1. O agente está abrindo posições mas não está fechando")
    print("2. Pode haver problemas na lógica de fechamento de posições")
    print("3. Risco de margin call com tantas posições abertas")

print("\n=== ANÁLISE DAS POSIÇÕES ABERTAS ===")
if len(df_open) > 0:
    # Análise por tipo de operação
    buy_count = len(df_open[df_open['trade_type'] == 'BUY'])
    sell_count = len(df_open[df_open['trade_type'] == 'SELL'])

    print(f"\nPosições BUY abertas: {buy_count}")
    print(f"Posições SELL abertas: {sell_count}")

    # Verificar configuração de SL
    print("\n--- Configuração de Stop Loss (SL) ---")
    for idx, row in df_open.head(10).iterrows():
        sl_distance = abs(row['entry_price'] - row['sl_price']) if pd.notna(row['sl_price']) else None
        sl_pct = (sl_distance / row['entry_price'] * 100) if sl_distance else None

        print(f"\nTrade #{row['id']} ({row['trade_type']}):")
        print(f"  Entrada: ${row['entry_price']:.2f}")
        print(f"  SL: ${row['sl_price']:.2f}" if pd.notna(row['sl_price']) else "  SL: NÃO DEFINIDO ⚠️")
        print(f"  TP: ${row['tp_price']:.2f}" if pd.notna(row['tp_price']) else "  TP: NÃO DEFINIDO ⚠️")
        if sl_distance:
            print(f"  Distância SL: ${sl_distance:.2f} ({sl_pct:.3f}%)")
            print(f"  Volume: {row['volume']} lotes")

            # Calcular potencial de perda
            if row['symbol'] == 'BTCUSDc':
                # Para BTC, cada ponto vale aproximadamente $10 por 0.01 lote
                # Com 0.3 lotes, cada ponto vale $300
                potential_loss = sl_distance * 10 * (row['volume'] / 0.01)
                print(f"  Perda potencial se SL bater: ${potential_loss:.2f}")

print("\n=== ANÁLISE DAS OPERAÇÕES FECHADAS ===")
if len(df_closed) > 0:
    wins = len(df_closed[df_closed['profit_loss'] > 0])
    losses = len(df_closed[df_closed['profit_loss'] < 0])
    win_rate = (wins / len(df_closed) * 100) if len(df_closed) > 0 else 0

    print(f"\nTotal fechadas: {len(df_closed)}")
    print(f"Vitórias: {wins} ({win_rate:.1f}%)")
    print(f"Perdas: {losses} ({100-win_rate:.1f}%)")
    print(f"Lucro total: ${df_closed['profit_loss'].sum():.2f}")

    # Análise de perdas
    df_losses = df_closed[df_closed['profit_loss'] < 0]
    if len(df_losses) > 0:
        print("\n--- Detalhes das Operações com Prejuízo ---")
        for idx, row in df_losses.head(10).iterrows():
            print(f"\nTrade #{row['id']} ({row['trade_type']}):")
            print(f"  Entrada: ${row['entry_price']:.2f}")
            print(f"  Saída: ${row['exit_price']:.2f}")
            print(f"  SL: ${row['sl_price']:.2f}" if pd.notna(row['sl_price']) else "  SL: Não definido")
            print(f"  Razão de saída: {row['exit_reason']}")
            print(f"  Prejuízo: ${row['profit_loss']:.2f}")

            # Verificar se foi SL
            if pd.notna(row['exit_reason']) and 'SL' in str(row['exit_reason']).upper():
                print("  ⚠️ FECHADO POR STOP LOSS")
else:
    print("\n⚠️ NENHUMA OPERAÇÃO FECHADA NO BANCO DE DADOS")
    print("Isso explica o problema: o agente está apenas ABRINDO posições")
    print("mas não está FECHANDO elas!")

# Verificar timestamps
print("\n=== ANÁLISE TEMPORAL ===")
if len(df_all) > 0:
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    print(f"Primeira operação: {df_all['timestamp'].min()}")
    print(f"Última operação: {df_all['timestamp'].max()}")

    # Operações nas últimas horas
    recent = df_all[df_all['timestamp'] > (pd.Timestamp.now() - pd.Timedelta(hours=2))]
    print(f"Operações nas últimas 2 horas: {len(recent)}")

conn.close()

print("\n=== DIAGNÓSTICO ===")
print("\n1. PROBLEMA PRINCIPAL:")
print("   - O agente está abrindo muitas posições simultâneas")
print("   - As posições não estão sendo fechadas automaticamente")
print("   - SL configurado em 50 pontos (~$50 de distância)")
print("   - Com 0.3 lotes, cada SL pode gerar ~$1500 de perda!")

print("\n2. CAUSAS PROVÁVEIS:")
print("   - Lógica de fechamento de posições não está funcionando")
print("   - SL muito próximo da entrada (50 pontos)")
print("   - Volume muito alto (0.3 lotes = 3x o normal)")
print("   - Faltam verificações de posições abertas antes de abrir novas")

print("\n3. SOLUÇÕES RECOMENDADAS:")
print("   - Fechar TODAS as posições abertas manualmente primeiro")
print("   - Ajustar SL para distância maior (100-200 pontos)")
print("   - Reduzir volume para 0.01-0.02 lotes")
print("   - Implementar limite de posições abertas simultâneas")
print("   - Adicionar lógica de trailing stop")
print("   - Testar em conta demo primeiro")
