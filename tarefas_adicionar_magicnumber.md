# Lista de Tarefas - Adicionar Coluna MagicNumber

## Objetivo
Adicionar uma coluna `magicnumber` à tabela `trades` do banco de dados para armazenar o número mágico das operações do MetaTrader 5.

## Tarefas

### 1. Análise e Diagnóstico
- [ ] Verificar a estrutura atual do banco de dados
- [ ] Analisar discrepâncias entre schema e funções do database.py
- [ ] Identificar onde o magicnumber deve ser armazenado

### 2. Atualização do Schema
- [ ] Modificar a função setup_database() para incluir a coluna magicnumber
- [ ] Criar função de migração para adicionar a coluna em bancos existentes
- [ ] Atualizar todas as consultas para incluir o campo magicnumber

### 3. Atualização das Funções
- [ ] Modificar create_trade() para incluir o parâmetro magicnumber
- [ ] Atualizar update_trade_status() se necessário
- [ ] Atualizar get_open_trades() para incluir o magicnumber
- [ ] Adicionar função para buscar trades por magicnumber

### 4. Integração com MT5
- [ ] Verificar como obter o magicnumber das posições MT5
- [ ] Atualizar agentes para capturar e salvar o magicnumber
- [ ] Modificar conexões MT5 para usar o magicnumber

### 5. Testes e Validação
- [ ] Testar a criação da tabela com a nova coluna
- [ ] Testar inserção de trades com magicnumber
- [ ] Verificar consulta de trades por magicnumber
- [ ] Testar migração de banco existente

### 6. Documentação
- [ ] Atualizar documentação das funções
- [ ] Criar exemplos de uso
- [ ] Documentar mudanças no schema

## Status: INICIADO
