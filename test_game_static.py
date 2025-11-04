#!/usr/bin/env python3
"""Test static files for Gold Game"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from flask import Flask

# Setup Flask app
project_root = Path(__file__).parent
app = Flask(__name__, 
            static_folder=str(project_root / 'src' / 'web' / 'static'),
            template_folder=str(project_root / 'src' / 'web' / 'templates'))

print("\n" + "="*60)
print("GOLD GAME - Static Files Test")
print("="*60)

print(f"\nProject root: {project_root}")
print(f"Static folder: {app.static_folder}")
print(f"Template folder: {app.template_folder}")

# Check files
static_path = Path(app.static_folder)
template_path = Path(app.template_folder)

print(f"\n--- Static Folder ---")
print(f"Exists: {static_path.exists()}")
if static_path.exists():
    print(f"Contents: {list(static_path.iterdir())}")

print(f"\n--- CSS Folder ---")
css_path = static_path / 'css'
print(f"Exists: {css_path.exists()}")
if css_path.exists():
    print(f"Contents: {list(css_path.iterdir())}")
    
    game_css = css_path / 'game.css'
    print(f"\ngame.css exists: {game_css.exists()}")
    if game_css.exists():
        print(f"game.css size: {game_css.stat().st_size} bytes")

print(f"\n--- JS Folder ---")
js_path = static_path / 'js'
print(f"Exists: {js_path.exists()}")
if js_path.exists():
    print(f"Contents: {list(js_path.iterdir())}")
    
    game_js = js_path / 'game.js'
    print(f"\ngame.js exists: {game_js.exists()}")
    if game_js.exists():
        print(f"game.js size: {game_js.stat().st_size} bytes")

print(f"\n--- Template Folder ---")
print(f"Exists: {template_path.exists()}")
if template_path.exists():
    print(f"Contents: {list(template_path.iterdir())}")
    
    game_html = template_path / 'game.html'
    print(f"\ngame.html exists: {game_html.exists()}")
    if game_html.exists():
        print(f"game.html size: {game_html.stat().st_size} bytes")

print("\n" + "="*60)
print("Test URL paths:")
print("="*60)

with app.app_context():
    from flask import url_for
    try:
        print(f"CSS URL: {url_for('static', filename='css/game.css')}")
        print(f"JS URL: {url_for('static', filename='js/game.js')}")
        print(f"Manifest URL: {url_for('static', filename='manifest.json')}")
    except Exception as e:
        print(f"Error generating URLs: {e}")

print("\n" + "="*60)
