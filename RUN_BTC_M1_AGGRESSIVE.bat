@echo off
echo ================================
echo   BTC USD CENTS - M1 AGGRESSIVE
echo ================================
echo.

echo Iniciando Agente BTC M1 Aggressive...
echo.
echo CONFIGURACOES:
echo   - Symbol: BTCUSDc (cents)
echo   - Timeframe: M1
echo   - Volume: 0.05 lots (aggressive)
echo   - Target Profit: $1.0
echo   - Hedge Trigger: -$3.0
echo   - Hedge TP: $3.0
echo   - Check Interval: 15s
echo.

cd /d "%~dp0"
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from agents.btc_hedge_agent import BTCHedgeAgent
    
    print('Criando agente BTC M1 Aggressive...')
    
    # Configuracoes M1 Aggressive
    agent = BTCHedgeAgent(
        symbol='BTCUSDc',      # Cents
        volume=0.05,           # Aggressive volume
        target_profit=1.0,     # Menor TP para M1
        check_interval=15,     # Mais frequente
        hedge_trigger=-3.0,    # Mais sensivel
        hedge_tp_target=3.0,   # TP hedge menor
        atr_multiplier=1.5,    # SL mais apertado
        only_sell=False        # BUY habilitado
    )
    
    print()
    print('AGENTE BTC M1 AGGRESSIVE CRIADO!')
    print()
    print('Configuracoes:')
    print(f'  Symbol: {agent.symbol}')
    print(f'  Volume: {agent.volume} lots')
    print(f'  Target Profit: ${agent.target_profit}')
    print(f'  Hedge Trigger: ${agent.hedge_trigger}')
    print(f'  Hedge TP: ${agent.hedge_tp_target}')
    print(f'  Check Interval: {agent.check_interval}s')
    print(f'  ATR Multiplier: {agent.atr_multiplier}x')
    print(f'  BUY/SELL: {\"SELL-Only\" if agent.only_sell else \"BUY/SELL Habilitado\"}')
    print()
    print('VANTAGENS M1 AGGRESSIVE:')
    print('  - Scalping ativo em timeframe M1')
    print('  - Volume 67% maior que otimizado')
    print('  - TP 60% menor para trades rapidos')
    print('  - Hedge 25% mais sensivel')
    print('  - Check 2x mais frequente')
    print('  - BTCUSDc: menor spread')
    print('  - BUY/SELL habilitado')
    print()
    print('Para executar em modo live, descomente:')
    print('agent.run()')
    
except Exception as e:
    print(f'Erro: {e}')
"

echo.
echo Agente configurado! 
echo Para executar em live mode, modifique o script.
echo.
pause
