#!/usr/bin/env python3
"""
Testa exportação de dados para o dashboard MT5.
Gera dados simulados para verificar se o dashboard consegue ler o JSON.
"""

import json
from pathlib import Path
from datetime import datetime
import time

def create_test_data():
    """Cria dados de teste simulando o agente."""
    return {
        "agent": "BTC_Hedge_Agent",
        "state": "trading",
        "symbol": "BTCUSDc",
        "daily_trades": 5,
        "max_daily_trades": 20,
        "total_profit": 12.50,
        "winning_streak": 3,
        "hedge_active": True,
        "positions_count": 2,
        "timestamp": datetime.now().isoformat(),
        # Indicadores simulados
        "current_price": 45234.50,
        "trend": "UP",
        "rsi": 65.3,
        "macd": 12.45,
        "atr": 85.32,
        "sma_20": 45120.00,
        "sma_50": 44980.00,
        "bb_upper": 45450.00,
        "bb_middle": 45120.00,
        "bb_lower": 44790.00
    }

def main():
    """Gera arquivo JSON de teste."""
    print("="*60)
    print("🧪 TESTE DE DADOS PARA DASHBOARD MT5")
    print("="*60)
    print()

    json_path = Path('C:/mcp-trader/agent_data.json')

    print(f"[1] Criando dados de teste...")
    data = create_test_data()

    print(f"[2] Salvando em: {json_path}")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("    ✅ Arquivo criado com sucesso!")
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

    print()
    print("[3] Conteúdo do arquivo:")
    print("-"*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-"*60)

    print()
    print("="*60)
    print("✅ TESTE CONCLUÍDO!")
    print("="*60)
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("   1. Abra o MT5")
    print("   2. Abra um gráfico do BTCUSDc")
    print("   3. Adicione o Expert Advisor 'BTC_Agent_Dashboard'")
    print("   4. Verifique se o painel aparece no canto superior esquerdo")
    print()
    print("💡 Este arquivo será atualizado automaticamente quando o")
    print("   agente real estiver rodando (RUN_BTC_AGENT.bat)")
    print()

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
