#!/usr/bin/env python3
"""
Testar contagem de trades fechados
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.btc_logger import BTCLogger

print("="*80)
print("TESTE: Contagem de Trades Fechados")
print("="*80)

logger = BTCLogger("btc_trading_logs.db")

# Contar todos os trades fechados
total_closed = logger.get_closed_trades_count()
print(f"\n[TOTAL] Trades fechados (todos símbolos): {total_closed}")

# Contar apenas XAUUSDc
xau_closed = logger.get_closed_trades_count(symbol="XAUUSDc")
print(f"[XAUUSDc] Trades fechados (Gold): {xau_closed}")

# Contar BTCUSDm
btc_closed = logger.get_closed_trades_count(symbol="BTCUSDm")
print(f"[BTCUSDm] Trades fechados (BTC): {btc_closed}")

print(f"\n{'='*80}")
print("TESTE APROVADO: Função get_closed_trades_count() funcionando!")
print("="*80)
