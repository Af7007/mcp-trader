# 🚀 Visualizador BTC Loss Zero - Quick Start

## Opção 1: Teste Rápido (Sem Agente Real)

### 1. Gerar Dados de Teste
```batch
TESTAR_VISUALIZADOR_LOSS_ZERO.bat
```

Escolha opção **2** para teste dinâmico (simulação contínua)

### 2. Instalar EA no MT5

1. Abrir **MetaEditor** (F4)
2. Abrir arquivo: `EA_BTC_Loss_Zero_Visualizer.mq5`
3. **Compilar** (F7) - verificar 0 erros
4. Fechar MetaEditor
5. No MT5: **Navigator** (Ctrl+N) → **Expert Advisors**
6. Arrastar `EA_BTC_Loss_Zero_Visualizer` para gráfico **BTCUSDc**
7. Clicar **OK** nas configurações
8. Ativar **AutoTrading** (botão verde no topo)

### 3. Ver Resultado

Você deve ver:
- 📊 Painel de informações no canto superior esquerdo
- 🔵🔴🟢🟡 Linhas no gráfico (quando há posição simulada)
- Atualização automática a cada 5 segundos

---

## Opção 2: Uso Real com Agente

### 1. Iniciar Agente Python
```batch
python EXECUTAR_LOSS_ZERO.py
```

### 2. Adicionar EA ao MT5
(Mesmos passos da Opção 1, item 2)

### 3. Monitorar Trading ao Vivo

O visualizador mostrará **em tempo real**:
- Preço de entrada (azul)
- Stop Loss (vermelho) - $4 proteção
- Take Profit (verde) - ~$20 alvo
- Trailing Stop (amarelo tracejado) - sobe conforme lucro

---

## 🎨 O Que Você Verá

### Sem Posição
```
=== BTC LOSS ZERO AGENT ===
Status: ANALYZING
No position - Scanning for signals...
Using: RSI + MFI dual confirmation
```

### Com Posição + Trailing Ativo
```
=== BTC LOSS ZERO AGENT ===
Status: TRADING
Position: BUY #999999
Entry: 110220.00
Current: 110235.50
Profit: $15.50 ✅
Trailing: ACTIVE ($14.50)
Trail Level: 110230.50
SL: 110216.00 ($4 max)
TP: 110240.00 (~$20)
```

**Linhas no gráfico:**
```
  🟢 TP ━━━━━━━━━━━━━━ 110240.00 (~$20)
   |
  🟡 Trailing ╍╍╍╍╍╍╍╍ 110230.50 (Defending $14.50)
   |
  💰 Current: 110235.50 (+$15.50)
   |
  🔵 Entry ━━━━━━━━━━━ 110220.00 (BUY)
   |
  🔴 SL ━━━━━━━━━━━━━━ 110216.00 ($4 max)
```

---

## ❓ Problemas?

**Não aparece nada?**
→ Verificar que o arquivo existe: `C:\mcp-trader\btc_loss_zero_data.json`

**Erro ao abrir arquivo?**
→ Iniciar o agente Python ou script de teste

**Linhas não aparecem?**
→ Normal se não há posição. Aguardar sinal ou usar teste dinâmico

---

## 📚 Documentação Completa

- `GUIA_VISUALIZADOR_LOSS_ZERO.md` - Guia completo
- `VISUALIZADOR_IMPLEMENTADO.md` - Detalhes técnicos

---

✅ **Pronto para usar!**
