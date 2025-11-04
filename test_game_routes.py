#!/usr/bin/env python3
"""Test Gold Game routes"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from web.app import app

print("\n" + "="*60)
print("GOLD GAME - Routes Test")
print("="*60)

print(f"\nFlask app name: {app.name}")
print(f"Static folder: {app.static_folder}")
print(f"Template folder: {app.template_folder}")

print(f"\n--- Registered Blueprints ---")
for name, blueprint in app.blueprints.items():
    print(f"  {name}: {blueprint}")

print(f"\n--- URL Rules ---")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint:30s} {rule.rule}")

print("\n" + "="*60)
print("Testing with test client...")
print("="*60)

with app.test_client() as client:
    # Test static CSS
    print("\n1. Testing CSS file...")
    response = client.get('/static/css/game.css')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")
    print(f"   Size: {len(response.data)} bytes")
    
    # Test static JS
    print("\n2. Testing JS file...")
    response = client.get('/static/js/game.js')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")
    print(f"   Size: {len(response.data)} bytes")
    
    # Test game page
    print("\n3. Testing /game route...")
    response = client.get('/game')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")
    print(f"   Size: {len(response.data)} bytes")
    if response.status_code != 200:
        print(f"   Error: {response.data.decode('utf-8')[:200]}")
    else:
        content = response.data.decode('utf-8')
        print(f"   Has CSS link: {'game.css' in content}")
        print(f"   Has JS script: {'game.js' in content}")

print("\n" + "="*60)
print("✓ Test completed!")
print("="*60 + "\n")
