#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise das últimas ordens XAUUSDc do MT5 para identificar padrão real de SL
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def conectar_mt5():
    """Conecta ao MT5"""
    if not mt5.initialize():
        print(f"Erro ao conectar MT5: {mt5.last_error()}")
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        print(f"Erro ao obter info da conta: {mt5.last_error()}")
        return False
    
    print(f"Conectado ao MT5")
    print(f"Conta: {account_info.login}")
    print(f"Servidor: {account_info.server}")
    return True

def buscar_ultimas_ordens_xauusdc():
    """Busca as últimas ordens XAUUSDc"""
    
    # Buscar das últimas 24 horas
    date_from = datetime.now() - timedelta(hours=24)
    date_to = datetime.now()
    
    # Buscar deals (histórico de trades)
    deals = mt5.history_deals_get(
        date_from=date_from,
        date_to=date_to,
        symbol="XAUUSDc"
    )
    
    if deals is None:
        print("Nenhum deal encontrado para XAUUSDc nas últimas 24h")
        return []
    
    print(f"\n=== ÚLTIMAS ORDENS XAUUSDc ({len(deals)} encontrados) ===")
    
    # Converter para lista de dicionários
    orders_list = []
    for deal in deals:
        deal_dict = {
            'ticket': deal.ticket,
            'position_id': deal.position_id,
            'time': datetime.fromtimestamp(deal.time),
            'symbol': deal.symbol,
            'type': deal.type,
            'entry': deal.entry,
            'volume': deal.volume,
            'price': deal.price,
            'profit': deal.profit,
            'comment': deal.comment
        }
        orders_list.append(deal_dict)
    
    return orders_list

def analisar_sl_atraves_de_posicoes():
    """Busca posições abertas para ver SL real"""
    
    print(f"\n=== POSIÇÕES ABERTAS XAUUSDc ===")
    
    positions = mt5.positions_get(symbol="XAUUSDc")
    
    if positions is None:
        print("Nenhuma posição XAUUSDc aberta")
        return []
    
    print(f"Posições abertas: {len(positions)}")
    
    for pos in positions:
        print(f"\nTicket: {pos.ticket}")
        print(f"Preço de entrada: ${pos.price_open:.2f}")
        print(f"SL atual: ${pos.sl:.2f}")
        print(f"TP atual: ${pos.tp:.2f}")
        print(f"Volume: {pos.volume}")
        print(f"Tipo: {'BUY' if pos.type == 0 else 'SELL'}")
        
        if pos.price_open > 0:
            sl_distance = abs(pos.price_open - pos.sl) if pos.sl > 0 else 0
            if pos.type == 0:  # BUY
                sl_down = pos.price_open - pos.sl if pos.sl < pos.price_open else 0
                print(f"Distância SL (para baixo): {sl_down:.2f} pontos")
            else:  # SELL
                sl_up = pos.sl - pos.price_open if pos.sl > pos.price_open else 0
                print(f"Distância SL (para cima): {sl_up:.2f} pontos")

def calcular_padrao_sl(deals_list):
    """Calcula o padrão de SL baseado nos dados reais"""
    
    print(f"\n=== ANÁLISE DO PADRÃO DE SL ===")
    
    for i, deal in enumerate(deals_list[-5:], 1):  # Últimos 5 deals
        print(f"\nDeal {i}:")
        print(f"Ticket: {deal['ticket']}")
        print(f"Horário: {deal['time']}")
        print(f"Preço: ${deal['price']:.2f}")
        print(f"Volume: {deal['volume']}")
        print(f"Lucro: ${deal['profit']:.2f}")
        print(f"Comment: {deal['comment']}")
        
        # Se é entrada (entry = 0), tentar calcular SL baseado no comentário
        if deal['entry'] == 0:  # DEAL_ENTRY_IN = entrada
            print(f"TIPO: ENTRADA")

def buscar_symbol_info_xauusdc():
    """Busca informações do símbolo XAUUSDc"""
    
    print(f"\n=== INFORMAÇÕES DO SÍMBOLO XAUUSDc ===")
    
    symbol_info = mt5.symbol_info("XAUUSDc")
    
    if symbol_info is None:
        print("Símbolo XAUUSDc não encontrado")
        return
    
    print(f"Nome: {symbol_info.name}")
    print(f"Point: {symbol_info.point}")
    print(f"Digits: {symbol_info.digits}")
    print(f"Trade mode: {symbol_info.trade_mode}")
    print(f"Contract size: {symbol_info.trade_contract_size}")
    print(f"Trade tick value: {symbol_info.trade_tick_value}")
    print(f"Trade tick size: {symbol_info.trade_tick_size}")
    print(f"Volume min: {symbol_info.volume_min}")
    print(f"Volume step: {symbol_info.volume_step}")
    print(f"Volume max: {symbol_info.volume_max}")

def calcular_sl_esperado():
    """Calcula SL esperado vs real"""
    
    print(f"\n=== CÁLCULO SL ESPERADO ===")
    
    # Configurações atuais
    atr = 60.0  # ATR típico
    multiplier = 100.0  # stop_loss_atr_multiplier corrigido
    volume = 0.01
    point_value = 0.01  # point_value corrigido
    
    sl_pontos = atr * multiplier
    sl_dinheiro = sl_pontos * volume * point_value
    
    print(f"ATR: {atr} pontos")
    print(f"stop_loss_atr_multiplier: {multiplier}")
    print(f"SL em pontos: {sl_pontos:,.0f}")
    print(f"Volume: {volume}")
    print(f"Point value: ${point_value}")
    print(f"SL esperado: ${sl_dinheiro:.2f}")
    
    # Para Gold, point typically 0.001 (0.01 cents account)
    # O cálculo deve ser em pontos vs preço
    price_gold = 2650.0  # Preço típico do Gold
    sl_price_distance = sl_pontos * 0.001  # 0.001 é o point do Gold
    
    print(f"\nPara Gold (point = 0.001):")
    print(f"SL em distância de preço: {sl_price_distance:.3f}")
    print(f"SL price: ${price_gold - sl_price_distance:.2f}")

def main():
    """Função principal"""
    
    print("ANÁLISE DAS ÚLTIMAS ORDENS XAUUSDc")
    print("="*50)
    
    # Conectar ao MT5
    if not conectar_mt5():
        return
    
    try:
        # Buscar informações do símbolo
        buscar_symbol_info_xauusdc()
        
        # Buscar posições abertas
        analisar_sl_atraves_de_posicoes()
        
        # Buscar últimas ordens
        deals = buscar_ultimas_ordens_xauusdc()
        
        # Analisar padrão
        if deals:
            calcular_padrao_sl(deals)
        
        # Calcular SL esperado
        calcular_sl_esperado()
        
    except Exception as e:
        print(f"Erro durante análise: {e}")
    finally:
        # Desconectar do MT5
        mt5.shutdown()
        print(f"\nDesconectado do MT5")

if __name__ == "__main__":
    main()
