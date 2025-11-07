# 🔧 Troubleshooting - Integração Chatbot ↔ MT5

## 🚨 Erro: "Não foi possível conectar ao servidor MT5"

### Sintomas
```
❌ Falha na conexão com MT5: Não foi possível conectar ao servidor MT5 após 3 tentativas
```

### Causas Possíveis

1. **MT5 MCP Server não está rodando**
2. **MT5 Terminal não está rodando ou não está logado**
3. **Porta 8000 está bloqueada ou em uso**
4. **Firewall bloqueando a conexão**

### Solução Passo a Passo

#### Passo 1: Verificar Diagnóstico
```bash
python diagnose_system.py
```

Procure por:
- ✅ MT5 Terminal está RODANDO e LOGADO
- ✅ MT5 MCP Server está RODANDO

#### Passo 2: Iniciar MT5 Terminal
Se o diagnóstico mostrar que MT5 não está rodando:

1. Abra o **MetaTrader 5**
2. Faça **login** com suas credenciais
3. Aguarde até que a plataforma esteja completamente carregada

#### Passo 3: Iniciar MT5 MCP Server
```bash
python src/mcp_mt5/main.py
```

Você deve ver:
```
INFO - MT5 MCP Server iniciado
INFO - Listening on http://localhost:8000
```

#### Passo 4: Testar Conexão
```bash
# Teste 1: Verificar se o servidor está respondendo
curl http://localhost:8000/mcp

# Teste 2: Executar testes de integração
python test_chatbot_mt5_integration.py
```

### Verificação Rápida

```python
import requests

# Verificar se servidor está rodando
try:
    response = requests.get("http://localhost:8000/mcp", timeout=5)
    print("✅ Servidor MT5 MCP está rodando")
except:
    print("❌ Servidor MT5 MCP NÃO está rodando")
```

---

## 🚨 Erro: "Símbolo não encontrado"

### Sintomas
```
❌ Símbolo 'EURUSD' não disponível neste broker
```

### Causas Possíveis

1. **Símbolo não está disponível no broker**
2. **Grafia incorreta do símbolo**
3. **Símbolo não está adicionado ao Market Watch**

### Solução

#### Opção 1: Validar Símbolo
```python
from chatbot.mt5_integration import ChatbotMT5Integration

integration = ChatbotMT5Integration()
is_valid = await integration.validate_symbol("EURUSD")
print(f"EURUSD válido: {is_valid}")
```

#### Opção 2: Listar Símbolos Disponíveis
```python
from core.mt5_connector import MT5Connector
import MetaTrader5 as mt5

if mt5.initialize():
    symbols = mt5.symbols_get()
    print("Símbolos disponíveis:")
    for symbol in symbols[:20]:  # Primeiros 20
        print(f"  • {symbol.name}")
    mt5.shutdown()
```

#### Opção 3: Adicionar Símbolo ao Market Watch
1. Abra **MetaTrader 5**
2. Vá para **Market Watch**
3. Clique com botão direito e selecione **Símbolos**
4. Procure pelo símbolo desejado
5. Clique em **Mostrar** para adicioná-lo

---

## 🚨 Erro: "Ordem rejeitada"

### Sintomas
```
❌ Ordem SELL falhou: Insufficient balance
```

### Causas Possíveis

1. **Saldo insuficiente**
2. **Volume muito grande**
3. **Símbolo não está em horário de negociação**
4. **Posições conflitantes**
5. **Margem insuficiente**

### Solução

#### Passo 1: Verificar Saldo
```python
integration = ChatbotMT5Integration()
account = await integration.get_account_summary()

print(f"Saldo: ${account['balance']:.2f}")
print(f"Margem Livre: ${account['margin_free']:.2f}")
print(f"Nível de Margem: {account['margin_level']:.2f}%")
```

#### Passo 2: Verificar Volume Mínimo/Máximo
```python
from core.mt5_connector import MT5Connector

connector = MT5Connector()
symbol_info = connector.get_symbol_info("EURUSD")

print(f"Volume Mínimo: {symbol_info.get('volume_min')}")
print(f"Volume Máximo: {symbol_info.get('volume_max')}")
print(f"Passo de Volume: {symbol_info.get('volume_step')}")
```

#### Passo 3: Verificar Horário de Negociação
```python
import MetaTrader5 as mt5
from datetime import datetime

if mt5.initialize():
    symbol_info = mt5.symbol_info("EURUSD")
    
    # Verificar se símbolo está selecionado
    if not symbol_info.visible:
        print("⚠️  Símbolo não está visível no Market Watch")
    
    # Verificar horário de negociação
    print(f"Horário de Negociação: {symbol_info.trade_mode}")
    
    mt5.shutdown()
```

#### Passo 4: Usar Volume Menor
```python
# Tentar com volume menor
result = await integration.execute_buy_order(
    symbol="EURUSD",
    volume=0.01,  # Reduzir de 0.1 para 0.01
    sl=1.0800,
    tp=1.0950
)
```

---

## 🚨 Erro: "Timeout na conexão"

### Sintomas
```
❌ Timeout após 3 tentativas
```

### Causas Possíveis

1. **Servidor MT5 MCP está lento**
2. **Conexão de rede instável**
3. **Firewall bloqueando**
4. **Porta 8000 congestionada**

### Solução

#### Opção 1: Aumentar Timeout
```python
from core.mt5_connector import MT5Connector

connector = MT5Connector(
    server_url="http://localhost:8000",
    timeout=60,  # Aumentar de 30 para 60 segundos
    max_retries=5,  # Aumentar tentativas
    retry_delay=2.0  # Aumentar delay entre tentativas
)
```

