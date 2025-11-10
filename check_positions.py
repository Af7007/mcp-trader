import MetaTrader5 as mt5

mt5.initialize()
pos = mt5.positions_get(symbol='BTCUSDc')
print(f'Posicoes abertas: {len(pos) if pos else 0}')

if pos:
    for p in pos:
        print(f'\nTicket: {p.ticket}')
        print(f'Type: {"BUY" if p.type==0 else "SELL"}')
        print(f'Entry: {p.price_open}')
        print(f'Current: {p.price_current}')
        print(f'SL: {p.sl}')
        print(f'Profit: ${p.profit:.2f}')
        print(f'Volume: {p.volume}')
else:
    print('Nenhuma posicao aberta')

mt5.shutdown()
