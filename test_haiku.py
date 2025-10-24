#!/usr/bin/env python3
"""
Testa conexão com Claude Haiku 4.5
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

def test_haiku():
    """Testa conexão com Claude Haiku."""
    print("="*60)
    print("🧪 TESTE DE CONEXÃO - CLAUDE HAIKU 4.5")
    print("="*60)
    print()

    # Verificar API key
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ERRO: ANTHROPIC_API_KEY não encontrada no .env")
        print()
        print("📝 Passos para corrigir:")
        print("   1. Abra o arquivo .env")
        print("   2. Adicione: ANTHROPIC_API_KEY=sua_key_aqui")
        print("   3. Obtenha sua key em: https://console.anthropic.com/")
        print()
        return False

    if api_key == "your_anthropic_api_key_here":
        print("❌ ERRO: API key ainda está com valor padrão")
        print()
        print("📝 Você precisa:")
        print("   1. Obter sua API key em: https://console.anthropic.com/")
        print("   2. Substituir 'your_anthropic_api_key_here' pela key real")
        print()
        return False

    print(f"🔑 API Key encontrada: {api_key[:20]}...")
    print()

    # Verificar se anthropic está instalado
    try:
        from anthropic import Anthropic
        print("✅ Módulo 'anthropic' instalado")
    except ImportError:
        print("❌ ERRO: Módulo 'anthropic' não instalado")
        print()
        print("📝 Para instalar:")
        print("   uv pip install anthropic")
        print()
        return False

    # Obter configurações
    model = os.getenv('AI_MODEL', 'claude-3-5-haiku-20241022')
    max_tokens = int(os.getenv('AI_MAX_TOKENS', '100'))
    temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))

    print(f"📊 Configurações:")
    print(f"   Modelo: {model}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Temperature: {temperature}")
    print()

    # Testar conexão
    try:
        client = Anthropic(api_key=api_key)

        print("📤 Enviando mensagem de teste...")
        print()

        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": "Diga 'olá' brevemente e confirme que você é Claude 3.5 Haiku. Seja conciso."
                }
            ]
        )

        response_text = message.content[0].text

        print("="*60)
        print("✅ RESPOSTA DO CLAUDE HAIKU:")
        print("="*60)
        print()
        print(response_text)
        print()
        print("="*60)
        print()

        # Exibir métricas
        print(f"📊 Métricas:")
        print(f"   Input tokens: {message.usage.input_tokens}")
        print(f"   Output tokens: {message.usage.output_tokens}")
        print(f"   Total tokens: {message.usage.input_tokens + message.usage.output_tokens}")
        print()

        # Calcular custo aproximado (Haiku pricing)
        input_cost = message.usage.input_tokens * 0.00000025  # $0.25 per 1M tokens
        output_cost = message.usage.output_tokens * 0.00000125  # $1.25 per 1M tokens
        total_cost = input_cost + output_cost

        print(f"💰 Custo estimado:")
        print(f"   Input: ${input_cost:.6f}")
        print(f"   Output: ${output_cost:.6f}")
        print(f"   Total: ${total_cost:.6f}")
        print()

        print("="*60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print()
        print("🎯 Claude 3.5 Haiku está configurado e funcionando!")
        print()

        return True

    except Exception as e:
        print("="*60)
        print("❌ ERRO AO CONECTAR COM A API")
        print("="*60)
        print()
        print(f"Erro: {str(e)}")
        print()

        # Ajuda baseada no erro
        error_str = str(e).lower()

        if "authentication" in error_str or "api_key" in error_str:
            print("💡 Possível solução:")
            print("   - Verifique se a API key está correta")
            print("   - Confirme que a key começa com 'sk-ant-'")
            print("   - Gere uma nova key em: https://console.anthropic.com/")
        elif "rate" in error_str:
            print("💡 Possível solução:")
            print("   - Você atingiu o limite de requisições")
            print("   - Aguarde alguns segundos e tente novamente")
        elif "quota" in error_str or "insufficient" in error_str:
            print("💡 Possível solução:")
            print("   - Sem créditos na conta")
            print("   - Adicione créditos em: https://console.anthropic.com/settings/billing")
        elif "model" in error_str:
            print("💡 Possível solução:")
            print("   - Verifique o nome do modelo no .env")
            print("   - Use: claude-3-5-haiku-20241022")

        print()
        return False

if __name__ == "__main__":
    success = test_haiku()
    sys.exit(0 if success else 1)
