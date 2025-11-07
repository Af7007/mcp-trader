# CORREÇÃO: Recursão Infinita no Gold AI Agent

## Problema Identificado
Erro "maximum recursion depth exceeded" causado por loop de recursão entre GoldAIAgent e GoldLossZeroSimple.

## Plano de Correção

### ✅ TAREFA 1: Analisar Código e Identificar Recursão
- [x] Revisar estrutura de herança entre GoldAIAgent e GoldLossZeroSimple
- [x] Identificar método _analyze_and_open() como fonte do loop
- [x] Verificar dependências (ollama_client, btc_logger, mt5_direct_client)

### ⏳ TAREFA 2: Corrigir Loop de Recursão
- [ ] Modificar _analyze_and_open() no gold_ai_agent.py
- [ ] Eliminar chamada a super()._analyze_and_open()
- [ ] Implementar fallback sem recursão
- [ ] Adicionar proteções contra loops infinitos

### ⏳ TAREFA 3: Melhorar Tratamento de Erros
- [ ] Adicionar try/catch específicos no ollama_client.py
- [ ] Implementar timeout e retry nas chamadas de IA
- [ ] Adicionar circuit breaker para erros consecutivos
- [ ] Melhorar logs de debug

### ⏳ TAREFA 4: Otimizar Inicialização
- [ ] Adicionar cache de decisões da IA
- [ ] Implementar cooldown inteligente
- [ ] Melhorar verificação de conectividade MT5

### ⏳ TAREFA 5: Testes e Validação
- [ ] Criar teste isolado para verificar recursão
- [ ] Testar agente corrigido
- [ ] Validar funcionamento da IA
- [ ] Verificar se todos os erros foram eliminados

## Arquivos a Modificar
1. `src/agents/gold_ai_agent.py` - Correção principal
2. `src/core/ollama_client.py` - Tratamento de erros
3. `src/agents/gold_loss_zero_simple.py` - Proteções adicionais

## Status: EM PROGRESSO
Iniciado: 11/6/2025 16:46:42
