#!/usr/bin/env python3
"""
Dashboard para visualizar histórico de trades do banco de dados
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import get_db_connection

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """Página principal do dashboard."""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas gerais."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total de trades
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]

        # Lucros/Prejuízos
        cursor.execute("""
            SELECT
                SUM(CASE WHEN result > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(result) as total_profit,
                AVG(result) as avg_profit,
                MAX(result) as max_profit,
                MIN(result) as min_profit
            FROM trades
        """)
        stats = cursor.fetchone()

        win_rate = (stats[0] / total_trades * 100) if total_trades > 0 else 0

        # Trades por símbolo
        cursor.execute("""
            SELECT symbol, COUNT(*) as count, SUM(result) as profit
            FROM trades
            GROUP BY symbol
            ORDER BY count DESC
        """)
        by_symbol = cursor.fetchall()

        # Últimos 7 dias
        cursor.execute("""
            SELECT DATE(open_time) as date, COUNT(*) as count, SUM(result) as profit
            FROM trades
            WHERE open_time >= date('now', '-7 days')
            GROUP BY DATE(open_time)
            ORDER BY date
        """)
        last_7_days = cursor.fetchall()

        conn.close()

        return jsonify({
            'total_trades': total_trades,
            'wins': stats[0] or 0,
            'losses': stats[1] or 0,
            'total_profit': round(stats[2] or 0, 2),
            'avg_profit': round(stats[3] or 0, 2),
            'max_profit': round(stats[4] or 0, 2),
            'min_profit': round(stats[5] or 0, 2),
            'win_rate': round(win_rate, 1),
            'by_symbol': [{'symbol': row[0], 'count': row[1], 'profit': round(row[2], 2)} for row in by_symbol],
            'last_7_days': [{'date': row[0], 'count': row[1], 'profit': round(row[2], 2)} for row in last_7_days]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Retorna lista de trades com filtros."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Parâmetros de filtro
        symbol = request.args.get('symbol', '')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Query base
        query = "SELECT id, ticket, symbol, volume, entry_price, sl_price, tp_price, open_time, close_time, status, result FROM trades"
        params = []

        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        trades = cursor.fetchall()

        # Contar total
        count_query = "SELECT COUNT(*) FROM trades"
        if symbol:
            count_query += " WHERE symbol = ?"
            cursor.execute(count_query, [symbol])
        else:
            cursor.execute(count_query)

        total = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'trades': [
                {
                    'id': row[0],
                    'ticket': row[1],
                    'symbol': row[2],
                    'volume': row[3],
                    'entry_price': round(row[4], 5) if row[4] else 0,
                    'sl_price': round(row[5], 5) if row[5] else 0,
                    'tp_price': round(row[6], 5) if row[6] else 0,
                    'open_time': row[7],
                    'close_time': row[8],
                    'status': row[9],
                    'result': round(row[10], 2) if row[10] else 0
                }
                for row in trades
            ],
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance():
    """Retorna performance por símbolo e tipo."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Performance por símbolo
        cursor.execute("""
            SELECT
                symbol,
                COUNT(*) as total,
                SUM(CASE WHEN result > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(result) as total_profit,
                AVG(result) as avg_profit,
                MAX(result) as max_profit,
                MIN(result) as min_profit
            FROM trades
            GROUP BY symbol
            ORDER BY total DESC
        """)
        by_symbol = cursor.fetchall()

        # Performance por status
        cursor.execute("""
            SELECT
                status,
                COUNT(*) as total,
                SUM(CASE WHEN result > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(result) as total_profit,
                AVG(result) as avg_profit
            FROM trades
            GROUP BY status
        """)
        by_type = cursor.fetchall()

        conn.close()

        result = {
            'by_symbol': [
                {
                    'symbol': row[0],
                    'total': row[1],
                    'wins': row[2],
                    'losses': row[3],
                    'total_profit': round(row[4], 2),
                    'avg_profit': round(row[5], 2),
                    'max_profit': round(row[6], 2),
                    'min_profit': round(row[7], 2),
                    'win_rate': round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0
                }
                for row in by_symbol
            ],
            'by_type': [
                {
                    'type': row[0],
                    'total': row[1],
                    'wins': row[2],
                    'losses': row[3],
                    'total_profit': round(row[4], 2),
                    'avg_profit': round(row[5], 2),
                    'win_rate': round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0
                }
                for row in by_type
            ]
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equity-curve')
def get_equity_curve():
    """Retorna curva de patrimônio ao longo do tempo."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT close_time, result
            FROM trades
            WHERE close_time IS NOT NULL
            ORDER BY close_time ASC
        """)
        trades = cursor.fetchall()

        # Calcular patrimônio acumulado
        cumulative_profit = 0
        equity_curve = []

        for trade in trades:
            if trade[1]:  # Se result não é NULL
                cumulative_profit += trade[1]
            equity_curve.append({
                'date': trade[0],
                'equity': round(cumulative_profit, 2)
            })

        conn.close()

        return jsonify(equity_curve)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/symbols')
def get_symbols():
    """Retorna lista de símbolos no banco."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT symbol FROM trades ORDER BY symbol")
        symbols = [row[0] for row in cursor.fetchall()]

        conn.close()

        return jsonify(symbols)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001, threaded=True)
