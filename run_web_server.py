#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Web Server for Gold Game
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    print("Iniciando servidor web...")
    
    try:
        from src.web.app import create_app
        
        app = create_app()
        
        print("Servidor rodando em: http://localhost:3000")
        print("Acesse: http://localhost:3000/game")
        print("Pressione Ctrl+C para parar")
        
        app.run(
            host='0.0.0.0', 
            port=3000, 
            debug=False,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
