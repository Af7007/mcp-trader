#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se as ordens estao sendo salvas no banco de dados.
"""
import sqlite3
import os
import sys

DB_FILE = "trading_bot.db"

def check_database():
    """Verifica o status do banco de dados e mostra trades salvos."""

    if not os.path.exists(DB_FILE):
        print("[ERRO] Banco de dados '{}' NAO EXISTE!".format(DB_FILE))
        print("       O banco sera criado quando o agente iniciar e fechar a primeira posicao.")
        return False

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Verificar se a tabela trades existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
        if not cursor.fetchone():
            print("[ERRO] Tabela 'trades' nao existe no banco!")
            conn.close()
            return False

        # Contar trades
        cursor.execute("SELECT COUNT(*) FROM trades")
        total = cursor.fetchone()[0]

        if total == 0:
            print("[OK] Banco de dados OK")
            print("[INFO] Nenhuma ordem salva ainda")
            print("       As ordens serao salvas automaticamente quando as posicoes forem fechadas.")
            conn.close()
            return True

        print("[OK] Banco de dados OK - {} trade(s) salvos".format(total))
        print("\n=== ULTIMOS 10 TRADES ===")
        print("-" * 130)
        header = "{:<8} {:<12} {:<6} {:<8} {:<12} {:<12} {:<10} {:<10} {:<12}".format(
            "Ticket", "Symbol", "Type", "Volume", "Open", "Close", "SL", "TP", "Profit")
        print(header)
        print("-" * 130)

        cursor.execute("""
            SELECT ticket, symbol, type, volume, open_price, close_price, sl, tp, profit, open_time
            FROM trades
            ORDER BY open_time DESC
            LIMIT 10
        """)

        for row in cursor.fetchall():
            ticket, symbol, type_trade, volume, open_p, close_p, sl, tp, profit, open_time = row
            profit_str = "+${:.2f}".format(profit) if profit >= 0 else "-${:.2f}".format(abs(profit))
            line = "{:<8} {:<12} {:<6} {:<8.2f} ${:<11.2f} ${:<11.2f} ${:<9.2f} ${:<9.2f} {:<12}".format(
                ticket, symbol, type_trade, volume, open_p, close_p, sl, tp, profit_str)
            print(line)

        print("-" * 130)

        # Estatísticas
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                ROUND(SUM(profit), 2) as total_profit,
                ROUND(AVG(profit), 2) as avg_profit
            FROM trades
        """)

        total, wins, losses, total_profit, avg_profit = cursor.fetchone()
        win_rate = (wins / total * 100) if total > 0 else 0

        print("\n=== ESTATISTICAS ===")
        print("Total: {} | Vitorias: {} ({:.1f}%) | Derrotas: {}".format(total, wins, win_rate, losses))
        print("Lucro Total: ${:.2f} | Lucro Medio: ${:.2f}".format(total_profit, avg_profit))

        conn.close()
        return True

    except sqlite3.Error as e:
        print("[ERRO] Erro ao acessar banco de dados: {}".format(e))
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)
