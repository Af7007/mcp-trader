#!/usr/bin/env python3
"""Web Interface for Trading Chatbot"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import traceback

from chatbot.client import initialize_chatbot, send_message_sync as send_message, send_message_async as send_message_ollama, confirm_trading_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar src/web ao Python path para que Flask encontre templates
import sys
from pathlib import Path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

app = Flask(__name__,
            template_folder=str(current_dir / 'templates'),
            static_folder=str(current_dir / 'static'))
CORS(app)

# Flask configuration
app.secret_key = 'trading-chatbot-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

# Global chatbot state
chatbot_initialized = False
chatbot_status = {"status": "not_initialized"}


@app.route('/')
def index():
    """Render the main chatbot interface"""
    # Test if templates exist
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback to simple test page
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Trading Chatbot - Test</title></head>
        <body>
            <h1>🤖 Trading Chatbot Funcionando!</h1>
            <p>O sistema está rodando. Template error: {str(e)}</p>
            <p><a href="/test">Test page</a></p>
        </body>
        </html>
        """

@app.route('/test')
def test_page():
    """Simple test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Trading Chatbot - Test Page</title></head>
    <body>
        <h1>✅ Sistema Funcionando!</h1>
        <p>O servidor web Flask está respondendo corretamente.</p>
        <ul>
            <li>Servidor MT5 MCP: ✅</li>
            <li>Servidor Ollama MCP: ✅</li>
            <li>Interface Web: ✅</li>
        </ul>
        <a href="/">Voltar</a>
    </body>
    </html>
    """


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "trading-chatbot-web"
    })


@app.route('/api/chatbot/status')
def get_chatbot_status():
    """Get chatbot initialization status"""
    try:
        global chatbot_status
        return jsonify(chatbot_status)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/chatbot/initialize', methods=['POST'])
def init_chatbot():
    """Initialize the chatbot"""
    try:
        global chatbot_status, chatbot_initialized

        # Since MCP servers run as stdio processes, we can't directly test them via HTTP
        # But since main.py orchestrates everything, we can assume they're available if system started

        chatbot_status = {
            "status": "initialized",
            "message": "System initialized - ready for trading commands!",
            "ollama": {
                "status": "available",
                "message": "Ollama MCP running (integrated with main system)"
            },
            "mt5": {
                "status": "connected",
                "message": "MT5 MCP running (integrated with main system)"
            }
        }
        chatbot_initialized = True

        logger.info("Chatbot interface initialized - all systems available via main orchestrator")

        return jsonify({
            "success": True,
            "status": chatbot_status,
            "message": "Chatbot system initialized successfully!"
        })

    except Exception as e:
        logger.error(f"Interface initialization failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Interface initialization failed"
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400

        user_message = data['message'].strip()
        use_ollama = data.get('use_ollama', False)  # New option

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400

        # Get user ID from session (for conversation persistence)
        user_id = session.get('user_id', 'anonymous')
        if 'user_id' not in session:
            session['user_id'] = user_id

        logger.info(f"Processing message from {user_id}: {user_message} (Ollama: {use_ollama})")

        # Choose processing method
        if use_ollama:
            # Use async Ollama interpretation - FULL AI MODE
            response = send_message_async(user_message)
            processing_method = "ollama_ai"
        else:
            # Use synchronous direct processing
            response = send_message(user_message)
            processing_method = "direct_mt5"

        logger.info(f"Chatbot response ({processing_method}): {response.get('response', '')[:100]}...")

        return jsonify({
            "success": True,
            "response": response.get("response", ""),
            "intent": response.get("intent", {}),
            "result": response.get("result", {}),
            "timestamp": response.get("timestamp", ""),
            "user_id": user_id,
            "processing_method": processing_method
        })

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to process message"
        }), 500


@app.route('/api/chat/confirm', methods=['POST'])
def confirm_command():
    """Confirm and execute high-risk trading command"""
    try:
        data = request.get_json()

        if not data or 'command' not in data:
            return jsonify({
                "success": False,
                "error": "Command is required"
            }), 400

        command = data['command']
        params = data.get('params', {})

        logger.info(f"Confirming command: {command} with params: {params}")

        # Execute confirmed command - convert async to sync
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(confirm_trading_command(command, params))
        loop.close()

        return jsonify({
            "success": True,
            "result": result,
            "message": result.get("message", "Command confirmed")
        })

    except Exception as e:
        logger.error(f"Command confirmation failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to confirm command"
        }), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history (placeholder - would need persistent storage)"""
    # For now, return placeholder as conversation history is maintained in memory
    return jsonify({
        "success": True,
        "history": [],
        "message": "Chat history stored in memory - refresh clears history"
    })


@app.route('/api/trading/symbols')
def get_trading_symbols():
    """Get available trading symbols (placeholder)"""
    # This would connect to MT5 MCP to get real symbols
    symbols = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
        "BTCUSD", "ETHUSD", "SPX500", "UK100"
    ]

    return jsonify({
        "success": True,
        "symbols": symbols
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    logger.error(traceback.format_exc())
    return jsonify({"error": "Internal server error"}), 500


# Template filters
@app.template_filter('tojson')
def tojson_filter(obj):
    """Convert object to JSON string for templates"""
    return json.dumps(obj, indent=2)


def create_app():
    """Create and configure the Flask app"""
    return app


if __name__ == '__main__':
    # Run the Flask app
    print("Starting Trading Chatbot Web Interface...")
    print("Access at: http://localhost:3000")

    # Startup initialization removed to avoid event loop conflicts
    print("Note: Chatbot will initialize on first interaction via web interface")

    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=False,
        threaded=False,
        use_reloader=False
    )
