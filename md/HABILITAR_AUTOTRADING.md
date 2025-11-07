# Habilitar AutoTrading no MetaTrader 5

## Problema

Ao tentar abrir posições, o agente retorna erro:

```
AutoTrading disabled by client (retcode 10027)
```

## Solução

O MetaTrader 5 desabilita trading automático por padrão por segurança. Para habilitar:

### Passo 1: Abra MetaTrader 5

### Passo 2: Vá para o Menu Tools

Na barra de menu, clique em: **Tools** → **Options**

### Passo 3: Abra a Aba "Expert Advisors"

Na janela de Options:
- Clique na aba **"Expert Advisors"**

### Passo 4: Marque as Opções

Na aba "Expert Advisors", você verá estas opções:

1. **☑ Allow automated trading** (marque isso!)
2. **☑ Allow DLL imports** (opcional, deixe marcado)
3. **☑ Allow WebRequests** (opcional)

### Passo 5: Especifique a URL do Servidor

Se estiver usando MCP Server:
- **URL: http://localhost:8000** (ou seu IP/porta)
- Marque como **"Allowed"**

### Passo 6: Clique OK

Salve as configurações clicando **OK**

### Passo 7: Reinicie o MetaTrader 5 (se necessário)

Algumas configurações requerem reinicialização para funcionar corretamente.

---

## Verificação Rápida

Após habilitar, você verá na barra superior do MT5:

```
[===] <- Botão de AutoTrading ATIVADO (verde)
```

Se o botão estiver cinza/desativado, clique nele para ativar.

---

## Agora Tente Novamente

Após habilitar AutoTrading, execute:

```bash
python EXECUTAR_LOSS_ZERO.py
```

O agente deverá agora:
✓ Conectar ao MT5
✓ Enviar ordens com sucesso
✓ Abrir posições BUY/SELL
✓ Gerenciar trailing stop
✓ Fechar com lucro

---

## Se Ainda Não Funcionar

1. Verifique se está realmente marcado "Allow automated trading"
2. Reinicie completamente o MT5
3. Tente novamente

---

## Para Agentes em Servidor

Se estiver usando um servidor (não local), adicione o IP do servidor à lista de URLs permitidas:

**Exemplo:**
```
http://192.168.1.100:8000
```

---

Pronto! AutoTrading está habilitado e o agente Loss Zero funcionará perfeitamente!
