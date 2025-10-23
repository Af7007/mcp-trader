#!/usr/bin/env python3
"""
Script simplificado para rodar APENAS o servidor web
sem inicializar MT5 ou Ollama MCP servers
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

if __name__ == '__main__':
    logger.info("🚀 Iniciando apenas o Web Server...")
    logger.info("=" * 60)

    try:
        # Import Flask app
        from flask import Flask
        from flask_cors import CORS

        # Create a minimal Flask app
        app = Flask(
            __name__,
            static_folder=str(project_root / 'src' / 'web' / 'static'),
            template_folder=str(project_root / 'src' / 'web' / 'templates')
        )
        CORS(app)
        app.secret_key = 'trading-chatbot-secret-key'

        # Import routes from web app
        from web.app import (
            index, health_check, test_page, chat, chatbot_status,
            admin_panel, get_agents, create_agent
        )

        # Register routes
        app.add_url_rule('/', 'index', index)
        app.add_url_rule('/test', 'test', test_page)
        app.add_url_rule('/admin', 'admin', admin_panel)
        app.add_url_rule('/api/health', 'health', health_check)
        app.add_url_rule('/api/chatbot/status', 'status', chatbot_status)
        app.add_url_rule('/api/chat', 'chat', chat, methods=['POST'])
        app.add_url_rule('/api/agents', 'agents', get_agents)
        app.add_url_rule('/api/agents/create', 'create', create_agent, methods=['POST'])

        logger.info("=" * 60)
        logger.info("✅ Web Server Iniciado com Sucesso!")
        logger.info("")
        logger.info("🌐 Acesse o chatbot em:")
        logger.info("   http://localhost:3000")
        logger.info("")
        logger.info("📋 Outras URLs:")
        logger.info("   http://localhost:3000/test   - Página de teste")
        logger.info("   http://localhost:3000/admin  - Painel admin")
        logger.info("")
        logger.info("⚠️  NOTA: MT5 e Ollama devem ser iniciados separadamente")
        logger.info("=" * 60)

        # Run Flask
        app.run(
            host='0.0.0.0',
            port=3000,
            debug=True,
            threaded=True,  # IMPORTANTE: threaded=True para suportar múltiplas requisições
            use_reloader=False
        )

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}", exc_info=True)
        sys.exit(1)
