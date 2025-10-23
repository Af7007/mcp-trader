#!/usr/bin/env python3
"""
Servidor web ULTRA SIMPLES - apenas para testar se funciona
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
template_folder = project_root / 'src' / 'web' / 'templates'
static_folder = project_root / 'src' / 'web' / 'static'

# Create Flask app
app = Flask(
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder)
)
CORS(app)
app.secret_key = 'test-key'

@app.route('/')
def index():
    """Main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>Erro ao carregar template: {e}</h1><p>Template folder: {template_folder}</p>"

@app.route('/test')
def test():
    """Test page"""
    return """
    <html>
        <head><title>Teste OK</title></head>
        <body>
            <h1>✅ Servidor funcionando!</h1>
            <p>Port 3000 está respondendo corretamente</p>
            <p><a href="/">← Ir para o chatbot</a></p>
        </body>
    </html>
    """

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({"status": "ok", "message": "Servidor web rodando!"})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SERVIDOR WEB SIMPLES INICIANDO...")
    print("=" * 60)
    print("")
    print("🌐 Acesse: http://localhost:3000/test")
    print("🌐 Chatbot: http://localhost:3000")
    print("")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=3000,
        debug=True,
        threaded=True  # IMPORTANTE: permite múltiplas conexões
    )
