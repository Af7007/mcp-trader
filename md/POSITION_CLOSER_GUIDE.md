# 🔒 MT5 Position Closer - Guia de Uso

## O que é?

**MT5PositionCloser** é uma classe robusta para fechar posições no MT5 com:
- ✅ Retry automático (até 3 tentativas)
- ✅ Tratamento de erros
- ✅ Logging detalhado
- ✅ Suporte a FOK e IOC

---

## 📍 Localização

```
src/core/mt5_position_closer.py
```

---

## 🎯 Como Usar

### 1️⃣ Importar

```python
from src.core.mt5_position_closer import MT5PositionCloser
import MetaTrader5 as mt5

mt5.initialize()
closer = MT5PositionCloser(max_retries=3, retry_delay=0.5)
```

### 2️⃣ Fechar Posição Específica

```python
result = closer.close_position(
    ticket=105654221,
    comment="Fechamento automático"
)

if result['success']:
    print(f"✅ Posição fechada! Novo ticket: {result['order']}")
else:
    print(f"❌ Erro: {result['message']}")
```

### 3️⃣ Fechar Todas as Posições

```python
result = closer.close_all_positions(comment="Limpeza do sistema")

print(f"Total: {result['total']}")
print(f"Fechadas: {result['closed']}")
print(f"Falhadas: {result['failed']}")
```

---

## 📊 Retorno

### close_position()

```python
{
    'success': bool,      # True se fechou com sucesso
    'message': str,       # Mensagem de resultado
    'order': int or None  # Número do novo ticket
}
```

### close_all_positions()

```python
{
    'total': int,   # Total de posições encontradas
    'closed': int,  # Posições fechadas com sucesso
    'failed': int   # Posições que falharam
}
```

---

## 🔧 Configuração

```python
closer = MT5PositionCloser(
    max_retries=3,      # Número de tentativas
    retry_delay=0.5     # Delay entre tentativas (segundos)
)
```

---

## 🧪 Testar

```powershell
python test_position_closer.py
```

---

## 🎯 Integração com Chatbot

### Comando: Fechar Posição

```
💬 Você: fechar 105654221
   ✅ Posição fechada!
      Novo ticket: 105654872

💬 Você: fechar tudo
   ✅ Todas as posições fechadas!
      Total: 3
      Fechadas: 3
      Falhadas: 0
```

---

## 🔍 Como Funciona

### Algoritmo de Fechamento

```
1. Obter posição pelo ticket
2. Se não encontrou → erro
3. Obter preço atual
4. Determinar tipo de ordem (oposto ao tipo da posição)
5. Criar requisição de fechamento
6. Enviar ordem com IOC (Immediate or Cancel)
7. Se falhar → tentar com FOK (Fill or Kill)
8. Se ainda falhar → retry até max_retries
```

### Tratamento de Erros

```
✅ TRADE_RETCODE_DONE
   → Posição fechada com sucesso

⚠️  TRADE_RETCODE_PLACED
   → Ordem colocada mas não executada
   → Tentar novamente com FOK

❌ Outros retcodes
   → Falha, tentar novamente
   → Após max_retries → erro final
```

---

## 💡 Dicas

### 1. Sempre Verificar Resultado

```python
result = closer.close_position(ticket)
if result['success']:
    # Sucesso
else:
    # Falha - verificar result['message']
```

### 2. Usar Retry Apropriado

```python
# Para operações críticas
closer = MT5PositionCloser(max_retries=5, retry_delay=1.0)

# Para operações rápidas
closer = MT5PositionCloser(max_retries=1, retry_delay=0.1)
```

### 3. Logging Detalhado

```python
import logging
logging.basicConfig(level=logging.INFO)
# Agora verá todos os detalhes do fechamento
```

---

## 🆘 Troubleshooting

### Problema: order_send retorna None

**Causa:** Erro de configuração ou símbolo não selecionado

**Solução:**
```python
# Garantir que símbolo está selecionado
mt5.symbol_select(symbol, True)

# Usar retry maior
closer = MT5PositionCloser(max_retries=5)
```

### Problema: Ordem colocada mas não executada

**Causa:** Preço fora do intervalo permitido

**Solução:**
```python
# Aumentar desvio
request["deviation"] = 200  # Aumentar de 100

# Usar FOK em vez de IOC
request["type_filling"] = mt5.ORDER_FILLING_FOK
```

### Problema: Nível de margem baixo

**Causa:** Saldo insuficiente

**Solução:**
```python
# Verificar margem
account = mt5.account_info()
if account.margin_free < 100:
    print("Margem insuficiente!")
```

---

## 📈 Exemplo Completo

```python
import MetaTrader5 as mt5
from src.core.mt5_position_closer import MT5PositionCloser

# Conectar
mt5.initialize()

# Criar closer
closer = MT5PositionCloser(max_retries=3, retry_delay=0.5)

# Obter posições
positions = mt5.positions_get()

if positions:
    print(f"Encontradas {len(positions)} posição(ões)")
    
    # Fechar cada uma
    for pos in positions:
        result = closer.close_position(pos.ticket)
        
        if result['success']:
            print(f"✅ #{pos.ticket} fechada")
        else:
            print(f"❌ #{pos.ticket} falhou: {result['message']}")
else:
    print("Nenhuma posição aberta")

mt5.shutdown()
```

---

## 🚀 Próximos Passos

1. ✅ Integrar com chatbot
2. ✅ Adicionar comando "fechar tudo"
3. ✅ Adicionar persistência em BD
4. ✅ Adicionar sincronização automática

---

**MT5PositionCloser 100% Funcional!** ✅
