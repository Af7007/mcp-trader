# 🚀 Iniciar Agente BTC Loss Zero - Guia Rápido

## ⚡ Comece Agora (3 passos)

### Passo 1: Verifique Pré-requisitos

Certifique-se que:
- ✅ **MetaTrader 5 está ABERTO**
- ✅ **Você está logado na sua conta**
- ✅ **Python 3.8+ está instalado**

### Passo 2: Valide a Instalação

Abra o terminal/prompt na pasta do projeto:

```bash
python TESTAR_LOSS_ZERO.py
```

**Esperado**: `Resultado: 5/5 testes passaram`

Se falhar em algum teste, verifique o erro e ajuste.

### Passo 3: Inicie o Agente

**Opção A - Windows (Recomendado):**
```bash
RODAR_LOSS_ZERO.bat
```

**Opção B - Python Direto:**
```bash
python EXECUTAR_LOSS_ZERO.py
```

## ✅ Agente Está Rodando

Você verá na tela:
```
======================================================================
🤖 AGENTE BTC LOSS ZERO - TRAILING STOP ILIMITADO
======================================================================
Estratégia: Zero Losses + Lucros Ilimitados
Pressione Ctrl+C para parar
======================================================================
```

## 📊 Monitor em Tempo Real

O agente mostrará:
- Ciclo atual e horário
- Status de mercado
- Sinais detectados
- Posições abertas/fechadas
- Lucros e estatísticas

Exemplo:
```
Ciclo #1
Analisando mercado...
RSI: 35.2 - Sinal BUY detectado!

Ciclo #2
Posição aberta: LONG @ $100,000
Lucro: +0.2%
Trailing: INATIVO

Ciclo #3
Lucro: +0.6%
Trailing: ATIVADO em 0.5%
```

## 🛑 Parar Agente

Pressione `Ctrl+C` no terminal:
```
^C
==================================================
Agente BTC Loss Zero parado pelo usuário
==================================================
```

## 📱 Notificações via Telegram (OPCIONAL)

Se quiser receber notificações no Telegram:

1. Leia: `CONFIGURAR_TELEGRAM.md`
2. Configure seu bot
3. Reinicie o agente

Sem Telegram, o agente funciona normalmente - apenas sem notificações!

## 🔍 Troubleshooting

### Agente não inicializa

**Erro**: `Falha ao inicializar MT5`
- MT5 não está aberto
- Solução: Abra MetaTrader 5

**Erro**: `Símbolo BTCUSDc não encontrado`
- Símbolo não disponível na sua corretora
- Solução: Altere para `BTCUSDm` ou outro símbolo disponível

### Agente roda mas sem trades

Mercado pode estar em range (sem movimento extremo):
- RSI entre 30-70 = Neutro (sem sinais)
- Espere por movimento maior
- Verifique logs para status

### Telegram aviso

```
WARNING - ⚠️ Telegram não disponível
```

Isso é **NORMAL**! Significa que:
- Telegram não foi configurado (OPCIONAL)
- OU as credenciais estão incorretas

O agente funciona perfeitamente sem Telegram!

## 📈 Configuração Padrão

```
Symbol: BTCUSDc
Volume: 0.05 lots
Trailing Start: 0.5% de lucro
Trailing Increment: +0.1% por movimento
Check Interval: 15 segundos
BUY/SELL: Ambos habilitados
```

Para alterar, edite `EXECUTAR_LOSS_ZERO.py`:

```python
agent = BTCLossZeroOtimizado(
    symbol="BTCUSDc",      # Alterar aqui
    volume=0.05,           # Ou aqui
    check_interval=15,     # Etc...
)
```

## 📚 Documentação Completa

- `GUIA_LOSS_ZERO_OTIMIZADO.md` - Estratégia detalhada
- `CONFIGURAR_TELEGRAM.md` - Setup Telegram (opcional)
- `TESTAR_LOSS_ZERO.py` - Testes de validação

## ✨ Dicas

✅ **Volume**: Comece com 0.01-0.02 e aumente gradualmente
✅ **Saldo**: Mínimo recomendado $300-500
✅ **24/7**: Deixe rodando para máximas oportunidades
✅ **Monitor**: Monitore a primeira hora manualmente
✅ **Ajustes**: Altere parâmetros conforme necessário

## 🎯 Próximas Etapas

1. ✅ Executar `TESTAR_LOSS_ZERO.py`
2. ✅ Iniciar com `EXECUTAR_LOSS_ZERO.py`
3. ✅ Monitorar primeiros trades
4. ✅ Ajustar volume se necessário
5. ✅ Deixar rodando 24/7

---

**Pronto para começar?**

```bash
python EXECUTAR_LOSS_ZERO.py
```

Boa sorte! 🚀
