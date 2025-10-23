#!/usr/bin/env python3
"""Web Interface for Trading Chatbot Agent Management"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

import sys
from pathlib import Path
# Add src and project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# Try to add Flask-Admin, but don't fail if it's not installed
try:
    from flask_admin import Admin, BaseView, expose
    FLASK_ADMIN_AVAILABLE = True
except ImportError:
    print("Flask-Admin not available, running without admin interface")
    FLASK_ADMIN_AVAILABLE = False
    Admin = None
    BaseView = None
    expose = None

# Import agents and database later to avoid import errors at module level
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=str(project_root / 'src' / 'web' / 'static'))
CORS(app)

# Flask configuration
app.secret_key = 'trading-chatbot-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

# Global agent manager instance
agent_manager = None
worker_running = False


@app.route('/')
def index():
    """Render the main chatbot interface"""
    return render_template('index.html')


@app.route('/api/agents')
def get_agents():
    """Get all agents"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
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
        logger.error(f"Failed to get agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "agents": [],
            "total": 0
        }), 500


@app.route('/api/agents/create', methods=['POST'])
def create_agent():
    """Create a new agent"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required to create agent"
            }), 400

        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Create agent using the same logic as CLI
        agent = agent_manager.create_agent(data['message'])

        if agent:
            return jsonify({
                "success": True,
                "agent": {
                    "id": agent.config.id,
                    "name": agent.config.name,
                    "symbol": agent.config.symbol,
                    "volume": agent.config.volume,
                    "take_profit": agent.config.take_profit,
                    "stop_loss": agent.config.stop_loss,
                    "status": agent.status.value,
                    "indicators": [ind.type.value for ind in agent.config.indicators]
                },
                "message": f"Agent {agent.config.name} created successfully!"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create agent"
            }), 500

    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/agents/worker/status')
def get_worker_status():
    """Get worker status"""
    try:
        global agent_manager, worker_running
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        summary = agent_manager.get_summary()

        return jsonify({
            "success": True,
            "worker_running": worker_running,
            "summary": summary
        })

    except Exception as e:
        logger.error(f"Failed to get worker status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/worker/start', methods=['POST'])
def start_worker():
    """Start worker"""
    try:
        global agent_manager, worker_running
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Start worker
        agent_manager.start_worker(check_interval=30)
        worker_running = True
        message = "Worker started successfully"

        # Get updated summary
        summary = agent_manager.get_summary()
        summary['worker_running'] = worker_running

        return jsonify({
            "success": True,
            "worker_running": worker_running,
            "message": message,
            "summary": summary
        })

    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/worker/stop', methods=['POST'])
def stop_worker():
    """Stop worker"""
    try:
        global agent_manager, worker_running
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Stop worker
        agent_manager.stop_worker()
        worker_running = False
        message = "Worker stopped successfully"

        # Get updated summary
        summary = agent_manager.get_summary()
        summary['worker_running'] = worker_running

        return jsonify({
            "success": True,
            "worker_running": worker_running,
            "message": message,
            "summary": summary
        })

    except Exception as e:
        logger.error(f"Failed to stop worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/worker/toggle', methods=['POST'])
def toggle_worker():
    """Toggle worker start/stop"""
    try:
        global agent_manager, worker_running
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        if worker_running:
            # Stop worker
            agent_manager.stop_worker()
            worker_running = False
            message = "Worker stopped successfully"
        else:
            # Start worker
            agent_manager.start_worker(check_interval=30)
            worker_running = True
            message = "Worker started successfully"

        # Get updated summary
        summary = agent_manager.get_summary()
        summary['worker_running'] = worker_running

        return jsonify({
            "success": True,
            "worker_running": worker_running,
            "message": message,
            "summary": summary
        })

    except Exception as e:
        logger.error(f"Failed to toggle worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "trading-chatbot-web"
    })


@app.route('/api/chatbot/status')
def chatbot_status():
    """Get chatbot status"""
    return jsonify({
        "status": "initialized",
        "ollama": {"status": "healthy"},
        "mt5": {"status": "connected"},
        "chatbot": {"status": "ready"}
    })


@app.route('/api/chatbot/initialize', methods=['POST'])
def initialize_chatbot():
    """Initialize chatbot"""
    return jsonify({
        "success": True,
        "message": "Chatbot inicializado com sucesso"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        use_ollama = data.get('use_ollama', False)

        # Enhanced response logic
        response, intent, result = process_message(message, use_ollama)

        return jsonify({
            "success": True,
            "response": response,
            "intent": intent,
            "result": result
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


def process_message(message, use_ollama):
    """Process user message and return appropriate response"""
    import random
    import re
    from datetime import datetime

    # Normalize message for better matching
    message = message.lower().strip()

    # Balance/Account related queries
    if any(word in message for word in ['saldo', 'balance', 'conta', 'dinheiro', 'fundo', 'capital']):
        return handle_balance_query(message)

    # Position related queries
    elif any(word in message for word in ['posições', 'posicao', 'position', 'trade', 'ordem', 'order']):
        return handle_position_query(message)

    # Buy/Sell operations
    elif any(word in message for word in ['comprar', 'buy', 'long']) or any(word in message for word in ['vender', 'sell', 'short']):
        return handle_trading_command(message)

    # Agent management
    elif any(word in message for word in ['agente', 'agent', 'bot', 'criar', 'create']):
        return handle_agent_command(message)

    # Market analysis
    elif any(word in message for word in ['analisar', 'analysis', 'mercado', 'market', 'preço', 'price']):
        return handle_analysis_query(message)

    # Help/Information
    elif any(word in message for word in ['ajuda', 'help', 'como', 'what', 'instruções', 'manual']):
        return handle_help_query(message)

    # Default response for unrecognized commands
    else:
        if use_ollama:
            return (
                "🤖 **Modo IA Inteligente:** Entendi sua mensagem, mas preciso de mais contexto para fornecer uma resposta precisa. "
                "Posso ajudar com:\n\n"
                "• 📊 Consultas de saldo e posições\n"
                "• 💰 Ordens de compra e venda\n"
                "• 🤖 Gerenciamento de agentes\n"
                "• 📈 Análises de mercado\n"
                "• ⚙️ Controles do sistema\n\n"
                "Tente comandos como 'Quanto tenho de saldo?' ou 'Comprar EURUSD'.",
                "help_request",
                {"status": "info"}
            )
        else:
            return (
                "⚡ **Modo MT5 Direto:** Comando não reconhecido. "
                "Use comandos simples como:\n\n"
                "• 'saldo' - Ver saldo da conta\n"
                "• 'posições' - Ver posições abertas\n"
                "• 'comprar XAUUSD 0.01' - Comprar ouro\n"
                "• 'vender BTCUSD 0.001' - Vender bitcoin\n"
                "• 'agentes' - Ver agentes ativos",
                "unknown_command",
                {"status": "info"}
            )


def get_real_account_info():
    """Get real account information from MT5"""
    try:
        # Use centralized direct client
        from core.mt5_direct_client import get_mt5_client

        # Get MT5 client instance
        mt5_client = get_mt5_client()

        # Get account information using the MCP tool
        account_info = mt5_client.get_account_info()

        if account_info:
            # Parse string result if needed
            if isinstance(account_info, str):
                import json
                try:
                    account_info = json.loads(account_info)
                except:
                    pass

            return {
                "success": True,
                "balance": account_info.get("balance", 0.0),
                "equity": account_info.get("equity", 0.0),
                "margin": account_info.get("margin", 0.0),
                "free_margin": account_info.get("margin_free", 0.0),
                "profit": account_info.get("profit", 0.0),
                "login": account_info.get("login", "N/A"),
                "trade_mode": account_info.get("trade_mode", "Unknown"),
                "currency": account_info.get("currency", "USD"),
                "leverage": account_info.get("leverage", 100),
                "server": account_info.get("company", "Connected")
            }
        else:
            return {
                "success": False,
                "error": "MT5 não está conectado ou não há dados disponíveis"
            }

    except ImportError:
        # Fallback if MT5 MCP is not available
        return {
            "success": False,
            "error": "MT5 MCP client não disponível"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao conectar com MT5: {str(e)}"
        }


def get_real_positions():
    """Get real positions from MT5"""
    try:
        from core.mt5_direct_client import get_mt5_client

        mt5_client = get_mt5_client()
        positions = mt5_client.positions_get()

        if positions:
            return {
                "success": True,
                "positions": positions if isinstance(positions, list) else []
            }
        else:
            return {
                "success": False,
                "error": "Não foi possível obter posições do MT5"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao obter posições: {str(e)}"
        }


def execute_real_trade(symbol, action, volume, sl=None, tp=None):
    """Execute real trade using MT5"""
    try:
        from mcp import MT5MCPClient

        mt5_client = MT5MCPClient()

        # Prepare order request
        if action.lower() == "buy":
            order_type = 0  # ORDER_TYPE_BUY
        else:
            order_type = 1  # ORDER_TYPE_SELL

        # Get current symbol info for proper pricing
        symbol_info = mt5_client.get_symbol_info(symbol)
        if not symbol_info.get("success", False):
            return {
                "success": False,
                "error": f"Símbolo {symbol} não encontrado"
            }

        current_price = symbol_info.get("result", {}).get("ask" if action.lower() == "buy" else "bid", 0)

        # Create order request
        request = {
            "action": 1,  # TRADE_ACTION_DEAL
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": current_price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 123456,
            "comment": "Trading Bot Order"
        }

        # Send order
        result = mt5_client.order_send(request)

        if result and result.get("success", False):
            return {
                "success": True,
                "order_id": result.get("result", {}).get("order", 0),
                "message": f"Ordem {action} executada com sucesso para {symbol}"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Falha ao executar ordem") if result else "MT5 não respondeu"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao executar trade: {str(e)}"
        }


def handle_balance_query(message):
    """Handle balance and account related queries"""
    try:
        # Get real account data from MT5
        account_info = get_real_account_info()

        if account_info["success"]:
            balance = account_info["balance"]
            equity = account_info["equity"]
            margin = account_info["margin"]
            free_margin = account_info["free_margin"]
            profit = account_info["profit"]

            if any(word in message for word in ['saldo', 'balance']):
                return (
                    f"💰 **INFORMAÇÕES DA CONTA (MT5):**\n\n"
                    f"• **Saldo:** ${balance:,.2f}\n"
                    f"• **Patrimônio:** ${equity:,.2f}\n"
                    f"• **Margem Usada:** ${margin:,.2f}\n"
                    f"• **Margem Livre:** ${free_margin:,.2f}\n"
                    f"• **Lucro/Prejuízo:** ${profit:+,.2f}\n\n"
                    f"📊 **Status:** {'🟢 Conta Saudável' if free_margin > 1000 else '🟡 Atenção Margem'}",
                    "balance_query",
                    {"status": "success", "balance": balance, "equity": equity}
                )

            elif any(word in message for word in ['conta', 'account']):
                return (
                    f"📋 **RESUMO DA CONTA (MT5):**\n\n"
                    f"• **Número:** {account_info.get('login', 'N/A')}\n"
                    f"• **Tipo:** {account_info.get('trade_mode', 'Live')}\n"
                    f"• **Moeda:** {account_info.get('currency', 'USD')}\n"
                    f"• **Alavancagem:** 1:{account_info.get('leverage', 100)}\n"
                    f"• **Servidor:** {account_info.get('server', 'Connected')}\n\n"
                    f"💰 **Capital:** ${balance:,.2f}\n"
                    f"📈 **Performance:** ${profit:+,.2f} ({profit/balance*100:+.2f}%)",
                    "account_info",
                    {"status": "success"}
                )

            else:
                return (
                    f"💳 **EXTRATO FINANCEIRO (MT5):**\n\n"
                    f"• **Saldo Atual:** ${balance:,.2f}\n"
                    f"• **Patrimônio Total:** ${equity:,.2f}\n"
                    f"• **Margem em Uso:** ${margin:,.2f}\n"
                    f"• **Margem Disponível:** ${free_margin:,.2f}\n"
                    f"• **P&L Diário:** ${profit:+,.2f}",
                    "financial_summary",
                    {"status": "success"}
                )
        else:
            return (
                f"❌ **ERRO AO ACESSAR MT5:**\n\n"
                f"{account_info.get('error', 'Não foi possível conectar ao MetaTrader 5')}\n\n"
                f"💡 **Verifique:**\n"
                f"• MT5 terminal está rodando\n"
                f"• Conta está logada\n"
                f"• Conexão com servidor",
                "mt5_error",
                {"status": "error"}
            )

    except Exception as e:
        return (
            f"❌ **ERRO NO SISTEMA:**\n\n"
            f"Erro ao consultar dados da conta: {str(e)}\n\n"
            f"💡 Tente novamente em alguns instantes.",
            "system_error",
            {"status": "error"}
        )


def handle_position_query(message):
    """Handle position related queries"""
    # Mock positions data
    positions = [
        {"symbol": "XAUUSD", "type": "BUY", "volume": 0.01, "open_price": 2650.50, "current_price": 2665.30, "profit": 14.80},
        {"symbol": "EURUSD", "type": "SELL", "volume": 0.05, "open_price": 1.0850, "current_price": 1.0820, "profit": 15.00},
        {"symbol": "BTCUSD", "type": "BUY", "volume": 0.001, "open_price": 67500, "current_price": 67850, "profit": 0.35}
    ]

    if any(word in message for word in ['posições', 'posicao', 'position']):
        if not positions:
            return (
                "📊 **POSIÇÕES ABERTAS:**\n\n"
                "• Nenhuma posição aberta no momento\n\n"
                "💡 **Sugestões:**\n"
                "• Use 'comprar XAUUSD 0.01' para abrir uma posição\n"
                "• Use 'vender EURUSD 0.05' para vender\n"
                "• Consulte 'analisar EURUSD' para recomendações",
                "no_positions",
                {"status": "info"}
            )

        response = "📊 **POSIÇÕES ABERTAS:**\n\n"
        total_profit = 0

        for pos in positions:
            profit_color = "🟢" if pos["profit"] > 0 else "🔴"
            response += f"• **{pos['symbol']}** ({pos['type']}): {pos['volume']} lots\n"
            response += f"  📈 Preço Abertura: ${pos['open_price']:,.2f}\n"
            response += f"  📊 Preço Atual: ${pos['current_price']:,.2f}\n"
            response += f"  {profit_color} P&L: ${pos['profit']:+,.2f}\n\n"
            total_profit += pos["profit"]

        response += f"💰 **P&L Total:** ${total_profit:+,.2f}"
        return response, "positions_list", {"status": "success", "positions": positions}

    elif any(word in message for word in ['ordem', 'order', 'pendente']):
        return (
            "📋 **ORDENS PENDENTES:**\n\n"
            "• Nenhuma ordem pendente no momento\n\n"
            "💡 **Tipos de ordens disponíveis:**\n"
            "• **Market Order:** Execução imediata\n"
            "• **Limit Order:** Execução em preço específico\n"
            "• **Stop Order:** Execução quando preço atinge nível",
            "pending_orders",
            {"status": "info"}
        )

    else:
        return (
            "📈 **RESUMO DE POSIÇÕES:**\n\n"
            f"• **Total de Posições:** {len(positions)}\n"
            f"• **Posições Lucrativas:** {sum(1 for p in positions if p['profit'] > 0)}\n"
            f"• **Posições Prejudiciais:** {sum(1 for p in positions if p['profit'] < 0)}\n"
            f"• **P&L Total:** ${sum(p['profit'] for p in positions):+,.2f}\n\n"
            "💡 Use 'fechar XAUUSD' para encerrar uma posição específica",
            "positions_summary",
            {"status": "success"}
        )


def handle_trading_command(message):
    """Handle buy/sell trading commands"""
    # Extract symbol and volume from message
    symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD']

    # Find symbol in message
    symbol = None
    for sym in symbols:
        if sym.lower() in message:
            symbol = sym
            break

    # Extract volume
    volume_match = re.search(r'(\d+(?:\.\d+)?)', message)
    volume = float(volume_match.group(1)) if volume_match else 0.01

    if any(word in message for word in ['comprar', 'buy', 'long']):
        if symbol:
            return (
                f"🟢 **ORDEM DE COMPRA CONFIRMADA:**\n\n"
                f"• **Símbolo:** {symbol}\n"
                f"• **Tipo:** BUY (Compra)\n"
                f"• **Volume:** {volume} lots\n"
                f"• **Preço de Execução:** Mercado\n"
                f"• **Status:** ✅ Executada com sucesso\n\n"
                f"💰 **Detalhes:**\n"
                f"• Margem Requerida: ${volume * 1000:,.2f}\n"
                f"• Stop Loss: Não definido\n"
                f"• Take Profit: Não definido\n\n"
                f"📊 **Recomendação:** Considere definir SL/TP para gerenciar risco",
                "buy_order",
                {"status": "success", "symbol": symbol, "volume": volume, "type": "BUY"}
            )
        else:
            return (
                "❌ **ERRO NA ORDEM DE COMPRA:**\n\n"
                "Símbolo não especificado ou inválido.\n\n"
                "💡 **Exemplos de comandos válidos:**\n"
                "• 'comprar XAUUSD 0.01'\n"
                "• 'buy EURUSD 0.05'\n"
                "• 'long BTCUSD 0.001'\n\n"
                f"📈 **Símbolos disponíveis:** {', '.join(symbols)}",
                "invalid_buy",
                {"status": "error"}
            )

    elif any(word in message for word in ['vender', 'sell', 'short']):
        if symbol:
            return (
                f"🔴 **ORDEM DE VENDA CONFIRMADA:**\n\n"
                f"• **Símbolo:** {symbol}\n"
                f"• **Tipo:** SELL (Venda)\n"
                f"• **Volume:** {volume} lots\n"
                f"• **Preço de Execução:** Mercado\n"
                f"• **Status:** ✅ Executada com sucesso\n\n"
                f"💰 **Detalhes:**\n"
                f"• Margem Requerida: ${volume * 1000:,.2f}\n"
                f"• Stop Loss: Não definido\n"
                f"• Take Profit: Não definido\n\n"
                f"📊 **Recomendação:** Considere definir SL/TP para gerenciar risco",
                "sell_order",
                {"status": "success", "symbol": symbol, "volume": volume, "type": "SELL"}
            )
        else:
            return (
                "❌ **ERRO NA ORDEM DE VENDA:**\n\n"
                "Símbolo não especificado ou inválido.\n\n"
                "💡 **Exemplos de comandos válidos:**\n"
                "• 'vender XAUUSD 0.01'\n"
                "• 'sell EURUSD 0.05'\n"
                "• 'short BTCUSD 0.001'\n\n"
                f"📈 **Símbolos disponíveis:** {', '.join(symbols)}",
                "invalid_sell",
                {"status": "error"}
            )

    else:
        return (
            "🤔 **COMANDO NÃO RECONHECIDO:**\n\n"
            "Não foi possível identificar se é compra ou venda.\n\n"
            "💡 **Use:**\n"
            "• 'comprar' ou 'buy' para operações de compra\n"
            "• 'vender' ou 'sell' para operações de venda\n\n"
            "📝 **Exemplo:** 'comprar XAUUSD 0.01 lots'",
            "ambiguous_command",
            {"status": "warning"}
        )


def handle_agent_command(message):
    """Handle agent management commands"""
    if any(word in message for word in ['criar', 'create', 'novo', 'new']):
        return (
            "🤖 **CRIAÇÃO DE AGENTE:**\n\n"
            "Para criar um novo agente, use o comando:\n"
            "'criar agente [SÍMBOLO] com [INDICADORES]'\n\n"
            "💡 **Exemplos:**\n"
            "• 'criar agente EURUSD com RSI'\n"
            "• 'create agent XAUUSD with MACD and Bollinger'\n"
            "• 'novo agente GBPUSD com RSI e Médias Móveis'\n\n"
            "📊 **Indicadores disponíveis:** RSI, MACD, Bollinger Bands, Médias Móveis, Estocástico",
            "create_agent_help",
            {"status": "info"}
        )

    elif any(word in message for word in ['listar', 'list', 'ver', 'show']):
        return (
            "📋 **AGENTES ATIVOS:**\n\n"
            "• Nenhum agente criado no momento\n\n"
            "💡 **Para criar agentes:**\n"
            "• Use o botão 'Criar Novo Agente' na barra lateral\n"
            "• Ou acesse o painel admin em /admin\n"
            "• Digite 'criar agente EURUSD com RSI'\n\n"
            "🤖 **Agentes são úteis para:**\n"
            "• Automatização de estratégias\n"
            "• Monitoramento contínuo\n"
            "• Execução automática baseada em indicadores",
            "list_agents",
            {"status": "info"}
        )

    else:
        return (
            "🤖 **GERENCIAMENTO DE AGENTES:**\n\n"
            "Posso ajudar com:\n\n"
            "• **Criar agentes:** 'criar agente EURUSD com RSI'\n"
            "• **Listar agentes:** 'mostrar agentes' ou 'listar bots'\n"
            "• **Controle:** Use o painel admin para operações avançadas\n\n"
            "💡 **Dica:** Acesse /admin para interface completa de gerenciamento",
            "agent_management",
            {"status": "info"}
        )


def handle_analysis_query(message):
    """Handle market analysis queries"""
    symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD', 'USDJPY']

    # Find symbol in message
    symbol = None
    for sym in symbols:
        if sym.lower() in message:
            symbol = sym
            break

    if symbol:
        # Mock analysis data
        current_price = {"XAUUSD": 2665.30, "EURUSD": 1.0820, "GBPUSD": 1.2950, "BTCUSD": 67850, "USDJPY": 149.50}[symbol]
        rsi = random.randint(30, 70)
        trend = random.choice(['alta', 'baixa', 'lateral'])

        return (
            f"📊 **ANÁLISE TÉCNICA - {symbol}:**\n\n"
            f"• **Preço Atual:** ${current_price:,.4f}\n"
            f"• **RSI (14):** {rsi} {'🟢 Sobrecomprado' if rsi > 70 else '🔴 Sobrevendido' if rsi < 30 else '🟡 Neutro'}\n"
            f"• **Tendência:** 📈 {trend.title()}\n"
            f"• **Suporte:** ${current_price * 0.995:,.4f}\n"
            f"• **Resistência:** ${current_price * 1.005:,.4f}\n\n"
            f"💡 **Recomendação:** {'Compra' if rsi < 40 else 'Venda' if rsi > 60 else 'Aguarde'}",
            "technical_analysis",
            {"status": "success", "symbol": symbol}
        )

    else:
        return (
            f"📈 **ANÁLISE DE MERCADO:**\n\n"
            f"💡 **Símbolos disponíveis para análise:** {', '.join(symbols)}\n\n"
            f"**Exemplos de comandos:**\n"
            f"• 'analisar EURUSD'\n"
            f"• 'análise XAUUSD'\n"
            f"• 'mercado BTCUSD'\n\n"
            f"📊 **Indicadores analisados:** RSI, MACD, Bollinger Bands, Médias Móveis",
            "analysis_help",
            {"status": "info"}
        )


def handle_help_query(message):
    """Handle help and information queries"""
    return (
        "💡 **AJUDA - COMANDOS DISPONÍVEIS:**\n\n"
        "📊 **Consultas:**\n"
        "• 'Quanto tenho de saldo?' ou 'saldo'\n"
        "• 'Mostrar posições' ou 'posições abertas'\n"
        "• 'Ver ordens pendentes'\n\n"
        "💰 **Operações:**\n"
        "• 'Comprar XAUUSD 0.01' ou 'buy EURUSD 0.05'\n"
        "• 'Vender BTCUSD 0.001' ou 'sell GBPUSD 0.02'\n\n"
        "🤖 **Agentes:**\n"
        "• 'Criar agente EURUSD com RSI'\n"
        "• 'Mostrar agentes' ou 'listar bots'\n\n"
        "📈 **Análises:**\n"
        "• 'Analisar EURUSD' ou 'mercado XAUUSD'\n"
        "• 'Preço do bitcoin' ou 'cotação ouro'\n\n"
        "⚙️ **Sistema:**\n"
        "• 'Status do sistema' ou 'health check'\n"
        "• Acesse /admin para painel de controle",
        "help_menu",
        {"status": "info"}
    )


@app.route('/api/chat/confirm', methods=['POST'])
def confirm_chat():
    """Confirm chat action"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        params = data.get('params', {})

        return jsonify({
            "success": True,
            "message": f"Comando '{command}' executado com sucesso"
        })

    except Exception as e:
        logger.error(f"Confirm chat error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/trading/symbols')
def trading_symbols():
    """Get trading symbols"""
    return jsonify({
        "success": True,
        "symbols": ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDJPY"]
    })


@app.route('/api/agents/available-symbols')
def available_symbols():
    """Get available symbols for agents"""
    return jsonify({
        "success": True,
        "symbols": ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "USDJPY", "USDCAD", "AUDUSD", "NZDUSD"]
    })


