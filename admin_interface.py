#!/usr/bin/env python3
"""
Simple Auto-CRUD Interface for Trading Bot Agent Management
Similar to auto-crud but for Python/Flask
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.manager import AgentManager
from core.database import setup_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'admin-interface-secret-key'

# Global agent manager
agent_manager = None

# HTML Template for the admin interface
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Bot Admin - Auto CRUD Interface</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}

        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            color: white;
        }}

        .stat-value {{ font-size: 2.5rem; font-weight: bold; margin-bottom: 8px; }}
        .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}

        .form-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .form-row {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 15px;
            align-items: end;
            margin-bottom: 20px;
        }}

        .form-group {{ display: flex; flex-direction: column; }}
        label {{ margin-bottom: 5px; font-weight: bold; color: #555; }}
        input, select {{
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }}
        input:focus, select:focus {{ border-color: #667eea; outline: none; }}

        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}

        .btn-primary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: #212529; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn-secondary {{ background: #6c757d; color: white; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }

        .agents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }}

        .agent-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }}

        .agent-header {{
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .agent-title {{ font-size: 1.3rem; font-weight: bold; color: #333; }}
        .status-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .status-active {{ background: #d4edda; color: #155724; }}
        .status-paused {{ background: #fff3cd; color: #856404; }}
        .status-stopped {{ background: #f8d7da; color: #721c24; }}

        .agent-info {{ margin: 15px 0; }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin: 10px 0;
        }}
        .info-item {{ padding: 8px; background: #f8f9fa; border-radius: 5px; }}
        .info-label {{ font-weight: bold; color: #666; font-size: 0.9rem; }}
        .info-value {{ color: #333; font-size: 0.9rem; }}

        .controls-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            margin-top: 15px;
        }}

        .worker-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
        }}

        .worker-status {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
        }}

        .worker-running {{ color: #28a745; }}
        .worker-stopped {{ color: #dc3545; }}

        .bulk-controls {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
        }}

        .footer a {{ color: white; text-decoration: none; font-weight: bold; }}
        .footer a:hover {{ text-decoration: underline; }}

        @media (max-width: 768px) {
            .agents-grid {{ grid-template-columns: 1fr; }}
            .form-row {{ grid-template-columns: 1fr; }}
            .controls-grid {{ grid-template-columns: 1fr 1fr; }}
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Trading Bot Auto-CRUD Interface</h1>
            <p>Interface completa para gerenciamento automático de agentes de trading</p>
            <p style="margin-top: 10px; opacity: 0.9;">Similar ao auto-crud, mas para Python/Flask</p>
        </div>

        <!-- Statistics Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ total_agents }}</div>
                <div class="stat-label">Total de Agentes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ active_agents }}</div>
                <div class="stat-label">Agentes Ativos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ paused_agents }}</div>
                <div class="stat-label">Agentes Pausados</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stopped_agents }}</div>
                <div class="stat-label">Agentes Parados</div>
            </div>
        </div>

        <!-- Worker Status -->
        <div class="worker-card">
            <div class="worker-status {{ 'worker-running' if worker_running else 'worker-stopped' }}">
                {{ '🟢 Worker Rodando' if worker_running else '🔴 Worker Parado' }}
            </div>
            <form method="POST" action="/admin/worker/toggle" style="display: inline;">
                <button type="submit" class="btn {{ 'btn-danger' if worker_running else 'btn-success' }}">
                    {{ 'Parar Worker' if worker_running else 'Iniciar Worker' }}
                </button>
            </form>
        </div>

        <!-- Create Agent Form -->
        <div class="form-section">
            <h2>➕ Criar Novo Agente</h2>
            <form method="POST" action="/admin/agents/create">
                <div class="form-row">
                    <div class="form-group">
                        <label for="symbol">Símbolo de Trading:</label>
                        <select id="symbol" name="symbol" required>
                            <option value="">Selecione um símbolo</option>
                            <option value="EURUSD">EURUSD - Euro/Dólar</option>
                            <option value="GBPUSD">GBPUSD - Libra/Dólar</option>
                            <option value="USDJPY">USDJPY - Dólar/Iene</option>
                            <option value="BTCUSD">BTCUSD - Bitcoin/Dólar</option>
                            <option value="XAUUSD">XAUUSD - Ouro/Dólar</option>
                            <option value="SPX500">SPX500 - S&P 500</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="volume">Volume (lots):</label>
                        <input type="number" id="volume" name="volume" step="0.01" value="0.01" min="0.01" max="100">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="take_profit">Take Profit ($):</label>
                        <input type="number" id="take_profit" name="take_profit" step="0.01" value="100">
                    </div>
                    <div class="form-group">
                        <label for="stop_loss">Stop Loss ($):</label>
                        <input type="number" id="stop_loss" name="stop_loss" step="0.01" value="50">
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">Criar Agente</button>
            </form>
        </div>

        <!-- Bulk Operations -->
        <div class="form-section">
            <h3>🔄 Operações em Lote</h3>
            <div class="bulk-controls">
                <form method="POST" action="/admin/agents/bulk/pause" style="display: inline;">
                    <button type="submit" class="btn btn-warning">Pausar Todos os Agentes</button>
                </form>
                <form method="POST" action="/admin/agents/bulk/resume" style="display: inline;">
                    <button type="submit" class="btn btn-success">Retomar Todos os Agentes</button>
                </form>
                <form method="POST" action="/admin/agents/bulk/stop" style="display: inline;">
                    <button type="submit" class="btn btn-secondary">Parar Todos os Agentes</button>
                </form>
                <a href="/admin/agents/stats" class="btn btn-primary" target="_blank">Ver Estatísticas Detalhadas</a>
            </div>
        </div>

        <!-- Agents List -->
        <div class="form-section">
            <h2>🤖 Agentes Existentes ({{ agents|length }})</h2>
            {% if agents %}
                <div class="agents-grid">
                    {% for agent in agents %}
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-title">{{ agent.name }}</div>
                            <div class="status-badge status-{{ agent.status }}">{{ agent.status.upper() }}</div>
                        </div>

                        <div class="agent-info">
                            <div class="info-grid">
                                <div class="info-item">
                                    <div class="info-label">Símbolo:</div>
                                    <div class="info-value">{{ agent.symbol }}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Volume:</div>
                                    <div class="info-value">{{ agent.volume }}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Take Profit:</div>
                                    <div class="info-value">${{ agent.take_profit }}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Stop Loss:</div>
                                    <div class="info-value">${{ agent.stop_loss }}</div>
                                </div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Indicadores:</div>
                                <div class="info-value">{% if agent.indicators %}{{ agent.indicators|join(' | ') }}{% else %}Nenhum{% endif %}</div>
                            </div>
                        </div>

                        <div class="controls-grid">
                            <form method="POST" action="/admin/agents/{{ agent.id }}/pause" style="display: inline;">
                                <button type="submit" class="btn btn-warning">Pausar</button>
                            </form>
                            <form method="POST" action="/admin/agents/{{ agent.id }}/resume" style="display: inline;">
                                <button type="submit" class="btn btn-success">Retomar</button>
                            </form>
                            <form method="POST" action="/admin/agents/{{ agent.id }}/stop" style="display: inline;">
                                <button type="submit" class="btn btn-secondary">Parar</button>
                            </form>
                            <a href="/admin/agents/{{ agent.id }}/stats" class="btn btn-primary" target="_blank">Stats</a>
                            <form method="POST" action="/admin/agents/{{ agent.id }}/delete" style="display: inline;">
                                <button type="submit" class="btn btn-danger"
                                        onclick="return confirm('Tem certeza que deseja deletar este agente?')">
                                    Deletar
                                </button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div style="text-align: center; padding: 40px; color: #666;">
                    <h3>📭 Nenhum agente encontrado</h3>
                    <p>Crie seu primeiro agente usando o formulário acima!</p>
                </div>
            {% endif %}
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>
                <strong>Auto-CRUD Interface</strong> |
                <a href="/">← Voltar ao Chat Principal</a> |
                <a href="/api/agents" target="_blank">Ver API JSON</a> |
                <a href="/test">Página de Teste</a>
            </p>
            <p style="margin-top: 10px; font-size: 0.9rem; opacity: 0.7;">
                Sistema de gerenciamento automático de agentes de trading
            </p>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main chatbot interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Trading Chatbot</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 Trading Chatbot - Interface Principal</h1>
        <p>✅ Sistema funcionando perfeitamente!</p>
        <p>🔗 <a href="/admin">Ir para Interface de Gerenciamento de Agentes</a></p>
        <p>🔗 <a href="/api/agents">Ver API de Agentes</a></p>
        <p>🔗 <a href="/test">Página de Teste</a></p>
    </body>
    </html>
    """


