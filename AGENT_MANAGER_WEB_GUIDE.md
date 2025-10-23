# Agent Manager Web Integration Guide

Este guia documenta as funcionalidades avançadas do Agent Manager integradas na interface web do Trading Chatbot.

## 🚀 Funcionalidades Implementadas

### ✅ **Interface Web Completa**
- **Agent Manager** integrado na sidebar da interface web
- **Monitoramento em tempo real** dos agentes
- **Controle visual** do worker de monitoramento
- **Operações em lote** (bulk operations)
- **Histórico detalhado** de eventos dos agentes
- **Estatísticas avançadas** com métricas completas

### ✅ **API Endpoints Avançados**
- `/api/agents` - Listar todos os agentes
- `/api/agents/create` - Criar novo agente
- `/api/agents/{id}/pause` - Pausar agente
- `/api/agents/{id}/resume` - Retomar agente
- `/api/agents/{id}/stop` - Parar agente
- `/api/agents/{id}/delete` - Deletar agente
- `/api/agents/{id}/stats` - Estatísticas do agente
- `/api/agents/{id}/history` - Histórico de eventos
- `/api/agents/worker/start` - Iniciar worker
- `/api/agents/worker/stop` - Parar worker
- `/api/agents/worker/toggle` - Alternar worker
- `/api/agents/bulk/pause` - Pausar todos os agentes
- `/api/agents/bulk/resume` - Retomar todos os agentes
- `/api/agents/bulk/stop` - Parar todos os agentes
- `/api/agents/stats/all` - Estatísticas de todos os agentes
- `/api/agents/summary` - Resumo do sistema

## 🎯 Como Usar

### **1. Acessar a Interface Web**
```bash
# Iniciar o sistema completo
python main.py

# Ou iniciar apenas a interface web
python src/web/app.py
```

Acesse: **http://localhost:3000**

### **2. Criar um Agente**
1. Na sidebar, clique em **"Criar Novo Agente"**
2. Digite um comando como: `"criar agente EURUSD com RSI"`
3. O agente será criado automaticamente com as configurações detectadas

### **3. Gerenciar Agentes**
Cada agente na lista tem botões para:
- **⏸️ Pausar** - Pausar temporariamente o agente
- **▶️ Retomar** - Continuar execução do agente
- **⏹️ Parar** - Parar completamente o agente
- **📜 Histórico** - Ver histórico de eventos
- **🗑️ Deletar** - Remover o agente

### **4. Controle do Worker**
- **Worker Status** mostra se o sistema de monitoramento está ativo
- Clique no botão para **Iniciar/Parar** o worker
- O worker monitora agentes a cada 30 segundos por padrão

### **5. Operações em Lote**
- **Pausar Todos** - Pausa todos os agentes ativos
- **Retomar Todos** - Retoma todos os agentes pausados
- **Parar Todos** - Para todos os agentes
- **Atualizar** - Recarrega todos os dados

### **6. Ver Estatísticas**
- Clique em **"Ver Estatísticas"** para ver métricas detalhadas
- Informações incluem: trades, lucro, uptime, erros, indicadores

### **7. Histórico de Eventos**
- Clique no botão **📜** de qualquer agente para ver seu histórico
- Mostra todos os eventos: criação, trades, erros, mudanças de status

## 🔧 Comandos de Exemplo

### **Criar Agentes**
```
"criar agente EURUSD com RSI"
"criar agente XAUUSD com Bollinger Bands"
"criar agente BTCUSD com MACD e RSI"
"criar agente GBPUSD com RSI, TP $2, SL $1, volume 0.1"
```

### **Chat Commands**
```
"listar agentes" - Ver todos os agentes
"pausar agente <ID>" - Pausar agente específico
"retomar agente <ID>" - Retomar agente específico
"parar agente <ID>" - Parar agente específico
"deletar agente <ID>" - Deletar agente específico
"stats agente <ID>" - Ver estatísticas do agente
"resumo" - Ver resumo do sistema
"iniciar worker" - Iniciar monitoramento
"parar worker" - Parar monitoramento
```

