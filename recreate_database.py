#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recria o banco de dados btc_trading_logs.db com todas as tabelas atualizadas
"""

import os
import sqlite3
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.btc_logger import BTCLogger

def recreate_database():
    """
    Remove o banco antigo e cria um novo com todas as tabelas
    """
    db_path = "btc_trading_logs.db"

    # Fazer backup do banco antigo se existir
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        print(f"Fazendo backup do banco antigo: {backup_path}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(db_path, backup_path)

    # Criar novo logger (isso criará o banco com todas as tabelas)
    print("Criando novo banco de dados...")
    logger = BTCLogger()

    print("Banco de dados recriado com sucesso!")
    print("Tabelas criadas:")
    print("- cycles")
    print("- trades")
    print("- trailing_stops")
    print("- strategy_performance")

if __name__ == "__main__":
    recreate_database()