@app.route('/admin')
def admin_panel():
    """Auto-CRUD Admin Interface for Agent Management"""
    try:
        # Initialize agent manager
        global agent_manager
        if not agent_manager:
            setup_database()
            agent_manager = AgentManager()

        # Get agents data
        agents = agent_manager.list_agents() if agent_manager else []
        agents_data = []

        for agent in agents:
            agent_data = {
                'id': agent.config.id,
                'name': agent.config.name,
                'symbol': agent.config.symbol,
                'volume': agent.config.volume,
                'take_profit': agent.config.take_profit,
                'stop_loss': agent.config.stop_loss,
                'status': agent.status.value,
                'indicators': [ind.type.value for ind in agent.config.indicators]
            }
            agents_data.append(agent_data)

        # Calculate stats
        total_agents = len(agents_data)
        active_agents = sum(1 for a in agents_data if a['status'] == 'active')
        paused_agents = sum(1 for a in agents_data if a['status'] == 'paused')
        stopped_agents = sum(1 for a in agents_data if a['status'] == 'stopped')

        # Check worker status
        worker_running = False
        try:
            summary = agent_manager.get_summary() if agent_manager else {}
            worker_running = summary.get('worker_running', False)
        except:
            pass

        # Render template with data
        return render_template_string(ADMIN_TEMPLATE,
                                    agents=agents_data,
                                    total_agents=total_agents,
                                    active_agents=active_agents,
                                    paused_agents=paused_agents,
                                    stopped_agents=stopped_agents,
                                    worker_running=worker_running)

    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        return f"<h1>Error: {str(e)}</h1>"


