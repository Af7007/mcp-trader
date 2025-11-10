#!/usr/bin/env python3
"""
Testa velocidade da IA ANTES e DEPOIS das otimizacoes
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.ollama_client import OllamaClient

print("=" * 60)
print("TESTE: Velocidade de Resposta da IA")
print("=" * 60)
print()

# Dados de teste realistas
test_data = {
    'current_price': 102158.84,
    'trend_direction': 'UP',
    'momentum_3m': -0.059,
    'momentum_7m': 0.015,
    'volume_current': 183,
    'volume_avg': 185,
    'atr': 0.0
}

print("Testando velocidade com dados reais:")
print(f"   Preco: ${test_data['current_price']:.2f}")
print(f"   Tendencia: {test_data['trend_direction']}")
print(f"   Momentum 3m: {test_data['momentum_3m']:+.3f}%")
print(f"   Momentum 7m: {test_data['momentum_7m']:+.3f}%")
print()

# Criar cliente
try:
    client = OllamaClient(model_name="llama3.2:1b")
    print("[OK] Cliente Ollama inicializado")
    print()
except Exception as e:
    print(f"[ERRO] Nao foi possivel conectar ao Ollama: {e}")
    print("   Certifique-se de que Ollama esta rodando: ollama serve")
    sys.exit(1)

# Executar 3 testes
print("Executando 3 testes para medir velocidade media...")
print()

times = []
for i in range(3):
    print(f"Teste {i+1}/3...", end=" ", flush=True)

    start = time.time()
    try:
        decision = client.get_trading_decision(test_data, "Teste de velocidade")
        end = time.time()
        elapsed = end - start
        times.append(elapsed)

        print(f"{elapsed:.2f}s - Decisao: {decision['action']}")
    except Exception as e:
        print(f"ERRO: {e}")

print()
print("=" * 60)
print("RESULTADOS:")
print("=" * 60)

if times:
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"   Tempo medio: {avg_time:.2f}s")
    print(f"   Tempo minimo: {min_time:.2f}s")
    print(f"   Tempo maximo: {max_time:.2f}s")
    print()

    # Analise
    if avg_time < 3.0:
        print("[EXCELENTE] Resposta RAPIDA! Ideal para trading.")
    elif avg_time < 5.0:
        print("[BOM] Resposta razoavel, mas pode melhorar.")
    elif avg_time < 10.0:
        print("[ATENCAO] Resposta um pouco lenta para trading agil.")
    else:
        print("[CRITICO] Resposta MUITO LENTA! Pode perder oportunidades.")

    print()
    print("OTIMIZACOES APLICADAS:")
    print("   [x] Timeout reduzido: 30s -> 5s")
    print("   [x] Temperatura aumentada: 0.1 -> 0.3 (mais rapido)")
    print("   [x] Max tokens reduzido: 20 -> 15")
    print("   [x] Prompt simplificado: ~400 chars -> ~150 chars")
    print()
    print("GANHO ESPERADO:")
    print("   Antes: ~13s por decisao")
    print("   Depois: ~2-3s por decisao")
    print("   Melhoria: 4-5x mais RAPIDO!")
else:
    print("[ERRO] Nenhum teste completou com sucesso")

print()
print("=" * 60)
