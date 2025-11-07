# Como Configurar Claude Haiku 4.5

## 🤖 Sobre o Claude 3.5 Haiku

Claude 3.5 Haiku é o modelo mais rápido e econômico da Anthropic, ideal para:
- Análises rápidas de mercado
- Decisões de trading em tempo real
- Processamento de grandes volumes de dados
- Respostas de baixa latência

**Modelo**: `claude-3-5-haiku-20241022`

---

## 📋 Pré-requisitos

1. **Conta Anthropic**: Crie em https://console.anthropic.com/
2. **API Key**: Gere sua chave de API no console
3. **Créditos**: Certifique-se de ter créditos disponíveis

---

## ⚙️ Configuração Passo a Passo

### 1. Obter API Key da Anthropic

1. Acesse: https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Vá em **API Keys**
4. Clique em **Create Key**
5. Copie a chave (começa com `sk-ant-...`)

### 2. Configurar o Arquivo .env

Abra o arquivo `.env` na raiz do projeto e adicione/edite:

```env
# AI Model Configuration
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_MODEL=claude-3-5-haiku-20241022
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.7
```

**Importante**: Substitua `sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxx` pela sua chave real!

### 3. Instalar Dependência (se necessário)

```bash
uv pip install anthropic
```

Ou adicione ao `pyproject.toml`:

```toml
dependencies = [
    # ... outras dependências
    "anthropic>=0.40.0",
]
```

E execute:

```bash
uv sync
```

---

## 🔧 Opções de Configuração

### AI_PROVIDER
Define qual provedor de AI usar.

**Opções**:
- `anthropic` - Usa Claude (Anthropic)
- `ollama` - Usa Ollama (local)

**Padrão**: `anthropic`

### ANTHROPIC_API_KEY
Sua chave de API da Anthropic.

**Formato**: `sk-ant-api03-...`

**Obter em**: https://console.anthropic.com/

### AI_MODEL
Modelo Claude a usar.

**Opções disponíveis**:
- `claude-3-5-haiku-20241022` (Mais rápido e econômico) ⭐
- `claude-3-5-sonnet-20241022` (Balanceado)
- `claude-3-opus-20240229` (Mais avançado)

**Padrão**: `claude-3-5-haiku-20241022`

### AI_MAX_TOKENS
Número máximo de tokens na resposta.

**Valores**:
- Mínimo: 1
- Máximo: 8192 (Haiku), 200000 (Sonnet/Opus)
- **Padrão**: 4096

**Recomendação**:
- Análises rápidas: 1024-2048
- Análises detalhadas: 4096-8192

### AI_TEMPERATURE
Controla a aleatoriedade das respostas.

**Valores**:
- `0.0` - Determinístico, sempre a mesma resposta
- `0.7` - Padrão, equilíbrio
- `1.0` - Mais criativo/variado

**Recomendação para Trading**: `0.5-0.7` (previsível mas não rígido)

---

## 🧪 Testar Configuração

Crie um script de teste `test_haiku.py`:

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def test_haiku():
    """Testa conexão com Claude Haiku."""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY não configurada no .env")
        return False

    if api_key == "your_anthropic_api_key_here":
        print("❌ Você precisa substituir a API key no .env")
        return False

    print(f"🔑 API Key encontrada: {api_key[:20]}...")

    try:
        client = Anthropic(api_key=api_key)

        print("\n📤 Enviando mensagem de teste para Claude Haiku...")

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Diga 'olá' e confirme que você é Claude 3.5 Haiku"
                }
            ]
        )

        response_text = message.content[0].text
        print(f"\n✅ Resposta recebida:")
        print(f"   {response_text}")
        print(f"\n📊 Uso de tokens: {message.usage.input_tokens} input, {message.usage.output_tokens} output")

        return True

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        return False

if __name__ == "__main__":
    success = test_haiku()
    exit(0 if success else 1)
```

Execute:

```bash
uv run python test_haiku.py
```

**Saída esperada**:
```
🔑 API Key encontrada: sk-ant-api03-abc123...

📤 Enviando mensagem de teste para Claude Haiku...

✅ Resposta recebida:
   Olá! Sim, sou Claude 3.5 Haiku, o modelo mais rápido da família Claude.

