# 💬 Como Acessar o Chatbot de Trading

## ⚡ Acesso Rápido

### Terminal Interativo (Recomendado)

```powershell
cd c:\mcp-trader
.\.venv\Scripts\Activate.ps1
python run_chatbot.py
```

Você verá:

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🤖 TRADING CHATBOT - MODO INTERATIVO             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

✅ Conectado ao MT5 com sucesso!

💬 COMANDOS DISPONÍVEIS:
...
```

---

## 📊 Comandos Disponíveis

### 📈 Informações da Conta

```
💬 Você: saldo
📊 Obtendo informações da conta...
   ✅ Saldo: $1120.17
   ✅ Equity: $1120.17
   ✅ Margem Livre: $1120.17
```

```
💬 Você: posições
📋 Obtendo posições abertas...
   ✅ Nenhuma posição aberta
```

### 💹 Dados de Mercado

```
💬 Você: preço EURUSD
💹 Obtendo preço de EURUSDc...
   ✅ EURUSDc:
      Bid: 1.16100
      Ask: 1.16108
```

```
💬 Você: velas EURUSD
📊 Obtendo velas de EURUSDc...
   ✅ Últimas 3 velas de EURUSDc:
      1. O:1.16144 H:1.16152 L:1.16072 C:1.16088
      2. O:1.16088 H:1.16109 L:1.16045 C:1.16055
      3. O:1.16054 H:1.16101 L:1.16054 C:1.16100
```

### 🔄 Operações de Trading

```
💬 Você: comprar EURUSD 0.1
🟢 Executando compra de 0.1 EURUSDc...
   ✅ Ordem executada!
      Preço: 1.16108
      Order: 123456
```

```
💬 Você: vender EURUSD 0.1
🔴 Executando venda de 0.1 EURUSDc...
   ✅ Ordem executada!
      Preço: 1.16100
      Order: 123457
```

```
💬 Você: fechar 123456
🔒 Fechando posição 123456...
   ✅ Posição fechada!
      Preço: 1.16105
```

### 🛠️ Utilitários

```
💬 Você: ajuda
💬 Você: help
```

Mostra lista de comandos

```
💬 Você: sair
💬 Você: exit
```

Sai do chatbot

---

## 🎯 Exemplos Práticos

### Exemplo 1: Verificar Saldo

```powershell
python run_chatbot.py
```

```
💬 Você: saldo
📊 Obtendo informações da conta...
   ✅ Saldo: $1120.17
```

### Exemplo 2: Executar Compra

```
💬 Você: comprar EURUSD 0.1
🟢 Executando compra de 0.1 EURUSDc...
   ✅ Ordem executada!
      Preço: 1.16108
      Order: 123456

💬 Você: posições
📋 Obtendo posições abertas...
   ✅ 1 posição(ões) aberta(s):
      • EURUSDc: 0.1 lots @ 1.16108
```

### Exemplo 3: Fechar Posição

```
💬 Você: fechar 123456
🔒 Fechando posição 123456...
   ✅ Posição fechada!
      Preço: 1.16105
```

---

## 🔧 Pré-requisitos

Antes de acessar o chatbot, certifique-se de:

1. ✅ **MT5 Terminal rodando e logado**
   - Abra MetaTrader 5
   - Faça login com suas credenciais

2. ✅ **Testes passando**
   ```powershell
   python test_mt5_direct.py
   ```
   Resultado esperado: `6/6 testes passaram`

3. ✅ **Ambiente virtual ativado**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

---

## 🆘 Troubleshooting

### Erro: "Não foi possível conectar ao MT5"

**Solução:**
1. Verifique se MT5 Terminal está rodando
2. Verifique se está logado
3. Execute: `python test_mt5_direct.py`
4. Tente novamente

### Erro: "Símbolo não encontrado"

**Solução:**
1. Use símbolos com "c" no final (cents)
   - ✅ EURUSDc
   - ✅ GBPUSDc
   - ✅ XAUUSDm

### Erro: "Ordem rejeitada"

**Solução:**
1. Verifique saldo suficiente
2. Verifique volume mínimo (0.01 para cents)
3. Verifique horário de negociação

---

## 📚 Referências

- **Testes**: `python test_mt5_direct.py`
- **Exemplos**: `python example_chatbot_mt5_usage.py`
- **Documentação**: `docs/CHATBOT_MT5_INTEGRATION.md`

---

## 🎉 Pronto!

Agora você pode usar o chatbot para:
- ✅ Verificar saldo e posições
- ✅ Obter preços e dados de mercado
- ✅ Executar operações de trading
- ✅ Gerenciar posições

**Divirta-se tradando!** 🚀📈
