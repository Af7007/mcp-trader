#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar configuracao e recomendar versao ideal
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_config():
    """Verifica configuracao do .env"""
    load_dotenv()

    print("=" * 60)
    print("VALIDACAO DE CONFIGURACAO")
    print("=" * 60)
    print()

    # Verificar API Key
    api_key = os.getenv('ANTHROPIC_API_KEY', 'your_anthropic_api_key_here')
    has_api = api_key != 'your_anthropic_api_key_here' and len(api_key) > 20

    if has_api:
        print("[OK] ANTHROPIC_API_KEY configurada")
        print(f"     Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"     Model: {os.getenv('AI_MODEL', 'claude-3-5-haiku-20241022')}")
    else:
        print("[AVISO] ANTHROPIC_API_KEY nao configurada")
        print("        IA nao funcionara (usara fallback tecnico)")

    print()
    return has_api

def check_files():
    """Verifica se arquivos existem"""
    print("=" * 60)
    print("ARQUIVOS DISPONIVEIS")
    print("=" * 60)
    print()

    files = {
        'Gold v2.0.0': 'src/agents/gold_loss_zero_simple.py',
        'BTC v2.0.0 (Tecnico)': 'src/agents/btc_loss_zero_v2.py',
        'BTC v3.0.0 (IA)': 'src/agents/btc_ai_agent.py',
    }

    available = {}
    for name, path in files.items():
        exists = Path(path).exists()
        status = "[OK]" if exists else "[FALTA]"
        print(f"{status} {name}")
        print(f"     {path}")
        available[name] = exists

    print()
    return available

def recommend_version(has_api, available):
    """Recomenda versao baseado em configuracao"""
    print("=" * 60)
    print("RECOMENDACAO")
    print("=" * 60)
    print()

    if not available.get('Gold v2.0.0'):
        print("[ERRO] Arquivo gold_loss_zero_simple.py nao encontrado!")
        return

    print("Versoes Recomendadas:")
    print()

    # Sempre recomendar Gold v2.0.0
    print("1. GOLD v2.0.0 (Tecnico) - RECOMENDADO PARA COMECAR")
    print("   - Custo: $0/mes")
    print("   - Win Rate Esperado: 60-65%")
    print("   - Executar: RUN_GOLD_AGENT.bat")
    print("   - Use: Comece aqui! Teste 20-30 trades")
    print()

    # BTC v2.0.0 se disponivel
    if available.get('BTC v2.0.0 (Tecnico)'):
        print("2. BTC v2.0.0 (Tecnico) - ALTERNATIVA AO GOLD")
        print("   - Custo: $0/mes")
        print("   - Win Rate Esperado: 60-65%")
        print("   - Executar: RUN_BTC_V2.bat")
        print("   - Use: Se prefere BTC ao inves de Gold")
        print()

    # BTC v3.0.0 apenas se API configurada
    if available.get('BTC v3.0.0 (IA)'):
        if has_api:
            print("3. BTC v3.0.0 (IA) - EXPERIMENTAL")
            print("   - Custo: ~$3/mes")
            print("   - Win Rate Esperado: 65-70% (meta)")
            print("   - Executar: RUN_BTC_AI.bat")
            print("   - Use: Para testar IA vs Tecnico")
            print("   - [OK] API configurada - PRONTA PARA USAR")
        else:
            print("3. BTC v3.0.0 (IA) - NAO DISPONIVEL")
            print("   - Custo: ~$3/mes")
            print("   - Win Rate Esperado: 65-70% (meta)")
            print("   - [AVISO] API nao configurada")
            print("   - Para usar: Configure ANTHROPIC_API_KEY no .env")
            print("   - Guia: Ver QUICK_START_AI.md")
        print()

    print("-" * 60)
    print("SUGESTAO DE TESTE:")
    print("-" * 60)
    print()
    print("Fase 1 - Validar Gold (20-30 trades):")
    print("  RUN_GOLD_AGENT.bat")
    print()
    print("Fase 2 - Comparar com BTC Tecnico (20-30 trades):")
    print("  RUN_BTC_V2.bat")
    print()

    if has_api:
        print("Fase 3 - Testar IA vs Tecnico (20-30 trades cada):")
        print("  Terminal 1: RUN_BTC_V2.bat")
        print("  Terminal 2: RUN_BTC_AI.bat")
        print()
    else:
        print("Fase 3 - Para testar IA:")
        print("  1. Configure API Key (ver QUICK_START_AI.md)")
        print("  2. Execute: python test_btc_ai_config.py")
        print("  3. Execute: RUN_BTC_AI.bat")
        print()

def show_summary():
    """Mostra resumo final"""
    print("=" * 60)
    print("DOCUMENTACAO DISPONIVEL")
    print("=" * 60)
    print()

    docs = [
        ('VERSOES_DISPONIVEIS.md', 'Comparacao completa de todas versoes'),
        ('QUICK_START_AI.md', 'Configuracao rapida IA (5 min)'),
        ('CHANGELOG_V2.md', 'Historico de mudancas v2.0.x'),
        ('COMPARACAO_TECNICO_VS_IA.md', 'Tecnico vs IA detalhado'),
        ('GOLD_VS_BTC_V2_COMPARACAO.md', 'Gold vs BTC lado a lado'),
    ]

    for filename, desc in docs:
        if Path(filename).exists():
            print(f"[OK] {filename}")
            print(f"     {desc}")
        else:
            print(f"[FALTA] {filename}")

    print()

def main():
    print()
    print("*" * 60)
    print("VALIDACAO DE VERSOES - Gold e BTC Trading Bots")
    print("*" * 60)
    print()

    has_api = check_env_config()
    available = check_files()
    recommend_version(has_api, available)
    show_summary()

    print("=" * 60)
    print("PROXIMO PASSO")
    print("=" * 60)
    print()
    print("1. Escolha uma versao acima")
    print("2. Execute o comando .bat correspondente")
    print("3. Aguarde 20-30 trades")
    print("4. Analise resultados")
    print()
    print("Duvidas? Ver VERSOES_DISPONIVEIS.md")
    print()

if __name__ == '__main__':
    main()
