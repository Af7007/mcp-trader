#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise DETALHADA da Estratégia BTC Loss Zero
Verificar sinais, entradas, SL, TP e lógica
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def analise_estrategia():
    """
    Análise completa da estratégia
    """
    db_path = Path('btc_trading_logs.db')
    if not db_path.exists():
        print("Banco de dados não encontrado!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("ANÁLISE DETALHADA DA ESTRATÉGIA BTC LOSS ZERO")
    print("=" * 80)

    # 1. CÁLCULOS CORRETOS DE SL/TP
    print("\n[1] MATEMÁTICA CORRETA - SL/TP com Volume 0.03 lotes")
    print("-" * 80)

    volume = 0.03  # Volume atual
    sl_pontos = 80  # SL em pontos (dólares no preço)
    tp_pontos = 160  # TP em pontos

    # Para BTC: 1 lote = 1 BTC, então 0.03 lotes = 0.03 BTC
    # Se preço move $1, lucro/perda = volume * movimento
    sl_dinheiro = volume * sl_pontos
    tp_dinheiro = volume * tp_pontos

    print(f"   Volume operado: {volume} lotes (0.03 BTC)")
    print(f"   SL configurado: {sl_pontos} pontos ($)")
    print(f"   TP configurado: {tp_pontos} pontos ($)")
    print(f"")
    print(f"   PERDA MÁXIMA POR TRADE: ${sl_dinheiro:.2f}")
    print(f"   LUCRO MÁXIMO POR TRADE: ${tp_dinheiro:.2f}")
    print(f"   Risk/Reward: 1:{tp_pontos/sl_pontos}")
    print(f"")
    print(f"   ⚠️ ATENÇÃO: Com trailing de $5 ativação e $10 distância:")
    print(f"      - Trailing ativa com: ${volume * 5:.2f} de lucro")
    print(f"      - Trailing protege: ${volume * 10:.2f}")
    print(f"      - Lucro típico: ${volume * 10:.2f} - ${volume * 20:.2f}")

    # 2. ANÁLISE DOS SINAIS GERADOS
    print("\n[2] ANÁLISE DOS SINAIS GERADOS")
    print("-" * 80)

    # Últimos 20 ciclos com sinais
    cursor.execute('''
        SELECT
            timestamp,
            signal_type,
            signal_reason,
            price,
            bb_upper,
            bb_lower,
            rsi,
            momentum,
            volume_multiplier
        FROM cycles
        WHERE signal_type IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 20
    ''')

    sinais = cursor.fetchall()

    print(f"\n   ÚLTIMOS 20 SINAIS:")
    for i, (ts, tipo, razao, preco, bb_up, bb_low, rsi, mom, vol_mult) in enumerate(sinais, 1):
        print(f"\n   {i}. {ts} | {tipo} @ ${preco:.2f}")
        print(f"      Razão: {razao}")
        if bb_up and bb_low:
            print(f"      BB: [{bb_low:.2f} - {bb_up:.2f}]")
        if rsi:
            print(f"      RSI: {rsi:.1f}")
        if mom:
            print(f"      Momentum: {mom:.2f}")
        if vol_mult:
            print(f"      Volume: {vol_mult:.2f}x")

    # 3. DISTRIBUIÇÃO DE RAZÕES
    print("\n[3] QUALIDADE DOS SINAIS - Por Razão")
    print("-" * 80)

    cursor.execute('''
        SELECT
            signal_reason,
            COUNT(*) as total,
            COUNT(DISTINCT DATE(timestamp)) as dias_ativos
        FROM cycles
        WHERE signal_type IS NOT NULL
        GROUP BY signal_reason
        ORDER BY total DESC
    ''')

    print(f"\n   Razão                          | Total | Sinais/Dia")
    print(f"   {'-'*30} | {'-'*5} | {'-'*10}")
    for razao, total, dias in cursor.fetchall():
        sinais_por_dia = total / max(dias, 1)
        print(f"   {razao:30} | {total:5} | {sinais_por_dia:6.1f}")

    # 4. ANÁLISE DE CONVERSÃO SINAL → TRADE
    print("\n[4] TAXA DE CONVERSÃO SINAL → TRADE")
    print("-" * 80)

    cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL')
    total_sinais = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]

    taxa_conversao = (total_trades / total_sinais * 100) if total_sinais > 0 else 0

    print(f"   Total de sinais gerados: {total_sinais}")
    print(f"   Total de trades abertos: {total_trades}")
    print(f"   Taxa de conversão: {taxa_conversao:.1f}%")
    print(f"")
    if taxa_conversao < 30:
        print(f"   ⚠️ PROBLEMA: Taxa muito baixa! Muitos sinais não viram trades.")
        print(f"   Possíveis causas:")
        print(f"      - Cooldown entre trades")
        print(f"      - Filtros de horário")
        print(f"      - Posições já abertas")
        print(f"      - Erros de execução")

    # 5. VALIDAÇÃO DAS ENTRADAS
    print("\n[5] VALIDAÇÃO DAS ENTRADAS - Últimos 10 Trades")
    print("-" * 80)

    cursor.execute('''
        SELECT
            t.timestamp,
            t.trade_type,
            t.entry_price,
            t.sl_price,
            t.tp_price,
            t.volume,
            t.reason,
            t.status
        FROM trades t
        ORDER BY t.timestamp DESC
        LIMIT 10
    ''')

    trades = cursor.fetchall()

    for i, (ts, tipo, entry, sl, tp, vol, razao, status) in enumerate(trades, 1):
        print(f"\n   Trade #{i} - {ts}")
        print(f"   Tipo: {tipo} | Status: {status}")
        print(f"   Entrada: ${entry:.2f}")
        print(f"   SL: ${sl:.2f} | TP: ${tp:.2f}")
        print(f"   Volume: {vol} lotes")
        print(f"   Razão: {razao}")

        # Calcular distâncias
        if tipo == 'BUY':
            sl_dist = entry - sl
            tp_dist = tp - entry
        else:
            sl_dist = sl - entry
            tp_dist = entry - tp

        # Calcular valores reais em dinheiro
        sl_valor = vol * sl_dist
        tp_valor = vol * tp_dist

        print(f"   Distâncias: SL={sl_dist:.2f} pontos | TP={tp_dist:.2f} pontos")
        print(f"   Valores: PERDA=${sl_valor:.2f} | LUCRO=${tp_valor:.2f}")
        print(f"   R/R: 1:{tp_dist/sl_dist if sl_dist > 0 else 0:.2f}")

        # Validar entrada
        problemas = []

        if sl_dist < 50:
            problemas.append("SL muito próximo (< 50 pontos)")
        if tp_dist < 100:
            problemas.append("TP muito próximo (< 100 pontos)")
        if tp_dist / sl_dist < 1.5:
            problemas.append(f"R/R ruim ({tp_dist/sl_dist:.2f})")
        if "Strong_momentum" in razao and sl_dist < 80:
            problemas.append("Momentum forte precisa SL maior")

        if problemas:
            print(f"   ⚠️ PROBLEMAS:")
            for p in problemas:
                print(f"      - {p}")
        else:
            print(f"   ✅ Entrada parece válida")

    # 6. ANÁLISE DO PADRÃO DE SINAIS
    print("\n[6] PADRÃO DE SINAIS - Viés BUY vs SELL")
    print("-" * 80)

    cursor.execute('''
        SELECT
            signal_type,
            COUNT(*) as total,
            AVG(price) as preco_medio
        FROM cycles
        WHERE signal_type IS NOT NULL
        GROUP BY signal_type
    ''')

    for tipo, total, preco_medio in cursor.fetchall():
        pct = (total / total_sinais * 100) if total_sinais > 0 else 0
        print(f"   {tipo}: {total} sinais ({pct:.1f}%) | Preço médio: ${preco_medio:.2f}")

    # Verificar se há viés em relação ao movimento real do mercado
    cursor.execute('''
        SELECT MIN(price), MAX(price)
        FROM cycles
        WHERE signal_type IS NOT NULL
    ''')
    min_preco, max_preco = cursor.fetchone()

    if min_preco and max_preco:
        movimento = max_preco - min_preco
        print(f"\n   Movimento do mercado no período:")
        print(f"   Mínimo: ${min_preco:.2f}")
        print(f"   Máximo: ${max_preco:.2f}")
        print(f"   Range: ${movimento:.2f} ({(movimento/min_preco)*100:.2f}%)")

    # 7. RESUMO E DIAGNÓSTICO
    print("\n[7] DIAGNÓSTICO DA ESTRATÉGIA")
    print("-" * 80)

    problemas_estrategia = []

    # Problema 1: SL/TP muito grandes para o volume
    if sl_pontos > 50 and volume < 0.05:
        problemas_estrategia.append({
            'tipo': 'CRÍTICO',
            'problema': f'SL de {sl_pontos} pontos com volume {volume} = ${sl_dinheiro:.2f} perda',
            'solucao': f'Reduzir SL para 30-40 pontos OU aumentar volume para 0.10'
        })

    # Problema 2: Taxa de conversão baixa
    if taxa_conversao < 30:
        problemas_estrategia.append({
            'tipo': 'ALTO',
            'problema': f'Taxa de conversão {taxa_conversao:.1f}% muito baixa',
            'solucao': 'Revisar filtros de confirmação, podem estar muito rigorosos'
        })

    # Problema 3: Trailing ativa muito cedo
    trailing_ativa = 5
    if trailing_ativa < sl_pontos / 2:
        problemas_estrategia.append({
            'tipo': 'CRÍTICO',
            'problema': f'Trailing ativa em ${trailing_ativa} mas SL é ${sl_pontos}',
            'solucao': f'Aumentar trailing_activation para {sl_pontos} ou desativar trailing'
        })

    # Problema 4: Viés SELL excessivo
    cursor.execute('SELECT signal_type, COUNT(*) FROM cycles WHERE signal_type IS NOT NULL GROUP BY signal_type')
    dist = dict(cursor.fetchall())
    if 'SELL' in dist and 'BUY' in dist:
        ratio = dist['SELL'] / dist['BUY']
        if ratio > 1.8:
            problemas_estrategia.append({
                'tipo': 'MÉDIO',
                'problema': f'Viés SELL {ratio:.1f}x maior que BUY',
                'solucao': 'Revisar thresholds de momentum, podem favorecer SELL'
            })

    if problemas_estrategia:
        print("\n   ⚠️ PROBLEMAS IDENTIFICADOS:")
        for p in problemas_estrategia:
            print(f"\n   [{p['tipo']}] {p['problema']}")
            print(f"   Solução: {p['solucao']}")
    else:
        print("\n   ✅ Estratégia parece estar configurada corretamente")

    conn.close()
    print("\n" + "=" * 80)
    print("Análise concluída!")
    print("=" * 80)

if __name__ == "__main__":
    analise_estrategia()
