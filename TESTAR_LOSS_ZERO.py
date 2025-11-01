#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste rápido para validar o Agente Loss Zero

Testa:
1. Importacao do modulo
2. Inicializacao do agente
3. Conexao com MT5
4. Calculo de RSI
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Testa importacoes"""
    print("\n" + "="*70)
    print("TESTE 1: Importacoes")
    print("="*70)

    try:
        print("  Importando MetaTrader5...", end=" ")
        import MetaTrader5 as mt5
        print("[OK]")

        print("  Importando agente Loss Zero...", end=" ")
        from agents.btc_loss_zero_otimizado import BTCLossZeroOtimizado
        print("[OK]")

        print("  [SUCESSO] Importacoes OK!")
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def test_mt5_connection():
    """Testa conexao com MT5"""
    print("\n" + "="*70)
    print("TESTE 2: Conexao com MetaTrader 5")
    print("="*70)

    try:
        import MetaTrader5 as mt5

        print("  Inicializando MT5...", end=" ")
        if not mt5.initialize():
            error = mt5.last_error()
            print("[ERRO]")
            print(f"  MT5 nao inicializou: {error}")
            print("\n  ATENCAO: Certifique-se de que MetaTrader 5 esta aberto e logado!")
            return False
        print("[OK]")

        print("  Obtendo info da conta...", end=" ")
        account = mt5.account_info()
        if account:
            print("[OK]")
            print(f"    Conta: {account.login}")
            print(f"    Servidor: {account.server}")
            print(f"    Saldo: ${account.balance:.2f}")
            return True
        else:
            print("[ERRO] Nao foi possivel obter info da conta")
            return False

    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def test_symbol_availability():
    """Testa disponibilidade do simbolo BTCUSDc"""
    print("\n" + "="*70)
    print("TESTE 3: Disponibilidade do Simbolo BTCUSDc")
    print("="*70)

    try:
        import MetaTrader5 as mt5

        if not mt5.initialize():
            print("  [ERRO] MT5 nao inicializado")
            return False

        print("  Procurando simbolo BTCUSDc...", end=" ")

        # Tentar obter info do simbolo
        symbol_info = mt5.symbol_info("BTCUSDc")

        if symbol_info is None:
            print("[NAO ENCONTRADO]")
            print("\n  ATENCAO: Simbolo BTCUSDc nao encontrado!")
            print("  Procurando simbolos disponiveis...")

            # Listar simbolos de cripto
            symbols = mt5.symbols_get(group="*Crypto*")
            if symbols:
                print(f"\n  Simbolos cripto disponiveis:")
                for sym in symbols[:10]:
                    print(f"    - {sym.name}")

            return False

        print("[OK]")
        print(f"    Nome: {symbol_info.name}")
        print(f"    Ask: {symbol_info.ask}")
        print(f"    Bid: {symbol_info.bid}")
        print(f"    Min Lot: {symbol_info.volume_min}")
        print(f"    Max Lot: {symbol_info.volume_max}")
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def test_agent_init():
    """Testa inicializacao do agente"""
    print("\n" + "="*70)
    print("TESTE 4: Inicializacao do Agente Loss Zero")
    print("="*70)

    try:
        from agents.btc_loss_zero_otimizado import BTCLossZeroOtimizado

        print("  Criando agente...", end=" ")
        agent = BTCLossZeroOtimizado(
            symbol="BTCUSDc",
            volume=0.05,
            check_interval=15,
            trailing_start_percent=0.5,
            trailing_increment=0.1,
            use_buy=True,
            use_sell=True
        )
        print("[OK]")

        print("  Validando configuracao:")
        print(f"    Symbol: {agent.symbol}")
        print(f"    Volume: {agent.volume}")
        print(f"    Trailing Start: {agent.trailing_start_percent}%")
        print(f"    Trailing Increment: {agent.trailing_increment}%")
        print(f"    BUY/SELL: {'Ativo' if agent.use_buy and agent.use_sell else 'Seletivo'}")

        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def test_rsi_calculation():
    """Testa calculo de RSI"""
    print("\n" + "="*70)
    print("TESTE 5: Calculo de RSI")
    print("="*70)

    try:
        from agents.btc_loss_zero_otimizado import BTCLossZeroOtimizado
        import MetaTrader5 as mt5

        if not mt5.initialize():
            print("  [ERRO] MT5 nao inicializado")
            return False

        agent = BTCLossZeroOtimizado()

        print("  Obtendo dados M1...", end=" ")
        rates = mt5.copy_rates_from_pos(
            "BTCUSDc",
            mt5.TIMEFRAME_M1,
            0,
            50
        )

        if rates is None or len(rates) == 0:
            print("[ERRO] Nao foi possivel obter dados")
            return False

        print("[OK]")

        print("  Calculando RSI...", end=" ")
        rsi = agent._calculate_rsi(rates, 14)
        print("[OK]")
        print(f"    RSI (14): {rsi:.2f}")
        print(f"    Status: ", end="")

        if rsi > 70:
            print("OVERBOUGHT (Sinal de SELL)")
        elif rsi < 30:
            print("OVERSOLD (Sinal de BUY)")
        else:
            print("NEUTRO")

        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n")
    print("=" * 70)
    print(" " * 15 + "BTC LOSS ZERO - TESTES DE VALIDACAO")
    print("=" * 70)

    tests = [
        ("Importacoes", test_imports),
        ("Conexao MT5", test_mt5_connection),
        ("Simbolo BTCUSDc", test_symbol_availability),
        ("Inicializacao do Agente", test_agent_init),
        ("Calculo de RSI", test_rsi_calculation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\n[ABORTADO] Testes interrompidos pelo usuario")
            return 1
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado: {e}")
            results.append((name, False))

    # Resumo dos testes
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASSOU]" if result else "[FALHOU]"
        print(f"{status:12} - {name}")

    print("="*70)
    print(f"Resultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n[SUCESSO] Todos os testes passaram! O agente esta pronto para usar.")
        print("\nPara iniciar o agente, execute:")
        print("  python EXECUTAR_LOSS_ZERO.py")
        print("  ou")
        print("  RODAR_LOSS_ZERO.bat (Windows)")
        return 0
    else:
        print("\n[FALHA] Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
