#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold Loss Zero Game - Server Launcher
Inicia o servidor web com o jogo e o worker de trailing
"""

import sys
import os
import time
import logging
import shutil
import subprocess
import platform
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    print("\n" + "="*60)
    print("GOLD LOSS ZERO GAME - Server Launcher")
    print("="*60 + "\n")

    # NOTE: Para encerrar processos Python anteriores, use:
    # taskkill /F /IM python.exe (antes de rodar este script)

    # Clear Flask cache
    flask_cache = Path(__file__).parent / 'flask_session'
    if flask_cache.exists():
        shutil.rmtree(flask_cache)
        print("[OK] Flask session cache cleared")

    # Clear Python bytecode cache
    pycache_dirs = list(Path(__file__).parent.rglob('__pycache__'))
    for pycache in pycache_dirs:
        if pycache.exists():
            shutil.rmtree(pycache)
    print(f"[OK] Cleared {len(pycache_dirs)} __pycache__ directories")
    print("")

    # Import Flask app
    from web.app import app
    from web.game_api import GAME_STATE
    from web.game_worker import start_game_worker
    
    # Get magic number from game state
    magic_number = GAME_STATE['magic_number']
    
    print(f"Magic Number: {magic_number} (FIXO - Histórico Permanente)")
    print(f"Trailing Worker: ATIVO (a cada 0.5s)")
    print(f"\nAVISO: Use o Magic Number 777777 no MT5")
    print(f"   para que as trades apareçam no histórico!")
    print(f"\nRegras do Jogo v2.0 - TRAILING DINÂMICO:")
    print(f"  - Trailing ativa quando Lucro >= SL configurado")
    print(f"  - Proteção inicial: SL - $0.10 (98% do SL)")
    print(f"  - Sobe a cada $0.10 de lucro adicional")
    print(f"\nExemplos (SL=$5.00):")
    print(f"  Lucro $5.00 -> Protege $4.90")
    print(f"  Lucro $5.10 -> Protege $5.00 (breakeven)")
    print(f"  Lucro $5.20 -> Protege $5.10 (lucro garantido!)")
    print(f"  Lucro $5.50 -> Protege $5.40")
    print(f"\n" + "="*60)
    print(f"\nAcesse o jogo em: http://localhost:3000/game")
    print(f"\n" + "="*60 + "\n")
    
    # Start trailing worker with positions state
    try:
        start_game_worker(magic_number, positions_state=GAME_STATE['positions'])
        logger.info("✓ Trailing worker iniciado com lógica dinâmica")
        logger.info(f"✓ Magic Number: {magic_number}")
        logger.info(f"✓ Positions State Reference: {id(GAME_STATE['positions'])}")
    except Exception as e:
        logger.error(f"✗ Erro ao iniciar worker: {e}")
        import traceback
        traceback.print_exc()
    
    # Start Flask app
    try:
        app.run(host='0.0.0.0', port=3000, debug=True)  # Enable debug for template reloading
    except KeyboardInterrupt:
        print("\n\nServidor parado pelo usuário")
    except Exception as e:
        logger.error(f"Erro no servidor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
