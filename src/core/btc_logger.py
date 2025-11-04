#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Logger - Sistema de logging completo para análise de estratégias
Armazena ciclos, indicadores e sinais no banco de dados
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class BTCLogger:
    """
    Sistema completo de logging para análise de estratégias BTC
    """
    
    def __init__(self, db_path: str = "btc_trading_logs.db"):
        """
        Inicializa logger com banco de dados
        """
        self.db_path = Path(db_path)
        self.init_database()
        
    def init_database(self):
        """
        Cria tabelas do banco de dados
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de ciclos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cycle_number INTEGER,
                symbol TEXT,
                price REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                bb_position TEXT,
                rsi REAL,
                rsi_overbought REAL,
                rsi_oversold REAL,
                volume_current REAL,
                volume_avg REAL,
                volume_multiplier REAL,
                trend TEXT,
                momentum REAL,
                signal_type TEXT,
                signal_strength TEXT,
                signal_reason TEXT,
                signal_price REAL,
                sl_price REAL,
                tp_price REAL,
                order_result TEXT,
                order_error TEXT,
                agent_version TEXT
            )
        ''')
        
        # Tabela de trades executados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cycle_id INTEGER,
                symbol TEXT,
                trade_type TEXT,
                entry_price REAL,
                sl_price REAL,
                tp_price REAL,
                volume REAL,
                strength TEXT,
                reason TEXT,
                comment TEXT,
                status TEXT,
                exit_price REAL,
                exit_reason TEXT,
                profit_loss REAL,
                agent_version TEXT,
                FOREIGN KEY (cycle_id) REFERENCES cycles (id)
            )
        ''')
        
        # Tabela de trailing stops
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trailing_stops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                trade_id INTEGER,
                ticket INTEGER,
                symbol TEXT,
                action TEXT,  -- 'ACTIVATED', 'UPDATED', 'MOVED_UP', 'MOVED_DOWN'
                old_sl_price REAL,
                new_sl_price REAL,
                current_price REAL,
                profit_pontos REAL,
                profit_dinheiro REAL,
                trailing_distance_pontos REAL,
                trailing_distance_dinheiro REAL,
                reason TEXT,
                agent_version TEXT,
                FOREIGN KEY (trade_id) REFERENCES trades (id)
            )
        ''')

        # Tabela de performance das estratégias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy_name TEXT,
                signal_type TEXT,
                signal_strength TEXT,
                total_signals INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                failed_trades INTEGER DEFAULT 0,
                total_profit_loss REAL DEFAULT 0,
                avg_profit_loss REAL DEFAULT 0,
                success_rate REAL DEFAULT 0,
                agent_version TEXT
            )
        ''')

        # Verificar se tabela trailing_stops existe (para bancos antigos)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trailing_stops'")
        if not cursor.fetchone():
            print("Criando tabela trailing_stops em banco existente...")
            cursor.execute('''
                CREATE TABLE trailing_stops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    trade_id INTEGER,
                    ticket INTEGER,
                    symbol TEXT,
                    action TEXT,
                    old_sl_price REAL,
                    new_sl_price REAL,
                    current_price REAL,
                    profit_pontos REAL,
                    profit_dinheiro REAL,
                    trailing_distance_pontos REAL,
                    trailing_distance_dinheiro REAL,
                    reason TEXT,
                    agent_version TEXT,
                    FOREIGN KEY (trade_id) REFERENCES trades (id)
                )
            ''')

        conn.commit()
        conn.close()
        
    def log_cycle(self, cycle_data: dict):
        """
        Registra um ciclo completo
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cycles (
                cycle_number, symbol, price, bb_upper, bb_middle, bb_lower,
                bb_position, rsi, rsi_overbought, rsi_oversold,
                volume_current, volume_avg, volume_multiplier, trend, momentum,
                signal_type, signal_strength, signal_reason, signal_price,
                sl_price, tp_price, order_result, order_error, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_data.get('cycle_number'),
            cycle_data.get('symbol'),
            cycle_data.get('price'),
            cycle_data.get('bb_upper'),
            cycle_data.get('bb_middle'),
            cycle_data.get('bb_lower'),
            cycle_data.get('bb_position'),
            cycle_data.get('rsi'),
            cycle_data.get('rsi_overbought'),
            cycle_data.get('rsi_oversold'),
            cycle_data.get('volume_current'),
            cycle_data.get('volume_avg'),
            cycle_data.get('volume_multiplier'),
            cycle_data.get('trend'),
            cycle_data.get('momentum'),
            cycle_data.get('signal_type'),
            cycle_data.get('signal_strength'),
            cycle_data.get('signal_reason'),
            cycle_data.get('signal_price'),
            cycle_data.get('sl_price'),
            cycle_data.get('tp_price'),
            cycle_data.get('order_result'),
            cycle_data.get('order_error'),
            cycle_data.get('agent_version')
        ))
        
        cycle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return cycle_id
        
    def log_trade(self, trade_data: dict, cycle_id: int = None):
        """
        Registra um trade executado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                cycle_id, symbol, trade_type, entry_price, sl_price, tp_price,
                volume, strength, reason, comment, status, exit_price,
                exit_reason, profit_loss, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_id,
            trade_data.get('symbol'),
            trade_data.get('trade_type'),
            trade_data.get('entry_price'),
            trade_data.get('sl_price'),
            trade_data.get('tp_price'),
            trade_data.get('volume'),
            trade_data.get('strength'),
            trade_data.get('reason'),
            trade_data.get('comment'),
            trade_data.get('status'),
            trade_data.get('exit_price'),
            trade_data.get('exit_reason'),
            trade_data.get('profit_loss'),
            trade_data.get('agent_version')
        ))
        
        conn.commit()
        conn.close()

    def log_trailing_stop(self, trailing_data: dict):
        """
        Registra uma ação de trailing stop
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO trailing_stops (
                trade_id, ticket, symbol, action, old_sl_price, new_sl_price,
                current_price, profit_pontos, profit_dinheiro,
                trailing_distance_pontos, trailing_distance_dinheiro,
                reason, agent_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trailing_data.get('trade_id'),
            trailing_data.get('ticket'),
            trailing_data.get('symbol'),
            trailing_data.get('action'),
            trailing_data.get('old_sl_price'),
            trailing_data.get('new_sl_price'),
            trailing_data.get('current_price'),
            trailing_data.get('profit_pontos'),
            trailing_data.get('profit_dinheiro'),
            trailing_data.get('trailing_distance_pontos'),
            trailing_data.get('trailing_distance_dinheiro'),
            trailing_data.get('reason'),
            trailing_data.get('agent_version')
        ))

        conn.commit()
        conn.close()

    def update_trade_status(self, trade_id: int, status: str, exit_price: float = None,
                           exit_reason: str = None, profit_loss: float = None):
        """
        Atualiza o status de um trade quando é fechado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE trades
            SET status = ?, exit_price = ?, exit_reason = ?, profit_loss = ?
            WHERE id = ?
        ''', (status, exit_price, exit_reason, profit_loss, trade_id))

        conn.commit()
        conn.close()

    def get_trade_id_by_ticket(self, ticket: int) -> int:
        """
        Busca o ID do trade pelo ticket MT5
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM trades WHERE ticket = ? ORDER BY id DESC LIMIT 1', (ticket,))
        result = cursor.fetchone()

        conn.close()

        return result[0] if result else None

    def update_strategy_performance(self, strategy_name: str, signal_type: str,
                             signal_strength: str, success: bool, 
                             profit_loss: float = 0.0):
        """
        Atualiza performance de uma estratégia
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se estratégia já existe
        cursor.execute('''
            SELECT * FROM strategy_performance 
            WHERE strategy_name = ? AND signal_type = ? AND signal_strength = ? AND agent_version = 'Flexible'
        ''', (strategy_name, signal_type, signal_strength))
        
        existing = cursor.fetchone()
        
        if existing:
            # Atualizar registro existente
            total_signals = existing[4] + 1
            successful_trades = existing[5] + (1 if success else 0)
            failed_trades = existing[6] + (0 if success else 1)
            total_profit_loss = existing[7] + profit_loss
            avg_profit_loss = total_profit_loss / total_signals if total_signals > 0 else 0
            success_rate = (successful_trades / total_signals * 100) if total_signals > 0 else 0
            
            cursor.execute('''
                UPDATE strategy_performance 
                SET total_signals = ?, successful_trades = ?, failed_trades = ?,
                    total_profit_loss = ?, avg_profit_loss = ?, success_rate = ?
                WHERE id = ?
            ''', (total_signals, successful_trades, failed_trades,
                   total_profit_loss, avg_profit_loss, success_rate, existing[0]))
        else:
            # Criar novo registro
            total_signals = 1
            successful_trades = 1 if success else 0
            failed_trades = 0 if success else 1
            total_profit_loss = profit_loss
            avg_profit_loss = profit_loss
            success_rate = 100 if success else 0
            
            cursor.execute('''
                INSERT INTO strategy_performance (
                    strategy_name, signal_type, signal_strength, total_signals,
                    successful_trades, failed_trades, total_profit_loss,
                    avg_profit_loss, success_rate, agent_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Flexible')
            ''', (strategy_name, signal_type, signal_strength, total_signals,
                   successful_trades, failed_trades, total_profit_loss,
                   avg_profit_loss, success_rate))
        
        conn.commit()
        conn.close()
        
    def get_strategy_performance(self, limit: int = 50):
        """
        Retorna performance das estratégias
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM strategy_performance 
            WHERE agent_version = 'Flexible'
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    def get_recent_cycles(self, limit: int = 100):
        """
        Retorna ciclos recentes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cycles 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    def get_trades_by_strategy(self, strategy_name: str, limit: int = 50):
        """
        Retorna trades por estratégia
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, c.cycle_number FROM trades t
            JOIN cycles c ON t.cycle_id = c.id
            WHERE t.reason LIKE ? OR t.strength = ?
            ORDER BY t.timestamp DESC 
            LIMIT ?
        ''', (f"%{strategy_name}%", strategy_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    def export_to_csv(self, table: str, filename: str = None):
        """
        Exporta dados para CSV
        """
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"btc_{table}_{timestamp}.csv"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if table == 'cycles':
            cursor.execute('SELECT * FROM cycles ORDER BY timestamp DESC')
            headers = [description[0] for description in cursor.description]
        elif table == 'trades':
            cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
            headers = [description[0] for description in cursor.description]
        elif table == 'strategy_performance':
            cursor.execute('SELECT * FROM strategy_performance ORDER BY timestamp DESC')
            headers = [description[0] for description in cursor.description]
        else:
            conn.close()
            return None
            
        rows = cursor.fetchall()
        conn.close()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
            
        return filename
        
    def get_analysis_summary(self):
        """
        Retorna resumo analítico completo
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('SELECT COUNT(*) FROM cycles')
        total_cycles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trades')
        total_trades = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cycles WHERE signal_type IS NOT NULL')
        total_signals = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(profit_loss) FROM trades WHERE profit_loss IS NOT NULL')
        avg_profit_loss = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) FROM trades WHERE profit_loss IS NOT NULL')
        winning_trades = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM trades WHERE profit_loss IS NOT NULL')
        completed_trades = cursor.fetchone()[0] or 1
        
        win_rate = (winning_trades / completed_trades * 100) if completed_trades > 0 else 0
        
        # Performance por estratégia
        cursor.execute('''
            SELECT signal_strength, COUNT(*) as signals, 
                   SUM(CASE WHEN order_result LIKE '%10009%' THEN 1 ELSE 0 END) as successful,
                   AVG(CASE WHEN order_result LIKE '%10009%' THEN 1 ELSE 0 END) * 100 as success_rate
            FROM cycles 
            WHERE signal_type IS NOT NULL AND agent_version = 'Flexible'
            GROUP BY signal_strength
            ORDER BY signals DESC
        ''')
        
        strategy_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_cycles': total_cycles,
            'total_trades': total_trades,
            'total_signals': total_signals,
            'avg_profit_loss': avg_profit_loss,
            'win_rate': win_rate,
            'strategy_stats': strategy_stats
        }
