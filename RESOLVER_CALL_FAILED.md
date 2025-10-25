# Solução: Terminal: Call Failed

## 🔴 O Erro

```
Erro ao obter rates: (-1, 'Terminal: Call failed')
❌ Erro ao calcular indicadores
```

Este erro ocorre quando o MT5 não consegue processar a solicitação de dados.

---

## 🔍 Diagnóstico

Execute o script de diagnóstico:

```batch
DIAGNOSTICO_MT5.bat
```

Este script verifica:
1. ✅ Conexão com MT5
2. ✅ MT5 inicializado e logado
3. ✅ Símbolos disponíveis
4. ✅ Obtenção de rates
5. ✅ Posições abertas
6. 💡 Problemas comuns

---

## 🛠️ Soluções Passo a Passo

### Solução 1: Verificar MT5 Aberto

**Passo 1**: Abra o Terminal Windows (cmd ou PowerShell)

**Passo 2**: Procure pela janela do MetaTrader 5
- Se não estiver aberto: Abra o MT5

**Passo 3**: Verifique se está logado
- Procure pelo número de conta na barra de título
- Se não estiver logado: Faça login (nome de usuário e senha)

**Passo 4**: Verifique o status da conexão
- Lado direito da barra de status deve estar verde
- Se vermelho: Problema de conexão com o broker

**Resultado esperado**:
```
[1] Verificando conexão com MT5...
    ✅ MT5 Client criado com sucesso

[2] Verificando inicialização do MT5...
    ✅ MT5 inicializado e respondendo
       Login: 1234567
       Servidor: Broker-Demo
       Saldo: $10,000.00
```

---

### Solução 2: Adicionar BTCUSDm ao Market Watch

**Passo 1**: Abra MetaTrader 5

**Passo 2**: Clique em **Exibir** → **Observação de Mercado** (ou Ctrl+M)

**Passo 3**: Na janela "Observação de Mercado", clique com botão direito

**Passo 4**: Selecione **Símbolos** (ou **Adicionar Símbolo**)

**Passo 5**: Na lista que aparece:
- Procure por **BTCUSDm**
- Se não estiver visível, procure por **BTC**
- Selecione e clique em **OK** ou **Mostrar**

**Passo 6**: BTCUSDm agora deve aparecer no Market Watch

**Resultado esperado**:
```
[3] Verificando símbolos disponíveis...
    ✅ BTCUSDm: DISPONÍVEL
       Bid: 109545.23500
       Ask: 109546.23500
       Spread: 10 points
```

---

### Solução 3: Verificar Horário de Mercado

**Passo 1**: Observe a barra de status do MT5
- Se houver mensagem "Mercado fechado" ou "Weekend":
  - Aguarde o mercado abrir (24/5 para crypto)

**Passo 2**: Verifique o dia e hora
- Crypto opera 24/5 (seg-sex, 24h)
- Forex também opera 24/5

**Passo 3**: Se estiver fora do horário:
- Aguarde a reabertura do mercado
- Use símbolos que estejam abertos

**Nota**: Se estiver fechado, você pode:
- Testar com histórico
- Usar dados anteriores
- Aguardar reabertura

---

### Solução 4: Reiniciar MT5

Se nenhuma das anteriores funcionar:

**Passo 1**: Feche o MT5 completamente
- Clique no X para fechar
- Aguarde 3-5 segundos

**Passo 2**: Reabra o MT5
- Execute MetaTrader 5 do menu Iniciar
- Faça login novamente

**Passo 3**: Teste novamente
```batch
DIAGNOSTICO_MT5.bat
```

---

### Solução 5: Verificar Broker

Se persistir o erro:

**Passo 1**: Verifique o servidor
- MT5 → Arquivo → Configurações
- Abra a aba "Servidor"
- Verifique se está logado no servidor correto

**Passo 2**: Teste a conexão
- MT5 → Ferramentas → Verificar Atualização
- Se conseguir conectar, a conexão está OK

**Passo 3**: Contate o broker
- Se houver problema de conectividade
- Entre em contato com o suporte técnico

---

## 📊 Exemplo de Diagnóstico Bem-Sucedido

```
======================================================================
🔍 DIAGNOSTICO DO MT5
======================================================================

[1] Verificando conexão com MT5...
    ✅ MT5 Client criado com sucesso

[2] Verificando inicialização do MT5...
    ✅ MT5 inicializado e respondendo
       Login: 1234567
       Servidor: XM-Demo
       Saldo: $10,000.00
       Equity: $10,000.00
       Margem Livre: $8,000.00

[3] Verificando símbolos disponíveis...
    ✅ BTCUSDm: DISPONÍVEL
       Bid: 109545.23500
       Ask: 109546.23500
       Spread: 10 points
    ✅ XAUUSDc: DISPONÍVEL
    ✅ EURUSDc: DISPONÍVEL
    ✅ GBPUSDc: DISPONÍVEL

[4] Testando obtenção de rates (M5)...
    ✅ BTCUSDm: 5 barras obtidas
       Última barra: Open=$109540.00, Close=$109545.23

[5] Verificando posições abertas...
    ✅ Nenhuma posição aberta

[6] Checklist de Problemas Comuns
✅ Nenhum problema detectado!

======================================================================
✅ DIAGNOSTICO CONCLUÍDO
======================================================================
```

---

## ⚠️ Erro Persistente?

Se o erro continuar após tentar todas as soluções:

### Verificar Logs

**Passo 1**: Abra o diagnóstico com mais detalhes
```bash
uv run python diagnostico_mt5.py > diagnostico_log.txt
```

**Passo 2**: Procure por mensagens de erro em `diagnostico_log.txt`

### Verificar MT5 Nativo

**Passo 1**: Teste o MT5 manualmente
- Abra o gráfico de BTCUSDm no MT5
- Verifique se consegue ver os preços e histórico
- Se conseguir, o problema está no agente, não no MT5

### Reiniciar Completamente

**Passo 1**: Feche tudo
```bash
taskkill /F /IM python.exe
# Feche MT5 também
```

**Passo 2**: Aguarde 10 segundos

**Passo 3**: Reabra MT5 e o agente
```batch
# Primeiro: abra o MT5 manualmente e espere ele carregar
# Depois: execute
RUN_BTC_AGENT.bat
```

---

## 📞 Próximas Etapas

Após resolver o erro:

1. ✅ Agente deve conectar e calcular indicadores
2. ✅ Começa a buscar sinais de compra/venda
3. ✅ Abre posições quando há sinal válido
4. ✅ Gerencia SL e TP automaticamente

Se tudo funcionar:
```
🤖 Agente BTCUSD inicializado
   Symbol: BTCUSDm
   Volume: 0.02
   Target Profit: $2.0
   Max Daily Trades: 20

🚀 Iniciando agente de trading BTCUSD...

📈 MERCADO (BTCUSDm):
   Preço: $109,545.23
   Tendência: UP
   RSI: 65.3
   ✅ Posição aberta!
```

---

## 🎯 Checklist de Resolução

- [ ] MT5 está aberto
- [ ] MT5 está logado na conta
- [ ] BTCUSDm está no Market Watch
- [ ] Mercado está aberto (24/5)
- [ ] Diagnóstico não mostra erros
- [ ] Agente conecta e calcula indicadores
- [ ] Agente abre posições

---

✅ **Problema resolvido!**

Se ainda tiver dúvidas, execute:
```batch
DIAGNOSTICO_MT5.bat
```

E compartilhe a saída do diagnóstico para análise.
