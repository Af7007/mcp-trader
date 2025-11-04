import sqlite3

print('=== VERIFICANDO STOP LOSS NO BANCO BTC ===')
conn = sqlite3.connect('btc_trading_logs.db')
cursor = conn.cursor()

# Verificar os últimos trades com SL
cursor.execute('SELECT id, sl_price, symbol, status FROM trades WHERE sl_price IS NOT NULL ORDER BY id DESC LIMIT 10')
trades = cursor.fetchall()

print('Ultimos 10 trades com Stop Loss:')
for trade in trades:
    trade_id, sl_price, symbol, status = trade
    print(f'  ID: {trade_id}, SL: ${sl_price:.2f}, Symbol: {symbol}, Status: {status}')

# Verificar estatísticas de SL
cursor.execute('SELECT COUNT(*), AVG(sl_price), MIN(sl_price), MAX(sl_price) FROM trades WHERE sl_price IS NOT NULL')
stats = cursor.fetchone()
count, avg_sl, min_sl, max_sl = stats

print(f'\nEstatisticas Stop Loss:')
print(f'  Total com SL: {count}')
print(f'  Media: ${avg_sl:.2f}')
print(f'  Minimo: ${min_sl:.2f}')
print(f'  Maximo: ${max_sl:.2f}')

# Verificar SLs problemáticos (< $1)
cursor.execute('SELECT COUNT(*) FROM trades WHERE sl_price > 0 AND sl_price < 1')
problem_count = cursor.fetchone()[0]
print(f'  Trades com SL < $1.0: {problem_count}')

# Verificar trades recentes com magic number
cursor.execute('SELECT COUNT(*) FROM trades WHERE magic_number IS NOT NULL')
magic_count = cursor.fetchone()[0]
print(f'  Trades com magic number: {magic_count}')

# Verificar se há problemas de conversão (preço em centavos vs dólares)
cursor.execute('SELECT COUNT(*) FROM trades WHERE sl_price > 0 AND sl_price < 10')
potencial_problema = cursor.fetchone()[0]
print(f'  Trades com SL < $10 (possivel problema): {potencial_problema}')

conn.close()
print('\n=== VERIFICACAO CONCLUIDA ===')
