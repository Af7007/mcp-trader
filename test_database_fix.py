#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das correções no banco de dados para Gold Loss Zero
Verifica se trades são fechados corretamente e trailing stops são registrados
"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.btc_logger import BTCLogger

def test_database_structure():
    """
    Testa se as tabelas foram criadas corretamente
    """
    print("TESTE DA ESTRUTURA DO BANCO DE DADOS")
    print("="*50)

    # Conectar ao banco
    db_path = "btc_trading_logs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    print(f"Tabelas encontradas: {table_names}")

    required_tables = ['cycles', 'trades', 'trailing_stops', 'strategy_performance']
    missing_tables = []

    for table in required_tables:
        if table not in table_names:
            missing_tables.append(table)
        else:
            print(f"[OK] Tabela '{table}' existe")

    if missing_tables:
        print(f"[ERRO] Tabelas faltando: {missing_tables}")
    else:
        print("[OK] Todas as tabelas necessárias existem")

    # Verificar estrutura da tabela trailing_stops
    if 'trailing_stops' in table_names:
        cursor.execute("PRAGMA table_info(trailing_stops)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        expected_columns = [
            'id', 'timestamp', 'trade_id', 'ticket', 'symbol', 'action',
            'old_sl_price', 'new_sl_price', 'current_price', 'profit_pontos',
            'profit_dinheiro', 'trailing_distance_pontos', 'trailing_distance_dinheiro',
            'reason', 'agent_version'
        ]

        missing_columns = []
        for col in expected_columns:
            if col not in column_names:
                missing_columns.append(col)

        if missing_columns:
            print(f"[ERRO] Colunas faltando na tabela trailing_stops: {missing_columns}")
        else:
            print("[OK] Tabela trailing_stops tem todas as colunas necessárias")

    # Verificar estrutura da tabela trades
    if 'trades' in table_names:
        cursor.execute("PRAGMA table_info(trades)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        expected_columns = [
            'id', 'timestamp', 'cycle_id', 'symbol', 'trade_type', 'entry_price',
            'sl_price', 'tp_price', 'volume', 'strength', 'reason', 'comment',
            'status', 'exit_price', 'exit_reason', 'profit_loss', 'agent_version'
        ]

        missing_columns = []
        for col in expected_columns:
            if col not in column_names:
                missing_columns.append(col)

        if missing_columns:
            print(f"[ERRO] Colunas faltando na tabela trades: {missing_columns}")
        else:
            print("[OK] Tabela trades tem todas as colunas necessárias")

    conn.close()

def test_logger_methods():
    """
    Testa se os métodos do logger funcionam
    """
    print("\nTESTE DOS MÉTODOS DO LOGGER")
    print("="*50)

    logger = BTCLogger()

    # Testar log_trade
    try:
        trade_data = {
            'trade_type': 'BUY',
            'entry_price': 2600.50,
            'sl_price': 2594.50,
            'tp_price': None,
            'volume': 0.02,
            'symbol': 'XAUUSDc',
            'agent_version': "1.0.0",
            'reason': 'test_signal',
            'status': "OPEN",
            'comment': 'Test trade'
        }
        trade_id = logger.log_trade(trade_data)
        print(f"[OK] log_trade funcionou - Trade ID: {trade_id}")

        # Testar log_trailing_stop
        trailing_data = {
            'trade_id': trade_id,
            'ticket': 12345,
            'symbol': 'XAUUSDc',
            'action': 'ACTIVATED',
            'old_sl_price': 2594.50,
            'new_sl_price': 2605.50,
            'current_price': 2610.50,
            'profit_pontos': 24000,
            'profit_dinheiro': 4.80,
            'trailing_distance_pontos': 18000,
            'trailing_distance_dinheiro': 3.60,
            'reason': 'Trailing activated at 24,000pts profit',
            'agent_version': "1.0.0"
        }
        logger.log_trailing_stop(trailing_data)
        print("[OK] log_trailing_stop funcionou")

        # Testar update_trade_status
        logger.update_trade_status(
            trade_id=trade_id,
            status="CLOSED_WIN",
            exit_price=2620.50,
            exit_reason="TP_TRAILING",
            profit_loss=4.00
        )
        print("[OK] update_trade_status funcionou")

    except Exception as e:
        print(f"[ERRO] Erro nos métodos do logger: {e}")

def check_recent_data():
    """
    Verifica dados recentes no banco
    """
    print("\nVERIFICAÇÃO DE DADOS RECENTES")
    print("="*50)

    db_path = "btc_trading_logs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar trades recentes
    cursor.execute("""
        SELECT id, symbol, trade_type, status, entry_price, exit_price, profit_loss
        FROM trades
        WHERE symbol = 'XAUUSDc'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    trades = cursor.fetchall()

    if trades:
        print("Trades recentes para XAUUSDc:")
        for trade in trades:
            trade_id, symbol, trade_type, status, entry_price, exit_price, profit_loss = trade
            print(f"  ID: {trade_id}, Tipo: {trade_type}, Status: {status}, Entry: ${entry_price}, Exit: ${exit_price}, Profit: ${profit_loss}")
    else:
        print("Nenhum trade recente encontrado para XAUUSDc")

    # Verificar trailing stops recentes
    cursor.execute("""
        SELECT trade_id, action, old_sl_price, new_sl_price, profit_dinheiro
        FROM trailing_stops
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    trailings = cursor.fetchall()

    if trailings:
        print("\nTrailing stops recentes:")
        for trailing in trailings:
            trade_id, action, old_sl, new_sl, profit = trailing
            print(f"  Trade ID: {trade_id}, Ação: {action}, SL: ${old_sl} -> ${new_sl}, Profit: ${profit}")
    else:
        print("Nenhum trailing stop recente encontrado")

    conn.close()

if __name__ == "__main__":
    test_database_structure()
    test_logger_methods()
    check_recent_data()

    print("\n" + "="*50)
    print("TESTE CONCLUÍDO")
    print("Se tudo estiver [OK], as correções funcionaram!")