## 📊 Interface Visual

### **Status dos Agentes**
- 🟢 **Verde**: Agente ativo e funcionando
- 🟡 **Amarelo**: Agente pausado
- 🔴 **Vermelho**: Agente parado
- ❌ **Vermelho escuro**: Agente com erro

### **Indicadores de Status**
- **Pontos coloridos** mostram status em tempo real
- **Animações** indicam atividade (pulse para worker ativo)
- **Contadores** mostram número total de agentes

### **Resumo do Sistema**
```
🤖 Total: 5
🟢 Ativos: 3
🟡 Pausados: 1
🔴 Parados: 1
📊 Trades: 25
💰 Lucro: $125.50
⚙️ Worker: 🟢 Rodando
```

## 🧪 Testar as Funcionalidades

### **Script de Teste**
```bash
# Testar todas as funcionalidades
python test_agent_manager_web.py

# Testar funcionalidade específica
python test_agent_manager_web.py --test health
python test_agent_manager_web.py --test agents
python test_agent_manager_web.py --test worker
```

### **Testes Disponíveis**
- `health` - Verificar se o servidor está respondendo
- `init` - Testar inicialização do chatbot
- `agents` - Testar listagem de agentes
- `create` - Testar criação de agente
- `worker` - Testar operações do worker
- `bulk` - Testar operações em lote
- `stats` - Testar estatísticas
- `summary` - Testar resumo do sistema
- `chat` - Testar mensagens do chat

## 🔄 Monitoramento em Tempo Real

### **Atualização Automática**
- Lista de agentes atualiza a cada 10 segundos
- Status do worker atualiza em tempo real
- Indicador visual mostra quando há atualizações

### **Indicador de Atividade**
- **Ponto verde piscando** quando o worker está ativo
- **Mensagem temporária** "Atualização em tempo real ativa"
- **Contadores atualizados** automaticamente

## 🛠️ Troubleshooting

### **Problemas Comuns**

1. **Agentes não aparecem**
   ```bash
   # Verificar se o AgentManager está inicializado
   curl http://localhost:3000/api/agents
   ```

2. **Worker não inicia**
   ```bash
   # Verificar logs do servidor
   curl http://localhost:3000/api/agents/worker/status
   ```

3. **Interface não carrega**
   ```bash
   # Verificar se o servidor web está rodando
   curl http://localhost:3000/api/health
   ```

### **Logs e Debug**
- Verificar console do navegador para erros JavaScript
- Verificar logs do servidor Flask
- Usar ferramentas de desenvolvedor do navegador

## 📈 Próximas Funcionalidades

### **Planejadas**
- [ ] **Dashboard avançado** com gráficos e métricas
- [ ] **Alertas em tempo real** via WebSocket
- [ ] **Configuração visual** de agentes
- [ ] **Exportação de relatórios** em PDF/Excel
- [ ] **Backup e restauração** de configurações
- [ ] **Templates de agentes** pré-configurados

### **Melhorias**
- [ ] **Interface responsiva** para mobile
- [ ] **Tema dark/light** automático
- [ ] **Notificações push** para eventos importantes
- [ ] **API REST completa** para integração externa
- [ ] **Suporte a múltiplos usuários** com autenticação

## 🎉 Conclusão

A integração do Agent Manager na interface web está **100% funcional** e oferece:

✅ **Controle completo** dos agentes via interface visual
✅ **Monitoramento em tempo real** com indicadores visuais
✅ **Operações em lote** para gerenciar múltiplos agentes
✅ **Histórico detalhado** de todos os eventos
✅ **Estatísticas avançadas** com métricas completas
✅ **API robusta** para automação e integração
✅ **Interface intuitiva** e responsiva

O sistema está pronto para uso em produção e oferece todas as funcionalidades do CLI através da interface web moderna e intuitiva.
