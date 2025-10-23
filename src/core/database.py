#!/usr/bin/env python3
"""
Módulo de Banco de Dados para o Trading Chatbot.
Usa SQLite para persistir informações sobre trades.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "trading_bot.db"
logger = logging.getLogger(__name__)


def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """
    Cria as tabelas necessárias no banco de dados se elas não existirem.
    Esta função deve ser chamada na inicialização do sistema.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabela para armazenar trades iniciados pela IA ou comandos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket INTEGER UNIQUE,
                symbol TEXT NOT NULL,
                volume REAL NOT NULL,
                entry_price REAL NOT NULL,
                sl_price REAL,
                tp_price REAL,
                status TEXT NOT NULL DEFAULT 'open', -- 'open', 'closed'
                result REAL, -- Lucro/Prejuízo
                open_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                close_time TIMESTAMP,
                reason TEXT -- 'tp', 'sl', 'manual', 'worker'
            );
        """)

        conn.commit()
        conn.close()
        logger.info("Banco de dados configurado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao configurar o banco de dados: {e}")


def create_trade(ticket: int, symbol: str, volume: float, entry_price: float, sl_price: Optional[float], tp_price: Optional[float]) -> Optional[int]:
    """
    Registra um novo trade no banco de dados.
    Retorna o ID do trade inserido ou None em caso de falha.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO trades (ticket, symbol, volume, entry_price, sl_price, tp_price) VALUES (?, ?, ?, ?, ?, ?)",
            (ticket, symbol, volume, entry_price, sl_price, tp_price)
        )
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Novo trade registrado no DB: Ticket {ticket}, ID {trade_id}")
        return trade_id
    except sqlite3.IntegrityError:
        logger.warning(f"Trade com ticket {ticket} já existe no banco de dados.")
        return None
    except Exception as e:
        logger.error(f"Erro ao criar trade no DB: {e}")
        return None


def update_trade_status(ticket: int, status: str, result: float, reason: str):
    """Atualiza o status de um trade (ex: para 'closed')."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE trades SET status = ?, result = ?, reason = ?, close_time = ? WHERE ticket = ?",
            (status, result, reason, datetime.now(), ticket)
        )
        conn.commit()
        conn.close()
        logger.info(f"Trade {ticket} atualizado para status '{status}' com resultado {result}.")
    except Exception as e:
        logger.error(f"Erro ao atualizar trade {ticket} no DB: {e}")


def get_open_trades() -> List[Dict[str, Any]]:
    """Retorna uma lista de todos os trades com status 'open'."""
    conn = get_db_connection()
    trades = conn.execute("SELECT * FROM trades WHERE status = 'open'").fetchall()
    conn.close()
    return [dict(trade) for trade in trades]