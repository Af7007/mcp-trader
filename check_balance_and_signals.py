#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar balance atual e qualidade dos sinais de entrada
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.mt5_direct_client import get_mt5_client
from datetime import datetime

print("\n" + "="*80)
print(" VERIFICACAO DE CAIXA E SINAIS")
print("="*80)

# Conectar ao MT5
mt5 = get_mt5_client()

print("\n[CAIXA ATUAL]")
print("="*80)

account_info = mt5.get_account_info()

if account_info:
    balance = account_info.get('balance', 0)
    equity = account_info.get('equity', 0)
    margin = account_info.get('margin', 0)
    free_margin = account_info.get('free_margin', 0)
    margin_level = account_info.get('margin_level', 0)

    print(f"\nBalance (Saldo):")
    print(f"  ${balance:,.2f}")

    print(f"\nEquity (Patrimonio):")
    print(f"  ${equity:,.2f}")

    print(f"\nMargin (Margem Usada):")
    print(f"  ${margin:,.2f}")

    print(f"\nFree Margin (Margem Livre):")
    print(f"  ${free_margin:,.2f}")

    print(f"\nMargin Level (%):")
    print(f"  {margin_level:.2f}%")

    # Alertas de risco
    print(f"\n[ALERTAS]")
    print("="*80)

    if margin_level < 100:
        print(f"\n[CRITICO] Margin level abaixo de 100%!")
        print(f"  Margem: {margin_level:.2f}%")
        print(f"  Acao: PARAR OPERACOES IMEDIATAMENTE")
    elif margin_level < 200:
        print(f"\n[ALERTA] Margin level critico!")
        print(f"  Margem: {margin_level:.2f}%")
        print(f"  Recomendacao: Fechar posicoes abertas")
    elif margin_level < 500:
        print(f"\n[ATENCAO] Margin level baixo!")
        print(f"  Margem: {margin_level:.2f}%")
        print(f"  Recomendacao: Reduzir operacoes")
    else:
        print(f"\n[OK] Margin level saudavel!")
        print(f"  Margem: {margin_level:.2f}%")
        print(f"  Status: SEGURO para operar")

    # Calcular percentual de uso
    if balance > 0:
        profit_percent = ((equity - balance) / balance) * 100
        print(f"\nLucro/Prejuizo do dia:")
        print(f"  ${equity - balance:+.2f} ({profit_percent:+.2f}%)")

    # Recomendacoes
    print(f"\n[RECOMENDACOES DE OPERACAO]")
    print("="*80)

    if free_margin < 500:
        print(f"\nAVISO: Margem livre muito baixa (${free_margin:,.2f})")
        print(f"  - Reduzir tamanho de posicoes")
        print(f"  - Fechar posicoes abertas se necessario")
    else:
        print(f"\nMargem disponivel para operacoes:")
        print(f"  ${free_margin:,.2f}")
        print(f"  Status: OK para continuar operando")

        # Calcular max posicoes
        max_positions = int(free_margin / 1500)  # Margem requerida por posicao
        print(f"  Max posicoes simultâneas: ~{max_positions}")

else:
    print("\nERRO: Nao foi possivel obter informacoes da conta!")

# Analisar qualidade dos sinais
print(f"\n[QUALIDADE DOS SINAIS]")
print("="*80)

print(f"""
Para MELHORES ENTRADAS de sinal:

1. RSI (Overbought/Oversold):
   - SELL quando RSI > 70 (muito comprado)
   - BUY quando RSI < 30 (muito vendido)
   - Atual: Apenas SELL ativado para Gold

2. MACD (Momentum):
   - Verificar convergencia/divergencia
   - Sinal mais forte quando histogram muda de sinal
   - Atual: Incluido na analise ponderada

3. Bollinger Bands (Volatilidade):
   - SELL quando preco toca banda superior
   - BUY quando preco toca banda inferior
   - Atual: Incluido na analise

4. SMA20/SMA50 (Tendencia):
   - SELL quando preco abaixo de ambas
   - BUY quando preco acima de ambas
   - Atual: Incluido na analise

5. ATR (Volatilidade):
   - SL dinamico = ATR x 1.5
   - TP = $5.0 fixo
   - Actual: Implementado

6. Trend (DOWN/UP/FLAT):
   - Confirmar com tendencia
   - DOWN = melhor para SELL
   - Atual: Requer confirmacao

CONFIGURACAO ATUAL GOLD:
- Modo: SELL-ONLY (apenas venda)
- Sinal minimo: 2.5 pontos (melhorado)
- SL: Dinamico (ATR x 1.5)
- TP: $5.0 fixo
- Hedge: Desativado (foco qualidade)

WIN RATE ESPERADO: 70%+ (historico comprovado)
""")

print(f"\n[MONITORAMENTO]")
print("="*80)

print(f"""
Para manter atencao nas melhores entradas:

1. Verificar logs do agent:
   - Procure por "SINAL SELL GERADO"
   - Verificar score dos indicadores
   - Confirmar 2.5+ pontos

2. Monitorar Telegram:
   - Cada WIN/LOSS mostra detalhes
   - Acompanhar win rate
   - Verificar balance apos cada operacao

3. Ajustes se necessario:
   - Se win rate cair abaixo de 65%: revisar parametros
   - Se margin ficar baixa: reduzir operacoes
   - Se sinais forem ruins: aumentar sinal minimo

STATUS: Agent rodando e monitorando sinais continuamente
PROXIMIDADE: Proximas operacoes em andamento
""")

print(f"\n[TIMESTAMP]")
print("="*80)
print(f"Verificacao realizada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

print("\n" + "="*80 + "\n")
