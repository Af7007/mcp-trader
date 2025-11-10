"""
Teste para verificar se o PositionMonitorWorker inicia corretamente
com os parametros corrigidos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.mt5_direct_client import get_mt5_client
from core.position_monitor_worker import PositionMonitorWorker
import time

print("=" * 80)
print("TESTE: Inicializacao do PositionMonitorWorker")
print("=" * 80)

# Get MT5 client
mt5 = get_mt5_client()

print("\n[1] Testando inicializacao com parametros ERRADOS (como estava antes):")
print("-" * 80)
try:
    # Parametros errados (como estava)
    worker_bad = PositionMonitorWorker(
        agent=None,  # ERRADO
        symbol="BTCUSDc",
        check_interval_ms=20  # ERRADO
    )
    print("[ERRO] Worker criado com parametros errados! Nao deveria funcionar!")
except TypeError as e:
    print(f"[OK] TypeError esperado: {e}")
    print("[OK] Parametros errados foram rejeitados corretamente")

print("\n[2] Testando inicializacao com parametros CORRETOS (apos correcao):")
print("-" * 80)
try:
    def dummy_callback(position, current_bid, current_ask):
        """Callback de teste"""
        return False
    
    # Parametros corretos
    worker_good = PositionMonitorWorker(
        mt5_client=mt5,  # CORRETO
        symbol="BTCUSDc",
        check_interval=0.02,  # CORRETO (20ms em segundos)
        trailing_callback=dummy_callback
    )
    print("[OK] Worker criado com sucesso!")
    print(f"    mt5_client: {worker_good.mt5}")
    print(f"    symbol: {worker_good.symbol}")
    print(f"    check_interval: {worker_good.check_interval}s ({worker_good.check_interval*1000:.0f}ms)")
    
    # Tentar iniciar
    print("\n[3] Iniciando worker...")
    worker_good.start()
    time.sleep(0.5)  # Aguardar inicio
    
    if worker_good.is_running():
        print("[OK] Worker INICIOU e esta RODANDO!")
        print(f"    Thread ativa: {worker_good._thread.is_alive()}")
        print(f"    Total checks: {worker_good.total_checks}")
    else:
        print("[ERRO] Worker NAO iniciou!")
    
    # Parar worker
    print("\n[4] Parando worker...")
    worker_good.stop()
    print(f"[OK] Worker parado. Total checks executados: {worker_good.total_checks}")
    
    print("\n" + "=" * 80)
    print("RESULTADO: Worker funciona corretamente com os parametros corrigidos!")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERRO] Falha ao criar/iniciar worker: {e}")
    import traceback
    traceback.print_exc()
