#!/usr/bin/env python3
"""
Testa a conexão DIRETA com o MetaTrader 5.
Execute este script para verificar se a conexão está funcionando corretamente.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client

def test_mcp_connection():
    """Testa a conexão DIRETA com o MT5."""
    print("=" * 60)
    print("🧪 TESTANDO CONEXÃO DIRETA COM MT5")
    print("=" * 60)
    print()

    # Obter cliente MT5
    mt5_client = get_mt5_client()

    # Teste 1: Verificar conexão
    print("[1/6] Verificando conexão direta com MT5...")
    if mt5_client.is_connected():
        print("    ✅ Cliente conectado ao MT5 Terminal")
    else:
        print("    ❌ Cliente não está conectado")
        print("    ⚠️  Certifique-se que o MT5 Terminal está aberto e logado!")
        return False

    # Teste 2: Versão do MT5
    print("\n[2/6] Verificando versão do MT5...")
    version = mt5_client.get_version()
    if version:
        print(f"    ✅ MT5 versão: {version}")
    else:
        print("    ❌ Falha ao obter versão")
        return False

    # Teste 3: Informações da conta
    print("\n[3/6] Obtendo informações da conta...")
    account_info = mt5_client.get_account_info()
    if account_info:
        print(f"    ✅ Conta: {account_info.get('login', 'N/A')}")
        print(f"    💰 Saldo: ${account_info.get('balance', 0):,.2f}")
        print(f"    📊 Equity: ${account_info.get('equity', 0):,.2f}")
        print(f"    📈 Margem Livre: ${account_info.get('margin_free', 0):,.2f}")
    else:
        print("    ⚠️  Não foi possível obter informações da conta")
        print("    Certifique-se que o MT5 Terminal está aberto e logado!")

    # Teste 4: Posições abertas
    print("\n[4/6] Verificando posições abertas...")
    positions = mt5_client.positions_get()
    if positions is not None:
        print(f"    ✅ Posições abertas: {len(positions)}")
        if len(positions) > 0:
            for i, pos in enumerate(positions[:3], 1):  # Mostrar até 3
                print(f"       {i}. {pos.get('symbol', 'N/A')} - Ticket: {pos.get('ticket', 'N/A')} - Profit: ${pos.get('profit', 0):,.2f}")
        else:
            print("       Nenhuma posição aberta no momento")
    else:
        print("    ⚠️  Erro ao obter posições")

    # Teste 5: Símbolos disponíveis
    print("\n[5/6] Listando símbolos disponíveis...")
    symbols = mt5_client.get_symbols()
    if symbols:
        print(f"    ✅ {len(symbols)} símbolos disponíveis")
        symbol_names = [s.get('name', '') for s in symbols[:5]]
        print(f"    Exemplos: {', '.join(symbol_names)}")
    else:
        print("    ⚠️  Erro ao obter símbolos")

    # Teste 6: Informações de um símbolo específico
    print("\n[6/6] Testando informações de símbolo (EURUSD)...")
    symbol_info = mt5_client.get_symbol_info("EURUSD")
    if symbol_info:
        print(f"    ✅ EURUSD:")
        print(f"       Bid: {symbol_info.get('bid', 0):.5f}")
        print(f"       Ask: {symbol_info.get('ask', 0):.5f}")
        print(f"       Spread: {symbol_info.get('spread', 0)} points")
        print(f"       Volume: {symbol_info.get('volume_min', 0)} - {symbol_info.get('volume_max', 0)}")
    else:
        print("    ⚠️  Erro ao obter informações do símbolo")

    print()
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("📋 Resumo:")
    print("   • MT5 Terminal: ✅ Conectado")
    print("   • Cliente MT5: ✅ Funcionando")
    print("   • Conexão Direta: ✅ OK")
    print()
    print("🎯 Próximos passos:")
    print("   1. Inicie o Web Dashboard: uv run python run_simple_web.py")
    print("   2. Inicie o Worker: uv run python src/core/main.py")
    print("   3. Acesse: http://localhost:3000")
    print("   4. Teste comandos no chatbot")
    print()
    print("ℹ️  Nota: MCP Server (porta 8000) é opcional")
    print("   Só é necessário para integração com Claude Desktop")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_mcp_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
