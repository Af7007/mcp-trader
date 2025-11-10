#!/usr/bin/env python3
"""
Testa se a remocao de _close_opposite_positions funciona corretamente
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.gold_loss_zero_simple import GoldLossZeroSimple

print("="*100)
print("TESTE: REMOCAO DE _close_opposite_positions")
print("="*100)

# Verificar se o metodo ainda existe
if hasattr(GoldLossZeroSimple, '_close_opposite_positions'):
    print("\n[ERRO] Metodo _close_opposite_positions ainda existe na classe!")
    print("       A remocao falhou!")
    sys.exit(1)
else:
    print("\n[OK] Metodo _close_opposite_positions foi removido com sucesso!")

# Verificar se o codigo compila sem erros
try:
    # Tentar instanciar a classe (nao vai conectar ao MT5, mas vai validar o codigo)
    agent = GoldLossZeroSimple.__new__(GoldLossZeroSimple)
    print("[OK] Classe GoldLossZeroSimple compila sem erros!")
except Exception as e:
    print(f"[ERRO] Erro ao instanciar classe: {e}")
    sys.exit(1)

# Verificar se _open_position nao tem mais a chamada
import inspect
source = inspect.getsource(GoldLossZeroSimple._open_position)

if '_close_opposite_positions' in source:
    print("\n[ERRO] Metodo _open_position ainda chama _close_opposite_positions!")
    print("       A remocao da chamada falhou!")
    sys.exit(1)
else:
    print("[OK] Metodo _open_position nao chama mais _close_opposite_positions!")

print("\n" + "="*100)
print("RESULTADO DO TESTE:")
print("="*100)
print("""
[OK] Todas as verificacoes passaram!

MUDANCAS APLICADAS:
1. Metodo _close_opposite_positions foi REMOVIDO
2. Chamada em _open_position foi REMOVIDA
3. Agora o agente NAO fecha posicoes opostas automaticamente

COMPORTAMENTO NOVO:
- Quando um sinal BUY aparece, NAO fecha posicoes SELL existentes
- Quando um sinal SELL aparece, NAO fecha posicoes BUY existentes
- Cada posicao vive ate seu SL ou TP ser atingido
- O trailing stop funciona SEM interferencia de sinais opostos

VANTAGENS:
- Trailing stop pode proteger lucros ate o fim
- Sem fechamentos prematuros por reversao de sinal
- Cada trade tem chance de atingir seu objetivo

DESVANTAGENS:
- Pode haver posicoes BUY e SELL abertas simultaneamente
- Requer mais margem disponivel
- Exposicao de risco aumenta

RECOMENDACAO:
- Monitorar margem disponivel
- Limitar numero maximo de posicoes simultaneas
- Configurar limits diarios para controle de risco
""")

print("\n[INFO] Teste concluido com sucesso!")