@app.route('/admin/agents/create', methods=['POST'])
def create_agent():
    """Create a new agent via web form"""
    try:
        symbol = request.form.get('symbol', '')
        volume = float(request.form.get('volume', 0.01))
        take_profit = float(request.form.get('take_profit', 100))
        stop_loss = float(request.form.get('stop_loss', 50))

        if not symbol:
            return "Symbol is required"

        # Create agent message
        message = f"criar agente {symbol} com RSI volume {volume} tp {take_profit} sl {stop_loss}"

        if agent_manager:
            agent = agent_manager.create_agent(message)
            if agent:
                return f"""
                <h1>Success!</h1>
                <p>Agent '{agent.config.name}' created successfully!</p>
                <p><strong>Symbol:</strong> {agent.config.symbol}</p>
                <p><strong>Volume:</strong> {agent.config.volume}</p>
                <p><a href="/admin">← Back to Admin</a></p>
                """
            else:
                return "Failed to create agent"
        else:
            return "Agent manager not initialized"

    except Exception as e:
        return f"Error creating agent: {str(e)}"


@app.route('/admin/agents/<agent_id>/pause', methods=['POST'])
def pause_agent(agent_id):
    """Pause an agent"""
    try:
        if agent_manager:
            success = agent_manager.pause_agent(agent_id)
            return "Agent paused" if success else "Agent not found"
        else:
            return "Agent manager not initialized"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/agents/<agent_id>/resume', methods=['POST'])
def resume_agent(agent_id):
    """Resume an agent"""
    try:
        if agent_manager:
            success = agent_manager.resume_agent(agent_id)
            return "Agent resumed" if success else "Agent not found"
        else:
            return "Agent manager not initialized"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/agents/<agent_id>/stop', methods=['POST'])
def stop_agent(agent_id):
    """Stop an agent"""
    try:
        if agent_manager:
            success = agent_manager.stop_agent(agent_id)
            return "Agent stopped" if success else "Agent not found"
        else:
            return "Agent manager not initialized"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/agents/<agent_id>/delete', methods=['POST'])
def delete_agent(agent_id):
    """Delete an agent"""
    try:
        if agent_manager:
            success = agent_manager.delete_agent(agent_id)
            return "Agent deleted" if success else "Agent not found"
        else:
            return "Agent manager not initialized"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/worker/toggle', methods=['POST'])
def toggle_worker():
    """Toggle worker start/stop"""
    try:
        if agent_manager:
            # Check current status and toggle
            summary = agent_manager.get_summary()
            worker_running = summary.get('worker_running', False)

            if worker_running:
                agent_manager.stop_worker()
                message = "Worker stopped"
            else:
                agent_manager.start_worker(check_interval=30)
                message = "Worker started"

            return f"""
            <h1>Worker Updated</h1>
            <p>{message}</p>
            <p><a href="/admin">← Back to Admin</a></p>
            """
        else:
            return "Agent manager not initialized"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/agents/bulk/<action>', methods=['POST'])
