# 🔧 Troubleshooting - Agentes e Posições

## ⚠️ Problema: Agente Não Aparece na Listagem

### Causa

1. **Agentes em Memória** - Armazenados apenas na RAM
   - Quando o chatbot fecha, agentes são perdidos
   - Não há persistência em banco de dados

2. **Posições Persistem** - Armazenadas no MT5
   - Posições abertas continuam mesmo sem agentes
   - Precisam ser fechadas manualmente

3. **Falta de Sincronização** - Agentes e posições desincronizados
   - Agente criado mas chatbot fechado
   - Posição aberta mas agente perdido

### Solução

#### 1️⃣ Diagnosticar Problema

```powershell
python diagnose_agents.py
```

Mostra:
- ✅ Posições abertas no MT5
- ✅ Agentes em memória
- ✅ Status do worker
- ✅ Recomendações

#### 2️⃣ Fechar Posições Órfãs

```powershell
python close_all_positions.py
```

Fecha todas as posições abertas no MT5.

#### 3️⃣ Sincronizar Sistema

```powershell
# Limpar tudo
python close_all_positions.py

# Reiniciar chatbot
python run_chatbot_manager.py

# Criar agentes novamente
💬 Você: criar agente XAUUSD com RSI, TP $3, SL $1, volume 0.1
💬 Você: iniciar worker
```

---

## 🎯 Melhores Práticas

### ✅ Fazer

```
1. Sempre iniciar worker antes de criar agentes
   💬 Você: iniciar worker
   💬 Você: criar agente EURUSD com RSI

2. Listar agentes antes de fechar
   💬 Você: listar agentes
   💬 Você: pausar agente <ID>

3. Pausar antes de deletar
   💬 Você: pausar agente <ID>
   💬 Você: deletar agente <ID>

4. Diagnosticar antes de fechar posições
   python diagnose_agents.py
   python close_all_positions.py
```

### ❌ Evitar

```
1. Fechar chatbot sem pausar agentes
   ❌ Agentes perdidos, posições órfãs

2. Criar agentes sem worker
   ❌ Agentes não monitoram

3. Fechar posições manualmente no MT5
   ❌ Agentes desincronizados

4. Deixar posições abertas
   ❌ Risco de prejuízo
```

---

## 📊 Estados Possíveis

### Estado Ideal

```
✅ Agentes em memória = Posições no MT5
✅ Worker rodando
✅ Agentes ativos
✅ Posições sincronizadas
```

### Estado Problemático

```
❌ Agentes em memória ≠ Posições no MT5
❌ Worker parado
❌ Posições órfãs
❌ Desincronização
```

---

## 🚀 Solução Permanente (Próxima Fase)

Para evitar esses problemas, implementaremos:

### 1. **Persistência em Banco de Dados**
```python
# Salvar agentes em SQLite
agents:
  id, name, symbol, strategy_config, status, created_at

agent_trades:
  id, agent_id, ticket, entry_price, exit_price, profit
```

### 2. **Sincronização Automática**
```python
# Ao iniciar, carregar agentes do DB
manager.load_agents_from_db()

# Ao criar, salvar no DB
manager.create_and_save_agent(command)

# Ao fechar, atualizar DB
manager.update_agent_status(agent_id, status)
```

### 3. **Validação de Posições**
```python
# Verificar se posições correspondem a agentes
orphaned = manager.find_orphaned_positions()

# Fechar posições órfãs automaticamente
manager.close_orphaned_positions()
```

### 4. **Recuperação de Falhas**
```python
# Se chatbot fecha, recuperar agentes
manager.recover_from_crash()

# Se worker falha, reiniciar
manager.restart_worker()
```

---

## 📝 Checklist de Sincronização

Antes de fechar o chatbot:

- [ ] Listar agentes: `listar agentes`
- [ ] Verificar posições: `resumo`
- [ ] Pausar agentes: `pausar agente <ID>`
- [ ] Parar worker: `parar worker`
- [ ] Fechar chatbot: `sair`

Ao reiniciar:

- [ ] Diagnosticar: `python diagnose_agents.py`
- [ ] Fechar órfãs: `python close_all_positions.py`
- [ ] Iniciar chatbot: `python run_chatbot_manager.py`
- [ ] Criar agentes: `criar agente ...`
- [ ] Iniciar worker: `iniciar worker`

---

## 🆘 Comandos de Emergência

### Fechar Todas as Posições

```powershell
python close_all_positions.py
```

### Diagnosticar Sistema

```powershell
python diagnose_agents.py
```

### Limpar Tudo

```powershell
# 1. Fechar posições
python close_all_positions.py

# 2. Reiniciar chatbot
python run_chatbot_manager.py

# 3. Criar agentes novamente
💬 Você: criar agente EURUSD com RSI
```

---

## 📞 Suporte

Se o problema persistir:

1. Execute `diagnose_agents.py`
2. Verifique posições abertas no MT5
3. Execute `close_all_positions.py`
4. Reinicie o chatbot
5. Crie agentes novamente

---

**Problema Resolvido! ✅**