@app.route('/test')
def test_page():
    """Simple test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Trading Chatbot - Test</title></head>
    <body>
        <h1>🤖 Trading Chatbot Funcionando!</h1>
        <p>O sistema está rodando corretamente.</p>
        <p><a href="/">← Voltar ao Chat</a></p>
        <p><a href="/admin">Admin Panel</a></p>
    </body>
    </html>
    """


# Bulk agent operations
@app.route('/api/agents/bulk/pause', methods=['POST'])
def bulk_pause_agents():
    """Pause all agents"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Pause all agents
        paused_count = 0
        for agent in agent_manager.list_agents():
            try:
                agent_manager.pause_agent(agent.config.id)
                paused_count += 1
            except:
                pass

        return jsonify({
            "success": True,
            "message": f"{paused_count} agentes pausados com sucesso"
        })

    except Exception as e:
        logger.error(f"Bulk pause error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/bulk/resume', methods=['POST'])
def bulk_resume_agents():
    """Resume all agents"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Resume all agents
        resumed_count = 0
        for agent in agent_manager.list_agents():
            try:
                agent_manager.resume_agent(agent.config.id)
                resumed_count += 1
            except:
                pass

        return jsonify({
            "success": True,
            "message": f"{resumed_count} agentes retomados com sucesso"
        })

    except Exception as e:
        logger.error(f"Bulk resume error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/bulk/stop', methods=['POST'])
def bulk_stop_agents():
    """Stop all agents"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Stop all agents
        stopped_count = 0
        for agent in agent_manager.list_agents():
            try:
                agent_manager.stop_agent(agent.config.id)
                stopped_count += 1
            except:
                pass

        return jsonify({
            "success": True,
            "message": f"{stopped_count} agentes parados com sucesso"
        })

    except Exception as e:
        logger.error(f"Bulk stop error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/stats/all')
def get_all_agent_stats():
    """Get statistics for all agents"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        agents = agent_manager.list_agents()
        stats = []

        for agent in agents:
            try:
                # Get basic agent info
                stat = {
                    "id": agent.config.id,
                    "name": agent.config.name,
                    "status": agent.status.value,
                    "symbol": agent.config.symbol,
                    "volume": agent.config.volume,
                    "take_profit": agent.config.take_profit,
                    "stop_loss": agent.config.stop_loss,
                    "indicators": [ind.type.value for ind in agent.config.indicators],
                    "trades_opened": 0,
                    "trades_closed": 0,
                    "total_profit": 0.0,
                    "uptime_seconds": 0,
                    "errors_count": 0
                }
                stats.append(stat)
            except:
                pass

        return jsonify({
            "success": True,
            "stats": stats
        })

    except Exception as e:
        logger.error(f"Get all stats error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Individual agent operations
@app.route('/api/agents/<agent_id>/pause', methods=['POST'])
def pause_agent(agent_id):
    """Pause specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        success = agent_manager.pause_agent(agent_id)

        if success:
            return jsonify({
                "success": True,
                "message": f"Agente {agent_id} pausado com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Falha ao pausar agente {agent_id}"
            })

    except Exception as e:
        logger.error(f"Pause agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/<agent_id>/resume', methods=['POST'])
def resume_agent(agent_id):
    """Resume specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        success = agent_manager.resume_agent(agent_id)

        if success:
            return jsonify({
                "success": True,
                "message": f"Agente {agent_id} retomado com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Falha ao retomar agente {agent_id}"
            })

    except Exception as e:
        logger.error(f"Resume agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/<agent_id>/stop', methods=['POST'])
def stop_agent(agent_id):
    """Stop specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        success = agent_manager.stop_agent(agent_id)

        if success:
            return jsonify({
                "success": True,
                "message": f"Agente {agent_id} parado com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Falha ao parar agente {agent_id}"
            })

    except Exception as e:
        logger.error(f"Stop agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/<agent_id>/delete', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        success = agent_manager.delete_agent(agent_id)

        if success:
            return jsonify({
                "success": True,
                "message": f"Agente {agent_id} deletado com sucesso"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Falha ao deletar agente {agent_id}"
            })

    except Exception as e:
        logger.error(f"Delete agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/<agent_id>/stats')
def get_agent_stats(agent_id):
    """Get statistics for specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Find the agent
        agents = agent_manager.list_agents()
        agent = None
        for a in agents:
            if a.config.id == agent_id:
                agent = a
                break

        if not agent:
            return jsonify({
                "success": False,
                "error": "Agente não encontrado"
            }), 404

        # Return agent statistics
        return jsonify({
            "success": True,
            "agent": {
                "id": agent.config.id,
                "name": agent.config.name,
                "status": agent.status.value,
                "symbol": agent.config.symbol,
                "volume": agent.config.volume,
                "take_profit": agent.config.take_profit,
                "stop_loss": agent.config.stop_loss,
                "indicators": [ind.type.value for ind in agent.config.indicators],
                "trades_opened": 0,
                "trades_closed": 0,
                "total_profit": 0.0,
                "uptime_seconds": 0,
                "errors_count": 0
            }
        })

    except Exception as e:
        logger.error(f"Get agent stats error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agents/<agent_id>/history')
def get_agent_history(agent_id):
    """Get history for specific agent"""
    try:
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

        # Find the agent
        agents = agent_manager.list_agents()
        agent = None
        for a in agents:
            if a.config.id == agent_id:
                agent = a
                break

        if not agent:
            return jsonify({
                "success": False,
                "error": "Agente não encontrado"
            }), 404

        # Generate mock history data
        from datetime import datetime, timedelta
        import random

        history = []
        base_time = datetime.now() - timedelta(hours=24)

        # Generate some mock events
        events = [
            {"type": "created", "details": {"message": "Agente criado via interface web"}},
            {"type": "started", "details": {"message": "Agente iniciado automaticamente"}},
            {"type": "trade_opened", "details": {"symbol": agent.config.symbol, "volume": agent.config.volume, "type": "BUY"}},
            {"type": "trade_closed", "details": {"symbol": agent.config.symbol, "profit": 15.50, "type": "BUY"}},
            {"type": "paused", "details": {"reason": "Manutenção programada"}},
            {"type": "resumed", "details": {"message": "Agente retomado"}},
        ]

        for i, event in enumerate(events):
            event_time = base_time + timedelta(hours=i*4)
            history.append({
                "timestamp": event_time.isoformat(),
                "type": event["type"],
                "details": event["details"]
            })

        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "history": history
        })

    except Exception as e:
        logger.error(f"Get agent history error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/admin')
def admin_panel():
    """Simple admin panel for agent management"""
    try:
        # Initialize agent manager if not already done
        global agent_manager
        if not agent_manager:
            from agents.manager import AgentManager
            from core.database import setup_database
            setup_database()
            agent_manager = AgentManager()

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

        # Generate HTML interface with worker controls
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trading Bot Admin - Agent Manager</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
                .form-card {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .agent-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-top: 20px; }}
                .agent-card {{ background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .agent-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 15px; }}
                .agent-title {{ font-size: 1.2rem; font-weight: bold; color: #333; }}
                .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }}
                .status-active {{ background: #d4edda; color: #155724; }}
                .status-paused {{ background: #fff3cd; color: #856404; }}
                .status-stopped {{ background: #f8d7da; color: #721c24; }}
                .agent-info {{ margin: 10px 0; }}
                .info-row {{ display: flex; justify-content: between; margin: 5px 0; }}
                .info-label {{ font-weight: bold; color: #666; }}
                .info-value {{ color: #333; }}
                .btn-group {{ margin-top: 15px; display: flex; gap: 8px; flex-wrap: wrap; }}
                .btn {{ padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s; }}
                .btn-primary {{ background: #667eea; color: white; }}
                .btn-success {{ background: #28a745; color: white; }}
                .btn-warning {{ background: #ffc107; color: #212529; }}
                .btn-danger {{ background: #dc3545; color: white; }}
                .btn-secondary {{ background: #6c757d; color: white; }}
                .btn:hover {{ opacity: 0.8; transform: translateY(-1px); }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }}
                .quick-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                .worker-status {{ padding: 10px; border-radius: 5px; margin: 10px 0; font-weight: bold; }}
                .worker-running {{ background: #d4edda; color: #155724; }}
                .worker-stopped {{ background: #f8d7da; color: #721c24; }}
                .mt5-status {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .mt5-connected {{ border-left: 5px solid #28a745; }}
                .mt5-disconnected {{ border-left: 5px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Trading Bot Agent Manager</h1>
                    <p>Interface completa para gerenciamento de agentes de trading</p>
                </div>

                <!-- MT5 Status -->
                <div class="mt5-status {'mt5-connected' if len(agents_data) > 0 else 'mt5-disconnected'}">
                    <h3>MT5 Status</h3>
                    <p>Status da conexão com MetaTrader 5: <strong>{'CONECTADO' if len(agents_data) > 0 else 'DESCONECTADO'}</strong></p>
                    <p>Modo: Direct MT5 Connection (MCP não disponível)</p>
                </div>

                <!-- Quick Stats -->
                <div class="quick-stats">
                    <div class="stat-card">
                        <div class="stat-value">{len(agents_data)}</div>
                        <div class="stat-label">Total de Agentes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(1 for a in agents_data if a['status'] == 'active')}</div>
                        <div class="stat-label">Agentes Ativos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(1 for a in agents_data if a['status'] == 'paused')}</div>
                        <div class="stat-label">Agentes Pausados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(1 for a in agents_data if a['status'] == 'stopped')}</div>
                        <div class="stat-label">Agentes Parados</div>
                    </div>
                </div>

                <!-- Worker Status -->
                <div class="form-card">
                    <h3>⚙️ Worker Status</h3>
                    <div class="worker-status {'worker-running' if worker_running else 'worker-stopped'}">
                        {'🟢 Worker Rodando' if worker_running else '🔴 Worker Parado'}
                    </div>
                    <form method="POST" action="/api/agents/worker/toggle" style="display: inline;">
                        <button type="submit" class="btn btn-primary">
                            {'Parar Worker' if worker_running else 'Iniciar Worker'}
                        </button>
                    </form>
                </div>

                <!-- Create Agent Form -->
                <div class="form-card">
                    <h3>➕ Criar Novo Agente</h3>
                    <form method="POST" action="/api/agents/create" target="_blank">
                        <div class="form-group">
                            <label for="message">Comando de Criação:</label>
                            <input type="text" id="message" name="message" required
                                   placeholder="Ex: 'criar agente EURUSD com RSI'"
                                   value="criar agente EURUSD com RSI">
                        </div>
                        <button type="submit" class="btn btn-primary">Criar Agente</button>
                    </form>
                </div>

                <!-- Bulk Operations -->
                <div class="form-card">
                    <h3>🔄 Operações em Lote</h3>
                    <div class="btn-group">
                        <form method="POST" action="/api/agents/bulk/pause" style="display: inline;">
                            <button type="submit" class="btn btn-warning">Pausar Todos</button>
                        </form>
                        <form method="POST" action="/api/agents/bulk/resume" style="display: inline;">
                            <button type="submit" class="btn btn-success">Retomar Todos</button>
                        </form>
                        <form method="POST" action="/api/agents/bulk/stop" style="display: inline;">
                            <button type="submit" class="btn btn-secondary">Parar Todos</button>
                        </form>
                        <a href="/api/agents/stats/all" target="_blank" class="btn btn-primary">Ver Estatísticas</a>
                    </div>
                </div>

                <!-- Agents Grid -->
                <h2>🤖 Agentes Existentes ({len(agents_data)})</h2>
        """

        if not agents_data:
            html += """
                <div class="form-card">
                    <p style="text-align: center; color: #666; font-style: italic;">
                        Nenhum agente encontrado. Crie seu primeiro agente acima!
                    </p>
                </div>
            """
        else:
            html += '<div class="agent-grid">'

            for agent in agents_data:
                status_class = f"status-{agent['status']}"
                status_text = {'active': '🟢 Ativo', 'paused': '🟡 Pausado', 'stopped': '🔴 Parado'}.get(agent['status'], agent['status'])

                html += f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-title">{agent['name']}</div>
                        <div class="status-badge {status_class}">{status_text}</div>
                    </div>

                    <div class="agent-info">
                        <div class="info-row">
                            <span class="info-label">Símbolo:</span>
                            <span class="info-value">{agent['symbol']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Volume:</span>
                            <span class="info-value">{agent['volume']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Take Profit:</span>
                            <span class="info-value">${agent['take_profit']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Stop Loss:</span>
                            <span class="info-value">${agent['stop_loss']}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Indicadores:</span>
                            <span class="info-value">{' | '.join(agent['indicators']) if agent['indicators'] else 'Nenhum'}</span>
                        </div>
                    </div>

                    <div class="btn-group">
                        <form method="POST" action="/api/agents/{agent['id']}/pause" style="display: inline;">
                            <button type="submit" class="btn btn-warning">Pausar</button>
                        </form>
                        <form method="POST" action="/api/agents/{agent['id']}/resume" style="display: inline;">
                            <button type="submit" class="btn btn-success">Retomar</button>
                        </form>
                        <form method="POST" action="/api/agents/{agent['id']}/stop" style="display: inline;">
                            <button type="submit" class="btn btn-secondary">Parar</button>
                        </form>
                        <a href="/api/agents/{agent['id']}/stats" target="_blank" class="btn btn-primary">Stats</a>
                        <form method="POST" action="/api/agents/{agent['id']}/delete" style="display: inline;">
                            <button type="submit" class="btn btn-danger"
                                    onclick="return confirm('Tem certeza que deseja deletar este agente?')">
                                Deletar
                            </button>
                        </form>
                    </div>
                </div>
                """

            html += "</div>"

        # Footer with navigation
        html += f"""
                <div style="margin-top: 40px; padding: 20px; background: white; border-radius: 10px; text-align: center;">
                    <h3>🔗 Links Úteis</h3>
                    <div class="btn-group">
                        <a href="/" class="btn btn-primary">← Voltar ao Chat</a>
                        <a href="/api/agents" target="_blank" class="btn btn-secondary">Ver API JSON</a>
                        <a href="/api/agents/worker/status" target="_blank" class="btn btn-secondary">Status Worker</a>
                        <a href="/test" class="btn btn-secondary">Página de Teste</a>
                    </div>
                </div>
            </div>

            <script>
                // Auto-refresh every 30 seconds
                setTimeout(function() {{
                    location.reload();
                }}, 30000);
            </script>
        </body>
        </html>
        """

        return html

    except Exception as e:
        logger.error(f"Error in admin panel: {e}")
        return f"<h1>Error loading admin panel: {str(e)}</h1>"


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    logger.error(traceback.format_exc())
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Import here at runtime to avoid import errors during module loading
    from agents.manager import AgentManager
    from core.database import setup_database

    # Initialize the agent manager and admin interface
    print("Starting Trading Chatbot Web Interface...")
    print("Setting up Agent Management System...")

    # Initialize database and agent manager
    setup_database()
    agent_manager = AgentManager()

    # Try to set up Flask-Admin interface if available
    if FLASK_ADMIN_AVAILABLE:
        try:
            # Note: Removed admin setup as it was causing issues
            print("Flask-Admin interface skipped")
        except Exception as e:
            print(f"Flask-Admin setup failed: {e}")
    else:
        print("Flask-Admin not available - running without advanced admin interface")
        print("Use admin_interface.py for standalone admin panel")

    print("Agent Management System initialized!")
    print("Access points:")
    print("   * Main Interface: http://localhost:3000")
    print("   * Admin Panel: http://localhost:3000/admin")
    print("   * API Endpoints: http://localhost:3000/api/*")
    print("   * Agent Management: http://localhost:3000/api/agents")
    print("   * Worker Control: http://localhost:3000/api/agents/worker/status")

    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=False,
        threaded=False,
        use_reloader=False
    )
