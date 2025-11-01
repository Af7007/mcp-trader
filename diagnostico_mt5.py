#!/usr/bin/env python3
"""
Script de diagnóstico para verificar estado do MT5
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def diagnose():
    """Executa diagnóstico completo do MT5."""
    print("="*70)
    print("🔍 DIAGNÓSTICO DO MT5")
    print("="*70)
    print()

    # 1. Verificar conexão
    print("[1] Verificando conexão com MT5...")
    try:
        mt5 = get_mt5_client()
        print("    ✅ MT5 Client criado com sucesso")
    except Exception as e:
        print(f"    ❌ Erro ao criar MT5 Client: {e}")
        return False

    print()

    # 2. Verificar inicialização
    print("[2] Verificando inicialização do MT5...")
    try:
        # Tentar obter informações da conta
        account_info = mt5.get_account_info()
        if account_info:
            print("    ✅ MT5 inicializado e respondendo")
            print(f"       Login: {account_info.get('login', 'N/A')}")
            print(f"       Servidor: {account_info.get('server', 'N/A')}")
            print(f"       Saldo: ${account_info.get('balance', 0):,.2f}")
            print(f"       Equity: ${account_info.get('equity', 0):,.2f}")
            print(f"       Margem Livre: ${account_info.get('margin_free', 0):,.2f}")
        else:
            print("    ⚠️  MT5 não retornou informações da conta")
    except Exception as e:
        print(f"    ❌ Erro ao obter informações da conta: {e}")

    print()

    # 3. Verificar símbolos
    print("[3] Verificando símbolos disponíveis...")
    symbols_to_check = ['BTCUSDm', 'BTCUSDc', 'XAUUSDm', 'EURUSDc', 'GBPUSDc', 'USDJPYc']

    for symbol in symbols_to_check:
        try:
            symbol_info = mt5.get_symbol_info(symbol)
            if symbol_info:
                print(f"    ✅ {symbol}: DISPONÍVEL")
                print(f"       Bid: {symbol_info.get('bid', 0):.5f}")
                print(f"       Ask: {symbol_info.get('ask', 0):.5f}")
                print(f"       Spread: {symbol_info.get('spread', 0)} points")
            else:
                print(f"    ❌ {symbol}: NÃO ENCONTRADO")
        except Exception as e:
            print(f"    ❌ {symbol}: Erro - {e}")

    print()

    # 4. Testar obtenção de rates
    print("[4] Testando obtenção de rates (M5)...")
    for symbol in ['BTCUSDm', 'BTCUSDc']:
        try:
            rates = mt5.copy_rates_from_pos(
                symbol=symbol,
                timeframe="M5",
                start_pos=0,
                count=5
            )
            if rates:
                print(f"    ✅ {symbol}: {len(rates)} barras obtidas")
                print(f"       Última barra: Open=${rates[-1]['open']:,.2f}, Close=${rates[-1]['close']:,.2f}")
                break  # Se conseguiu, sai do loop
            else:
                print(f"    ⚠️  {symbol}: Nenhuma barra retornada")
        except Exception as e:
            print(f"    ❌ {symbol}: Erro - {e}")

    print()

    # 5. Verificar posições abertas
    print("[5] Verificando posições abertas...")
    try:
        positions = mt5.positions_get()
        if positions:
            print(f"    ℹ️  {len(positions)} posição(ões) aberta(s)")
            for pos in positions[:3]:  # Mostrar até 3
                print(f"       - Ticket {pos.get('ticket')}: {pos.get('type')} {pos.get('volume')} lots")
        else:
            print("    ✅ Nenhuma posição aberta")
    except Exception as e:
        print(f"    ❌ Erro ao obter posições: {e}")

    print()

    # 6. Checklist de problemas comuns
    print("[6] Checklist de Problemas Comuns")
    print()

    issues = []

    # Verificar MT5 aberto
    try:
        account_info = mt5.get_account_info()
        if not account_info:
            issues.append("MT5 pode não estar aberto ou logado")
    except:
        issues.append("MT5 pode não estar aberto ou logado")

    # Verificar símbolo
    try:
        symbol_info = mt5.get_symbol_info("BTCUSDm")
        if not symbol_info:
            issues.append("BTCUSDm não está no Market Watch do MT5")
    except:
        issues.append("BTCUSDm não está no Market Watch do MT5")

    # Verificar rates
    try:
        rates = mt5.copy_rates_from_pos("BTCUSDm", "M5", 0, 5)
        if not rates:
            issues.append("Não consegue obter rates de BTCUSDm (pode estar lateral)")
    except:
        issues.append("Erro ao obter rates (verificar símbolo e horário de mercado)")

    if issues:
        print("⚠️  Problemas Potenciais Detectados:")
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. {issue}")
        print()
        print("💡 Soluções:")
        print("    1. Certifique-se que o MT5 está aberto")
        print("    2. Verifique se está logado na conta")
        print("    3. Adicione BTCUSDm ao Market Watch (Ctrl+M no MT5)")
        print("    4. Verifique se o mercado está aberto (não está fora do horário)")
        print("    5. Reinicie o MT5 se persistir o problema")
    else:
        print("✅ Nenhum problema detectado!")

    print()
    print("="*70)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("="*70)
    print()

if __name__ == "__main__":
    diagnose()
