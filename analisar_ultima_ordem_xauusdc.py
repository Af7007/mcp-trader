#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise da última ordem XAUUSDc para diagnosticar problema do trailing stop
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.database import setup_database

def get_database():
    """Obtém conexão com o banco de dados"""
    db = setup_database()
    return db

def analisar_ultima_ordem():
    """Analisa a última ordem XAUUSDc com magic number 123456"""
    
    try:
        db = get_database()
        
        print("="*60)
        print("ANÁLISE DA ÚLTIMA ORDEM XAUUSDc")
        print("="*60)
        
        # Buscar última ordem XAUUSDc com magic number 123456
        query = """
        SELECT * FROM trades 
        WHERE symbol = 'XAUUSDc' AND magic = 123456 
        ORDER BY id DESC LIMIT 1
        """
        
        resultado = db.execute(query)
        
        if resultado:
            trade = resultado[0]
            print(f"ID: {trade.get('id')}")
            print(f"Symbol: {trade.get('symbol')}")
            print(f"Magic: {trade.get('magic')}")
            print(f"Trade Type: {trade.get('trade_type')}")
            print(f"Entry Price: ${trade.get('entry_price', 0):.2f}")
            print(f"SL Price: ${trade.get('sl_price', 0):.2f}")
            print(f"TP Price: ${trade.get('tp_price', 0):.2f}")
            print(f"Volume: {trade.get('volume', 0)}")
            print(f"Status: {trade.get('status')}")
            print(f"Reason: {trade.get('reason')}")
            print(f"Comment: {trade.get('comment')}")
            print(f"Profit: ${trade.get('profit', 0):.2f}")
            print(f"Open Time: {trade.get('open_time')}")
            print(f"Close Time: {trade.get('close_time')}")
            
            # Calcular diferença de preços
            entry_price = float(trade.get('entry_price', 0))
            sl_price = float(trade.get('sl_price', 0))
            volume = float(trade.get('volume', 0))
            
            print(f"\nCÁLCULOS:")
            print(f"Entry Price: ${entry_price:.2f}")
            print(f"SL Price: ${sl_price:.2f}")
            print(f"Diferença: {abs(entry_price - sl_price):.2f} pontos")
            
            # Para XAUUSDc, vamos calcular o valor por ponto
            # Point typically 0.01 for XAUUSDc
            point_value = 0.01
            points_difference = abs(entry_price - sl_price)
            dollars_per_point = volume * point_value * 100  # Para conta cents
            
            print(f"Volume: {volume}")
            print(f"Diferença em pontos: {points_difference}")
            print(f"Valor por ponto (volume {volume}): ${dollars_per_point:.2f}")
            print(f"Perda esperada se SL atingido: ${points_difference * dollars_per_point:.2f}")
            
        else:
            print("Nenhuma ordem encontrada para XAUUSDc com magic 123456")
            
    except Exception as e:
        print(f"Erro ao analisar ordem: {e}")

def verificar_trailing_logs():
    """Verificar logs de trailing stop para a última ordem"""
    
    try:
        db = get_database()
        
        print("\n" + "="*60)
        print("LOGS DE TRAILING STOP")
        print("="*60)
        
        # Buscar logs de cycles para ver se trailing foi ativado
        query = """
        SELECT * FROM cycles 
        WHERE symbol = 'XAUUSDc' AND cycle_number > (
            SELECT MAX(cycle_number) - 20 FROM cycles WHERE symbol = 'XAUUSDc'
        )
        ORDER BY id DESC LIMIT 20
        """
        
        resultado = db.execute(query)
        
        if resultado:
            print("Últimos 20 ciclos para XAUUSDc:")
            for cycle in resultado:
                print(f"Ciclo {cycle.get('cycle_number')}:")
                print(f"  Preço: ${cycle.get('price', 0):.2f}")
                print(f"  Signal: {cycle.get('signal_type')} - {cycle.get('signal_reason')}")
                print(f"  SL: ${cycle.get('sl_price', 0):.2f}")
                print(f"  TP: ${cycle.get('tp_price', 0):.2f}")
                print(f"  Timestamp: {cycle.get('timestamp')}")
                print()
        else:
            print("Nenhum log de ciclo encontrado para XAUUSDc")
            
    except Exception as e:
        print(f"Erro ao verificar logs: {e}")

def analisar_configuracao_gold():
    """Analisa configuração do agente Gold Loss Zero"""
    
    try:
        print("\n" + "="*60)
        print("CONFIGURAÇÃO AGENTE GOLD LOSS ZERO")
        print("="*60)
        
        # Ler arquivo de configuração
        with open("src/agents/gold_loss_zero_simple.py", "r", encoding="utf-8") as f:
            conteudo = f.read()
            
        # Procurar configurações importantes
        if "stop_loss_atr_multiplier" in conteudo:
            print("✅ stop_loss_atr_multiplier encontrado")
            
        if "trailing_activation_atr_multiplier" in conteudo:
            print("✅ trailing_activation_atr_multiplier encontrado")
            
        if "trailing_distance_atr_multiplier" in conteudo:
            print("✅ trailing_distance_atr_multiplier encontrado")
            
        if "_safe_modify_sl" in conteudo:
            print("✅ _safe_modify_sl implementado")
            
        if "_trailing_lock" in conteudo:
            print("✅ _trailing_lock implementado")
            
    except Exception as e:
        print(f"Erro ao analisar configuração: {e}")

if __name__ == "__main__":
    analisar_ultima_ordem()
    verificar_trailing_logs()
    analisar_configuracao_gold()