def bulk_action(action):
    """Handle bulk operations"""
    try:
        if not agent_manager:
            return "Agent manager not initialized"

        agents = agent_manager.list_agents()
        count = 0

        if action == 'pause':
            for agent in agents:
                if agent.status.value == "active":
                    if agent_manager.pause_agent(agent.config.id):
                        count += 1
            message = f"Paused {count} agents"
        elif action == 'resume':
            for agent in agents:
                if agent.status.value == "paused":
                    if agent_manager.resume_agent(agent.config.id):
                        count += 1
            message = f"Resumed {count} agents"
        elif action == 'stop':
            for agent in agents:
                if agent_manager.stop_agent(agent.config.id):
                    count += 1
            message = f"Stopped {count} agents"
        else:
            return "Invalid action"

        return f"""
        <h1>Bulk Operation Completed</h1>
        <p>{message}</p>
        <p><a href="/admin">← Back to Admin</a></p>
        """

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/admin/agents/stats')
def agents_stats():
    """Show detailed statistics"""
    try:
        if not agent_manager:
            setup_database()
            agent_manager = AgentManager()

        agents = agent_manager.list_agents()
        stats_data = []

        for agent in agents:
            stats = agent.get_stats()
            stats_data.append({
                'name': agent.config.name,
                'symbol': agent.config.symbol,
                'status': agent.status.value,
                'trades_opened': stats.get('trades_opened', 0),
                'trades_closed': stats.get('trades_closed', 0),
                'total_profit': stats.get('total_profit', 0),
                'uptime': stats.get('uptime_seconds', 0)
            })

        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Agent Statistics</title></head>
        <body style="font-family: Arial; margin: 20px;">
            <h1>📊 Estatísticas Detalhadas dos Agentes</h1>
            <p><a href="/admin">← Voltar ao Admin</a></p>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f8f9fa;">
                    <th style="padding: 10px;">Nome</th>
                    <th style="padding: 10px;">Símbolo</th>
                    <th style="padding: 10px;">Status</th>
                    <th style="padding: 10px;">Trades Abertos</th>
                    <th style="padding: 10px;">Trades Fechados</th>
                    <th style="padding: 10px;">Lucro Total</th>
                    <th style="padding: 10px;">Uptime (seg)</th>
                </tr>
        """

        for stat in stats_data:
            html += f"""
                <tr>
                    <td style="padding: 10px;">{stat['name']}</td>
                    <td style="padding: 10px;">{stat['symbol']}</td>
                    <td style="padding: 10px;">{stat['status']}</td>
                    <td style="padding: 10px;">{stat['trades_opened']}</td>
                    <td style="padding: 10px;">{stat['trades_closed']}</td>
                    <td style="padding: 10px;">${stat['total_profit']:.2f}</td>
                    <td style="padding: 10px;">{stat['uptime']}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html

    except Exception as e:
        return f"<h1>Error loading stats: {str(e)}</h1>"


@app.route('/api/agents')
def api_agents():
    """API endpoint for agents data"""
    try:
        global agent_manager
        if not agent_manager:
            setup_database()
            agent_manager = AgentManager()

        agents = agent_manager.list_agents()
        agents_data = []

        for agent in agents:
            agents_data.append({
                "id": agent.config.id,
                "name": agent.config.name,
                "symbol": agent.config.symbol,
                "volume": agent.config.volume,
                "take_profit": agent.config.take_profit,
                "stop_loss": agent.config.stop_loss,
                "status": agent.status.value,
                "indicators": [ind.type.value for ind in agent.config.indicators]
            })

        return jsonify({
            "success": True,
            "agents": agents_data,
            "total": len(agents_data)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("Starting Auto-CRUD Trading Bot Interface...")
    print("Agent Management System initializing...")

    # Initialize database and agent manager
    setup_database()
    agent_manager = AgentManager()

    print("Auto-CRUD Interface ready!")
    print("Access points:")
    print("   * Main Interface: http://localhost:3000")
    print("   * Admin Panel: http://localhost:3000/admin")
    print("   * API Endpoints: http://localhost:3000/api/*")

    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=False,
        threaded=False,
        use_reloader=False
    )
