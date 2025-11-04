#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação simples da configuração Gold Loss Zero
"""

import re

def verificar_configuracao():
    print("VERIFICACAO CONFIGURACAO GOLD LOSS ZERO")
    print("="*50)
    
    try:
        with open("src/agents/gold_loss_zero_simple.py", "r") as f:
            conteudo = f.read()
            
        # Buscar stop_loss_atr_multiplier
        match = re.search(r'stop_loss_atr_multiplier[:\s=]+([0-9.]+)', conteudo)
        if match:
            valor = float(match.group(1))
            print(f"stop_loss_atr_multiplier: {valor}")
            
            if valor == 100.0:
                print("STATUS: CORRETO (foi alterado de 10.0 para 100.0)")
            elif valor == 10.0:
                print("STATUS: INCORRETO (ainda era 10.0)")
            else:
                print(f"STATUS: VALOR DESCONHECIDO ({valor})")
        else:
            print("ERRO: stop_loss_atr_multiplier nao encontrado")
            
        # Verificar point value calculation
        if "_calculate_point_value" in conteudo:
            print("calculate_point_value: IMPLEMENTADO")
            
        if "_safe_modify_sl" in conteudo:
            print("safe_modify_sl: IMPLEMENTADO")
            
        if "_trailing_lock" in conteudo:
            print("trailing_lock: IMPLEMENTADO")
            
    except Exception as e:
        print(f"ERRO: {e}")

def mostrar_calculo_real():
    print("\n" + "="*50)
    print("CALCULO REAL STOP LOSS GOLD")
    print("="*50)
    
    # Valores reais do Gold para conta cents
    atr = 60.0
    multiplier = 100.0
    volume = 0.01
    point_value_gold = 1.0  # $1 por ponto para 1 lote Gold
    
    sl_pontos = atr * multiplier
    sl_dinheiro = sl_pontos * volume * point_value_gold
    
    print(f"ATR Gold: {atr} pontos")
    print(f"stop_loss_atr_multiplier: {multiplier}")
    print(f"Volume: {volume} lotes")
    print(f"Point value Gold: ${point_value_gold} por ponto")
    
    print(f"\nCalculo:")
    print(f"SL em pontos: {atr} x {multiplier} = {sl_pontos:,.0f} pontos")
    print(f"SL em dinheiro: {sl_pontos:,.0f} x {volume} x ${point_value_gold} = ${sl_dinheiro:.2f}")
    
    if sl_dinheiro == 6.0:
        print("\nRESULTADO: CORRETO! SL = $6.00")
    else:
        print(f"\nRESULTADO: INCORRETO! SL = ${sl_dinheiro:.2f}")

if __name__ == "__main__":
    verificar_configuracao()
    mostrar_calculo_real()