📊 Uso de tokens: 15 input, 18 output
```

---

## 💰 Custos do Claude Haiku

**Claude 3.5 Haiku** (Mais Econômico):
- **Input**: $0.25 por milhão de tokens (~$0.000000250 por token)
- **Output**: $1.25 por milhão de tokens (~$0.000001250 por token)

**Exemplo de custo**:
- 1 análise de mercado (~500 tokens input + 200 tokens output):
  - Input: 500 × $0.000000250 = $0.000125
  - Output: 200 × $0.000001250 = $0.000250
  - **Total**: ~$0.000375 (menos de 1 centavo)

- 1000 análises por dia: ~$0.375/dia ou ~$11.25/mês

**Comparação**:
- Haiku é **3x mais barato** que Sonnet
- Haiku é **20x mais barato** que Opus

---

## 🚀 Modelos Disponíveis

### Claude 3.5 Haiku (Recomendado para Trading)
```env
AI_MODEL=claude-3-5-haiku-20241022
```
- ⚡ **Velocidade**: Mais rápido (~1-2s)
- 💰 **Custo**: Mais barato
- 🎯 **Uso**: Análises rápidas, decisões em tempo real
- 📊 **Contexto**: 200K tokens

### Claude 3.5 Sonnet (Balanceado)
```env
AI_MODEL=claude-3-5-sonnet-20241022
```
- ⚡ **Velocidade**: Médio (~2-4s)
- 💰 **Custo**: Médio
- 🎯 **Uso**: Análises complexas, relatórios detalhados
- 📊 **Contexto**: 200K tokens

### Claude 3 Opus (Premium)
```env
AI_MODEL=claude-3-opus-20240229
```
- ⚡ **Velocidade**: Mais lento (~4-8s)
- 💰 **Custo**: Mais caro
- 🎯 **Uso**: Análises muito complexas, pesquisa profunda
- 📊 **Contexto**: 200K tokens

---

## 🔄 Alternar Entre Modelos

Para trocar de modelo, simplesmente edite o `.env`:

**Para Haiku** (rápido e econômico):
```env
AI_MODEL=claude-3-5-haiku-20241022
```

**Para Sonnet** (balanceado):
```env
AI_MODEL=claude-3-5-sonnet-20241022
```

**Para Opus** (premium):
```env
AI_MODEL=claude-3-opus-20240229
```

Reinicie o agente/serviço após mudar.

---

## 🔐 Segurança

### ⚠️ NUNCA FAÇA:
- ❌ Commit do `.env` com API key real
- ❌ Compartilhe sua API key publicamente
- ❌ Deixe a key em código-fonte

### ✅ SEMPRE FAÇA:
- ✅ Use `.env` (já está no .gitignore)
- ✅ Mantenha sua key em segredo
- ✅ Revogue keys comprometidas imediatamente
- ✅ Use `.env.example` para templates

### Revogar Key Comprometida:
1. Acesse https://console.anthropic.com/
2. Vá em **API Keys**
3. Clique em **Delete** na key comprometida
4. Gere uma nova key

---

## 📊 Monitoramento de Uso

Acompanhe seu uso em:
https://console.anthropic.com/settings/usage

Você pode ver:
- Total de tokens usados
- Custo acumulado
- Breakdown por modelo
- Histórico de uso

---

## ❓ Solução de Problemas

### Erro: "authentication_error"
**Problema**: API key inválida ou não configurada

**Solução**:
1. Verifique se `ANTHROPIC_API_KEY` está no `.env`
2. Confirme que a key está correta (começa com `sk-ant-`)
3. Verifique se há espaços extras antes/depois da key

### Erro: "rate_limit_error"
**Problema**: Muitas requisições em pouco tempo

**Solução**:
1. Aguarde alguns segundos
2. Implemente retry com backoff
3. Considere aumentar seu tier na Anthropic

### Erro: "insufficient_quota"
**Problema**: Sem créditos na conta

**Solução**:
1. Acesse https://console.anthropic.com/settings/billing
2. Adicione créditos à conta
3. Configure alertas de uso

### Modelo não encontrado
**Problema**: Nome do modelo incorreto

**Solução**:
1. Verifique se usou o nome completo: `claude-3-5-haiku-20241022`
2. Confirme que o modelo está disponível na sua região
3. Veja modelos disponíveis em: https://docs.anthropic.com/en/docs/models-overview

---

## 📚 Recursos

- **Documentação Anthropic**: https://docs.anthropic.com/
- **Console**: https://console.anthropic.com/
- **Pricing**: https://www.anthropic.com/pricing
- **API Reference**: https://docs.anthropic.com/en/api

---

## ✅ Checklist de Configuração

- [ ] Conta criada na Anthropic
- [ ] API key gerada
- [ ] API key adicionada ao `.env`
- [ ] Modelo configurado (Haiku)
- [ ] Dependência `anthropic` instalada
- [ ] Teste de conexão executado com sucesso
- [ ] Créditos disponíveis na conta

---

✅ **Configuração concluída! Claude 3.5 Haiku pronto para usar!**
