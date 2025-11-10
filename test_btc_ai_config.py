"""
Teste de configuracao para BTC AI Agent v3.0.0
Valida API Key e faz teste de chamada
"""

import os
from dotenv import load_dotenv

print("="*80)
print("TESTE DE CONFIGURACAO - BTC AI AGENT v3.0.0")
print("="*80)

# Carregar .env
load_dotenv()

print("\n[1] VERIFICANDO VARIAVEIS DE AMBIENTE")
print("-"*80)

ai_provider = os.getenv('AI_PROVIDER', 'N/A')
api_key = os.getenv('ANTHROPIC_API_KEY', 'N/A')
ai_model = os.getenv('AI_MODEL', 'N/A')
max_tokens = os.getenv('AI_MAX_TOKENS', 'N/A')
temperature = os.getenv('AI_TEMPERATURE', 'N/A')

print(f"AI_PROVIDER: {ai_provider}")
print(f"AI_MODEL: {ai_model}")
print(f"AI_MAX_TOKENS: {max_tokens}")
print(f"AI_TEMPERATURE: {temperature}")

# Verificar API Key
if api_key == 'N/A' or api_key == 'your_anthropic_api_key_here':
    print(f"\n[FALHA] ANTHROPIC_API_KEY nao configurada!")
    print("Configure no arquivo .env:")
    print("  ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXX")
    print("\nObtenha em: https://console.anthropic.com/")
    exit(1)
else:
    # Mascarar chave
    masked_key = api_key[:12] + "..." + api_key[-4:]
    print(f"ANTHROPIC_API_KEY: {masked_key} [OK]")

print("\n[2] TESTANDO CONEXAO COM ANTHROPIC")
print("-"*80)

try:
    from anthropic import Anthropic

    print("Importando biblioteca anthropic... [OK]")

    client = Anthropic(api_key=api_key)
    print(f"Cliente Anthropic criado... [OK]")

    print(f"Enviando mensagem de teste para {ai_model}...")

    message = client.messages.create(
        model=ai_model,
        max_tokens=50,
        messages=[
            {"role": "user", "content": "Responda apenas: OK"}
        ]
    )

    response = message.content[0].text
    print(f"Resposta recebida: '{response}' [OK]")

    print("\n[OK] TESTE COMPLETO COM SUCESSO!")
    print("-"*80)
    print("Configuracao validada. BTC AI Agent pronto para uso!")

    # Calcular custo estimado
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens

    # Haiku pricing (aproximado)
    input_cost = (input_tokens / 1_000_000) * 0.25
    output_cost = (output_tokens / 1_000_000) * 1.25
    total_cost = input_cost + output_cost

    print(f"\nCUSTO DO TESTE:")
    print(f"  Input tokens: {input_tokens}")
    print(f"  Output tokens: {output_tokens}")
    print(f"  Custo total: ${total_cost:.6f}")

    print(f"\nCUSTO ESTIMADO POR TRADE:")
    print(f"  ~500 tokens/analise")
    print(f"  ~$0.001 por trade")
    print(f"  100 trades/dia = $0.10/dia = $3/mes")

except ImportError:
    print("\n[FALHA] Biblioteca 'anthropic' nao instalada")
    print("Instale com:")
    print("  pip install anthropic")
    print("  OU")
    print("  uv pip install anthropic")
    exit(1)

except Exception as e:
    print(f"\n[FALHA] Erro ao conectar com Anthropic:")
    print(f"  {e}")
    print("\nVerifique:")
    print("  1. API Key esta correta")
    print("  2. Tem creditos na conta Anthropic")
    print("  3. Internet esta funcionando")
    exit(1)

print("\n" + "="*80)
print("PROXIMO PASSO: Execute o agente com RUN_BTC_AI.bat")
print("="*80)