#### Opção 2: Reiniciar Servidor
```bash
# Parar o servidor (Ctrl+C)
# Aguardar 5 segundos
# Reiniciar
python src/mcp_mt5/main.py
```

#### Opção 3: Verificar Conexão de Rede
```bash
# Testar conectividade
ping localhost
ping 127.0.0.1

# Testar porta 8000
netstat -an | findstr 8000
```

---

## 🚨 Erro: "Ollama Service não está rodando"

### Sintomas
```
❌ Ollama Service NÃO ESTÁ RODANDO
```

### Solução

#### Passo 1: Instalar Ollama
1. Visite https://ollama.ai
2. Baixe e instale para seu SO
3. Aguarde a instalação completar

#### Passo 2: Iniciar Ollama
```bash
ollama serve
```

Você deve ver:
```
Ollama is running on 127.0.0.1:11434
```

#### Passo 3: Puxar Modelos (Opcional)
```bash
# Puxar modelo Llama
ollama pull llama2

# Puxar modelo Qwen
ollama pull qwen2.5-coder
```

---

## 🚨 Erro: "Web Interface não está rodando"

### Sintomas
```
❌ Web Interface NÃO ESTÁ RODANDO
```

### Solução

#### Passo 1: Iniciar Web Server
```bash
python src/web/app.py
```

Você deve ver:
```
Running on http://127.0.0.1:3000
```

#### Passo 2: Acessar Interface
Abra seu navegador e vá para:
```
http://localhost:3000
```

#### Passo 3: Se Porta 3000 Estiver em Uso
```bash
# Encontrar processo usando porta 3000
netstat -ano | findstr :3000

# Matar processo (substitua PID)
taskkill /PID <PID> /F

# Ou usar porta diferente
python src/web/app.py --port 3001
```

---

## 🚨 Erro: "Banco de dados bloqueado"

### Sintomas
```
❌ database is locked
```

### Causas Possíveis

1. **Múltiplas instâncias acessando o banco**
2. **Processo anterior não foi encerrado**
3. **Arquivo de lock não foi removido**

### Solução

#### Opção 1: Remover Arquivo de Lock
```bash
# Remover arquivo de lock
del trading_bot.db-journal
del trading_bot.db-wal
del trading_bot.db-shm
```

#### Opção 2: Encerrar Processos Python
```bash
# Listar processos Python
tasklist | findstr python.exe

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

#### Opção 3: Reconstruir Banco de Dados
```bash
# Backup do banco atual
ren trading_bot.db trading_bot.db.backup

# Banco será recriado automaticamente
python test_chatbot_mt5_integration.py
```

---

## 🚨 Erro: "MetaTrader5 Python API não instalada"

### Sintomas
```
❌ ModuleNotFoundError: No module named 'MetaTrader5'
```

### Solução

```bash
# Instalar MetaTrader5
pip install MetaTrader5

# Verificar instalação
python -c "import MetaTrader5; print('OK')"
```

---

## 🚨 Erro: "Porta já está em uso"

### Sintomas
```
❌ Address already in use: ('127.0.0.1', 8000)
```

### Solução

#### Opção 1: Encontrar e Matar Processo
```bash
# Encontrar processo usando porta 8000
netstat -ano | findstr :8000

# Matar processo (substitua PID)
taskkill /PID <PID> /F
```

#### Opção 2: Aguardar Liberação
```bash
# Aguardar 30 segundos e tentar novamente
timeout 30
python src/mcp_mt5/main.py
```

#### Opção 3: Usar Porta Diferente
```bash
# Modificar arquivo de configuração
# Editar src/mcp_mt5/main.py e alterar porta
```

---

## 📋 Checklist de Troubleshooting

Use este checklist para resolver problemas:

- [ ] Executar `python diagnose_system.py`
- [ ] Verificar se MT5 Terminal está rodando
- [ ] Verificar se MT5 Terminal está logado
- [ ] Verificar se MT5 MCP Server está rodando (porta 8000)
- [ ] Verificar se Ollama Service está rodando (porta 11434)
- [ ] Verificar se Web Interface está rodando (porta 3000)
- [ ] Verificar se banco de dados existe
- [ ] Verificar se pacotes Python estão instalados
- [ ] Executar `python test_chatbot_mt5_integration.py`
- [ ] Verificar logs para mensagens de erro

---

## 🆘 Ainda Não Funciona?

### Coletar Informações de Debug

```bash
# 1. Executar diagnóstico
python diagnose_system.py > diagnostico.txt

# 2. Executar testes
python test_chatbot_mt5_integration.py > testes.txt

# 3. Verificar logs
type trading_bot.log

# 4. Compartilhar arquivos
# Envie: diagnostico.txt, testes.txt, trading_bot.log
```

### Recursos Úteis

- **Documentação MT5**: https://www.mql5.com/en/docs/integration/python_metatrader5
- **Documentação FastMCP**: https://github.com/jlopp/fastmcp
- **Issues do Projeto**: Abra uma issue no repositório
- **Logs**: Verifique `trading_bot.log` para detalhes

---

## 💡 Dicas Gerais

1. **Sempre verificar diagnóstico primeiro**
   ```bash
   python diagnose_system.py
   ```

2. **Manter logs detalhados**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Testar componentes isoladamente**
   ```bash
   python test_chatbot_mt5_integration.py
   ```

4. **Usar exemplos como referência**
   ```bash
   python example_chatbot_mt5_usage.py
   ```

5. **Reiniciar quando necessário**
   - Reiniciar MT5
   - Reiniciar servidores MCP
   - Reiniciar computador (último recurso)

---

**Última atualização**: 2024-01-15  
**Versão**: 1.0.0
